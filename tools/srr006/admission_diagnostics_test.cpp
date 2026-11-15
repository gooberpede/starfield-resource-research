#define NOMINMAX
#include <cassert>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include "journal.h"
#include "stage_a.h"

using namespace srr006;
namespace fs = std::filesystem;

static AdmissionCheck census(bool main_seen, bool loader_seen, DWORD end_error,
                             bool first_ok = true) {
    unsigned index = 0;
    return scan_attach_modules(
        [&] {
            if (!first_ok) SetLastError(ERROR_BAD_LENGTH);
            return first_ok;
        },
        [&] {
            if (++index < 2) return true;
            SetLastError(end_error);
            return false;
        },
        [&](bool& main, bool& loader) {
            if (index == 0) main = main_seen;
            if (index == 1) loader = loader_seen;
            return AdmissionCheck{};
        });
}

static AdmissionCheck changed_code() {
    constexpr uint64_t base = 0x140000000;
    std::array<BYTE, 4096> bytes{};
    IMAGE_DOS_HEADER dos{};
    dos.e_magic = IMAGE_DOS_SIGNATURE;
    dos.e_lfanew = sizeof dos;
    IMAGE_NT_HEADERS64 pe{};
    pe.Signature = IMAGE_NT_SIGNATURE;
    pe.FileHeader.Machine = IMAGE_FILE_MACHINE_AMD64;
    pe.FileHeader.SizeOfOptionalHeader = sizeof(IMAGE_OPTIONAL_HEADER64);
    pe.OptionalHeader.Magic = IMAGE_NT_OPTIONAL_HDR64_MAGIC;
    pe.OptionalHeader.ImageBase = base;
    pe.OptionalHeader.SizeOfImage = static_cast<DWORD>(bytes.size());
    pe.OptionalHeader.SizeOfHeaders = 512;
    std::memcpy(bytes.data(), &dos, sizeof dos);
    std::memcpy(bytes.data() + dos.e_lfanew, &pe, sizeof pe);
    const auto headers = sha256_memory(bytes.data(), 512);
    const auto code = sha256_memory(bytes.data() + 512, 1);
    const uint64_t relocated = base + 512;
    std::memcpy(bytes.data() + 520, &relocated, sizeof relocated);
    const ImageWindow windows[]{{0, 512, headers, false}, {512, 1, code, true}};
    const ImageSlot slots[]{{520, 512}};
    const ImageProfile profile{{}, {}, 0, base, pe.OptionalHeader.SizeOfImage, windows, slots};
    auto reader = [&](uint64_t address, void* out, size_t size, bool) {
        std::memcpy(out, bytes.data() + (address - base), size);
        return true;
    };
    assert(verify_profile_windows(profile, base, reader));
    bytes[512] ^= 1;
    const auto result = verify_profile_windows(profile, base, reader);
    assert(!result);
    AdmissionCheck check{result.failure};
    check.detail = "main_image_mapping";
    check.rva = result.rva;
    return check;
}

int wmain(int argc, wchar_t** argv) {
    if (argc != 2 || !space_available()) return 2;
    const fs::path output = argv[1];
    if (!fs::create_directory(output)) return 2;
    const auto failed_dir = output / "write-failure";
    fs::create_directory(failed_dir);
    const auto pid = GetCurrentProcessId();
    HANDLE process = nullptr;
    assert(open_attach_target(pid, process));
    const StageHandle target(process);
    const auto born = profile_detail::process_birth(target.get());
    assert(check_process_epoch(target.get(), pid, born));
    assert(check_debugger_absent(target.get()));
    const StageHandle limited(OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION | PROCESS_VM_READ | SYNCHRONIZE,
                                          FALSE, pid));
    assert(limited && check_process_epoch(limited.get(), pid, born));
    const auto denied = check_debugger_absent(limited.get());
    assert(!denied && denied.winerror == DWORD{ERROR_ACCESS_DENIED});
    HANDLE rejected_handle = nullptr;
    auto open_error = open_attach_target(0, rejected_handle);
    assert(!open_error && !rejected_handle && open_error.winerror == DWORD{ERROR_INVALID_PARAMETER});
    open_error.expected = attach_target_access;
    std::ofstream(output / "first").put('1');
    std::ofstream(output / "second").put('1');
    const auto first = read_file((output / "first").c_str());
    const auto second = read_file((output / "second").c_str());
    assert(first && second && check_file_identity(first.get(), first.get()));
    assert(census(true, true, ERROR_NO_MORE_FILES));

    Journal journal(output / "events.jsonl", 64, false, false, false);
    auto refusal = [&](const char* scenario, AttachDecision result) {
        assert(!result);
        assert(report_attach_refusal(journal, result, [&](const std::string& fields) {
            const std::string row = "\"kind\":\"attach_refused\",\"case\":\"" +
                                    std::string(scenario) + "\"" + fields;
            return journal.append(row) ? journal.accepted : 0;
        }));
        assert(journal.durable == journal.accepted);
    };
    auto not_eligible = []() -> AdmissionCheck { assert(false); return {}; };
    auto not_attached = [] { assert(false); return FALSE; };
    auto reject = [&](const char* scenario, AdmissionCheck check) {
        refusal(scenario, decide_attach(check, not_eligible, not_attached));
    };
    reject("debugger-query-denied", denied);
    refusal("target-open-invalid", {"target_open", open_error});
    reject("pid", check_process_epoch(target.get(), pid + 1, born));
    reject("epoch", check_process_epoch(target.get(), pid, born + 1));
    reject("file-id", check_file_identity(first.get(), second.get()));
    reject("mapping", changed_code());
    reject("first-module", census(false, false, ERROR_NO_MORE_FILES, false));
    reject("iteration", census(true, true, ERROR_PARTIAL_COPY));
    reject("missing-loader", census(true, false, ERROR_NO_MORE_FILES));
    reject("missing-main", census(false, true, ERROR_NO_MORE_FILES));
    reject("overlay", check_backing_path(first.get(), fs::absolute(output / "second").wstring()));
    refusal("eligibility", decide_attach({}, [] { return AdmissionCheck{"operator_cancel"}; }, not_attached));
    refusal("attach-api", decide_attach({}, [] { return AdmissionCheck{}; }, [] {
        SetLastError(ERROR_ACCESS_DENIED);
        return FALSE;
    }));
    unsigned attach_calls = 0;
    assert(decide_attach({}, [] { return AdmissionCheck{}; }, [&] { ++attach_calls; return TRUE; }));
    assert(attach_calls == 1);
    journal.finish();

    // The writer cuts the next row after a separately flushed 64-row prefix.
    Journal broken(failed_dir / "events.jsonl", 128, true, false, false);
    assert(flush_attach_refusal(broken, [&] {
        for (unsigned i = 0; i < 64; ++i) assert(broken.append("\"kind\":\"fixture_prefix\""));
        return broken.accepted;
    }));
    const auto rejected = decide_attach({"target_already_debugged"}, not_eligible, not_attached);
    assert(!report_attach_refusal(broken, rejected, [&](const std::string& fields) {
        return broken.append("\"kind\":\"attach_refused\"" + fields) ? broken.accepted : 0;
    }));
    assert(broken.failed && broken.durable == 64);
    broken.finish();
    std::puts("13 durable diagnostic refusals; actual query success and denial; injected write failure retained prefix");
}
