#pragma once

#include <windows.h>
#include <wincrypt.h>
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <span>
#include <string>
#include <string_view>
#include "admission_diagnostics.h"

namespace srr006 {

struct ImageWindow {
    uint32_t rva, size;
    std::string_view sha256;
    bool executable;
};

struct ImageSlot {
    uint32_t rva, target;
};

struct ImageProfile {
    std::string_view image_sha256, profile_sha256;
    uint64_t file_size, preferred_base;
    uint32_t extent;
    std::span<const ImageWindow> windows;
    std::span<const ImageSlot> slots;
};

struct RetailVerification {
    uint64_t base = 0;
    uint32_t extent = 0;
    const char* failure = "unverified";
    uint32_t rva = 0;
    AdmissionCheck diagnostic{};
    explicit operator bool() const { return failure == nullptr; }
};

namespace profile_detail {

class Sha256 {
    HCRYPTPROV provider = 0;
    HCRYPTHASH hash = 0;
    AdmissionCheck* diagnostic;

    bool crypto_failure(const char* operation) const {
        if (diagnostic) *diagnostic = win32_failure("image_hash_api", operation);
        return false;
    }

public:
    explicit Sha256(AdmissionCheck* failure = nullptr) : diagnostic(failure) {
        if (!CryptAcquireContextW(&provider, nullptr, nullptr, PROV_RSA_AES, CRYPT_VERIFYCONTEXT))
            crypto_failure("CryptAcquireContextW");
        else if (!CryptCreateHash(provider, CALG_SHA_256, 0, 0, &hash))
            crypto_failure("CryptCreateHash");
    }
    Sha256(const Sha256&) = delete;
    Sha256& operator=(const Sha256&) = delete;
    ~Sha256() {
        if (hash) CryptDestroyHash(hash);
        if (provider) CryptReleaseContext(provider, 0);
    }
    bool add(const void* data, DWORD size) {
        return hash && (CryptHashData(hash, static_cast<const BYTE*>(data), size, 0) ||
                        crypto_failure("CryptHashData"));
    }
    std::string finish() const {
        std::array<BYTE, 32> bytes{};
        DWORD size = static_cast<DWORD>(bytes.size());
        if (!hash) return {};
        if (!CryptGetHashParam(hash, HP_HASHVAL, bytes.data(), &size, 0)) {
            crypto_failure("CryptGetHashParam");
            return {};
        }
        if (size != bytes.size()) return {};
        constexpr char hex[] = "0123456789abcdef";
        std::string result;
        result.reserve(64);
        for (auto value : bytes) {
            result += hex[value >> 4];
            result += hex[value & 15];
        }
        return result;
    }
    std::string snapshot() const {
        Sha256 copy;
        if (!hash || !copy.hash) return {};
        CryptDestroyHash(copy.hash);
        copy.hash = 0;
        if (!CryptDuplicateHash(hash, nullptr, 0, &copy.hash)) return {};
        return copy.finish();
    }
};

inline uint64_t filetime(FILETIME value) {
    return uint64_t(value.dwHighDateTime) << 32 | value.dwLowDateTime;
}

inline uint64_t process_birth(HANDLE process) {
    FILETIME created{}, exit{}, kernel{}, user{};
    return GetProcessTimes(process, &created, &exit, &kernel, &user) ? filetime(created) : 0;
}

struct FileStamp {
    FILE_ID_INFO id{};
    uint64_t size = 0, modified = 0, changed = 0;

    bool read(HANDLE file) {
        if (!file || file == INVALID_HANDLE_VALUE || GetFileType(file) != FILE_TYPE_DISK) return false;
        FILE_BASIC_INFO basic{};
        FILE_STANDARD_INFO standard{};
        if (!GetFileInformationByHandleEx(file, FileIdInfo, &id, sizeof id) ||
            !GetFileInformationByHandleEx(file, FileBasicInfo, &basic, sizeof basic) ||
            !GetFileInformationByHandleEx(file, FileStandardInfo, &standard, sizeof standard) ||
            standard.Directory || standard.DeletePending || standard.EndOfFile.QuadPart <= 0)
            return false;
        size = static_cast<uint64_t>(standard.EndOfFile.QuadPart);
        modified = static_cast<uint64_t>(basic.LastWriteTime.QuadPart);
        changed = static_cast<uint64_t>(basic.ChangeTime.QuadPart);
        return true;
    }
    bool operator==(const FileStamp& other) const {
        return id.VolumeSerialNumber == other.id.VolumeSerialNumber &&
               std::memcmp(&id.FileId, &other.id.FileId, sizeof id.FileId) == 0 &&
               size == other.size && modified == other.modified && changed == other.changed;
    }
};

inline std::string file_sha256(HANDLE file, uint64_t size) {
    // The creation event owns this synchronous file handle. Hash the handle
    // directly and restore its position rather than reopening a path.
    LARGE_INTEGER zero{}, saved{};
    if (!SetFilePointerEx(file, zero, &saved, FILE_CURRENT) ||
        !SetFilePointerEx(file, zero, nullptr, FILE_BEGIN))
        return {};
    Sha256 sha;
    std::array<BYTE, 65536> block{};
    bool ok = true;
    while (size) {
        const DWORD want = size < block.size() ? static_cast<DWORD>(size) : static_cast<DWORD>(block.size());
        DWORD got = 0;
        if (!ReadFile(file, block.data(), want, &got, nullptr) || got != want ||
            !sha.add(block.data(), got)) {
            ok = false;
            break;
        }
        size -= got;
    }
    const bool restored = SetFilePointerEx(file, saved, nullptr, FILE_BEGIN) != 0;
    return ok && restored ? sha.finish() : std::string{};
}

inline bool executable_page(DWORD protection) {
    switch (protection & 0xff) {
    case PAGE_EXECUTE:
    case PAGE_EXECUTE_READ:
    case PAGE_EXECUTE_READWRITE:
    case PAGE_EXECUTE_WRITECOPY:
        return true;
    default:
        return false;
    }
}

inline bool read_image(HANDLE process, uint64_t base, uint64_t address, void* out,
                       size_t size, bool executable, AdmissionCheck* failure = nullptr) {
    auto refuse = [&](AdmissionCheck reason) {
        if (failure) *failure = reason;
        return false;
    };
    if (!size || address < base || size > UINT64_MAX - address) return refuse({"image_read_range"});
    for (uint64_t cursor = address, end = address + size; cursor < end;) {
        MEMORY_BASIC_INFORMATION region{};
        if (!VirtualQueryEx(process, reinterpret_cast<const void*>(cursor), &region, sizeof region))
            return refuse(win32_failure("image_region_query", "VirtualQueryEx"));
        if (region.Type != MEM_IMAGE) return refuse(value_mismatch("image_region_type", MEM_IMAGE, region.Type));
        if (region.State != MEM_COMMIT) return refuse(value_mismatch("image_region_state", MEM_COMMIT, region.State));
        if (reinterpret_cast<uint64_t>(region.AllocationBase) != base)
            return refuse({"image_allocation_base"});
        if (region.Protect & (PAGE_GUARD | PAGE_NOACCESS))
            return refuse(value_mismatch("image_region_guard_or_noaccess", 0,
                                         region.Protect & (PAGE_GUARD | PAGE_NOACCESS)));
        if (executable && !executable_page(region.Protect))
            return refuse({"image_region_not_executable", nullptr, {}, {}, region.Protect});
        const auto start = reinterpret_cast<uint64_t>(region.BaseAddress);
        if (start > cursor || region.RegionSize > UINT64_MAX - start ||
            start + region.RegionSize <= cursor)
            return refuse({"image_region_bounds"});
        cursor = start + region.RegionSize;
    }
    SIZE_T got = 0;
    if (!ReadProcessMemory(process, reinterpret_cast<const void*>(address), out, size, &got))
        return refuse(win32_failure("image_memory_read", "ReadProcessMemory"));
    if (got != size) return refuse(value_mismatch("image_memory_short_read", size, got));
    return true;
}

inline bool range(uint32_t rva, uint32_t size, uint32_t extent) {
    return size && rva < extent && size <= extent - rva;
}

} // namespace profile_detail

inline std::string sha256_memory(const void* data, size_t size, AdmissionCheck* failure = nullptr) {
    profile_detail::Sha256 sha(failure);
    return size <= MAXDWORD && sha.add(data, static_cast<DWORD>(size)) ? sha.finish() : std::string{};
}

inline std::string sha256_image_headers(const void* data, size_t size, uint64_t preferred_base,
                                        AdmissionCheck* failure = nullptr) {
    IMAGE_DOS_HEADER dos{};
    if (size < sizeof dos || size > MAXDWORD) return {};
    const auto* bytes = static_cast<const BYTE*>(data);
    std::memcpy(&dos, bytes, sizeof dos);
    if (dos.e_magic != IMAGE_DOS_SIGNATURE || dos.e_lfanew < sizeof dos ||
        static_cast<size_t>(dos.e_lfanew) > size ||
        sizeof(IMAGE_NT_HEADERS64) > size - static_cast<size_t>(dos.e_lfanew))
        return {};
    constexpr auto in_nt = offsetof(IMAGE_NT_HEADERS64, OptionalHeader) +
                           offsetof(IMAGE_OPTIONAL_HEADER64, ImageBase);
    const auto field = static_cast<DWORD>(dos.e_lfanew + in_nt);
    const auto remaining = static_cast<DWORD>(size - field - sizeof preferred_base);
    // Windows may rewrite this field when constructing an ASLR image
    // mapping. Hash the preferred value from the authenticated profile.
    profile_detail::Sha256 sha(failure);
    return sha.add(bytes, field) && sha.add(&preferred_base, sizeof preferred_base) &&
           sha.add(bytes + field + sizeof preferred_base, remaining) ? sha.finish() : std::string{};
}

// Caller supplies a trusted, immutable profile. Retail always selects the
// compiled profile below. Reader tests can model a separately pinned fixture.
template<class Reader>
RetailVerification verify_profile_windows(const ImageProfile& profile, uint64_t base, Reader read) {
    RetailVerification result{base, profile.extent};
    auto fail = [&](const char* reason, AdmissionCheck diagnostic = {}) {
        result.failure = reason;
        result.diagnostic = diagnostic;
        return result;
    };
    if (!base) return fail("image_extent_or_profile", {"image_base_missing"});
    if (base & 0xffff) return fail("image_extent_or_profile", {"image_base_alignment"});
    if (profile.extent > UINT64_MAX - base) return fail("image_extent_or_profile", {"image_extent_overflow"});
    if (!profile.extent) return fail("image_extent_or_profile", {"profile_extent_missing"});
    if (profile.windows.empty()) return fail("image_extent_or_profile", {"profile_windows_missing"});
    if (profile.slots.empty()) return fail("image_extent_or_profile", {"profile_slots_missing"});
    IMAGE_DOS_HEADER dos{};
    if (!read(base, &dos, sizeof dos, false)) return fail("mapped_dos_header");
    if (dos.e_magic != IMAGE_DOS_SIGNATURE)
        return fail("mapped_dos_header", value_mismatch("mapped_dos_signature", IMAGE_DOS_SIGNATURE, dos.e_magic));
    if (dos.e_lfanew < sizeof dos)
        return fail("mapped_dos_header", {"mapped_pe_offset_before_header"});
    if (!profile_detail::range(static_cast<uint32_t>(dos.e_lfanew), sizeof(IMAGE_NT_HEADERS64), profile.extent))
        return fail("mapped_dos_header", {"mapped_pe_offset_outside_image"});
    result.rva = static_cast<uint32_t>(dos.e_lfanew);
    IMAGE_NT_HEADERS64 pe{};
    if (!read(base + result.rva, &pe, sizeof pe, false)) return fail("mapped_pe_header");
    auto pe_field = [&](const char* field, uint64_t expected, uint64_t observed) {
        return fail("mapped_pe_header", value_mismatch(field, expected, observed));
    };
    if (pe.Signature != IMAGE_NT_SIGNATURE)
        return pe_field("mapped_pe_signature", IMAGE_NT_SIGNATURE, pe.Signature);
    if (pe.FileHeader.Machine != IMAGE_FILE_MACHINE_AMD64)
        return pe_field("mapped_pe_machine", IMAGE_FILE_MACHINE_AMD64, pe.FileHeader.Machine);
    if (pe.FileHeader.SizeOfOptionalHeader != sizeof(IMAGE_OPTIONAL_HEADER64))
        return pe_field("mapped_pe_optional_header_size", sizeof(IMAGE_OPTIONAL_HEADER64),
                        pe.FileHeader.SizeOfOptionalHeader);
    if (pe.OptionalHeader.Magic != IMAGE_NT_OPTIONAL_HDR64_MAGIC)
        return pe_field("mapped_pe_optional_magic", IMAGE_NT_OPTIONAL_HDR64_MAGIC, pe.OptionalHeader.Magic);
    if (pe.OptionalHeader.SizeOfImage != profile.extent)
        return pe_field("mapped_pe_image_size", profile.extent, pe.OptionalHeader.SizeOfImage);
    if (pe.OptionalHeader.ImageBase != profile.preferred_base && pe.OptionalHeader.ImageBase != base)
        return fail("mapped_pe_header", {"mapped_pe_image_base"});
    if (base != profile.preferred_base &&
        !(pe.OptionalHeader.DllCharacteristics & IMAGE_DLLCHARACTERISTICS_DYNAMIC_BASE))
        return fail("mapped_pe_header", {"mapped_pe_rebase_not_allowed"});
    std::array<BYTE, 4096> bytes{};
    bool verified_headers = false;
    for (const auto& window : profile.windows) {
        result.rva = window.rva;
        if (!profile_detail::range(window.rva, window.size, profile.extent))
            return fail("invalid_window_profile", {"profile_window_range"});
        if (window.size > bytes.size()) return fail("invalid_window_profile", {"profile_window_size"});
        if (window.sha256.size() != 64) return fail("invalid_window_profile", {"profile_window_digest_length"});
        if (!read(base + window.rva, bytes.data(), window.size, window.executable))
            return fail("mapped_window_unreadable");
        if (window.rva == 0) {
            IMAGE_DOS_HEADER current{};
            std::memcpy(&current, bytes.data(), sizeof current);
            if (window.size != pe.OptionalHeader.SizeOfHeaders)
                return fail("mapped_header_mismatch", value_mismatch("mapped_header_size", window.size,
                            pe.OptionalHeader.SizeOfHeaders));
            if (current.e_lfanew != dos.e_lfanew)
                return fail("mapped_header_mismatch", {"mapped_header_pe_offset_changed"});
            if (static_cast<size_t>(dos.e_lfanew) > window.size ||
                sizeof pe > window.size - static_cast<size_t>(dos.e_lfanew))
                return fail("mapped_header_mismatch", {"mapped_header_pe_outside_window"});
            if (std::memcmp(bytes.data() + dos.e_lfanew, &pe, sizeof pe) != 0)
                return fail("mapped_header_mismatch", {"mapped_header_pe_changed"});
            verified_headers = true;
        }
        AdmissionCheck hash_failure;
        const auto digest = window.rva == 0 ?
            sha256_image_headers(bytes.data(), window.size, profile.preferred_base, &hash_failure) :
            sha256_memory(bytes.data(), window.size, &hash_failure);
        if (digest != window.sha256) {
            if (digest.empty() && hash_failure) hash_failure.predicate = "mapped_window_hash_unavailable";
            return fail("mapped_window_digest", hash_failure);
        }
    }
    if (!verified_headers) return fail("mapped_headers_not_pinned");
    for (const auto& slot : profile.slots) {
        result.rva = slot.rva;
        uint64_t moved = 0;
        if (!profile_detail::range(slot.rva, sizeof moved, profile.extent))
            return fail("mapped_dir64_slot", {"profile_slot_range"});
        if (!profile_detail::range(slot.target, 1, profile.extent))
            return fail("mapped_dir64_slot", {"profile_slot_target_range"});
        if (!read(base + slot.rva, &moved, sizeof moved, false))
            return fail("mapped_dir64_slot");
        if (moved != base + slot.target) {
            AdmissionCheck mismatch{"mapped_dir64_target"};
            mismatch.expected = slot.target;
            if (moved >= base && moved - base < profile.extent) mismatch.observed = moved - base;
            else mismatch.predicate = "mapped_dir64_target_outside_image";
            return fail("mapped_dir64_slot", mismatch);
        }
    }
    result.failure = nullptr;
    return result;
}

inline RetailVerification verify_loaded_mapping(HANDLE process, uint64_t base,
                                                 const ImageProfile& profile) {
    AdmissionCheck read_failure;
    auto result = verify_profile_windows(profile, base, [&](uint64_t address, void* out,
                                                           size_t size, bool executable) {
        return profile_detail::read_image(process, base, address, out, size, executable, &read_failure);
    });
    if (!read_failure) result.diagnostic = read_failure;
    return result;
}

inline RetailVerification verify_stopped_mapping(HANDLE process, HANDLE pinned_file,
                                                  const CREATE_PROCESS_DEBUG_INFO& event,
                                                  DWORD expected_pid, uint64_t expected_birth,
                                                  const ImageProfile& profile) {
    const auto base = reinterpret_cast<uint64_t>(event.lpBaseOfImage);
    RetailVerification result{base, profile.extent};
    result.failure = "creation_process_identity";
    if (!expected_pid || !expected_birth || GetProcessId(process) != expected_pid ||
        GetProcessId(event.hProcess) != expected_pid ||
        profile_detail::process_birth(process) != expected_birth ||
        profile_detail::process_birth(event.hProcess) != expected_birth)
        return result;
    profile_detail::FileStamp pin{}, before{}, after{}, pin_after{};
    result.failure = "creation_image_file_identity";
    if (!pin.read(pinned_file) || !before.read(event.hFile) || !(pin == before) ||
        before.size != profile.file_size)
        return result;
    result.failure = "creation_image_file_digest";
    if (profile.image_sha256.size() != 64 ||
        profile_detail::file_sha256(event.hFile, before.size) != profile.image_sha256)
        return result;
    result.failure = "creation_image_file_changed";
    if (!after.read(event.hFile) || !pin_after.read(pinned_file) ||
        !(after == before) || !(pin_after == pin))
        return result;
    return verify_loaded_mapping(process, base, profile);
}

} // namespace srr006

#include "retail_manifest.h"

namespace srr006 {

inline constexpr auto retail_profile_sha256 = retail_image_profile.profile_sha256;

inline RetailVerification verify_retail_mapping(HANDLE process, HANDLE pinned_file,
                                                 const CREATE_PROCESS_DEBUG_INFO& event,
                                                 DWORD expected_pid, uint64_t expected_birth) {
    return verify_stopped_mapping(process, pinned_file, event, expected_pid, expected_birth,
                                  retail_image_profile);
}

} // namespace srr006
