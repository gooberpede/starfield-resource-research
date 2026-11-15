#pragma once

#include <windows.h>
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <optional>
#include <string>
#include <string_view>

namespace srr006 {

struct AdmissionCheck {
    const char* predicate = nullptr;
    const char* operation = nullptr;
    std::optional<DWORD> winerror{};
    std::optional<uint64_t> expected{}, observed{};
    const char* detail = nullptr;
    std::optional<uint32_t> rva{};

    explicit operator bool() const { return predicate == nullptr; }
};

inline AdmissionCheck win32_failure(const char* predicate, const char* operation) {
    const DWORD error = GetLastError();
    return {predicate, operation, error};
}

inline constexpr DWORD attach_target_access = PROCESS_QUERY_INFORMATION | PROCESS_VM_READ | SYNCHRONIZE;

inline AdmissionCheck open_attach_target(DWORD pid, HANDLE& process) {
    process = OpenProcess(attach_target_access, FALSE, pid);
    if (!process) return win32_failure("target_handle_open", "OpenProcess");
    return {};
}

inline AdmissionCheck check_debugger_absent(HANDLE process) {
    BOOL debugged = FALSE;
    if (!CheckRemoteDebuggerPresent(process, &debugged))
        return win32_failure("target_debugger_query", "CheckRemoteDebuggerPresent");
    if (debugged) return {"target_already_debugged"};
    return {};
}

inline AdmissionCheck value_mismatch(const char* predicate, uint64_t expected, uint64_t observed) {
    AdmissionCheck result{predicate};
    result.expected = expected;
    result.observed = observed;
    return result;
}

inline AdmissionCheck check_process_epoch(HANDLE process, DWORD expected_pid, uint64_t expected_birth) {
    if (!expected_birth) return {"target_epoch_unset"};
    if (!process || process == INVALID_HANDLE_VALUE) return {"process_handle_missing"};
    const DWORD pid = GetProcessId(process);
    if (!pid) return win32_failure("process_pid_query", "GetProcessId");
    if (pid != expected_pid) return value_mismatch("process_pid_mismatch", expected_pid, pid);
    FILETIME created{}, exit{}, kernel{}, user{};
    if (!GetProcessTimes(process, &created, &exit, &kernel, &user))
        return win32_failure("process_creation_query", "GetProcessTimes");
    const uint64_t born = uint64_t(created.dwHighDateTime) << 32 | created.dwLowDateTime;
    if (born != expected_birth) return value_mismatch("process_epoch_mismatch", expected_birth, born);
    const DWORD status = WaitForSingleObject(process, 0);
    if (status == WAIT_FAILED) return win32_failure("process_wait_failed", "WaitForSingleObject");
    if (status != WAIT_TIMEOUT) return value_mismatch("process_not_running", WAIT_TIMEOUT, status);
    return {};
}

inline AdmissionCheck check_file_identity(HANDLE observed, HANDLE expected) {
    FILE_ID_INFO x{}, y{};
    if (!GetFileInformationByHandleEx(observed, FileIdInfo, &x, sizeof x))
        return win32_failure("observed_file_id_query", "GetFileInformationByHandleEx");
    if (!GetFileInformationByHandleEx(expected, FileIdInfo, &y, sizeof y))
        return win32_failure("expected_file_id_query", "GetFileInformationByHandleEx");
    if (x.VolumeSerialNumber != y.VolumeSerialNumber) return {"file_volume_mismatch"};
    if (std::memcmp(&x.FileId, &y.FileId, sizeof x.FileId)) return {"file_id_mismatch"};
    return {};
}

// The census uses the iterator's error immediately after the failing call.
// A normal end is distinct from an incomplete enumeration with missing images.
template<class First, class Next, class Inspect>
AdmissionCheck scan_attach_modules(First first, Next next, Inspect inspect) {
    if (!first()) return win32_failure("module_first", "Module32FirstW");
    bool main_seen = false, loader_seen = false;
    do {
        if (auto result = inspect(main_seen, loader_seen); !result) return result;
    } while (next());
    const DWORD error = GetLastError();
    if (error != ERROR_NO_MORE_FILES) return {"module_iteration", "Module32NextW", error};
    if (!loader_seen) return {"ntdll_missing"};
    if (!main_seen) return {"main_image_missing"};
    return {};
}

struct AttachDecision {
    const char* stage = nullptr;
    AdmissionCheck check{};
    bool preflight_passed() const {
        return !stage || std::string_view(stage) == "eligibility" || std::string_view(stage) == "debug_attach";
    }
    explicit operator bool() const { return stage == nullptr; }
};

template<class Eligible, class Attach>
AttachDecision decide_attach(AdmissionCheck preflight, Eligible eligible, Attach attach) {
    if (!preflight) return {"preflight", preflight};
    if (auto result = eligible(); !result) return {"eligibility", result};
    if (!attach()) return {"debug_attach", win32_failure("debug_attach_api", "DebugActiveProcess")};
    return {};
}

inline std::string attach_refusal_fields(const AttachDecision& result) {
    const auto& check = result.check;
    auto quoted = [](const char* value) {
        return value ? std::string("\"") + value + "\"" : std::string("null");
    };
    auto number = [](auto value) { return value ? std::to_string(*value) : "null"; };
    return ",\"diagnostic_schema\":1,\"stage\":" + quoted(result.stage) +
           ",\"predicate\":" + quoted(check.predicate) +
           ",\"operation\":" + quoted(check.operation) +
           ",\"winerror\":" + number(check.winerror) +
           ",\"expected\":" + number(check.expected) +
           ",\"observed\":" + number(check.observed) +
           ",\"detail\":" + quoted(check.detail) +
           ",\"rva\":" + number(check.rva) +
           ",\"preflight\":" + std::to_string(result.preflight_passed()) +
           ",\"attach_attempted\":" +
           std::to_string(result.stage && std::string_view(result.stage) == "debug_attach");
}

// The refusal watermark is independent of target liveness. No debugger
// connection exists, so waiting here holds no target event or thread.
template<class JournalType, class Record>
bool flush_attach_refusal(JournalType& journal, Record record) {
    const auto seq = record();
    if (!seq) return false;
    journal.request_flush();
    while (journal.durable.load() < seq && !journal.failed) Sleep(1);
    return journal.durable.load() >= seq;
}

template<class JournalType, class Record>
bool report_attach_refusal(JournalType& journal, const AttachDecision& result, Record record) {
    const auto fields = attach_refusal_fields(result);
    if (flush_attach_refusal(journal, [&] { return record(fields); })) return true;
    std::fprintf(stderr, "ATTACH_REFUSAL_NOT_DURABLE {\"kind\":\"attach_refused\"%s}\n", fields.c_str());
    std::fflush(stderr);
    return false;
}

} // namespace srr006
