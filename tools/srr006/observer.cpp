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
#include <sstream>
#include <vector>
#include "correlation.h"
#include "fixture.h"
#include "journal.h"
#include "retail_profile.h"
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
static bool read_context(HANDLE thread, CONTEXT& c) {
    c.ContextFlags = CONTEXT_CONTROL | CONTEXT_INTEGER | CONTEXT_DEBUG_REGISTERS;
    return GetThreadContext(thread, &c);
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
    FILE_ID_INFO x{}, y{};
    return GetFileInformationByHandleEx(a, FileIdInfo, &x, sizeof x) &&
           GetFileInformationByHandleEx(b, FileIdInfo, &y, sizeof y) &&
           x.VolumeSerialNumber == y.VolumeSerialNumber &&
           std::memcmp(&x.FileId, &y.FileId, sizeof x.FileId) == 0;
}

struct Thread {
    HANDLE handle;
    uint64_t created, generation;
    CONTEXT original{};
    bool armed = false;
    Correlation frames;
};

enum class ProfileRole { fixture, pinned_retail };

class Observer {
    Journal& journal;
    fs::path folder;
    std::wstring scenario;
    const ProfileRole profile_role;
    PROCESS_INFORMATION child{};
    HANDLE image;
    std::string digest;
    Address local, base = 0, ntdll = 0, loader_rva = 0;
    unsigned extent;
    Layout layout;
    std::array<Address, 4> addresses{};
    std::map<DWORD, Thread> threads;
    std::map<Address, std::string> modules;
    WindowEvidence windows{{"fixture_startup", "fixture_title", "fixture_menu"}};
    uint64_t created = 0, births = 0, continued = 0, foreign = 0;
    uint64_t phase_ack = 0, menu_ack = 0, stop_ack = 0, event_number = 0;
    uint64_t first_invoked = 0, first_allocator = 0, rejected = 0;
    unsigned phase = 0;
    bool loader = false, identity = false, healthy = true, stopped = false;
    bool handoff = false;
    bool forced = false, exit_event = false, signaled = false;
    bool emergency_requested = false, recovery_unconfirmed = false, abrupt_queued = false;
    bool cross_phase = false, cross_menu = false;
    DWORD emergency_error = 0;
    DWORD event_exit = UINT32_MAX, process_exit = UINT32_MAX;
    std::array<uint64_t, 4> hits{};
    std::array<uint64_t, 4> after_stop{};
    std::array<uint64_t, 4> after_gap{};
    std::array<unsigned char, 16> loader_bytes{};
    std::wstring loader_mapping;
    LARGE_INTEGER frequency{};

    bool is(const wchar_t* name) const { return scenario == name; }
    bool retail_profile() const { return profile_role == ProfileRole::pinned_retail; }

    void gap() {
        healthy = false;
        windows.gap();
        for (auto& [tid, thread] : threads) thread.frames.clear();
    }
    uint64_t row(const char* kind, DWORD tid, const std::string& fields = "") {
        LARGE_INTEGER qpc{};
        FILETIME utc{};
        QueryPerformanceCounter(&qpc);
        GetSystemTimePreciseAsFileTime(&utc);
        const auto thread = threads.find(tid);
        std::ostringstream out;
        out << "\"kind\":\"" << kind << "\",\"run\":\"" << digest << '-' << child.dwProcessId
            << '-' << created << "\",\"role\":\"fixture\",\"qpc\":" << qpc.QuadPart
            << ",\"qpc_frequency\":" << frequency.QuadPart << ",\"utc_filetime\":" << ticks(utc)
            << ",\"pid\":" << child.dwProcessId << ",\"process_birth\":" << created
            << ",\"tid\":" << tid << ",\"thread_birth\":"
            << (thread == threads.end() ? 0 : thread->second.created)
            << ",\"generation\":" << (thread == threads.end() ? 0 : thread->second.generation)
            << ",\"base\":" << base << ",\"extent\":" << extent
            << ",\"image_sha256\":\"" << digest << "\",\"identity\":" << identity
            << ",\"phase\":" << phase << ",\"stopped\":" << stopped
            << ",\"healthy\":" << healthy << ",\"event\":" << event_number << fields;
        if (!journal.append(out.str())) { gap(); return 0; }
        return journal.accepted;
    }

    bool mapped(Address address, void* data, size_t size) const {
        SIZE_T received = 0;
        return ReadProcessMemory(child.hProcess, reinterpret_cast<void*>(address), data,
                                 size, &received) && received == size;
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
    // Called between events using only balanced, observer-owned suspensions.
    // A thread born/exiting around the check can make the census indeterminate.
    bool checkpoint() {
        if (!identity || !loader) return false;
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
            if (entry == threads.end() || !entry->second.armed) { complete = false; continue; }
            const auto& thread = entry->second;
            if (SuspendThread(thread.handle) == DWORD(-1)) { complete = false; continue; }
            CONTEXT c{};
            const bool readback = read_context(thread.handle, c);
            // Simulate a persistent loss at the same decision boundary as the
            // real readback. Windows may restore loader-exception context
            // transiently cleared by the separate native injection control.
            if (is(L"slot-loss") && item.th32ThreadID == child.dwThreadId) c.Dr7 = 0;
            const bool valid = birth(thread.handle, false) == thread.created && readback && owns(c);
            const bool released = ResumeThread(thread.handle) != DWORD(-1);
            if (!valid || !released) complete = false;
        } while (Thread32Next(snapshot, &item));
        complete = complete && GetLastError() == ERROR_NO_MORE_FILES;
        CloseHandle(snapshot);
        return complete && observed == threads.size() && observed != 0;
    }
    bool add(DWORD tid, HANDLE handle) {
        const auto stamp = birth(handle, false);
        if (!identity || threads.size() == 256 || !stamp ||
            GetProcessIdOfThread(handle) != child.dwProcessId || GetThreadId(handle) != tid)
            return false;
        auto [entry, inserted] = threads.try_emplace(tid, Thread{handle, stamp, ++births});
        if (!inserted) return false;
        auto& thread = entry->second;
        auto& c = thread.original;
        if (!read_context(handle, c)) return false;
        // Inject a conflicting original snapshot at the decision boundary.
        CONTEXT before = c;
        if (is(L"conflict") && tid == child.dwThreadId) before.Dr7 |= 1;
        const auto initial_slots = slots(before);
        std::ostringstream state;
        state << ",\"original_dr\":[" << before.Dr0 << ',' << before.Dr1 << ','
              << before.Dr2 << ',' << before.Dr3 << "],\"original_dr6\":" << before.Dr6
              << ",\"original_dr7\":" << before.Dr7 << ",\"original_flags\":" << before.EFlags;
        row("arm_attempt", tid, state.str());
        if ((before.Dr7 & dr7_fields) || (before.Dr6 & dr6_causes) ||
            (before.EFlags & (tf | rf)) ||
            std::any_of(initial_slots.begin(), initial_slots.end(), [](auto a) { return a != 0; }))
            return false;
        CONTEXT armed = c;
        armed.ContextFlags = CONTEXT_DEBUG_REGISTERS;
        armed.Dr0 = addresses[0]; armed.Dr1 = addresses[1];
        armed.Dr2 = addresses[2]; armed.Dr3 = addresses[3];
        armed.Dr7 = (armed.Dr7 & ~dr7_fields) | 0x55;
        CONTEXT check{};
        if (!SetThreadContext(handle, &armed) || !read_context(handle, check)) return false;
        if (is(L"readback") && tid == child.dwThreadId) check.Dr3 ^= 1;
        const bool verified = owns(check) && !(check.EFlags & rf) &&
                              (check.Dr6 & dr6_causes) == 0;
        std::ostringstream actual;
        actual << ",\"dr\":[" << check.Dr0 << ',' << check.Dr1 << ',' << check.Dr2 << ','
               << check.Dr3 << "],\"dr6\":" << check.Dr6 << ",\"dr7\":" << check.Dr7
               << ",\"flags\":" << check.EFlags << ",\"verified\":" << verified;
        row("arm_readback", tid, actual.str());
        thread.armed = verified;
        return thread.armed;
    }
    bool terminate_exact() {
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
    std::string module(const LOAD_DLL_DEBUG_INFO& info) {
        const Address at = reinterpret_cast<Address>(info.lpBaseOfDll);
        wchar_t path[32768]{};
        const bool readable = K32GetMappedFileNameW(child.hProcess, info.lpBaseOfDll, path, ARRAYSIZE(path)) != 0;
        if (!ntdll && readable &&
            _wcsicmp(path, loader_mapping.c_str()) == 0 &&
            (!info.hFile || same_file(info.hFile, loader_file)))
            ntdll = at;
        if (info.hFile) CloseHandle(info.hFile);
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
        if (modules.size() < 256 && !modules.try_emplace(at, basename).second) gap();
        if (!expected || modules.size() == 256) gap();
        return ",\"module_base\":" + std::to_string(at) + ",\"module_name\":\"" + basename +
               "\",\"module_expected\":" + std::to_string(expected) +
               ",\"module_system_directory\":" + std::to_string(in_system) +
               ",\"module_mapped_image\":" + std::to_string(mapped_image);
    }
    std::string unload(const UNLOAD_DLL_DEBUG_INFO& info) {
        const auto address = reinterpret_cast<Address>(info.lpBaseOfDll);
        const auto module = modules.extract(address);
        // A loss of a qualified module is a change of the observed image set.
        if (!stopped || module.empty() || address == ntdll) gap();
        return ",\"module_base\":" + std::to_string(address) + ",\"module_name\":\"" +
               (module.empty() ? std::string{} : module.mapped()) + "\"";
    }
    bool loader_event(const DEBUG_EVENT& event, Address address) {
        const auto& e = event.u.Exception;
        if (loader || !identity || !ntdll || !loader_rva ||
            event.dwThreadId != child.dwThreadId || !e.dwFirstChance ||
            e.ExceptionRecord.ExceptionCode != EXCEPTION_BREAKPOINT ||
            address != ntdll + loader_rva)
            return false;
        std::array<unsigned char, 16> bytes{};
        MEMORY_BASIC_INFORMATION mapping{};
        if (!VirtualQueryEx(child.hProcess, reinterpret_cast<void*>(address), &mapping, sizeof mapping) ||
            mapping.Type != MEM_IMAGE || reinterpret_cast<Address>(mapping.AllocationBase) != ntdll ||
            !mapped(address, bytes.data(), bytes.size()) || bytes != loader_bytes) return false;
        for (const auto& [tid, entry] : threads) {
            CONTEXT c{};
            if (!entry.armed || !read_context(entry.handle, c) || !owns(c)) return false;
        }
        const auto initial = threads.find(event.dwThreadId);
        CONTEXT c{};
        if (initial == threads.end() || !read_context(initial->second.handle, c) ||
            c.Rip != address + 1 || c.EFlags & (tf | rf) || c.Dr6 & dr6_causes)
            return false;
        return loader = true;
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
            fields += ",\"owner\":\"loader\"";
            if (is(L"slot-loss")) {
                auto& initial = threads.at(event.dwThreadId);
                CONTEXT c{}, check{};
                bool changed = false;
                if (read_context(initial.handle, c)) {
                    c.Dr0 = c.Dr1 = c.Dr2 = c.Dr3 = c.Dr7 = 0;
                    c.ContextFlags = CONTEXT_DEBUG_REGISTERS;
                    changed = SetThreadContext(initial.handle, &c) &&
                              read_context(initial.handle, check) && !owns(check);
                }
                fields += ",\"fixture_slot_loss\":" + std::to_string(changed);
            }
            return DBG_CONTINUE;
        }
        auto entry = threads.find(event.dwThreadId);
        const auto found = std::find(addresses.begin(), addresses.end(), addr);
        const unsigned site = static_cast<unsigned>(found - addresses.begin());
        if (code == EXCEPTION_SINGLE_STEP && e.dwFirstChance && site < addresses.size() &&
            entry != threads.end() && entry->second.armed) {
            CONTEXT c{};
            if (!read_context(entry->second.handle, c) || !owns(c) || c.Rip != addr ||
                (c.Dr6 & dr6_causes) != (1ULL << site)) {
                gap();
                return DBG_EXCEPTION_NOT_HANDLED;
            }
            fields += ",\"owner\":\"hardware\",\"site\":" + std::to_string(site) +
                      ",\"rva\":" + std::to_string(layout.sites[site]) +
                      ",\"before_flags\":" + std::to_string(c.EFlags) +
                      ",\"before_dr6\":" + std::to_string(c.Dr6);
            if (stopped) ++after_stop[site];
            else if (!healthy) ++after_gap[site];
            else {
                captured_site = site;
                fields += capture(entry->second, site, c, result);
            }
            c.ContextFlags = CONTEXT_CONTROL | CONTEXT_DEBUG_REGISTERS;
            c.Dr6 &= ~(1ULL << site);
            c.EFlags |= rf;
            CONTEXT check{};
            const bool readback = SetThreadContext(entry->second.handle, &c) &&
                                  read_context(entry->second.handle, check);
            fields += ",\"resume_flags\":" + std::to_string(check.EFlags) +
                      ",\"resume_dr6\":" + std::to_string(check.Dr6) +
                      ",\"readback\":" + std::to_string(readback);
            if (!readback || !owns(check) ||
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
        if (!e.dwFirstChance || code != 0xe1230042) gap();
        else if (entry != threads.end()) {
            if (entry->second.frames.awaiting_callback()) gap();
            else entry->second.frames.clear();
        }
        return DBG_EXCEPTION_NOT_HANDLED;
    }
    void controls() {
        if (journal.failed && healthy) gap();
        const bool fixture_stop = is(L"stop-burst") && hits[0] >= 256;
        if (!stopped && phase == 0 && (fixture_stop || cross_phase || fs::exists(folder / "phase"))) {
            phase = 1;
            const bool checked = checkpoint();
            if (!checked) gap();
            phase_ack = row("operator_phase", 0, ",\"checkpoint\":" + std::to_string(checked));
            windows.phase(phase_ack, checked && healthy);
            journal.request_flush();
        }
        if (!stopped && phase == 1 && (cross_menu || fs::exists(folder / "menu"))) {
            phase = 2;
            const bool checked = checkpoint();
            if (!checked) gap();
            const auto marker = row("operator_menu", 0, ",\"checkpoint\":" + std::to_string(checked));
            windows.phase(marker, checked && healthy);
            menu_ack = marker;
            journal.request_flush();
        }
        if (!stopped && (fixture_stop || fs::exists(folder / "stop"))) {
            stopped = true;
            const bool checked = checkpoint();
            if (!checked) gap();
            for (auto& [tid, thread] : threads) {
                if (thread.frames.awaiting_callback()) healthy = false;
                thread.frames.clear();
            }
            stop_ack = row("stop", 0, ",\"checkpoint\":" + std::to_string(checked));
            windows.stop(stop_ack, checked && healthy);
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
        if (stop_ack && journal.durable >= stop_ack) {
            std::printf("STOP_DURABLE %llu\n", stop_ack);
            std::fflush(stdout);
            stop_ack = 0;
        }
        if (menu_ack && journal.durable >= menu_ack) {
            std::printf("MENU_DURABLE %llu\n", menu_ack);
            std::fflush(stdout);
            menu_ack = 0;
        }
        if (!emergency_requested && fs::exists(folder / "emergency")) terminate_exact();
    }
    HANDLE loader_file = INVALID_HANDLE_VALUE;

public:
    Observer(Journal& output, fs::path dir, const wchar_t* mode, HANDLE source, std::string sha,
             ProfileRole role)
        : journal(output), folder(std::move(dir)), scenario(mode), profile_role(role),
          image(source), digest(std::move(sha)) {
        local = reinterpret_cast<Address>(GetModuleHandleW(nullptr));
        const auto dos = reinterpret_cast<const IMAGE_DOS_HEADER*>(local);
        const auto pe = reinterpret_cast<const IMAGE_NT_HEADERS64*>(local + dos->e_lfanew);
        extent = pe->OptionalHeader.SizeOfImage;
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
            if (sha256(path) == "36b1a62e4bf6bf7d68458fff6e8a33b39f6527ec6a46e55ecdd12cde83894c8d") {
                // This OS image delivers its startup breakpoint at an
                // internal ntdll instruction instead of the exported stub.
                loader_rva = 0xd0860;
                std::memcpy(loader_bytes.data(), reinterpret_cast<void*>(reinterpret_cast<Address>(module) +
                            loader_rva), loader_bytes.size());
            }
        }
        if (loader_file == INVALID_HANDLE_VALUE) throw std::runtime_error("system ntdll file");
        if (!loader_rva || loader_bytes[0] != 0xcc) throw std::runtime_error("unqualified loader image");
        if (!K32GetMappedFileNameW(GetCurrentProcess(), module, path, ARRAYSIZE(path)))
            throw std::runtime_error("system ntdll mapping");
        loader_mapping = path;
        QueryPerformanceFrequency(&frequency);
    }
    ~Observer() {
        if (child.hProcess) CloseHandle(child.hProcess);
        CloseHandle(loader_file);
    }

    bool run(const wchar_t* self) {
        std::wstring command = L"\"" + std::wstring(self) + L"\" --child " + scenario +
                               L" \"" + folder.wstring() + L"\"";
        STARTUPINFOW startup{};
        startup.cb = sizeof startup;
        if (!SetEnvironmentVariableW(L"SRR006_FIXTURE_MODE", scenario.c_str()) ||
            !CreateProcessW(self, command.data(), nullptr, nullptr, FALSE,
                            DEBUG_ONLY_THIS_PROCESS | CREATE_NO_WINDOW, nullptr, nullptr,
                            &startup, &child))
            return false;
        CloseHandle(child.hThread);
        created = birth(child.hProcess, true);
        const bool kill_policy = DebugSetProcessKillOnExit(TRUE) != 0;
        std::printf("EXACT_CHILD %lu %llu\n", child.dwProcessId, created);
        std::fflush(stdout);
        if (!kill_policy) gap();
        bool pump_ok = true;
        while (!exit_event) {
            controls();
            DEBUG_EVENT event{};
            const bool inject_wait = (is(L"wait-persistent") || is(L"combined-failure")) && loader &&
                                     fs::exists(folder / "fault");
            if (inject_wait || !WaitForDebugEvent(&event, 25)) {
                const DWORD error = inject_wait ? ERROR_INVALID_HANDLE : GetLastError();
                if (error == ERROR_SEM_TIMEOUT) continue;
                gap();
                row("pump_failure", 0, ",\"operation\":\"wait\",\"winerror\":" +
                    std::to_string(error));
                terminate_exact();
                return unqualified_recovery();
            }
            ++event_number;
            const DWORD tid = event.dwThreadId;
            DWORD disposition = DBG_CONTINUE;
            bool fatal = false, thread_exit = false;
            std::optional<unsigned> captured_site;
            Result result{Verdict::sample};
            std::string fields = ",\"event_code\":" + std::to_string(event.dwDebugEventCode);
            if (event.dwProcessId != child.dwProcessId) {
                fatal = true;
                disposition = DBG_EXCEPTION_NOT_HANDLED;
            } else switch (event.dwDebugEventCode) {
            case CREATE_PROCESS_DEBUG_EVENT: {
                const auto& info = event.u.CreateProcessInfo;
                base = reinterpret_cast<Address>(info.lpBaseOfImage);
                const auto verified = verify_creation(info);
                identity = kill_policy && tid == child.dwThreadId && bool(verified);
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
            case CREATE_THREAD_DEBUG_EVENT:
                fatal = !forced && !add(tid, event.u.CreateThread.hThread);
                break;
            case EXIT_THREAD_DEBUG_EVENT: {
                const auto entry = threads.find(tid);
                if (entry == threads.end() || (!stopped && entry->second.frames.awaiting_callback()))
                    gap();
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
                break;
            case EXIT_PROCESS_DEBUG_EVENT:
                event_exit = event.u.ExitProcess.dwExitCode;
                fields += ",\"exit_code\":" + std::to_string(event_exit);
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
            if (result.verdict == Verdict::unknown && captured_site != 3u) gap();
            if (result.verdict == Verdict::nonfocal) ++rejected;
            const bool persistent = is(L"continue-persistent") && loader &&
                                    event.dwDebugEventCode == EXCEPTION_DEBUG_EVENT &&
                                    fs::exists(folder / "fault");
            const bool injected = (is(L"continue-error") &&
                                  event.dwDebugEventCode == CREATE_PROCESS_DEBUG_EVENT) || persistent;
            const bool resumed = !injected && ContinueDebugEvent(event.dwProcessId, tid, disposition) != 0;
            const DWORD continue_error = resumed ? 0 : injected ? ERROR_GEN_FAILURE : GetLastError();
            if (resumed) ++continued; else gap();
            fields += ",\"disposition\":" + std::to_string(disposition) +
                      ",\"continue_error\":" + std::to_string(continue_error);
            const auto sequence = row("event", tid, fields);
            if (event.dwDebugEventCode == CREATE_PROCESS_DEBUG_EVENT)
                windows.open(sequence, identity && healthy && resumed);
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
            if (!resumed) {
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
            !exit_event || event_exit != process_exit) gap();
        if (is(L"handoff") && fs::exists(folder / "handoff-pid")) {
            handoff = true;
            windows.gap_all();
            gap();
            row("coverage_ended_unobserved_successor", 0);
        }
        row("same_handle_wait", 0, ",\"signaled\":" + std::to_string(signaled) +
            ",\"exit_code\":" + std::to_string(process_exit));
        return pump_ok && signaled;
    }
    bool receipt(bool pump_ok) {
        windows.interrupt(journal.accepted);
        journal.finish();
        if (!space_available()) return false;
        const auto hash = sha256(folder / "events.jsonl");
        if (hash.empty()) return false;
        const auto durable = journal.durable.load();
        const bool complete = healthy && stopped && loader && identity && pump_ok &&
                              !journal.failed && !journal.first_lost && accepted_all(durable);
        const bool invoked = first_invoked && first_invoked <= durable;
        const bool allocator = first_allocator && first_allocator <= durable;
        const char* science = allocator ? "OBSERVED_REACHED_ALLOCATOR" : invoked ? "OBSERVED_INVOKED" :
                              complete ? "NOT_OBSERVED" : "INSTRUMENTATION_INCOMPLETE";
        std::ostringstream out;
        out << "{\"schema\":1,\"role\":\"fixture\",\"image_sha256\":\"" << digest
            << "\",\"journal_sha256\":\"" << hash << "\",\"pid\":" << child.dwProcessId
            << ",\"process_birth\":" << created << ",\"fixture_complete\":" << complete
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
        windows.write_json(out, durable);
        out << "}\n";
        return publish_record(folder / "receipt.json", out.str());
    }
private:
    bool accepted_all(uint64_t durable) const { return durable == journal.attempted; }
};

int wmain(int argc, wchar_t** argv) {
    if (argc == 4 && wcscmp(argv[1], L"--child") == 0) return fixture_child(argv[2], argv[3]);
    if (argc != 3) return 2;
    const std::wstring mode = argv[1];
    const std::array<std::wstring, 25> modes{L"baseline", L"busy", L"quiet", L"delay",
        L"conflict", L"readback", L"overflow", L"write-error", L"emergency", L"crash",
        L"callback-only", L"unreadable", L"handoff", L"foreign-step", L"continue-error", L"slot-loss",
        L"stop-burst", L"wait-persistent", L"continue-persistent", L"emergency-denied", L"abrupt-observer",
        L"reject-retail-profile", L"combined-failure", L"cross-window", L"unexpected-module"};
    if (std::find(modes.begin(), modes.end(), mode) == modes.end()) return 2;
    wchar_t self[32768]{};
    if (!GetModuleFileNameW(nullptr, self, ARRAYSIZE(self))) return 3;
    const auto folder = fs::absolute(argv[2]);
    if (!space_available() || !fs::create_directory(folder)) return 3;
    HANDLE image = CreateFileW(self, GENERIC_READ, FILE_SHARE_READ, nullptr, OPEN_EXISTING, 0, nullptr);
    if (image == INVALID_HANDLE_VALUE) return 3;
    int status = 3;
    try {
        const auto digest = sha256(self);
        if (digest.empty()) throw std::runtime_error("self hash");
        Journal journal(folder / "events.jsonl", mode == L"overflow" ? 32 : 8192,
                        mode == L"write-error", mode == L"overflow", mode == L"abrupt-observer");
        const auto role = mode == L"reject-retail-profile" ? ProfileRole::pinned_retail : ProfileRole::fixture;
        Observer observer(journal, folder, mode.c_str(), image, digest, role);
        const bool ok = observer.run(self);
        const bool reported = observer.receipt(ok);
        status = reported && (ok || mode == L"continue-error") ? 0 : 4;
    } catch (const std::exception& e) {
        std::fprintf(stderr, "%s\n", e.what());
    }
    CloseHandle(image);
    return status;
}
