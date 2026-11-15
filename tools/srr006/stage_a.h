#pragma once

#include <algorithm>
#include <charconv>
#include <filesystem>
#include <memory>
#include <optional>
#include <tlhelp32.h>
#include <utility>
#include <vector>
#include "retail_profile.h"

namespace srr006 {

inline constexpr wchar_t retail_exe[] = LR"(C:\Program Files (x86)\Steam\steamapps\common\Starfield\Starfield.exe)";
inline constexpr wchar_t steam_exe[] = LR"(C:\Program Files (x86)\Steam\steam.exe)";
inline constexpr wchar_t steam_log[] = LR"(C:\Program Files (x86)\Steam\logs\gameprocess_log.txt)";
inline constexpr wchar_t overlay_exe[] = LR"(C:\Program Files (x86)\Steam\gameoverlayrenderer64.dll)";
inline constexpr std::string_view ntdll_sha256 =
    "36b1a62e4bf6bf7d68458fff6e8a33b39f6527ec6a46e55ecdd12cde83894c8d";
// SRR-008 survey identities. Steam updates its own components independently:
// these pins are recorded evidence for drift reporting, never a silent
// substitution of one identity for another, and never an admission condition
// on their own. A credible-origin component whose hash differs is drifting.
inline constexpr std::string_view overlay_sha256_srr008 =
    "688cc70e58cd8d1f31345fdf93ba1b9ab08c77c38df847bd2b0ae2145a437a2f";
inline constexpr std::string_view steam_exe_sha256_srr008 =
    "1e17d08cc3aaf4e0bec9584db41348305c9c9fd73b0318543fb15f4c71d4d699";
inline constexpr std::string_view steam_api64_sha256_srr008 =
    "1db3fd414039d3e5815a5721925dd2e0a3a9f2549603c6cab7c49b84966a1af3";
inline constexpr uint32_t attach_break_rva = 0xa10d0;
inline constexpr uint32_t breakin_start_rva = 0xccaf0;
inline constexpr uint32_t breakin_return_rva = 0xccb3e;
inline constexpr ImageWindow attach_windows[]{
    {attach_break_rva, 16, "0229672a9098b885e0a272fdcfdfa0d415a101e034d17977128f621511bf9f8f", true},
    {breakin_start_rva, breakin_return_rva - breakin_start_rva,
     "b97171a50db725107c0071a6eeb04d340fdaa0b89bcf4a550543c40b332db466", true}
};

struct CloseStageHandle {
    void operator()(void* handle) const { if (handle && handle != INVALID_HANDLE_VALUE) CloseHandle(handle); }
};
using StageHandle = std::unique_ptr<void, CloseStageHandle>;

inline StageHandle read_file(const wchar_t* path, DWORD share = FILE_SHARE_READ) {
    HANDLE handle = CreateFileW(path, GENERIC_READ, share, nullptr, OPEN_EXISTING, 0, nullptr);
    return StageHandle(handle == INVALID_HANDLE_VALUE ? nullptr : handle);
}

inline std::wstring disk_path(HANDLE file, DWORD volume = VOLUME_NAME_DOS,
                              AdmissionCheck* failure = nullptr) {
    wchar_t path[32768]{};
    const auto length = GetFinalPathNameByHandleW(file, path, ARRAYSIZE(path), volume);
    if (failure && !length) *failure = win32_failure("backing_path_query", "GetFinalPathNameByHandleW");
    if (failure && length >= ARRAYSIZE(path))
        *failure = value_mismatch("backing_path_too_long", ARRAYSIZE(path) - 1, length);
    return length && length < ARRAYSIZE(path) ? std::wstring(path, length) : std::wstring{};
}

inline std::wstring process_path(HANDLE process) {
    wchar_t path[32768]{};
    DWORD length = ARRAYSIZE(path);
    return QueryFullProcessImageNameW(process, 0, path, &length) ? std::wstring(path, length) : std::wstring{};
}

inline AdmissionCheck check_backing_path(HANDLE image, std::wstring_view path) {
    AdmissionCheck failure;
    const auto final = disk_path(image, VOLUME_NAME_DOS, &failure);
    if (!failure) return failure;
    if (final.empty()) return {"backing_path_empty"};
    if (_wcsicmp(final.c_str(), (L"\\\\?\\" + std::wstring(path)).c_str()))
        return {"backing_path_mismatch"};
    return {};
}

inline bool matches_path(HANDLE image, std::wstring_view path) {
    return bool(check_backing_path(image, path));
}

inline bool pinned_file(HANDLE file, std::string_view digest, uint64_t size = 0) {
    profile_detail::FileStamp before{}, after{};
    return before.read(file) && (!size || before.size == size) &&
           profile_detail::file_sha256(file, before.size) == digest &&
           after.read(file) && before == after;
}

inline bool same_epoch(HANDLE process, DWORD pid, uint64_t birth) {
    return pid && birth && GetProcessId(process) == pid &&
           profile_detail::process_birth(process) == birth &&
           WaitForSingleObject(process, 0) == WAIT_TIMEOUT;
}

inline AdmissionCheck check_attach_code(HANDLE process, uint64_t base) {
    if (!base || base > UINT64_MAX - breakin_return_rva) return {"ntdll_mapping_base"};
    std::array<BYTE, 128> bytes{};
    for (const auto& window : attach_windows) {
        AdmissionCheck result;
        if (profile_detail::read_image(process, base, base + window.rva, bytes.data(),
                                       window.size, true, &result)) {
            const auto digest = sha256_memory(bytes.data(), window.size, &result);
            if (digest == window.sha256) continue;
            if (result)
                result.predicate = digest.empty() ? "ntdll_window_hash_unavailable" : "ntdll_window_digest";
        }
        result.rva = window.rva;
        return result;
    }
    return {};
}

inline bool attach_code(HANDLE process, uint64_t base) {
    return bool(check_attach_code(process, base));
}

enum class ModuleRisk { expected, incidental, drifting, unknown, incompatible };

// Comparison state of a Steam component against its recorded SRR-008 identity.
// unmatched means no credible origin/backing existed to compare at all.
enum class PinState { unmatched, pinned, drifted };

inline ModuleRisk stage_module(std::wstring_view basename, bool system, bool steam_origin,
                               PinState overlay, PinState steam_api, bool is_loader, bool mapped) {
    const std::wstring name(basename);
    if (!mapped || name.starts_with(L"sfse") || name == L"starfield.exe" ||
        (name == L"ntdll.dll" && !is_loader)) return ModuleRisk::incompatible;
    if (name == L"gameoverlayrenderer64.dll") {
        if (overlay == PinState::pinned) return ModuleRisk::expected;
        // A credible-origin overlay whose file identity is verified but whose
        // bytes differ from the SRR-008 survey: Steam updated its component.
        if (overlay == PinState::drifted) return ModuleRisk::drifting;
        // Unverifiable origin or backing: treat as a lookalike.
        return ModuleRisk::incompatible;
    }
    if (is_loader) return ModuleRisk::expected;
    if (name == L"steam_api64.dll")
        return !steam_origin ? ModuleRisk::unknown :
               steam_api == PinState::drifted ? ModuleRisk::drifting : ModuleRisk::expected;
    if (steam_origin && (name == L"steamclient64.dll" || name == L"tier0_s64.dll" ||
        name == L"vstdlib_s64.dll")) return ModuleRisk::expected;
    if (system) return ModuleRisk::incidental;
    return ModuleRisk::unknown;
}

// File version strings for evidence rows. Loaded dynamically so the observer
// keeps its import surface unchanged; failures yield empty strings.
inline std::pair<std::wstring, std::wstring> file_version_strings(const std::wstring& path) {
    struct VersionDll {
        HMODULE module = GetModuleHandleW(L"version.dll");
        VersionDll() { if (!module) module = LoadLibraryW(L"version.dll"); }
        ~VersionDll() { /* keep resident: avoid unload races in evidence paths */ }
    };
    static VersionDll library;
    if (!library.module) return {};
    const auto size = reinterpret_cast<decltype(&GetFileVersionInfoSizeExW)>(
        reinterpret_cast<void*>(GetProcAddress(library.module, "GetFileVersionInfoSizeExW")));
    const auto info = reinterpret_cast<decltype(&GetFileVersionInfoExW)>(
        reinterpret_cast<void*>(GetProcAddress(library.module, "GetFileVersionInfoExW")));
    const auto value = reinterpret_cast<decltype(&VerQueryValueW)>(
        reinterpret_cast<void*>(GetProcAddress(library.module, "VerQueryValueW")));
    if (!size || !info || !value) return {};
    DWORD handle = 0;
    const DWORD bytes = size(FILE_VER_GET_NEUTRAL, path.c_str(), &handle);
    if (!bytes) return {};
    std::vector<BYTE> buffer(bytes);
    if (!info(FILE_VER_GET_NEUTRAL, path.c_str(), 0, bytes, buffer.data())) return {};
    struct LANGANDCODEPAGE { WORD language, codepage; } const* translation = nullptr;
    UINT length = 0;
    if (!value(buffer.data(), L"\\VarFileInfo\\Translation",
               reinterpret_cast<void**>(const_cast<LANGANDCODEPAGE**>(&translation)), &length) ||
        length < sizeof *translation) return {};
    wchar_t prefix[64]{};
    swprintf_s(prefix, L"\\StringFileInfo\\%04x%04x\\",
               translation[0].language, translation[0].codepage);
    const auto read = [&](const wchar_t* field) {
        const void* text = nullptr;
        return value(buffer.data(), (std::wstring(prefix) + field).c_str(),
                     const_cast<void**>(&text), &length) && text ?
               std::wstring(static_cast<const wchar_t*>(text)) : std::wstring{};
    };
    return {read(L"FileVersion"), read(L"ProductVersion")};
}

// Match one new tracking line for this app/PID and the complete image path.
inline unsigned steam_matches(std::string_view delta, DWORD pid, std::string_view path,
                              size_t* match_offset = nullptr) {
    const auto target = "AppID 1716740 adding PID " + std::to_string(pid) +
                        " as a tracked process \"\"" + std::string(path) + "\"\"";
    unsigned count = 0;
    for (size_t begin = 0, end; (end = delta.find('\n', begin)) != delta.npos; begin = end + 1) {
        auto line = delta.substr(begin, end - begin);
        if (line.ends_with('\r')) line.remove_suffix(1);
        const auto timestamp_end = line.find("] ");
        if (line.starts_with('[') && timestamp_end != line.npos &&
            line.size() - timestamp_end - 2 == target.size() &&
            line.find('\0') == delta.npos &&
            _strnicmp(line.data() + timestamp_end + 2, target.c_str(), target.size()) == 0) {
            if (match_offset) *match_offset = begin;
            ++count;
        }
    }
    return count;
}

class SteamAttribution {
    profile_detail::FileStamp baseline{};
    std::string tail_digest;

    static StageHandle open() {
        return read_file(steam_log, FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE);
    }
    static std::optional<std::string> bytes(HANDLE file, uint64_t offset, DWORD length) {
        LARGE_INTEGER at{};
        at.QuadPart = offset;
        std::string value(length, '\0');
        DWORD got = 0;
        if (!SetFilePointerEx(file, at, nullptr, FILE_BEGIN) ||
            !ReadFile(file, value.data(), length, &got, nullptr) || got != length) return {};
        return value;
    }
    static auto tail(HANDLE file, uint64_t length) {
        const DWORD size = static_cast<DWORD>((std::min)(uint64_t{4096}, length));
        return bytes(file, length - size, size);
    }

public:
    bool start() {
        const auto log = open();
        if (!baseline.read(log.get())) return false;
        const auto value = tail(log.get(), baseline.size);
        if (!value || !value->ends_with('\n')) return false;
        tail_digest = sha256_memory(value->data(), value->size());
        return !tail_digest.empty();
    }
    uint64_t baseline_bytes() const { return baseline.size; }
    std::string_view baseline_tail_sha256() const { return tail_digest; }
    struct Result {
        unsigned matches = 0;
        std::string digest, evidence;
        uint64_t offset = 0;
    };
    Result check(DWORD pid) const {
        const auto log = open();
        profile_detail::FileStamp now{};
        if (!now.read(log.get()) || now.id.VolumeSerialNumber != baseline.id.VolumeSerialNumber ||
            std::memcmp(&now.id.FileId, &baseline.id.FileId, sizeof now.id.FileId) ||
            now.size < baseline.size || now.size - baseline.size > 1024 * 1024) return {};
        const auto old = tail(log.get(), baseline.size);
        if (!old || sha256_memory(old->data(), old->size()) != tail_digest) return {};
        const auto delta = bytes(log.get(), baseline.size, static_cast<DWORD>(now.size - baseline.size));
        if (!delta) return {};
        constexpr std::string_view target = R"(C:\Program Files (x86)\Steam\steamapps\common\Starfield\Starfield.exe)";
        size_t offset = 0;
        const auto matches = steam_matches(*delta, pid, target, &offset);
        const auto end = delta->find('\n', offset);
        return {matches, sha256_memory(delta->data(), delta->size()),
                matches == 1 ? delta->substr(offset, end - offset + 1) : std::string{},
                baseline.size + offset};
    }
};

struct StageProcess {
    DWORD pid = 0, parent = 0;
};

inline bool stage_processes(DWORD session, std::vector<StageProcess>& steam,
                            std::vector<StageProcess>& targets) {
    const StageHandle snapshot(CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0));
    PROCESSENTRY32W row{};
    row.dwSize = sizeof row;
    if (snapshot.get() == INVALID_HANDLE_VALUE || !Process32FirstW(snapshot.get(), &row)) return false;
    do {
        if (_wcsicmp(row.szExeFile, L"Starfield.exe") == 0)
            targets.push_back({row.th32ProcessID, row.th32ParentProcessID});
        if (_wcsicmp(row.szExeFile, L"steam.exe") != 0) continue;
        DWORD actual = 0;
        if (!ProcessIdToSessionId(row.th32ProcessID, &actual)) return false;
        if (actual == session) steam.push_back({row.th32ProcessID, row.th32ParentProcessID});
    } while (Process32NextW(snapshot.get(), &row));
    return GetLastError() == ERROR_NO_MORE_FILES;
}

inline AdmissionCheck check_interactive_user(HANDLE process, DWORD pid, DWORD session) {
    DWORD actual = 0;
    if (!session) return {"interactive_session_unset"};
    if (!ProcessIdToSessionId(pid, &actual))
        return win32_failure("interactive_session_query", "ProcessIdToSessionId");
    if (actual != session) return value_mismatch("interactive_session_mismatch", session, actual);
    HANDLE own = nullptr, theirs = nullptr;
    if (!OpenProcessToken(GetCurrentProcess(), TOKEN_QUERY, &own))
        return win32_failure("caller_token_open", "OpenProcessToken");
    const StageHandle ours(own);
    if (!OpenProcessToken(process, TOKEN_QUERY, &theirs))
        return win32_failure("target_token_open", "OpenProcessToken");
    const StageHandle token(theirs);
    alignas(TOKEN_USER) BYTE a[512]{}, b[512]{};
    DWORD size = 0;
    TOKEN_ELEVATION elevation{};
    if (!GetTokenInformation(own, TokenElevation, &elevation, sizeof elevation, &size))
        return win32_failure("caller_elevation_query", "GetTokenInformation");
    if (elevation.TokenIsElevated) return {"caller_token_elevated"};
    if (!GetTokenInformation(theirs, TokenElevation, &elevation, sizeof elevation, &size))
        return win32_failure("target_elevation_query", "GetTokenInformation");
    if (elevation.TokenIsElevated) return {"target_token_elevated"};
    if (!GetTokenInformation(own, TokenUser, a, sizeof a, &size))
        return win32_failure("caller_identity_query", "GetTokenInformation");
    if (!GetTokenInformation(theirs, TokenUser, b, sizeof b, &size))
        return win32_failure("target_identity_query", "GetTokenInformation");
    if (!EqualSid(reinterpret_cast<TOKEN_USER*>(a)->User.Sid,
                  reinterpret_cast<TOKEN_USER*>(b)->User.Sid)) return {"interactive_account_mismatch"};
    return {};
}

inline bool same_interactive_user(HANDLE process, DWORD pid, DWORD session) {
    return bool(check_interactive_user(process, pid, session));
}

} // namespace srr006
