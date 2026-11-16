#define NOMINMAX
#include <windows.h>
#include <wincrypt.h>
#include <psapi.h>
#include <tlhelp32.h>
#include <algorithm>
#include <array>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <map>
#include <set>
#include <sstream>
#include <vector>
#include "correlation.h"
#include "fixture.h"
#include "journal.h"
#include "retail_profile.h"
#include "stage_a.h"
#include "window_evidence.h"

namespace fs = std::filesystem;
using namespace srr006;

static uint64_t ticks(FILETIME t) {
    return uint64_t(t.dwHighDateTime) << 32 | t.dwLowDateTime;
}
static uint64_t birth(HANDLE handle, bool process) {
    FILETIME created{}, ended{}, kernel{}, user{};
    const BOOL ok = process ? GetProcessTimes(handle, &created, &ended, &kernel, &user)
                            : GetThreadTimes(handle, &created, &ended, &kernel, &user);
    return ok ? ticks(created) : 0;
}
static bool read_context(HANDLE thread, CONTEXT& c, bool floating = false) {
    c.ContextFlags = CONTEXT_CONTROL | CONTEXT_INTEGER | CONTEXT_DEBUG_REGISTERS;
    if (floating) c.ContextFlags |= CONTEXT_FLOATING_POINT;
    return GetThreadContext(thread, &c);
}
// Compare x64 architectural state covered by the D5B resume check.
static bool same_execution_state(const CONTEXT& a, const CONTEXT& b) {
    return std::memcmp(&a.Rax, &b.Rax, 17 * sizeof(DWORD64)) == 0 &&
        std::memcmp(&a.FltSave, &b.FltSave, sizeof(a.FltSave)) == 0 &&
        a.MxCsr == b.MxCsr && a.SegCs == b.SegCs && a.SegSs == b.SegSs &&
        ((a.EFlags ^ b.EFlags) & ~DWORD{2}) == 0;
}
static std::array<Address, 4> slots(const CONTEXT& c) { return {c.Dr0,c.Dr1,c.Dr2,c.Dr3}; }
static constexpr uint64_t dr7_fields = 0xffff20ff;
static constexpr uint64_t dr6_causes = 0xe00f;
static constexpr DWORD tf = 0x100, rf = 0x10000, emergency_exit = 0x6006;

static std::string sha256(const fs::path& path) {
    HCRYPTPROV provider = 0;
    HCRYPTHASH hash = 0;
    std::string result;
    if (CryptAcquireContextW(&provider, nullptr, nullptr, PROV_RSA_AES, CRYPT_VERIFYCONTEXT) &&
        CryptCreateHash(provider, CALG_SHA_256, 0, 0, &hash)) {
        std::ifstream input(path, std::ios::binary);
        std::array<char, 65536> bytes;
        bool okay = bool(input);
        while (okay && input.read(bytes.data(), bytes.size()).gcount()) {
            okay = CryptHashData(hash, reinterpret_cast<BYTE*>(bytes.data()),
                                 static_cast<DWORD>(input.gcount()), 0);
        }
        BYTE digest[32];
        DWORD size = sizeof digest;
        if (okay && input.eof() && !input.bad() &&
            CryptGetHashParam(hash, HP_HASHVAL, digest, &size, 0) && size == sizeof digest) {
            constexpr char hex[] = "0123456789abcdef";
            for (BYTE value : digest) { result += hex[value >> 4]; result += hex[value & 15]; }
        }
    }
    if (hash) CryptDestroyHash(hash);
    if (provider) CryptReleaseContext(provider, 0);
    return result;
}

static bool same_file(HANDLE a, HANDLE b) {
    return bool(check_file_identity(a, b));
}

struct Thread {
    HANDLE handle;
    uint64_t created, generation;
    CONTEXT original{};
    bool armed = false;
    bool debug_written = false;
    Address start_address = 0;
    Correlation frames;
};

enum class ProfileRole { fixture, pinned_retail, retail };

struct OperatorPhase {
    const char* label;
    const char* row;
    const char* ack;
};
static constexpr OperatorPhase load_phases[]{
    {"MAIN_MENU_CONFIRMED", "operator_menu", "MENU_DURABLE"},
    {"LOAD_BEGIN", "load_begin", "LOAD_BEGIN_DURABLE"},
    {"PLAYER_CONTROL", "player_control", "PLAYER_CONTROL_DURABLE"},
    {"LODGE_BEGIN", "lodge_begin", "LODGE_BEGIN_DURABLE"},
    {"LODGE_END", "lodge_end", "LODGE_END_DURABLE"},
};
static constexpr OperatorPhase control_phases[]{
    {"CONTROL_MENU_CONFIRMED", "control_menu", "CONTROL_MENU_DURABLE"},
    {"CONTROL_LOAD_BEGIN", "control_load_begin", "CONTROL_LOAD_BEGIN_DURABLE"},
    {"SETTLED_GAMEPLAY", "control_settled", "SETTLED_GAMEPLAY_DURABLE"},
    {"CONTROL_END", "control_end", "CONTROL_END_DURABLE"},
};
static constexpr auto load_windows = std::array{"uncovered_startup", "post_arming_title",
    "menu_preload", "load_in_progress", "post_load", "lodge_transition", "lodge_interior"};

class Observer {
    Journal& journal;
    fs::path folder;
    std::wstring scenario;
    const ProfileRole profile_role;
    const bool late_attach;
    const bool non_killing;
    PROCESS_INFORMATION child{};
    HANDLE image;
    std::string digest;
    Address local, base = 0, ntdll = 0, loader_rva = 0;
    bool loader_identity = false;
    unsigned fresh_breakin_threads = 0;
    unsigned extent;
    Layout layout;
    std::array<Address, 4> addresses{};
    std::map<DWORD, Thread> threads;
    std::set<DWORD> pending_release;
    struct ModuleRecord { std::string name; bool continuity_only; };
    std::map<Address, ModuleRecord> modules;
    WindowEvidence windows;
    uint64_t created = 0, births = 0, continued = 0, foreign = 0;
    uint64_t phase_ack = 0, menu_ack = 0, stop_ack = 0, event_number = 0;
    uint64_t title_boundary = 0, stop_boundary = 0, retire_ack = 0;
    uint64_t load_phase_prior = 0, load_phase_ack = 0, load_refusal_ack = 0;
    std::string load_challenge;
    uint64_t recovery_after_generation = 0;
    uint64_t attach_requested_at = 0, arm_barrier = 0, armed_ack = 0;
    uint64_t steam_birth = 0;
    DWORD steam_pid = 0, session = 0;
    StageHandle steam_client;
    uint64_t first_invoked = 0, first_allocator = 0, rejected = 0;
    unsigned phase = 0, control_durable_phase = 0;
    uint64_t control_end = 0, context_writes = 0, blocked_context_writes = 0;
    bool loader = false, identity = false, healthy = true, stopped = false;
    bool handoff = false;
    bool retired = false, stop_durable = false;
    bool detached = false, recovery_attempted = false, disarmed = false;
    bool recovery_break_pending = false, recovery_break_owned = false;
    bool forced = false, exit_event = false, signaled = false;
    bool emergency_requested = false, recovery_unconfirmed = false, abrupt_queued = false;
    bool cross_phase = false, cross_menu = false;
    DWORD emergency_error = 0;
    DWORD event_exit = UINT32_MAX, process_exit = UINT32_MAX;
    std::array<uint64_t, 4> hits{};
    std::array<uint64_t, 4> after_stop{};
    std::array<uint64_t, 4> after_gap{};
    std::array<unsigned char, 16> loader_bytes{};
    std::array<unsigned char, 5> breakin_call{};
    DWORD held_breakin = 0;
    std::wstring loader_mapping;
    std::wstring steam_directory, game_directory;
    std::wstring overlay_expected{overlay_exe};
    std::vector<std::string> drift_reported;
    std::string run_id;
    LARGE_INTEGER frequency{};

    bool is(const wchar_t* name) const { return scenario == name; }
    bool retail_profile() const { return profile_role != ProfileRole::fixture; }
    bool retail_run() const { return profile_role == ProfileRole::retail; }
    bool staged_arming() const { return retail_run() || scenario.starts_with(L"admission-"); }
    bool stage_b() const { return is(L"stage-b") || scenario.starts_with(L"admission-stage-b-"); }

    bool control_b() const { return is(L"control-b") || scenario.starts_with(L"admission-control-b-"); }

    bool write_context(HANDLE thread, CONTEXT* context) {
        if (control_b()) {
            ++blocked_context_writes;
            gap();
            return false;
        }
        ++context_writes;
        return SetThreadContext(thread, context) != 0;
    }

    static uint64_t utc_now() {
        FILETIME utc{};
        GetSystemTimePreciseAsFileTime(&utc);
        return ticks(utc);
    }

    bool control_file(const wchar_t* name) const {
        const auto attributes = GetFileAttributesW((folder / name).c_str());
        return attributes != INVALID_FILE_ATTRIBUTES &&
               !(attributes & (FILE_ATTRIBUTE_REPARSE_POINT | FILE_ATTRIBUTE_DIRECTORY));
    }

    void continuity_gap() {
        if (control_b()) healthy = false;
        else windows.gap();
        for (auto& [tid, thread] : threads) thread.frames.clear();
    }
    void gap() {
        healthy = false;
        continuity_gap();
    }
    uint64_t row(const char* kind, DWORD tid, const std::string& fields = "", bool seal_stop = false) {
        LARGE_INTEGER qpc{};
        FILETIME utc{};
        QueryPerformanceCounter(&qpc);
        GetSystemTimePreciseAsFileTime(&utc);
        const auto thread = threads.find(tid);
        std::ostringstream out;
        out << "\"kind\":\"" << kind << "\",\"run\":\"" << run_id
            << "\",\"role\":\"" << (retail_run() ? "retail" : "fixture")
            << "\",\"method\":\"" << (late_attach ? "late_attach" : "creation")
            << "\",\"qpc\":" << qpc.QuadPart
            << ",\"qpc_frequency\":" << frequency.QuadPart << ",\"utc_filetime\":" << ticks(utc)
            << ",\"pid\":" << child.dwProcessId << ",\"process_birth\":" << created
            << ",\"tid\":" << tid << ",\"thread_birth\":"
            << (thread == threads.end() ? 0 : thread->second.created)
            << ",\"generation\":" << (thread == threads.end() ? 0 : thread->second.generation)
            << ",\"base\":" << base << ",\"extent\":" << extent
            << ",\"image_sha256\":\"" << digest << "\",\"identity\":" << identity
            << ",\"phase\":" << phase << ",\"stopped\":" << stopped
            << ",\"healthy\":" << healthy << ",\"event\":" << event_number << fields;
        if (control_b()) out << ",\"control_mode\":\"debugger_only\"";
        if (!journal.append(out.str(), seal_stop)) { gap(); return 0; }
        return journal.accepted;
    }

    bool mapped(Address address, void* data, size_t size) const {
        SIZE_T received = 0;
        return ReadProcessMemory(child.hProcess, reinterpret_cast<void*>(address), data,
                                 size, &received) && received == size;
    }
    AdmissionCheck attach_preflight() {
        if (auto result = check_process_epoch(child.hProcess, child.dwProcessId, created); !result)
            return result;
        wchar_t path[32768]{};
        DWORD length = ARRAYSIZE(path);
        if (auto result = check_debugger_absent(child.hProcess); !result) return result;
        if (!QueryFullProcessImageNameW(child.hProcess, 0, path, &length))
            return win32_failure("target_image_path_query", "QueryFullProcessImageNameW");
        {
            const auto reported = read_file(path);
            if (!reported) return win32_failure("target_backing_open", "CreateFileW");
            if (auto result = check_file_identity(reported.get(), image); !result) {
                result.detail = "target_backing";
                return result;
            }
        }
        // The stopped verifier still authenticates the event's backing file,
        // executable bytes and relocation state before any register writes.
        if (!retail_run()) return {};
        if (_wcsicmp(path, retail_exe)) return {"target_retail_path_mismatch"};
        if (auto result = check_interactive_user(child.hProcess, child.dwProcessId, session); !result)
            return result;
        const StageHandle census(CreateToolhelp32Snapshot(TH32CS_SNAPMODULE, child.dwProcessId));
        if (census.get() == INVALID_HANDLE_VALUE)
            return win32_failure("module_snapshot", "CreateToolhelp32Snapshot");
        MODULEENTRY32W item{};
        item.dwSize = sizeof item;
        return scan_attach_modules([&] { return Module32FirstW(census.get(), &item); },
                                  [&] { return Module32NextW(census.get(), &item); },
                                  [&](bool& main_checked, bool& loader_checked) -> AdmissionCheck {
            const auto at = reinterpret_cast<Address>(item.modBaseAddr);
            if (_wcsicmp(item.szModule, L"Starfield.exe") == 0) {
                if (main_checked) return {"main_image_duplicate"};
                if (_wcsicmp(item.szExePath, retail_exe)) return {"main_image_path_mismatch"};
                const auto mapping = verify_loaded_mapping(child.hProcess, at, retail_image_profile);
                if (!mapping) {
                    auto result = mapping.diagnostic;
                    if (result) result.predicate = mapping.failure;
                    result.detail = "main_image_mapping";
                    result.rva = mapping.rva;
                    return result;
                }
                main_checked = true;
            }
            if (_wcsnicmp(item.szModule, L"sfse", 4) == 0) return {"sfse_module_present"};
            if (_wcsicmp(item.szModule, L"gameoverlayrenderer64.dll") == 0) {
                const auto overlay = read_file(item.szExePath);
                auto result = overlay ? check_backing_path(overlay.get(), overlay_expected) :
                    win32_failure("overlay_backing_open", "CreateFileW");
                if (!result) {
                    row("overlay_lookalike", 0,
                        ",\"mapped_name\":\"gameoverlayrenderer64.dll\",\"reason\":\"origin\"");
                    result.detail = "overlay_origin";
                    return result;
                }
                // Credible Steam origin: a pinned match passes silently; an
                // independently updated overlay is recorded drift and still
                // admissible. Both identities are preserved in the journal.
                steam_component_fields(L"gameoverlayrenderer64.dll", overlay.get(),
                                       overlay_sha256_srr008);
            }
            if (_wcsicmp(item.szModule, L"ntdll.dll") == 0) {
                const auto file = read_file(item.szExePath);
                const DWORD open_error = file ? ERROR_SUCCESS : GetLastError();
                if (loader_checked) return {"ntdll_duplicate"};
                if (!file) return {"ntdll_backing_open", "CreateFileW", open_error};
                if (auto result = check_file_identity(file.get(), loader_file); !result) {
                    result.detail = "ntdll_backing";
                    return result;
                }
                if (auto result = check_attach_code(child.hProcess, at); !result) {
                    result.detail = "ntdll_attach_mapping";
                    return result;
                }
                loader_checked = true;
            }
            return {};
        });
    }
    AdmissionCheck attach_eligibility() const {
        if (journal.failed) return {"journal_unavailable"};
        if (auto result = check_process_epoch(child.hProcess, child.dwProcessId, created); !result) {
            result.detail = "target_epoch_before_ownership";
            return result;
        }
        if (!retail_run()) return {};
        if (!steam_pid) return {"steam_pid_unset"};
        if (auto result = check_process_epoch(steam_client.get(), steam_pid, steam_birth); !result) {
            result.detail = "steam_epoch";
            return result;
        }
        if (auto result = check_process_epoch(child.hProcess, child.dwProcessId, created); !result) {
            result.detail = "target_epoch_during_ownership";
            return result;
        }
        if (auto result = check_interactive_user(child.hProcess, child.dwProcessId, session); !result)
            return result;
        if (control_file(L"cancel-before-target")) return {"operator_cancel"};
        if (!control_b() && marker(L"stop.request", "STOP", 3)) return {"operator_stop"};
        return {};
    }
    RetailVerification verify_creation(const CREATE_PROCESS_DEBUG_INFO& info) const {
        if (retail_profile())
            return verify_retail_mapping(child.hProcess, image, info, child.dwProcessId, created);
        const auto dos = reinterpret_cast<const IMAGE_DOS_HEADER*>(local);
        const auto pe = reinterpret_cast<const IMAGE_NT_HEADERS64*>(local + dos->e_lfanew);
        const auto header_size = pe->OptionalHeader.SizeOfHeaders;
        const auto code_size = uint32_t(reinterpret_cast<Address>(&fixture_end) -
                                        reinterpret_cast<Address>(&guard_site));
        std::array<unsigned char, 4096> header_bytes{};
        LARGE_INTEGER original{}, zero{};
        DWORD obtained = 0;
        if (header_size > header_bytes.size() ||
            !SetFilePointerEx(image, zero, &original, FILE_CURRENT) ||
            !SetFilePointerEx(image, zero, nullptr, FILE_BEGIN))
            return {base, extent, "fixture_disk_header"};
        const bool read_header = ReadFile(image, header_bytes.data(), header_size, &obtained, nullptr) &&
                                 obtained == header_size;
        const bool restored = SetFilePointerEx(image, original, nullptr, FILE_BEGIN) != 0;
        if (!read_header || !restored) return {base, extent, "fixture_disk_header"};
        IMAGE_NT_HEADERS64 disk_pe{};
        std::memcpy(&disk_pe, header_bytes.data() + dos->e_lfanew, sizeof disk_pe);
        const auto header = sha256_memory(header_bytes.data(), header_size);
        const auto code = sha256_memory(&guard_site, code_size);
        LARGE_INTEGER length{};
        if (!GetFileSizeEx(image, &length)) return {base, extent, "fixture_file_size"};
        const ImageWindow checks[] = {{0, header_size, header, false},
            {uint32_t(layout.sites[0]), code_size, code, true}};
        const ImageSlot slots[] = {{uint32_t(layout.vtable + 0x10), uint32_t(layout.sites[2])}};
        const ImageProfile profile{digest, digest, uint64_t(length.QuadPart),
            disk_pe.OptionalHeader.ImageBase, extent, checks, slots};
        return verify_stopped_mapping(child.hProcess, image, info, child.dwProcessId, created, profile);
    }
    bool owns(const CONTEXT& c) const {
        return slots(c) == addresses && (c.Dr7 & dr7_fields) == 0x55 && !(c.EFlags & tf);
    }
    bool unowned(const CONTEXT& c) const {
        return !(c.Dr7 & dr7_fields) && !(c.Dr6 & dr6_causes) &&
               !(c.EFlags & (tf | rf)) && slots(c) == std::array<Address, 4>{};
    }
    enum class Census { running, held, prearm, inventory };

    // Only the running slot check takes balanced, observer-owned suspensions.
    // A thread born/exiting around a snapshot can make it indeterminate.
    bool thread_census(Census mode) {
        const bool require_slots = !control_b() && mode != Census::prearm;
        const bool held = mode == Census::held || mode == Census::prearm;
        if (!identity) return false;
        HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0);
        if (snapshot == INVALID_HANDLE_VALUE) return false;
        THREADENTRY32 item{};
        item.dwSize = sizeof item;
        bool complete = Thread32First(snapshot, &item) != 0;
        size_t observed = 0;
        if (complete) do {
            if (item.th32OwnerProcessID != child.dwProcessId) continue;
            ++observed;
            const auto entry = threads.find(item.th32ThreadID);
            if (entry == threads.end() || pending_release.contains(item.th32ThreadID) ||
                (require_slots && !entry->second.armed)) {
                complete = false;
                continue;
            }
            const auto& thread = entry->second;
            if (mode == Census::inventory) {
                if (birth(thread.handle, false) != thread.created ||
                    WaitForSingleObject(thread.handle, 0) != WAIT_TIMEOUT) complete = false;
                continue;
            }
            if (!held && SuspendThread(thread.handle) == DWORD(-1)) { complete = false; continue; }
            CONTEXT c{};
            const bool readback = read_context(thread.handle, c);
            // Simulate a persistent loss at the same decision boundary as the
            // real readback. Windows may restore loader-exception context
            // transiently cleared by the separate native injection control.
            if (!held && item.th32ThreadID == child.dwThreadId) {
                if (is(L"slot-loss")) c.Dr7 = 0;
                if (is(L"admission-slot-replaced")) c.Dr3 ^= 1;
            }
            const bool valid = birth(thread.handle, false) == thread.created && readback &&
                               (require_slots ? owns(c) : unowned(c));
            bool released = held || ResumeThread(thread.handle) != DWORD(-1);
            if (!released && staged_arming()) {
                // Resume only the suspension acquired above. A failed
                // release leaves an exact-handle obligation, not a retry of
                // the observation or permission to terminate the process.
                gap();
                row("suspension_release_unconfirmed", item.th32ThreadID);
                const auto deadline = GetTickCount64() + 250;
                do {
                    released = ResumeThread(thread.handle) != DWORD(-1) ||
                               WaitForSingleObject(thread.handle, 0) == WAIT_OBJECT_0;
                    if (!released) Sleep(10);
                } while (!released && GetTickCount64() < deadline);
                if (!released) {
                    pending_release.insert(item.th32ThreadID);
                    recovery_unconfirmed = true;
                    std::puts("SUSPENSION_RELEASE_UNCONFIRMED");
                    std::fflush(stdout);
                }
            }
            if (!valid || !released) complete = false;
        } while (Thread32Next(snapshot, &item));
        complete = complete && GetLastError() == ERROR_NO_MORE_FILES;
        CloseHandle(snapshot);
        return complete && observed == threads.size() && observed != 0;
    }
    bool module_census() const {
        HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE, child.dwProcessId);
        if (snapshot == INVALID_HANDLE_VALUE) return false;
        MODULEENTRY32W item{};
        item.dwSize = sizeof item;
        size_t count = 0;
        bool complete = Module32FirstW(snapshot, &item) != 0;
        if (complete) do {
            const auto address = reinterpret_cast<Address>(item.modBaseAddr);
            if (address == base) continue;
            if (!modules.contains(address)) complete = false;
            ++count;
        } while (Module32NextW(snapshot, &item));
        complete = complete && GetLastError() == ERROR_NO_MORE_FILES;
        CloseHandle(snapshot);
        return complete && ntdll && count == modules.size();
    }
    bool checkpoint(Census mode = Census::running) {
        return loader && thread_census(mode) && (!late_attach || module_census()) &&
               (!staged_arming() || (stage_owner() && critical_mapping()));
    }
    bool held_slots() const {
        for (const auto& [tid, thread] : threads) {
            if (WaitForSingleObject(thread.handle, 0) == WAIT_OBJECT_0) continue;
            CONTEXT context{};
            if (!thread.armed || birth(thread.handle, false) != thread.created ||
                !read_context(thread.handle, context) || !owns(context)) return false;
        }
        return true;
    }
    void periodic_readback(bool held) {
        if (control_b() || !staged_arming() || !loader || stopped || !healthy) return;
        const auto now = GetTickCount64();
        auto& next = held ? next_held_readback : next_readback;
        if (now < next) return;
        next = now + 2000;
        // Tool Help census while another debug event is pending can see a
        // born/exiting thread outside our processed-event prefix.
        // Stage B uses delivered debug events for periodic slot sampling.
        // Keep exact identity/mapping on idle ticks and full operator checkpoints.
        const bool defer_threads = !held && stage_b();
        const bool checked = (defer_threads ||
                              (held ? held_slots() : thread_census(Census::running) && module_census())) &&
                             stage_owner() && critical_mapping();
        if (!checked) gap();
        row("periodic_readback", 0, ",\"checkpoint\":" + std::to_string(checked) +
            ",\"census_attempted\":" + std::to_string(!held && !defer_threads) +
            ",\"thread_readback_deferred\":" + std::to_string(defer_threads));
    }
    bool acknowledged(uint64_t sequence) const {
        return sequence && sequence <= journal.durable.load();
    }
    bool stop_acknowledged() const {
        return late_attach ? journal.stop_sealed(stop_boundary) : acknowledged(stop_boundary);
    }
    bool wait_durable(uint64_t sequence) const {
        if (!sequence) return false;
        while (!acknowledged(sequence) && !journal.failed &&
               (!child.hProcess || exact_running_process())) Sleep(20);
        return acknowledged(sequence);
    }
    bool add(DWORD tid, HANDLE handle, Address start_address = 0) {
        const auto stamp = birth(handle, false);
        if ((!identity && !staged_arming()) || !stamp ||
            GetProcessIdOfThread(handle) != child.dwProcessId || GetThreadId(handle) != tid)
            return false;
        auto [entry, inserted] = threads.try_emplace(tid, Thread{handle, stamp, ++births});
        if (!inserted) return false;
        auto& thread = entry->second;
        thread.start_address = start_address;
        if (control_b() || disarmed || (staged_arming() && (!loader || !healthy))) return true;
        return arm(tid, thread);
    }
    bool arm(DWORD tid, Thread& thread) {
        const HANDLE handle = thread.handle;
        auto& c = thread.original;
        if (!read_context(handle, c, stage_b())) return false;
        // Inject a conflicting original snapshot at the decision boundary.
        CONTEXT before = c;
        if (is(L"conflict") && tid == child.dwThreadId) before.Dr7 |= 1;
        std::ostringstream state;
        state << ",\"original_dr\":[" << before.Dr0 << ',' << before.Dr1 << ','
              << before.Dr2 << ',' << before.Dr3 << "],\"original_dr6\":" << before.Dr6
              << ",\"original_dr7\":" << before.Dr7 << ",\"original_flags\":" << before.EFlags;
        if (!row("arm_attempt", tid, state.str()) && staged_arming()) return false;
        if (!unowned(before)) return false;
        const bool recovered = stage_b();
        const bool disposable = recovered && !retail_run();
        if (disposable && control_file(L"fixture-omit-arm")) {
            row("fixture_arm_omitted", tid);
            return false;
        }
        CONTEXT armed = c;
        armed.ContextFlags = CONTEXT_DEBUG_REGISTERS;
        armed.Dr0 = addresses[0]; armed.Dr1 = addresses[1];
        armed.Dr2 = addresses[2]; armed.Dr3 = addresses[3];
        armed.Dr7 = (armed.Dr7 & ~dr7_fields) | 0x55;
        if (recovered) armed.Dr6 = 0;
        CONTEXT check{};
        if (!write_context(handle, &armed)) return false;
        thread.debug_written = true;
        const bool withheld = disposable && control_file(L"fixture-withhold-arm-readback");
        const bool sampled = !withheld && read_context(handle, check, recovered);
        if (!sampled && !recovered) return false;
        if (is(L"readback") && tid == child.dwThreadId) check.Dr3 ^= 1;
        const bool preserved = !recovered || (sampled && same_execution_state(c, check));
        const bool verified = sampled && owns(check) && !(check.EFlags & rf) &&
                              (check.Dr6 & dr6_causes) == 0 && preserved;
        std::ostringstream actual;
        actual << ",\"dr\":[" << check.Dr0 << ',' << check.Dr1 << ',' << check.Dr2 << ','
               << check.Dr3 << "],\"dr6\":" << check.Dr6 << ",\"dr7\":" << check.Dr7
               << ",\"flags\":" << check.EFlags << ",\"verified\":" << verified;
        if (recovered)
            actual << ",\"context_sampled\":" << sampled
                   << ",\"execution_state_preserved\":" << preserved;
        if (recovered && !verified) {
            // Restore only the debug registers changed on this exact held
            // thread. A failed readback never counts as a qualified arm.
            CONTEXT original = c, restored{};
            original.ContextFlags = CONTEXT_DEBUG_REGISTERS;
            const bool restored_ok = write_context(handle, &original) &&
                read_context(handle, restored) && unowned(restored) && slots(restored) == slots(c);
            thread.debug_written = !restored_ok;
            row("arm_rollback", tid, ",\"verified\":" + std::to_string(restored_ok));
        }
        const auto recorded = row("arm_readback", tid, actual.str());
        thread.armed = verified;
        return verified && (!staged_arming() || recorded);
    }
    bool terminate_exact() {
        if (non_killing) {
            if (!emergency_requested) {
                emergency_requested = true;
                emergency_error = ERROR_ACCESS_DENIED;
                row("termination_refused", 0);
            }
            return false;
        }
        if (forced) return true;
        if (emergency_requested) return false;
        emergency_requested = true;
        if (!created || birth(child.hProcess, true) != created ||
            GetProcessId(child.hProcess) != child.dwProcessId) {
            emergency_error = ERROR_INVALID_HANDLE;
        } else if (is(L"emergency-denied") || is(L"combined-failure")) {
            HANDLE restricted{};
            if (DuplicateHandle(GetCurrentProcess(), child.hProcess, GetCurrentProcess(), &restricted,
                                PROCESS_QUERY_LIMITED_INFORMATION | SYNCHRONIZE, FALSE, 0)) {
                forced = TerminateProcess(restricted, emergency_exit) != 0;
                if (!forced) emergency_error = GetLastError();
                CloseHandle(restricted);
            } else emergency_error = GetLastError();
        } else {
            forced = TerminateProcess(child.hProcess, emergency_exit) != 0;
            if (!forced) emergency_error = GetLastError();
        }
        gap();
        row("exact_child_emergency", 0, ",\"success\":" + std::to_string(forced) +
            ",\"winerror\":" + std::to_string(emergency_error));
        return forced;
    }
    bool unqualified_recovery() {
        recovery_unconfirmed = true;
        gap();
        row("recovery_unconfirmed", 0);
        return false;
    }
    bool critical_mapping() const {
        if (!loader_identity || !modules.contains(ntdll) || !attach_code(child.hProcess, ntdll)) return false;
        return !retail_run() || bool(verify_loaded_mapping(child.hProcess, base, retail_image_profile));
    }
    bool stage_owner() const {
        return !retail_run() ||
               (same_epoch(steam_client.get(), steam_pid, steam_birth) && exact_running_process() &&
                same_interactive_user(child.hProcess, child.dwProcessId, session));
    }
    static std::string evidence_text(std::wstring_view text) {
        // Keep journal rows ASCII-safe regardless of on-disk version strings.
        std::string out;
        for (auto ch : text)
            out += (ch >= L'0' && ch <= L'9') || (ch >= L'A' && ch <= L'Z') ||
                   (ch >= L'a' && ch <= L'z') || ch == L'.' || ch == L'_' || ch == L'-' ||
                   ch == L' ' ? char(ch) : '?';
        return out;
    }
    // Observed identity of one Steam component against its recorded SRR-008
    // pin. Steam updates its own components independently: a credible-origin
    // file whose hash differs is reported drift with both identities and the
    // file identity/version preserved, never a silent substitution and never
    // an admission refusal on its own. One summary row per component.
    std::string steam_component_fields(const wchar_t* component, HANDLE backing,
                                       std::string_view pin, const char* prefix = "module_") {
        profile_detail::FileStamp stamp{};
        if (!stamp.read(backing)) return {};
        const std::string observed = profile_detail::file_sha256(backing, stamp.size);
        if (observed.empty()) return {};
        const auto [file_version, product_version] =
            file_version_strings(disk_path(backing, VOLUME_NAME_DOS));
        char id[33]{};
        for (unsigned i = 0; i < sizeof stamp.id.FileId.Identifier; ++i)
            snprintf(id + 2 * i, 3, "%02x", stamp.id.FileId.Identifier[i]);
        const bool drifted = observed != pin;
        const std::string file_id(id);
        // Render the identical identity under a per-row field prefix so module
        // and baseline rows stay unambiguous while the summary row reads plainly.
        const auto block = [&](const std::string& p) {
            return ",\"" + p + "sha256\":\"" + observed + "\",\"" + p + "srr008_sha256\":\"" +
                   std::string(pin) + "\",\"" + p + "drift\":" + (drifted ? "true" : "false") +
                   ",\"" + p + "bytes\":" + std::to_string(stamp.size) +
                   ",\"" + p + "volume\":" + std::to_string(stamp.id.VolumeSerialNumber) +
                   ",\"" + p + "file_id\":\"" + file_id + '"' +
                   ",\"" + p + "file_version\":\"" + evidence_text(file_version) +
                   "\",\"" + p + "product_version\":\"" + evidence_text(product_version) + '"';
        };
        if (drifted) {
            const std::string key = evidence_text(component);
            if (std::find(drift_reported.begin(), drift_reported.end(), key) == drift_reported.end()) {
                drift_reported.push_back(key);
                row("steam_component_drift", 0, ",\"component\":\"" + key +
                    "\",\"observed_sha256\":\"" + observed +
                    "\",\"srr008_sha256\":\"" + std::string(pin) +
                    "\",\"observed_bytes\":" + std::to_string(stamp.size) +
                    ",\"file_id\":\"" + file_id + '"' +
                    ",\"file_version\":\"" + evidence_text(file_version) +
                    "\",\"product_version\":\"" + evidence_text(product_version) + '"');
            }
        }
        return block(prefix);
    }
    std::string module(const LOAD_DLL_DEBUG_INFO& info) {
        const Address at = reinterpret_cast<Address>(info.lpBaseOfDll);
        wchar_t path[32768]{};
        const bool readable = K32GetMappedFileNameW(child.hProcess, info.lpBaseOfDll, path, ARRAYSIZE(path)) != 0;
        const StageHandle backing(info.hFile);
        const bool loader_path = readable && _wcsicmp(path, loader_mapping.c_str()) == 0;
        if (!ntdll && loader_path) {
            const bool verified = staged_arming() ?
                ((!backing || same_file(backing.get(), loader_file)) &&
                 pinned_file(loader_file, ntdll_sha256) && attach_code(child.hProcess, at)) :
                (!backing || same_file(backing.get(), loader_file));
            if (verified) {
                ntdll = at;
                loader_identity = !is(L"admission-critical");
            }
        }
        const auto slash = wcsrchr(path, L'\\');
        const std::wstring_view name = slash ? slash + 1 : path;
        const auto system = loader_mapping.substr(0, loader_mapping.find_last_of(L'\\') + 1);
        const bool in_system = readable && slash && size_t(slash - path + 1) == system.size() &&
                               _wcsnicmp(path, system.c_str(), system.size()) == 0;
        const std::array<const wchar_t*, 8> fixture_modules{
            L"kernel32.dll", L"kernelbase.dll", L"advapi32.dll", L"msvcrt.dll", L"sechost.dll",
            L"rpcrt4.dll", L"bcrypt.dll", L"kernel.appcore.dll"
        };
        MEMORY_BASIC_INFORMATION map{};
        const bool mapped_image = VirtualQueryEx(child.hProcess, info.lpBaseOfDll, &map, sizeof map) &&
                                  map.Type == MEM_IMAGE && map.AllocationBase == info.lpBaseOfDll;
        std::string stage_fields;
        if (staged_arming()) {
            std::wstring lower(name);
            for (auto& ch : lower) if (ch >= L'A' && ch <= L'Z') ch += L'a' - 'A';
            PinState overlay_pin = PinState::unmatched, api_pin = PinState::unmatched;
            if (lower == L"gameoverlayrenderer64.dll") {
                const auto overlay = read_file(overlay_expected.c_str());
                if (overlay && backing && same_file(overlay.get(), backing.get()) &&
                    _wcsicmp(path, disk_path(overlay.get(), VOLUME_NAME_NT).c_str()) == 0) {
                    profile_detail::FileStamp stamp{};
                    const std::string observed = stamp.read(backing.get()) ?
                        profile_detail::file_sha256(backing.get(), stamp.size) : std::string();
                    overlay_pin = observed.empty() ? PinState::unmatched :
                        observed == overlay_sha256_srr008 ? PinState::pinned : PinState::drifted;
                }
                if (overlay_pin != PinState::unmatched)
                    stage_fields += steam_component_fields(L"gameoverlayrenderer64.dll", backing.get(),
                                                           overlay_sha256_srr008);
            }
            const std::wstring_view mapped_path(path);
            const auto directory = mapped_path.substr(0, slash ? slash - path + 1 : 0);
            const auto origin = lower == L"steam_api64.dll" ? game_directory : steam_directory;
            const bool steam_origin = !origin.empty() && directory.size() == origin.size() &&
                                      _wcsnicmp(directory.data(), origin.c_str(), origin.size()) == 0;
            if (lower == L"steam_api64.dll" && backing && steam_origin) {
                profile_detail::FileStamp stamp{};
                const std::string observed = stamp.read(backing.get()) ?
                    profile_detail::file_sha256(backing.get(), stamp.size) : std::string();
                api_pin = observed.empty() ? PinState::unmatched :
                    observed == steam_api64_sha256_srr008 ? PinState::pinned : PinState::drifted;
                if (api_pin != PinState::unmatched)
                    stage_fields += steam_component_fields(L"steam_api64.dll", backing.get(),
                                                           steam_api64_sha256_srr008);
            }
            const auto risk = stage_module(lower, in_system, steam_origin, overlay_pin, api_pin,
                                           at == ntdll && loader_identity, mapped_image);
            const char* labels[]{"expected", "incidental", "drifting", "unknown", "incompatible"};
            stage_fields = ",\"module_risk\":\"" + std::string(labels[static_cast<int>(risk)]) +
                           "\",\"module_file_handle\":" + std::to_string(bool(backing)) +
                           ",\"loader_path_match\":" + std::to_string(loader_path) + stage_fields;
            if (!at || !modules.try_emplace(at, ModuleRecord{"", risk == ModuleRisk::unknown ||
                    (!control_b() && risk == ModuleRisk::drifting)}).second ||
                risk == ModuleRisk::incompatible ||
                (loader_path && at != ntdll)) gap();
            // Existing joins cannot span a change involving unclassified or
            // credibly updated code arriving during observation. Pre-session
            // drift of an origin-verified component stays admissible.
            else if (loader && !stopped &&
                     (risk == ModuleRisk::unknown || (!control_b() && risk == ModuleRisk::drifting))) continuity_gap();
        }
        const bool expected = mapped_image && (at == ntdll || (!retail_profile() && in_system &&
            std::any_of(fixture_modules.begin(), fixture_modules.end(),
                        [&](auto expected_name) { return _wcsicmp(name.data(), expected_name) == 0; })));
        // Restrict fixture paths to the local evidence. Escape unusual basenames
        // instead of allowing an arbitrary module filename to corrupt JSON.
        std::string basename;
        for (auto ch : name)
            basename += (ch >= L'0' && ch <= L'9') || (ch >= L'A' && ch <= L'Z') ||
                        (ch >= L'a' && ch <= L'z') || ch == L'.' || ch == L'_' || ch == L'-'
                        ? char(ch) : '?';
        // Only the disposable control vouches for this DLL's role. An
        // arbitrary unqualified module still quarantines the capture.
        const bool continuity_only = late_attach && is(L"unexpected-module") &&
            mapped_image && in_system && _wcsicmp(name.data(), L"version.dll") == 0;
        if (staged_arming()) {
            if (auto it = modules.find(at); it != modules.end()) it->second.name = basename;
        } else if (modules.size() == 256 ||
            !modules.try_emplace(at, ModuleRecord{basename, continuity_only}).second ||
            (!expected && !continuity_only)) gap();
        else if (continuity_only) continuity_gap();
        return ",\"module_base\":" + std::to_string(at) + ",\"module_name\":\"" + basename +
               "\",\"module_expected\":" + std::to_string(expected) +
               ",\"module_system_directory\":" + std::to_string(in_system) +
               ",\"module_mapped_image\":" + std::to_string(mapped_image) + stage_fields;
    }
    std::string unload(const UNLOAD_DLL_DEBUG_INFO& info) {
        const auto address = reinterpret_cast<Address>(info.lpBaseOfDll);
        const auto module = modules.extract(address);
        // A loss of a qualified module is a change of the observed image set.
        if (module.empty() || address == ntdll) gap();
        else if (!stopped && staged_arming()) {
            if (module.mapped().continuity_only) continuity_gap();
        }
        else if (!stopped && late_attach && module.mapped().continuity_only) continuity_gap();
        else if (!stopped) gap();
        return ",\"module_base\":" + std::to_string(address) + ",\"module_name\":\"" +
               (module.empty() ? std::string{} : module.mapped().name) + "\"";
    }
    bool loader_event(const DEBUG_EVENT& event, Address address) {
        const auto& e = event.u.Exception;
        if ((loader && !recovery_break_pending) || (!identity && !staged_arming()) || !ntdll || !loader_rva ||
            (!late_attach && event.dwThreadId != child.dwThreadId) || !e.dwFirstChance ||
            e.ExceptionRecord.ExceptionCode != EXCEPTION_BREAKPOINT ||
            address != ntdll + loader_rva)
            return false;
        std::array<unsigned char, 16> bytes{};
        MEMORY_BASIC_INFORMATION mapping{};
        if (!VirtualQueryEx(child.hProcess, reinterpret_cast<void*>(address), &mapping, sizeof mapping) ||
            mapping.Type != MEM_IMAGE || reinterpret_cast<Address>(mapping.AllocationBase) != ntdll ||
            !mapped(address, bytes.data(), bytes.size()) || bytes != loader_bytes) return false;
        if (!staged_arming() || loader)
            for (const auto& [tid, entry] : threads) {
                CONTEXT c{};
                if (!entry.armed || !read_context(entry.handle, c) || !owns(c)) return false;
            }
        const auto initial = threads.find(event.dwThreadId);
        CONTEXT c{};
        if (initial == threads.end() || !read_context(initial->second.handle, c) ||
            c.Rip != address + 1 || c.EFlags & (tf | rf) || c.Dr6 & dr6_causes)
            return false;
        if (late_attach) {
            Address return_address = 0;
            std::array<unsigned char, 5> call{};
            MEMORY_BASIC_INFORMATION stack{};
            if (initial->second.start_address != ntdll + breakin_start_rva ||
                (recovery_break_pending && initial->second.generation <= recovery_after_generation) ||
                c.Rsp % 16 != 8 ||
                !VirtualQueryEx(child.hProcess, reinterpret_cast<void*>(c.Rsp), &stack, sizeof stack) ||
                stack.Type != MEM_PRIVATE || stack.State != MEM_COMMIT ||
                !mapped(c.Rsp, &return_address, sizeof return_address) ||
                return_address != ntdll + breakin_return_rva ||
                !profile_detail::read_image(child.hProcess, ntdll, return_address - call.size(),
                                            call.data(), call.size(), true) || call != breakin_call)
                return false;
        }
        if (staged_arming() && !loader) {
            // A rejected image or a changed runtime must never get slots.
            // Recognize the synthetic exception separately from the decision
            // to instrument. Keep servicing the process even after refusal.
            const bool fresh = initial->second.created >= attach_requested_at;
            if (!fresh) return false;
            const bool owner = identity && stage_owner();
            const bool mapped = owner && critical_mapping();
            const bool modules_checked = owner && module_census();
            const bool threads_checked = owner && thread_census(Census::prearm);
            const bool checked = !stopped && healthy && fresh_breakin_threads == 1 &&
                                 mapped && modules_checked && threads_checked;
            row("stopped_admission", event.dwThreadId, ",\"prearm_checks\":" + std::to_string(checked) +
                ",\"process_checked\":" + std::to_string(owner) +
                ",\"critical_mapping_checked\":" + std::to_string(mapped) +
                ",\"module_census_checked\":" + std::to_string(modules_checked) +
                ",\"thread_census_checked\":" + std::to_string(threads_checked) +
                ",\"fresh_breakin_threads\":" + std::to_string(fresh_breakin_threads));
            if (checked && healthy && !control_b()) {
                for (auto& [tid, thread] : threads) {
                    if (!arm(tid, thread)) { gap(); break; }
                }
                if (!thread_census(Census::held)) gap();
            } else if (!checked || !healthy) gap();
        }
        if (recovery_break_pending) {
            recovery_break_owned = true;
            recovery_break_pending = false;
            return true;
        }
        if (late_attach && !staged_arming() && (!thread_census(Census::held) || !module_census())) gap();
        return loader = true;
    }
    // The debugger event keeps all threads stopped while we validate the census
    // and take one extra suspend per live thread. The duplicate handles remain
    // valid after debug-event continuation and detach.
    struct Suspension { DWORD tid; HANDLE handle; };
    bool suspend_for_detach(std::vector<Suspension>& suspended) {
        if (!thread_census(Census::held)) return false;
        suspended.reserve(threads.size());
        for (const auto& [tid, thread] : threads) {
            HANDLE owned{};
            if (!DuplicateHandle(GetCurrentProcess(), thread.handle, GetCurrentProcess(), &owned,
                                 THREAD_SUSPEND_RESUME | THREAD_GET_CONTEXT |
                                 THREAD_QUERY_INFORMATION | SYNCHRONIZE, FALSE, 0) ||
                SuspendThread(owned) == DWORD(-1)) {
                if (owned) CloseHandle(owned);
                return false;
            }
            suspended.push_back({tid, owned});
        }
        return !suspended.empty();
    }
    void release_suspensions(std::vector<Suspension>& suspended) {
        while (!suspended.empty()) {
            const auto [tid, handle] = suspended.back();
            if (ResumeThread(handle) == DWORD(-1) &&
                WaitForSingleObject(handle, 0) != WAIT_OBJECT_0) {
                row("suspension_release_unconfirmed", tid);
                // Retain the duplicate and our suspend obligation while
                // leaving the exact child untouched by any kill fallback.
                do { Sleep(100); } while (ResumeThread(handle) == DWORD(-1) &&
                    WaitForSingleObject(handle, 0) != WAIT_OBJECT_0);
            }
            CloseHandle(handle);
            suspended.pop_back();
        }
    }
    bool original_debug_state(const CONTEXT& check, const CONTEXT& original) const {
        return slots(check) == slots(original) &&
            ((check.Dr7 ^ original.Dr7) & dr7_fields) == 0 &&
            ((check.Dr6 ^ original.Dr6) & dr6_causes) == 0;
    }
    bool verify_released_event_state(const std::vector<Suspension>& suspended) {
        bool verified = true;
        for (const auto& [tid, handle] : suspended) {
            auto& thread = threads.at(tid);
            CONTEXT check{};
            const bool read = birth(handle, false) == thread.created && read_context(handle, check);
            const bool original = read && original_debug_state(check, thread.original);
            if (!original) {
                verified = false;
                // If continuation reinstated our exact slots, continue to
                // service them. A foreign context is never overwritten.
                thread.armed = read && owns(check);
                thread.debug_written = thread.armed;
            }
            row("post_continue_debug_state", tid, ",\"verified\":" + std::to_string(original));
        }
        return verified;
    }
    bool restore_debug_state() {
        bool restored = true;
        bool restored_one = false;
        for (auto& [tid, thread] : threads) {
            if (!thread.debug_written) continue;
            CONTEXT current{}, check{};
            bool ok = birth(thread.handle, false) == thread.created &&
                      read_context(thread.handle, current) && owns(current) &&
                      (current.Dr6 & dr6_causes) == 0;
            if (is(L"recover-partial") && restored_one) ok = false;
            if (ok) {
                CONTEXT restore = thread.original;
                restore.ContextFlags = CONTEXT_DEBUG_REGISTERS;
                ok = write_context(thread.handle, &restore) && read_context(thread.handle, check) &&
                    original_debug_state(check, thread.original) &&
                    check.Rip == current.Rip && check.Rsp == current.Rsp;
            }
            if (ok) {
                thread.armed = thread.debug_written = false;
                restored_one = true;
            }
            else restored = false;
            row("restore_debug_state", tid, ",\"verified\":" + std::to_string(ok));
        }
        return restored;
    }
    bool exact_running_process() const {
        return created && GetProcessId(child.hProcess) == child.dwProcessId &&
            birth(child.hProcess, true) == created &&
            WaitForSingleObject(child.hProcess, 0) == WAIT_TIMEOUT;
    }
    std::string capture(Thread& thread, unsigned site, const CONTEXT& c, Result& result) {
        MEMORY_BASIC_INFORMATION bounds{};
        VirtualQueryEx(child.hProcess, reinterpret_cast<void*>(c.Rsp), &bounds, sizeof bounds);
        std::ostringstream reads;
        auto read = [&](Address address, unsigned width, bool stack) -> std::optional<Address> {
            MEMORY_BASIC_INFORMATION page{};
            Address value = 0;
            bool within = !stack ||
                ((address & 7) == 0 && bounds.AllocationBase &&
                 VirtualQueryEx(child.hProcess, reinterpret_cast<void*>(address), &page, sizeof page) &&
                 bounds.AllocationBase == page.AllocationBase && page.State == MEM_COMMIT &&
                 address - reinterpret_cast<Address>(page.BaseAddress) <= page.RegionSize &&
                 width <= page.RegionSize - (address - reinterpret_cast<Address>(page.BaseAddress)));
            const bool ok = within && mapped(address, &value, width);
            const DWORD error = ok ? 0 : within ? GetLastError() : ERROR_INVALID_ADDRESS;
            if (reads.tellp() > 0) reads << ',';
            reads << "{\"address\":" << address << ",\"width\":" << width
                  << ",\"stack\":" << stack << ",\"error\":" << error;
            if (ok) reads << ",\"value\":" << value;
            reads << '}';
            return ok ? std::optional<Address>{value} : std::nullopt;
        };
        result = thread.frames.hit(site, layout, base, {c.Rsp,c.Rax,c.Rcx,c.Rdx,c.R14,c.Rsi},
                                   journal.attempted + 1, read);
        std::ostringstream fields;
        fields << ",\"rip\":" << c.Rip << ",\"rsp\":" << c.Rsp << ",\"rax\":" << c.Rax
               << ",\"rcx\":" << c.Rcx << ",\"rdx\":" << c.Rdx << ",\"r14\":" << c.R14
               << ",\"rsi\":" << c.Rsi << ",\"reads\":[" << reads.str()
               << "],\"verdict\":" << static_cast<int>(result.verdict)
               << ",\"ingress\":" << result.ingress << ",\"callback\":" << result.callback
               << ",\"sweep\":" << result.sweep << ",\"type\":";
        if (result.type) fields << *result.type; else fields << "null";
        return fields.str();
    }
    DWORD exception(const DEBUG_EVENT& event, std::string& fields, Result& result,
                    std::optional<unsigned>& captured_site) {
        const auto& e = event.u.Exception;
        const auto addr = reinterpret_cast<Address>(e.ExceptionRecord.ExceptionAddress);
        const auto code = e.ExceptionRecord.ExceptionCode;
        fields += ",\"address\":" + std::to_string(addr) + ",\"exception\":" +
                  std::to_string(code) + ",\"first_chance\":" + std::to_string(e.dwFirstChance);
        if (code == EXCEPTION_BREAKPOINT)
            fields += ",\"ntdll\":" + std::to_string(ntdll) +
                      ",\"loader_candidate\":" + std::to_string(ntdll + loader_rva);
        if (loader_event(event, addr)) {
            fields += recovery_break_owned ? ",\"owner\":\"recovery_breakin\"" : ",\"owner\":\"loader\"";
            if (is(L"slot-loss") && !late_attach) {
                auto& initial = threads.at(event.dwThreadId);
                CONTEXT c{}, check{};
                bool changed = false;
                if (read_context(initial.handle, c)) {
                    c.Dr0 = c.Dr1 = c.Dr2 = c.Dr3 = c.Dr7 = 0;
                    c.ContextFlags = CONTEXT_DEBUG_REGISTERS;
                    changed = write_context(initial.handle, &c) &&
                              read_context(initial.handle, check) && !owns(check);
                }
                fields += ",\"fixture_slot_loss\":" + std::to_string(changed);
            }
            return DBG_CONTINUE;
        }
        if (control_b()) {
            fields += ",\"owner\":\"foreign\"";
            return DBG_EXCEPTION_NOT_HANDLED;
        }
        auto entry = threads.find(event.dwThreadId);
        const auto found = std::find(addresses.begin(), addresses.end(), addr);
        const unsigned site = static_cast<unsigned>(found - addresses.begin());
        if (code == EXCEPTION_SINGLE_STEP && e.dwFirstChance && site < addresses.size() &&
            entry != threads.end() && entry->second.armed) {
            CONTEXT c{};
            if (!read_context(entry->second.handle, c, stage_b()) || !owns(c) || c.Rip != addr ||
                (c.Dr6 & dr6_causes) != (1ULL << site)) {
                gap();
                return DBG_EXCEPTION_NOT_HANDLED;
            }
            fields += ",\"owner\":\"hardware\",\"site\":" + std::to_string(site) +
                      ",\"rva\":" + std::to_string(layout.sites[site]) +
                      ",\"before_flags\":" + std::to_string(c.EFlags) +
                      ",\"before_dr6\":" + std::to_string(c.Dr6);
            if (staged_arming() && !stopped && healthy && !critical_mapping()) gap();
            if (stopped) ++after_stop[site];
            else if (!healthy || (late_attach && !loader)) ++after_gap[site];
            else {
                captured_site = site;
                fields += capture(entry->second, site, c, result);
            }
            c.ContextFlags = CONTEXT_CONTROL | CONTEXT_DEBUG_REGISTERS;
            c.Dr6 &= ~(1ULL << site);
            c.EFlags |= rf;
            CONTEXT check{};
            const bool readback = write_context(entry->second.handle, &c) &&
                                  read_context(entry->second.handle, check, stage_b());
            const bool preserved = !stage_b() || (readback && same_execution_state(c, check));
            if (stage_b()) fields += ",\"execution_state_preserved\":" + std::to_string(preserved);
            fields += ",\"resume_flags\":" + std::to_string(check.EFlags) +
                      ",\"resume_dr6\":" + std::to_string(check.Dr6) +
                      ",\"readback\":" + std::to_string(readback);
            if (!readback || !preserved || !owns(check) ||
                check.Rip != c.Rip || check.Rsp != c.Rsp ||
                ((check.EFlags ^ c.EFlags) & ~DWORD{2}) || (check.Dr6 & dr6_causes)) {
                result = {Verdict::unknown};
                gap();
                return DBG_EXCEPTION_NOT_HANDLED;
            }
            ++hits[site];
            return DBG_CONTINUE;
        }
        ++foreign;
        fields += ",\"owner\":\"foreign\"";
        // Only the fixture's deliberately handled, non-debug exception is
        // a known continuity control. Other exceptions could unwind a frame.
        if (late_attach && !loader && e.dwFirstChance && code == EXCEPTION_BREAKPOINT &&
            addr == ntdll + loader_rva) {
            fields += ",\"attach_candidate_refused\":1";
        } else if (late_attach && e.dwFirstChance && code != EXCEPTION_BREAKPOINT &&
            code != EXCEPTION_SINGLE_STEP && (retail_run() || code != 0xe1230042)) continuity_gap();
        else if (!e.dwFirstChance || retail_run() || code != 0xe1230042) gap();
        else if (entry != threads.end()) {
            if (entry->second.frames.awaiting_callback()) gap();
            else entry->second.frames.clear();
        }
        return DBG_EXCEPTION_NOT_HANDLED;
    }
    // The local run directory ACL is the trust boundary. The payload binds a
    // statement to the retained process epoch and a single transition.
    std::optional<std::string> read_marker(const wchar_t* name, bool consume = false) const {
        const HANDLE file = CreateFileW((folder / name).c_str(), GENERIC_READ | (consume ? DELETE : 0),
                                        FILE_SHARE_READ, nullptr, OPEN_EXISTING,
                                        FILE_FLAG_OPEN_REPARSE_POINT | (consume ? FILE_FLAG_DELETE_ON_CLOSE : 0),
                                        nullptr);
        if (file == INVALID_HANDLE_VALUE) return {};
        char bytes[256]{};
        DWORD size = 0;
        BY_HANDLE_FILE_INFORMATION info{};
        const bool read = GetFileInformationByHandle(file, &info) &&
            !(info.dwFileAttributes & (FILE_ATTRIBUTE_REPARSE_POINT | FILE_ATTRIBUTE_DIRECTORY)) &&
            ReadFile(file, bytes, sizeof bytes, &size, nullptr);
        CloseHandle(file);
        return read ? std::string(bytes, size) : std::string{};
    }
    bool marker(const wchar_t* name, const char* label, unsigned ordinal, uint64_t prior = 0) const {
        const auto payload = read_marker(name);
        return payload && *payload == run_id + " " + std::to_string(ordinal) + " " + label +
                                      " " + std::to_string(prior) + "\n";
    }
    bool load_acknowledge(const char* label, uint64_t sequence) {
        // A new challenge is issued only after the predecessor is durable.
        // Files published early cannot become valid by predicting a sequence.
        HCRYPTPROV provider{};
        BYTE nonce[16]{};
        const bool opened = CryptAcquireContextW(&provider, nullptr, nullptr, PROV_RSA_AES,
                                                  CRYPT_VERIFYCONTEXT) != 0;
        const bool generated = opened && CryptGenRandom(provider, sizeof nonce, nonce);
        if (opened) CryptReleaseContext(provider, 0);
        if (!generated) {
            row("phase_ack_refused", 0, ",\"prior\":" + std::to_string(sequence) +
                                       ",\"reason\":\"challenge_unavailable\"");
            journal.request_flush();
            return false;
        }
        static constexpr char hex[] = "0123456789abcdef";
        load_challenge.clear();
        for (const auto byte : nonce) {
            load_challenge += hex[byte >> 4];
            load_challenge += hex[byte & 15];
        }
        load_phase_prior = sequence;
        std::printf("%s %llu %s\n", label, sequence, load_challenge.c_str());
        std::fflush(stdout);
        return true;
    }
    void load_controls() {
        if (acknowledged(load_phase_ack)) {
            const bool ok = !stopped && healthy &&
                            load_acknowledge(load_phases[phase - 2].ack, load_phase_ack);
            if (!ok) std::puts("PHASE_BOUNDARY_UNCONFIRMED");
            std::fflush(stdout);
            load_phase_ack = 0;
        }
        if (acknowledged(load_refusal_ack)) {
            std::printf("PHASE_REFUSED %llu\n", load_refusal_ack);
            std::fflush(stdout);
            load_refusal_ack = 0;
        }
        if (load_refusal_ack || journal.failed || journal.first_lost) return;
        const auto payload = read_marker(L"phase.request", true);
        if (!payload) return;
        const auto* next = phase && phase <= std::size(load_phases) ? &load_phases[phase - 1] : nullptr;
        const bool ready = !stopped && armed_ack && healthy && next && !load_challenge.empty();
        if (!ready || *payload != run_id + " " + next->label + " " + std::to_string(load_phase_prior) +
                                  " " + load_challenge + "\n") {
            load_refusal_ack = row("phase_request_refused", 0,
                ",\"reason\":\"" + std::string(ready ? "binding_mismatch" : "phase_unavailable") + "\"" +
                ",\"expected\":\"" + (ready ? next->label : "") + "\"" +
                ",\"prior\":" + std::to_string(ready ? load_phase_prior : 0));
            journal.request_flush();
            return;
        }
        load_challenge.clear();
        const bool inventory = phase == 2;  // LOAD_BEGIN
        ++phase;
        const bool checked = checkpoint(inventory ? Census::inventory : Census::running);
        if (!checked) gap();
        // A read-only LOAD_BEGIN can open a load covered by the enclosing
        // menu/control slot samples. It cannot close a qualified menu zero.
        const bool opening = checked && healthy && (!inventory || windows.can_bridge_boundary());
        load_phase_ack = row(next->row, 0, ",\"checkpoint\":" + std::to_string(checked) +
                             ",\"thread_slot_readback\":" + std::to_string(!inventory && checked) +
                             ",\"opening_eligible\":" + std::to_string(opening) +
                             ",\"prior\":" + std::to_string(load_phase_prior));
        if (load_phase_ack) windows.phase(load_phase_ack, !inventory && opening, opening);
        journal.request_flush();
    }
    void control_b_phases() {
        if (acknowledged(arm_barrier)) {
            if (healthy && load_acknowledge("DEBUGGER_ONLY_READY", arm_barrier))
                control_durable_phase = 1;
            else {
                healthy = false;
                std::puts("DEBUGGER_ONLY_REFUSED");
                std::fflush(stdout);
            }
            arm_barrier = 0;
        }
        if (acknowledged(load_phase_ack)) {
            const auto& boundary = control_phases[phase - 2];
            const bool terminal = phase == std::size(control_phases) + 1;
            if (control_end && !journal.stop_sealed(control_end) && !journal.failed) return;
            if (healthy && !journal.failed &&
                (terminal || load_acknowledge(boundary.ack, load_phase_ack))) {
                control_durable_phase = phase;
                if (terminal) {
                    retired = true;
                    std::printf("%s %llu\n", boundary.ack, load_phase_ack);
                }
            } else {
                healthy = false;
                std::puts("CONTROL_BOUNDARY_UNCONFIRMED");
            }
            std::fflush(stdout);
            load_phase_ack = 0;
        }
        if (acknowledged(load_refusal_ack)) {
            std::printf("PHASE_REFUSED %llu\n", load_refusal_ack);
            std::fflush(stdout);
            load_refusal_ack = 0;
        }
        if (load_refusal_ack || load_phase_ack || journal.failed || journal.first_lost) return;
        const auto payload = read_marker(L"phase.request", true);
        if (!payload) return;
        const auto* next = control_durable_phase && control_durable_phase <= std::size(control_phases)
            ? &control_phases[control_durable_phase - 1] : nullptr;
        const bool ready = healthy && next && !load_challenge.empty();
        if (!ready || *payload != run_id + " " + next->label + " " + std::to_string(load_phase_prior) +
                                  " " + load_challenge + "\n") {
            load_refusal_ack = row("phase_request_refused", 0,
                ",\"reason\":\"" + std::string(ready ? "binding_mismatch" : "phase_unavailable") + "\"" +
                ",\"expected\":\"" + (ready ? next->label : "") + "\"" +
                ",\"prior\":" + std::to_string(ready ? load_phase_prior : 0));
            journal.request_flush();
            return;
        }
        load_challenge.clear();
        ++phase;
        const bool checked = exact_running_process() && checkpoint(Census::inventory);
        if (!checked) gap();
        const bool seal = checked && phase == std::size(control_phases) + 1;
        load_phase_ack = row(next->row, 0, ",\"checkpoint\":" + std::to_string(checked) +
                             ",\"prior\":" + std::to_string(load_phase_prior), seal);
        if (seal) control_end = load_phase_ack;
        journal.request_flush();
    }
    void controls() {
        if (journal.failed && healthy) gap();
        if (control_b()) {
            control_b_phases();
            return;
        }
        for (auto item = pending_release.begin(); item != pending_release.end();) {
            const auto thread = threads.find(*item);
            if (thread != threads.end() && ResumeThread(thread->second.handle) == DWORD(-1) &&
                WaitForSingleObject(thread->second.handle, 0) != WAIT_OBJECT_0) {
                ++item;
                continue;
            }
            row("suspension_release_resolved", *item);
            item = pending_release.erase(item);
        }
        if (staged_arming() && acknowledged(arm_barrier)) {
            if (healthy && !stopped) {
                if (!stage_b() || load_acknowledge("ATTACH_ARMED", arm_barrier)) {
                    armed_ack = arm_barrier;
                    if (!stage_b()) std::printf("ATTACH_ARMED %llu\n", armed_ack);
                } else std::puts("ARMING_REFUSED");
            } else std::puts("ARMING_REFUSED");
            std::fflush(stdout);
            arm_barrier = 0;
        }
        const bool fixture_stop = is(L"stop-burst") && hits[0] >= 256;
        if (!staged_arming() && !stopped && phase == 0 &&
            (late_attach ? loader && marker(L"title.request", "TITLE_CARD", 1) :
             fixture_stop || cross_phase || fs::exists(folder / "phase"))) {
            phase = 1;
            const bool checked = checkpoint();
            if (!checked) gap();
            phase_ack = row("operator_phase", 0, ",\"checkpoint\":" + std::to_string(checked));
            title_boundary = phase_ack;
            windows.phase(phase_ack, checked && healthy);
            journal.request_flush();
        }
        if (!stage_b() && !stopped && phase == 1 &&
            (late_attach ? !phase_ack && (staged_arming() ? armed_ack != 0 : title_boundary != 0) &&
                           marker(L"menu.request", staged_arming() ? "MAIN_MENU_CONFIRMED" : "MAIN_MENU",
                                  2, staged_arming() ? armed_ack : title_boundary) :
             cross_menu || fs::exists(folder / "menu"))) {
            phase = 2;
            const bool checked = checkpoint();
            if (!checked) gap();
            const auto marker = row("operator_menu", 0, ",\"checkpoint\":" + std::to_string(checked));
            windows.phase(marker, checked && healthy);
            menu_ack = marker;
            journal.request_flush();
        }
        // STOP is always available, even if a UI phase never arrives.
        if (!stopped && (late_attach ? marker(L"stop.request", "STOP", 3) :
                         fixture_stop || fs::exists(folder / "stop"))) {
            stopped = true;
            const bool checked = checkpoint();
            if (!checked) gap();
            for (auto& [tid, thread] : threads) {
                if (thread.frames.awaiting_callback()) healthy = false;
                thread.frames.clear();
            }
            std::string fields = ",\"checkpoint\":" + std::to_string(checked);
            const bool missing_end = stage_b() && (phase == 3 || phase == 5);
            if (stage_b()) {
                const char* missing = !armed_ack ? "ATTACH_ARMED" : phase == 1 ? "MAIN_MENU_CONFIRMED" :
                                      phase == 2 ? "LOAD_BEGIN" : phase == 3 ? "PLAYER_CONTROL" :
                                      phase == 5 ? "LODGE_END" : "";
                const uint64_t sequence = journal.attempted + 1;
                auto sealed = windows;
                sealed.stop(sequence, checked && healthy && !missing_end);
                std::ostringstream summary;
                summary << ",\"missing_boundary\":\"" << missing << "\",\"windows\":";
                sealed.write_json(summary, sequence);
                fields += summary.str();
            }
            stop_ack = row("stop", 0, fields, late_attach);
            stop_boundary = stop_ack;
            windows.stop(stop_ack, checked && healthy && !missing_end);
            journal.request_flush();
        }
        if (phase_ack && journal.durable >= phase_ack) {
            std::printf("PHASE_DURABLE %llu\n", phase_ack);
            std::fflush(stdout);
            phase_ack = 0;
            if (is(L"abrupt-observer") && !abrupt_queued) {
                abrupt_queued = true;
                row("abrupt_probe", 0);
            }
        }
        if (stop_ack && stop_acknowledged()) {
            std::printf("STOP_DURABLE %llu\n", stop_ack);
            std::fflush(stdout);
            stop_ack = 0;
            stop_durable = true;
        }
        if (menu_ack && journal.durable >= menu_ack) {
            std::printf("MENU_DURABLE %llu\n", menu_ack);
            std::fflush(stdout);
            menu_ack = 0;
        }
        if (stage_b()) load_controls();
        if (late_attach && stop_durable && !retired &&
            marker(L"retire.request", staged_arming() ? "QUIT_REQUESTED" : "RETIRE", 4, stop_boundary)) {
            retired = true;
            retire_ack = row("retire", 0, ",\"strategy\":\"observe_exact_process_to_exit\"");
            journal.request_flush();
        }
        if (retire_ack && journal.durable >= retire_ack) {
            std::printf("RETIRE_DURABLE %llu\n", retire_ack);
            std::fflush(stdout);
            retire_ack = 0;
        }
        if (non_killing && !retail_run() && retired && !retire_ack && !recovery_attempted &&
            marker(L"recover.request", "RECOVER", 6, stop_boundary)) {
            recovery_attempted = true;
            recovery_after_generation = births;
            recovery_break_pending = exact_running_process() && DebugBreakProcess(child.hProcess);
            row("recovery_request", 0, ",\"break_requested\":" + std::to_string(recovery_break_pending));
            if (!recovery_break_pending) recovery_unconfirmed = true;
        }
        if (!retail_run() && !emergency_requested && (late_attach ? marker(L"emergency.request", "EMERGENCY", 5) :
                                     fs::exists(folder / "emergency"))) terminate_exact();
    }
    uint64_t next_readback = 0, next_held_readback = 0;
    HANDLE loader_file = INVALID_HANDLE_VALUE;

    bool prepare_stage() {
        if (!ProcessIdToSessionId(GetCurrentProcessId(), &session)) return false;
        std::vector<StageProcess> steam, targets;
        if (!stage_processes(session, steam, targets) || steam.size() != 1 || !targets.empty()) return false;
        steam_pid = steam.front().pid;
        steam_client.reset(OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION | SYNCHRONIZE, FALSE, steam_pid));
        if (!steam_client || _wcsicmp(process_path(steam_client.get()).c_str(), steam_exe) ||
            !same_interactive_user(steam_client.get(), steam_pid, session) ||
            !pinned_file(image, retail_image_profile.image_sha256, retail_image_profile.file_size))
            return false;
        steam_birth = birth(steam_client.get(), true);
        const auto exact_steam = [&] { return same_epoch(steam_client.get(), steam_pid, steam_birth); };
        SteamAttribution log;
        if (!exact_steam() || !log.start()) return false;
        // The Steam client updates itself independently of this research.
        // Record its observed identity against the SRR-008 survey pin and
        // report drift; a changed client hash never refuses admission.
        const auto client_file = read_file(steam_exe);
        const std::string client_fields = client_file ?
            steam_component_fields(L"steam.exe", client_file.get(), steam_exe_sha256_srr008,
                                   "steam_exe_") : std::string();
        const auto ready = row("steam_baseline", 0, ",\"steam_pid\":" + std::to_string(steam_pid) +
            ",\"steam_birth\":" + std::to_string(steam_birth) + ",\"session\":" + std::to_string(session) +
            ",\"log_baseline_bytes\":" + std::to_string(log.baseline_bytes()) +
            ",\"log_baseline_tail_sha256\":\"" + std::string(log.baseline_tail_sha256()) + "\"" +
            client_fields);
        journal.request_flush();
        if (!wait_durable(ready)) return false;
        const auto earliest = utc_now();
        std::puts("BASELINE_DURABLE");
        std::fflush(stdout);
        while (exact_steam() && !journal.failed && space_available()) {
            if (control_file(L"cancel-before-target")) return false;
            steam.clear();
            targets.clear();
            if (!stage_processes(session, steam, targets) || steam.size() != 1 ||
                steam.front().pid != steam_pid || targets.size() > 1) return false;
            if (targets.empty()) { Sleep(250); continue; }
            const auto target = targets.front();
            if (target.parent != steam_pid) return false;
            child.dwProcessId = target.pid;
            if (auto result = open_attach_target(target.pid, child.hProcess); !result) {
                result.expected = attach_target_access;
                report_attach_refusal(journal, {"target_open", result},
                    [&](const std::string& fields) { return row("attach_refused", 0, fields); });
                return false;
            }
            created = birth(child.hProcess, true);
            if (created < earliest || !same_epoch(child.hProcess, target.pid, created) ||
                _wcsicmp(process_path(child.hProcess).c_str(), retail_exe) ||
                !same_interactive_user(child.hProcess, target.pid, session)) return false;
            run_id = digest + '-' + std::to_string(target.pid) + '-' + std::to_string(created) +
                     '-' + std::to_string(earliest);
            USHORT process_machine = 0, host_machine = 0;
            if (!IsWow64Process2(child.hProcess, &process_machine, &host_machine) ||
                process_machine != IMAGE_FILE_MACHINE_UNKNOWN || host_machine != IMAGE_FILE_MACHINE_AMD64)
                return false;
            const auto bound = row("target_bound", 0, ",\"steam_pid\":" + std::to_string(steam_pid) +
                ",\"earliest_birth\":" + std::to_string(earliest) +
                ",\"requested_process_access\":" + std::to_string(attach_target_access));
            journal.request_flush();
            if (!wait_durable(bound) || !exact_running_process()) return false;
            std::printf("TARGET_BOUND %s\n", run_id.c_str());
            std::fflush(stdout);
            while (!journal.failed && exact_running_process() &&
                   exact_steam() && space_available()) {
                if (control_file(L"cancel-before-target") ||
                    (!control_b() && marker(L"stop.request", "STOP", 3)))
                    return false;
                if (marker(L"title.request", "TITLE_CONFIRMED", 1)) {
                    const auto attribution = log.check(target.pid);
                    if (attribution.matches != 1 || attribution.digest.empty() ||
                        !space_available() || !publish_record(folder / "steam-attribution-line.txt",
                                                              attribution.evidence)) return false;
                    phase = 1;
                    title_boundary = row("title_confirmed", 0, ",\"steam_log_append_sha256\":\"" +
                        attribution.digest + "\",\"steam_log_match_offset\":" +
                        std::to_string(attribution.offset) + ",\"covered\":false");
                    journal.request_flush();
                    return wait_durable(title_boundary) && stage_owner();
                }
                Sleep(100);
            }
            return false;
        }
        return false;
    }

public:
    Observer(Journal& output, fs::path dir, const wchar_t* mode, HANDLE source, std::string sha,
             ProfileRole role, bool attach)
        : journal(output), folder(std::move(dir)), scenario(mode), profile_role(role),
          late_attach(attach), non_killing(role == ProfileRole::retail ||
                  scenario.starts_with(L"recover-") || scenario.starts_with(L"admission-")),
          image(source), digest(std::move(sha)),
          windows(stage_b() ? WindowEvidence(load_windows) :
                  WindowEvidence(staged_arming() ?
                           std::array{"uncovered_startup", "post_arming_title", "main_menu"} :
                  attach ? std::array{"fixture_attach_barrier", "fixture_title", "fixture_menu"} :
                           std::array{"fixture_startup", "fixture_title", "fixture_menu"})) {
        local = reinterpret_cast<Address>(GetModuleHandleW(nullptr));
        const auto dos = reinterpret_cast<const IMAGE_DOS_HEADER*>(local);
        const auto pe = reinterpret_cast<const IMAGE_NT_HEADERS64*>(local + dos->e_lfanew);
        extent = pe->OptionalHeader.SizeOfImage;
        // The Steam-origin drift controls simulate an updated client layout:
        // the fixture child materializes its own "Steam root" in the run
        // directory and the observer pins that as the overlay's origin.
        if (scenario == L"admission-overlay-drift" || scenario == L"admission-drift-arrival" ||
            scenario == L"admission-overlay-lookalike")
            overlay_expected = (folder / L"steam-root" / L"gameoverlayrenderer64.dll").wstring();
        auto offset = [&](auto* p) { return reinterpret_cast<Address>(p) - local; };
        layout = {{offset(&guard_site), offset(&iterator_site), offset(&callback_site), offset(&allocator_site)},
                  offset(fixture_vtable), offset(&fixture_guard), offset(&fixture_flag),
                  {offset(&early_return), offset(&later_return)}, offset(&iterator_return),
                  offset(&callback_return), offset(&adapter_return)};
        if (retail_profile()) layout = retail;
        const HMODULE module = GetModuleHandleW(L"ntdll.dll");
        wchar_t path[32768]{};
        if (GetModuleFileNameW(module, path, ARRAYSIZE(path))) {
            loader_file = CreateFileW(path, GENERIC_READ, FILE_SHARE_READ, nullptr, OPEN_EXISTING, 0, nullptr);
            if (pinned_file(loader_file, ntdll_sha256)) {
                // This OS image delivers its startup breakpoint at an
                // internal ntdll instruction instead of the exported stub.
                loader_rva = 0xd0860;
                if (late_attach) {
                    const auto entry = reinterpret_cast<Address>(GetProcAddress(module, "DbgBreakPoint"));
                    if (!entry) throw std::runtime_error("missing attach breakpoint export");
                    loader_rva = entry - reinterpret_cast<Address>(module);
                    std::memcpy(breakin_call.data(), reinterpret_cast<void*>(
                        reinterpret_cast<Address>(module) + breakin_return_rva - breakin_call.size()),
                        breakin_call.size());
                }
                std::memcpy(loader_bytes.data(), reinterpret_cast<void*>(reinterpret_cast<Address>(module) +
                            loader_rva), loader_bytes.size());
            }
        }
        if (loader_file == INVALID_HANDLE_VALUE) throw std::runtime_error("system ntdll file");
        if (!loader_rva || loader_bytes[0] != 0xcc) throw std::runtime_error("unqualified loader image");
        if (staged_arming() && (loader_rva != attach_break_rva ||
            !attach_code(GetCurrentProcess(), reinterpret_cast<Address>(module))))
            throw std::runtime_error("unqualified attach runtime windows");
        if (!K32GetMappedFileNameW(GetCurrentProcess(), module, path, ARRAYSIZE(path)))
            throw std::runtime_error("system ntdll mapping");
        loader_mapping = path;
        if (retail_run()) {
            const auto client = read_file(steam_exe);
            auto directory = [](HANDLE file) {
                const auto mapped = disk_path(file, VOLUME_NAME_NT);
                return mapped.substr(0, mapped.find_last_of(L'\\') + 1);
            };
            steam_directory = directory(client.get());
            game_directory = directory(image);
            if (steam_directory.empty() || game_directory.empty())
                throw std::runtime_error("unqualified installation paths");
        }
        QueryPerformanceFrequency(&frequency);
    }
    ~Observer() {
        if (child.hProcess) CloseHandle(child.hProcess);
        CloseHandle(loader_file);
    }

    bool run(const wchar_t* self) {
        if (retail_run()) {
            if (!prepare_stage()) { row("admission_refused", 0); return false; }
        } else if (!start_fixture(self)) return false;
        if (late_attach) {
            const auto preflight = is(L"admission-control-b-epoch")
                ? check_process_epoch(child.hProcess, child.dwProcessId, created + 1) : attach_preflight();
            attach_requested_at = utc_now();
            const auto decision = decide_attach(preflight, [&] { return attach_eligibility(); },
                                                [&] {
                if (is(L"admission-control-b-attach-failure")) {
                    if (!publish_record(folder / "advance", "disposable fixture\n") ||
                        !publish_record(folder / "quit", "disposable attach race\n") ||
                        WaitForSingleObject(child.hProcess, 5000) != WAIT_OBJECT_0) {
                        SetLastError(ERROR_TIMEOUT);
                        return FALSE;
                    }
                }
                return DebugActiveProcess(child.dwProcessId);
            });
            if (!decision) {
                report_attach_refusal(journal, decision,
                    [&](const std::string& fields) { return row("attach_refused", 0, fields); });
                if (!retail_run() && !control_b()) terminate_exact();
                return false;
            }
        }
        return pump();
    }

private:
    bool start_fixture(const wchar_t* self) {
        std::wstring command = L"\"" + std::wstring(self) + L"\" --child " + scenario +
                               L" \"" + folder.wstring() + L"\"";
        STARTUPINFOW startup{};
        startup.cb = sizeof startup;
        if (!SetEnvironmentVariableW(L"SRR006_FIXTURE_MODE", scenario.c_str()) ||
            !SetEnvironmentVariableW(L"SRR007_DISPOSABLE_ATTACH", late_attach ? L"1" : nullptr) ||
            !CreateProcessW(self, command.data(), nullptr, nullptr, FALSE,
                            (late_attach ? 0 : DEBUG_ONLY_THIS_PROCESS) | CREATE_NO_WINDOW, nullptr, nullptr,
                            &startup, &child))
            return false;
        CloseHandle(child.hThread);
        created = birth(child.hProcess, true);
        run_id = digest + '-' + std::to_string(child.dwProcessId) + '-' + std::to_string(created);
        std::printf("EXACT_CHILD %lu %llu\n", child.dwProcessId, created);
        std::fflush(stdout);
        if (late_attach) {
            row("startup", 0, ",\"covered\":false");
            // A fixture-only watchdog covers a failed synthetic startup.
            const auto start = GetTickCount64();
            while (!fs::exists(folder / "attach-ready")) {
                if (WaitForSingleObject(child.hProcess, 20) != WAIT_TIMEOUT ||
                    GetTickCount64() - start >= 10000) {
                    terminate_exact();
                    return false;
                }
            }
            if (is(L"admission-fixture") || control_b()) {
                // Exercise the retail handle acquisition in a disposable
                // four-slot session instead of using CreateProcess's handle.
                HANDLE process = nullptr;
                auto access = open_attach_target(child.dwProcessId, process);
                StageHandle opened(process);
                if (access) access = check_process_epoch(opened.get(), child.dwProcessId, created);
                if (!access) {
                    report_attach_refusal(journal, {"target_open", access},
                        [&](const std::string& fields) { return row("attach_refused", 0, fields); });
                    return false;
                }
                CloseHandle(child.hProcess);
                child.hProcess = opened.release();
                row("fixture_target_access", 0,
                    ",\"requested_process_access\":" + std::to_string(attach_target_access));
            }
            if (staged_arming()) {
                while (!marker(L"title.request", "TITLE_CONFIRMED", 1)) {
                    if (!exact_running_process() || journal.failed) return false;
                    Sleep(20);
                }
                phase = 1;
                title_boundary = row("title_confirmed", 0, ",\"covered\":false");
                journal.request_flush();
                if (!wait_durable(title_boundary)) return false;
            }
        }
        return true;
    }
    bool pump() {
        const bool kill_policy = DebugSetProcessKillOnExit(!non_killing) != 0;
        const DWORD policy_error = kill_policy ? 0 : GetLastError();
        if (non_killing) row("non_killing_policy", 0, ",\"confirmed\":" + std::to_string(kill_policy) +
                             ",\"winerror\":" + std::to_string(policy_error));
        if (!kill_policy && retail_run()) {
            std::puts("NON_KILLING_POLICY_REFUSED");
            std::fflush(stdout);
            journal.request_flush();
        }
        if (!kill_policy) gap();
        bool pump_ok = true;
        bool wait_fault_injected = false;
        while (!exit_event && !detached) {
            controls();
            DEBUG_EVENT event{};
            const bool transient_wait = is(L"recover-wait") && recovery_break_pending &&
                                        !wait_fault_injected;
            if (transient_wait) wait_fault_injected = true;
            const bool inject_wait = transient_wait || ((is(L"wait-persistent") || is(L"combined-failure")) &&
                                     loader && fs::exists(folder / "fault"));
            if (inject_wait || !WaitForDebugEvent(&event, 25)) {
                const DWORD error = inject_wait ? ERROR_INVALID_HANDLE : GetLastError();
                if (error == ERROR_SEM_TIMEOUT) { periodic_readback(false); continue; }
                gap();
                row("pump_failure", 0, ",\"operation\":\"wait\",\"winerror\":" +
                    std::to_string(error));
                if (transient_wait) continue;
                if (non_killing) {
                    // No verified stopped state exists. Keep the owning pump
                    // available for recovery or a real EXIT event.
                    recovery_unconfirmed = true;
                    Sleep(25);
                    continue;
                }
                terminate_exact();
                return unqualified_recovery();
            }
            ++event_number;
            const DWORD tid = event.dwThreadId;
            const bool loader_before = loader;
            DWORD disposition = DBG_CONTINUE;
            bool fatal = false, thread_exit = false;
            std::optional<unsigned> captured_site;
            Result result{Verdict::sample};
            std::string fields = ",\"event_code\":" + std::to_string(event.dwDebugEventCode);
            if (loader_before && event.dwProcessId == child.dwProcessId &&
                event.dwDebugEventCode != EXIT_PROCESS_DEBUG_EVENT) periodic_readback(true);
            if (event.dwProcessId != child.dwProcessId) {
                fatal = true;
                disposition = DBG_EXCEPTION_NOT_HANDLED;
            } else switch (event.dwDebugEventCode) {
            case CREATE_PROCESS_DEBUG_EVENT: {
                const auto& info = event.u.CreateProcessInfo;
                if (staged_arming()) child.dwThreadId = tid;
                base = reinterpret_cast<Address>(info.lpBaseOfImage);
                const auto verified = verify_creation(info);
                const bool event_kind = late_attach ? info.lpStartAddress == nullptr : tid == child.dwThreadId;
                identity = kill_policy && event_kind && bool(verified);
                fields += ",\"creation_start_address\":" +
                    std::to_string(reinterpret_cast<Address>(info.lpStartAddress));
                fields += ",\"profile_sha256\":\"" +
                    std::string(retail_profile() ? retail_profile_sha256 : digest) + "\"";
                if (!verified) fields += ",\"mapping_failure\":\"" + std::string(verified.failure) + "\"";
                if (identity) {
                    base = verified.base;
                    extent = verified.extent;
                    for (unsigned i = 0; i < addresses.size(); ++i) addresses[i] = base + layout.sites[i];
                }
                if (info.hFile) CloseHandle(info.hFile);
                fatal = !identity || !add(tid, info.hThread);
                break;
            }
            case CREATE_THREAD_DEBUG_EVENT: {
                const auto start = reinterpret_cast<Address>(event.u.CreateThread.lpStartAddress);
                fields += ",\"thread_start_address\":" + std::to_string(start);
                fatal = !forced && !add(tid, event.u.CreateThread.hThread, start);
                if (staged_arming() && ntdll && start == ntdll + breakin_start_rva &&
                    birth(event.u.CreateThread.hThread, false) >= attach_requested_at) {
                    ++fresh_breakin_threads;
                    if (loader) gap();
                }
                if (!fatal && (is(L"competing-breakpoint") || is(L"admission-competitor")) &&
                    ntdll && start == ntdll + breakin_start_rva) {
                    if (held_breakin || SuspendThread(event.u.CreateThread.hThread) == DWORD(-1)) {
                        fatal = true;
                    } else {
                        held_breakin = tid;
                        std::puts("COMPETING_BREAKPOINT_GO");
                        std::fflush(stdout);
                    }
                }
                break;
            }
            case EXIT_THREAD_DEBUG_EVENT: {
                const auto entry = threads.find(tid);
                if (entry == threads.end() || (!stopped && entry->second.frames.awaiting_callback()))
                    gap();
                pending_release.erase(tid);
                thread_exit = true;
                break;
            }
            case LOAD_DLL_DEBUG_EVENT:
                fields += module(event.u.LoadDll);
                break;
            case UNLOAD_DLL_DEBUG_EVENT:
                fields += unload(event.u.UnloadDll);
                break;
            case EXCEPTION_DEBUG_EVENT:
                disposition = exception(event, fields, result, captured_site);
                if (held_breakin && fields.find("\"attach_candidate_refused\":1") != std::string::npos) {
                    if (ResumeThread(threads.at(held_breakin).handle) == DWORD(-1)) fatal = true;
                    held_breakin = 0;
                }
                break;
            case EXIT_PROCESS_DEBUG_EVENT:
                event_exit = event.u.ExitProcess.dwExitCode;
                fields += ",\"exit_code\":" + std::to_string(event_exit);
                if (control_b())
                    fields += ",\"after_durable_control_end\":" +
                        std::to_string(control_durable_phase == std::size(control_phases) + 1);
                else fields += ",\"after_durable_stop\":" + std::to_string(stop_acknowledged());
                for (const auto& [id, thread] : threads) {
                    if (thread.frames.awaiting_callback()) gap();
                }
                exit_event = true;
                break;
            }
            if (fatal) {
                gap();
                row("unsafe_context", tid);
                terminate_exact();
            }
            if (!late_attach && result.verdict == Verdict::unknown && captured_site != 3u) gap();
            if (result.verdict == Verdict::nonfocal) ++rejected;
            const bool persistent = is(L"continue-persistent") && loader &&
                                    event.dwDebugEventCode == EXCEPTION_DEBUG_EVENT &&
                                    fs::exists(folder / "fault");
            const bool injected = (is(L"continue-error") &&
                                  event.dwDebugEventCode == CREATE_PROCESS_DEBUG_EVENT) || persistent;
            std::vector<Suspension> suspended;
            bool restored = false;
            if (recovery_break_owned) {
                // Exercise the refusal path before any context mutation.
                if (!is(L"recover-refusal") && suspend_for_detach(suspended)) {
                    disarmed = true;
                    restored = restore_debug_state();
                }
                if (!restored) row("recovery_unconfirmed", tid);
            }
            const bool inject_recovery_continue = recovery_break_owned && is(L"recover-continue");
            const bool inject_stage_continue = is(L"admission-continue") && !stopped &&
                                               captured_site == 3u;
            bool resumed = !injected && !inject_recovery_continue && !inject_stage_continue &&
                           ContinueDebugEvent(event.dwProcessId, tid, disposition) != 0;
            const DWORD continue_error = resumed ? 0 :
                injected || inject_recovery_continue || inject_stage_continue ? ERROR_GEN_FAILURE : GetLastError();
            if (!resumed && staged_arming()) {
                gap();
                captured_site.reset();
                result = {Verdict::unknown};
            }
            if (!resumed && non_killing) {
                const auto retry_until = GetTickCount64() + 250;
                do {
                    resumed = ContinueDebugEvent(event.dwProcessId, tid, disposition) != 0;
                    if (!resumed) Sleep(10);
                } while (!resumed && GetTickCount64() < retry_until);
                row("recovery_continue", tid, ",\"success\":" + std::to_string(resumed) +
                    ",\"initial_error\":" + std::to_string(continue_error));
            }
            if (resumed) ++continued; else gap();
            fields += ",\"disposition\":" + std::to_string(disposition) +
                      ",\"continue_error\":" + std::to_string(continue_error);
            if (control_b()) fields += ",\"continued\":" + std::to_string(resumed);
            const auto sequence = row("event", tid, fields);
            if (!late_attach && event.dwDebugEventCode == CREATE_PROCESS_DEBUG_EVENT)
                windows.open(sequence, identity && healthy && resumed);
            if (late_attach && !loader_before && loader) {
                const auto barrier = row(control_b() ? "debugger_only_barrier" : "attach_barrier", tid,
                    ",\"continued\":" + std::to_string(resumed) +
                    (control_b() ? ",\"research_context_writes\":" + std::to_string(context_writes) : ""));
                const bool verified = identity && healthy && resumed && barrier && !stopped;
                if (control_b()) {
                    if (verified) arm_barrier = barrier;
                    else {
                        std::puts("DEBUGGER_ONLY_REFUSED");
                        std::fflush(stdout);
                    }
                } else if (staged_arming()) {
                    if (!stopped) {
                        windows.open(title_boundary, false);
                        windows.phase(barrier, false, verified);
                        if (verified) arm_barrier = barrier;
                    }
                    if (!verified) {
                        std::puts("ARMING_REFUSED");
                        std::fflush(stdout);
                    }
                } else windows.open(barrier, verified);
                journal.request_flush();
                if (!staged_arming() && verified) {
                    std::puts("ATTACH_ARMED");
                    std::fflush(stdout);
                }
            }
            if (captured_site && resumed && disposition == DBG_CONTINUE)
                windows.observe(*captured_site, result, sequence);
            if (is(L"cross-window") && sequence && resumed) {
                cross_phase |= result.verdict == Verdict::iterator;
                cross_menu |= result.verdict == Verdict::invoked;
            }
            if (sequence && resumed && result.verdict == Verdict::invoked && !first_invoked)
                first_invoked = sequence;
            if (sequence && resumed && result.verdict == Verdict::allocator && !first_allocator)
                first_allocator = sequence;
            if (thread_exit) threads.erase(tid);
            if (recovery_break_owned) {
                recovery_break_owned = false;
                const bool detach_attempted = resumed && restored &&
                    verify_released_event_state(suspended) && exact_running_process();
                detached = detach_attempted && !is(L"recover-detach-error") &&
                           DebugActiveProcessStop(child.dwProcessId);
                const DWORD detach_error = detached || !detach_attempted ? 0 :
                    is(L"recover-detach-error") ? ERROR_ACCESS_DENIED : GetLastError();
                release_suspensions(suspended);
                recovery_unconfirmed = !detached;
                row("recovery_outcome", 0, ",\"detached\":" + std::to_string(detached) +
                    ",\"detach_attempted\":" + std::to_string(detach_attempted) +
                    ",\"detach_error\":" + std::to_string(detach_error) +
                    ",\"suspensions_released\":1");
                journal.request_flush();
                if (resumed) {
                    std::printf("RECOVERY_RESULT %u\n", detached);
                    std::fflush(stdout);
                }
            }
            if (!resumed) {
                if (non_killing) {
                    // Keep this exact event and disposition. Dropping the
                    // pump could strand an armed target or change its fate.
                    unqualified_recovery();
                    while (!ContinueDebugEvent(event.dwProcessId, tid, disposition)) Sleep(100);
                    ++continued;
                    continue;
                }
                // Recovery is fixture-only. Release the exact held event after
                // requesting termination before waiting on that process.
                pump_ok = false;
                const bool requested = terminate_exact();
                const bool released = requested && !persistent &&
                                      ContinueDebugEvent(event.dwProcessId, tid, disposition);
                row("emergency_continue", tid, ",\"success\":" + std::to_string(released) +
                    ",\"winerror\":" + std::to_string(released ? 0 : persistent ? ERROR_GEN_FAILURE :
                        requested ? GetLastError() : emergency_error));
                if (!released) return unqualified_recovery();
                ++continued;
                if (!exit_event) continue;
            }
        }
        if (!pump_ok) {
            gap();
            row("pump_failure", 0);
            if (!exit_event && !terminate_exact()) return false;
        }
        signaled = WaitForSingleObject(child.hProcess, INFINITE) == WAIT_OBJECT_0;
        if (!signaled || !GetExitCodeProcess(child.hProcess, &process_exit) ||
            (!detached && (!exit_event || event_exit != process_exit))) gap();
        if (is(L"handoff") && fs::exists(folder / "handoff-pid")) {
            handoff = true;
            windows.gap_all();
            gap();
            row("coverage_ended_unobserved_successor", 0);
        }
        row("same_handle_wait", 0, ",\"signaled\":" + std::to_string(signaled) +
            ",\"exit_code\":" + std::to_string(process_exit));
        if (late_attach)
            row("retire_outcome", 0, ",\"requested\":" + std::to_string(retired) +
                ",\"clean\":" + std::to_string(retired && signaled && !recovery_unconfirmed &&
                                               (detached || event_exit == 0) && process_exit == 0));
        return pump_ok && signaled;
    }
public:
    bool receipt(bool pump_ok) {
        if ((retail_run() || control_b()) && !signaled && child.hProcess &&
            WaitForSingleObject(child.hProcess, 0) == WAIT_OBJECT_0) {
            signaled = true;
            GetExitCodeProcess(child.hProcess, &process_exit);
            row("same_handle_wait", 0, ",\"signaled\":1,\"exit_code\":" + std::to_string(process_exit));
        }
        if (control_b()) return control_b_receipt(pump_ok);
        windows.interrupt(journal.accepted);
        journal.finish();
        if (!space_available()) return false;
        const auto hash = sha256(folder / "events.jsonl");
        if (hash.empty()) return false;
        const auto durable = journal.durable.load();
        const bool sealed = stop_acknowledged();
        // A failed STOP sidecar can leave the STOP row in the operational
        // watermark. Its planned closing boundary is ineligible for science.
        const auto scientific_prefix = late_attach && stop_boundary && !sealed ?
            std::min(durable, stop_boundary - 1) : durable;
        const bool complete = !late_attach && healthy && stopped && loader && identity && pump_ok &&
                              !journal.failed && !journal.first_lost && accepted_all(durable);
        const bool invoked = staged_arming() ? windows.has_positive(scientific_prefix, false) :
                             first_invoked && first_invoked <= durable;
        const bool allocator = staged_arming() ? windows.has_positive(scientific_prefix, true) :
                                first_allocator && first_allocator <= durable;
        const bool qualified_zero = stage_b() ?
            sealed && windows.qualified_zero_between(3, 4, scientific_prefix) :
            staged_arming() && windows.qualified_zero_since(1, scientific_prefix);
        const char* science = allocator ? "OBSERVED_REACHED_ALLOCATOR" : invoked ? "OBSERVED_INVOKED" :
                              complete || qualified_zero ? "NOT_OBSERVED" : "INSTRUMENTATION_INCOMPLETE";
        std::ostringstream out;
        out << "{\"schema\":1,\"role\":\"" << (retail_run() ? "retail" : "fixture") << "\",\"method\":\""
            << (late_attach ? "late_attach" : "creation") << "\",\"image_sha256\":\"" << digest
            << "\",\"journal_sha256\":\"" << hash << "\",\"pid\":" << child.dwProcessId
            << ",\"process_birth\":" << created << ",\"fixture_complete\":" << complete
            << ",\"stop_sequence\":" << stop_boundary
            << ",\"stop_durable\":" << sealed
            << ",\"retire_requested\":" << retired
            << ",\"non_killing\":" << non_killing << ",\"detached\":" << detached
            << ",\"observer_healthy\":" << healthy << ",\"pump_completed\":" << pump_ok
            << ",\"target_failed\":";
        if (signaled && process_exit != UINT32_MAX) out << (process_exit != 0); else out << "null";
        out << ",\"forced\":" << forced
            << ",\"emergency_requested\":" << emergency_requested
            << ",\"emergency_error\":" << emergency_error
            << ",\"recovery_unconfirmed\":" << recovery_unconfirmed
            << ",\"handoff_refused\":" << handoff
            << ",\"science\":\"" << science << "\",\"loader\":" << loader
            << ",\"stopped\":" << stopped << ",\"same_handle_signaled\":" << signaled
            << ",\"exit_event\":" << exit_event << ",\"exit_code\":" << process_exit
            << ",\"events\":" << event_number << ",\"continued\":" << continued
            << ",\"foreign\":" << foreign << ",\"thread_births\":" << births
            << ",\"attempted\":" << journal.attempted << ",\"accepted\":" << journal.accepted
            << ",\"rejected\":" << rejected << ",\"flushed\":" << durable
            << ",\"first_lost\":" << journal.first_lost
            << ",\"first_uncommitted\":" << (durable < journal.accepted ? durable + 1 : 0)
            << ",\"queue_high_water\":" << journal.high_water()
            << ",\"writer_failed\":" << journal.failed.load() << ",\"hits\":["
            << hits[0] << ',' << hits[1] << ',' << hits[2] << ',' << hits[3]
            << "],\"after_stop\":[" << after_stop[0] << ',' << after_stop[1] << ','
            << after_stop[2] << ',' << after_stop[3] << "],\"after_gap\":["
            << after_gap[0] << ',' << after_gap[1] << ',' << after_gap[2] << ',' << after_gap[3]
            << "],\"windows\":";
        windows.write_json(out, scientific_prefix, !stage_b() || sealed);
        out << "}\n";
        return publish_record(folder / "receipt.json", out.str());
    }
private:
    bool control_b_receipt(bool pump_ok) {
        journal.finish();
        const auto hash = sha256(folder / "events.jsonl");
        if (hash.empty() || !space_available()) return false;
        const auto durable = journal.durable.load();
        const bool sealed = journal.stop_sealed(control_end);
        const bool complete = identity && loader && healthy && pump_ok && exit_event && signaled &&
            process_exit == event_exit && continued == event_number && !recovery_unconfirmed &&
            !journal.failed && !journal.first_lost && accepted_all(durable) &&
            !context_writes && !blocked_context_writes;
        const bool survived = complete && sealed && control_durable_phase == std::size(control_phases) + 1 &&
                              process_exit == 0;
        const bool load_failed = complete && phase == 3 && control_durable_phase == 3 && process_exit != 0;
        std::ostringstream out;
        out << "{\"schema\":1,\"control_mode\":\"debugger_only\",\"run\":\"" << run_id
            << "\",\"observer_pid\":" << GetCurrentProcessId()
            << ",\"observer_birth\":" << birth(GetCurrentProcess(), true)
            << ",\"pid\":" << child.dwProcessId << ",\"process_birth\":" << created
            << ",\"image_sha256\":\"" << digest << "\",\"journal_sha256\":\"" << hash
            << "\",\"result\":\"" << (survived ? "LOAD_SURVIVED_DEBUGGER_ONLY" :
                                      load_failed ? "LOAD_FAILED_DEBUGGER_ONLY" : "CONTROL_INCOMPLETE")
            << "\",\"last_durable_phase\":" << control_durable_phase
            << ",\"last_requested_phase\":" << phase
            << ",\"native_event_service_complete\":" << complete
            << ",\"continued_events\":" << continued << ",\"native_events\":" << event_number
            << ",\"target_signaled\":" << signaled << ",\"native_exit_event\":" << exit_event
            << ",\"native_exit_code\":" << (exit_event ? std::to_string(event_exit) : "null")
            << ",\"handle_exit_code\":" << (signaled ? std::to_string(process_exit) : "null")
            << ",\"operational_end_sealed\":" << sealed << ",\"operational_end_sequence\":" << control_end
            << ",\"durable_sequence\":" << durable << ",\"writer_failed\":" << journal.failed.load()
            << ",\"research_context_writes\":" << context_writes
            << ",\"blocked_research_context_writes\":" << blocked_context_writes
            << ",\"research_hardware_hits\":" << hits[0] + hits[1] + hits[2] + hits[3] << "}\n";
        return publish_record(folder / "control-receipt.json", out.str());
    }
    bool accepted_all(uint64_t durable) const { return durable == journal.attempted; }
};

int wmain(int argc, wchar_t** argv) {
    if (argc == 4 && wcscmp(argv[1], L"--child") == 0) return fixture_child(argv[2], argv[3]);
    const bool attach = argc == 4 && wcscmp(argv[1], L"--fixture-attach") == 0;
    const bool stage_a = argc == 4 && wcscmp(argv[1], L"--stage-a") == 0 &&
                         wcscmp(argv[2], L"--approved-stage-a") == 0;
    const bool stage_b = argc == 4 && wcscmp(argv[1], L"--stage-b") == 0 &&
                         wcscmp(argv[2], L"--approved-stage-b") == 0;
    const bool control_b = argc == 4 && wcscmp(argv[1], L"--control-b") == 0 &&
                           wcscmp(argv[2], L"--approved-control-b") == 0;
    const bool stage = stage_a || stage_b || control_b;
    if (!attach && !stage && argc != 3) return 2;
    const std::wstring mode = control_b ? L"control-b" : stage_b ? L"stage-b" : stage_a ? L"stage-a" : argv[attach ? 2 : 1];
    const std::array<std::wstring, 25> modes{L"baseline", L"busy", L"quiet", L"delay",
        L"conflict", L"readback", L"overflow", L"write-error", L"emergency", L"crash",
        L"callback-only", L"unreadable", L"handoff", L"foreign-step", L"continue-error", L"slot-loss",
        L"stop-burst", L"wait-persistent", L"continue-persistent", L"emergency-denied", L"abrupt-observer",
        L"reject-retail-profile", L"combined-failure", L"cross-window", L"unexpected-module"};
    const std::array<std::wstring, 36> attach_modes{L"baseline", L"busy", L"overflow", L"write-error",
        L"unexpected-module", L"reject-retail-profile", L"emergency", L"emergency-denied", L"handoff",
        L"slot-loss", L"conflict", L"readback", L"crash", L"unreadable", L"anomalous-return",
        L"competing-breakpoint", L"recover-detach", L"recover-refusal", L"recover-wait",
        L"recover-continue", L"recover-partial", L"recover-detach-error",
        L"admission-fixture", L"admission-critical", L"admission-quiet",
        L"admission-competitor", L"admission-slot-replaced", L"admission-continue",
        L"admission-overlay-drift", L"admission-drift-arrival", L"admission-overlay-lookalike",
        L"admission-stage-b-quiet", L"admission-stage-b-cross",
        L"admission-control-b-load", L"admission-control-b-epoch", L"admission-control-b-attach-failure"};
    if (!stage && (attach ? std::find(attach_modes.begin(), attach_modes.end(), mode) == attach_modes.end() :
                 std::find(modes.begin(), modes.end(), mode) == modes.end())) return 2;
    wchar_t self[32768]{};
    if (!GetModuleFileNameW(nullptr, self, ARRAYSIZE(self))) return 3;
    const auto folder = fs::absolute(argv[attach || stage ? 3 : 2]);
    if (!space_available() || !fs::create_directory(folder)) return 3;
    const auto image = read_file(stage ? retail_exe : self);
    if (!image || (stage && !matches_path(image.get(), retail_exe))) return 3;
    int status = 3;
    try {
        const std::string digest = stage ? std::string(retail_image_profile.image_sha256) : sha256(self);
        if (digest.empty()) throw std::runtime_error("self hash");
        Journal journal(folder / "events.jsonl", mode == L"overflow" ? 32 : 8192,
                        mode == L"write-error", mode == L"overflow", mode == L"abrupt-observer",
                        control_b || mode.starts_with(L"admission-control-b-") ?
                            L"operational-end-prefix.json" : L"stop-prefix.json");
        const auto role = stage ? ProfileRole::retail :
            mode == L"reject-retail-profile" ? ProfileRole::pinned_retail : ProfileRole::fixture;
        Observer observer(journal, folder, mode.c_str(), image.get(), digest, role, attach || stage);
        const bool ok = observer.run(self);
        const bool reported = observer.receipt(ok);
        status = reported && (ok || mode == L"continue-error") ? 0 : 4;
    } catch (const std::exception& e) {
        std::fprintf(stderr, "%s\n", e.what());
    }
    return status;
}
