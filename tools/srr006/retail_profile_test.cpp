#define NOMINMAX
#include "retail_profile.h"
#include <cassert>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <vector>

using namespace srr006;

static int marker(int n) { return n + 6006; }
using Marker = int(*)(int);
static Marker volatile moved_slot = marker;

// Read the authenticated disk image as data, then present the exact bytes
// expected in a rebased image. This tests predicates and arithmetic only.
static void test_retail_bytes(const std::filesystem::path& path) {
    std::ifstream stream(path, std::ios::binary);
    std::vector<char> bytes(static_cast<size_t>(retail_image_profile.file_size));
    assert(stream.read(bytes.data(), bytes.size()) && stream.peek() == EOF);
    assert(sha256_memory(bytes.data(), bytes.size()) == retail_image_profile.image_sha256);
    IMAGE_DOS_HEADER dos{};
    std::memcpy(&dos, bytes.data(), sizeof dos);
    IMAGE_NT_HEADERS64 pe{};
    std::memcpy(&pe, bytes.data() + dos.e_lfanew, sizeof pe);
    std::vector<IMAGE_SECTION_HEADER> sections(pe.FileHeader.NumberOfSections);
    std::memcpy(sections.data(), bytes.data() + dos.e_lfanew + sizeof pe,
                sections.size() * sizeof sections.front());
    auto read_disk = [&](uint64_t rva, void* dst, size_t size) {
        if (rva < pe.OptionalHeader.SizeOfHeaders && size <= pe.OptionalHeader.SizeOfHeaders - rva) {
            std::memcpy(dst, bytes.data() + rva, size);
            return true;
        }
        for (const auto& section : sections) {
            if (rva >= section.VirtualAddress) {
                const auto delta = rva - section.VirtualAddress;
                if (delta < section.SizeOfRawData && size <= section.SizeOfRawData - delta) {
                    std::memcpy(dst, bytes.data() + section.PointerToRawData + delta, size);
                    return true;
                }
            }
        }
        return false;
    };
    for (const uint64_t base : {retail_image_profile.preferred_base, uint64_t{0x7ff700000000}}) {
        auto read_relocated = [&](uint64_t address, void* dst, size_t size, bool) {
            assert(address >= base);
            const auto rva = address - base;
            for (const auto& slot : retail_slots) {
                if (rva == slot.rva) {
                    assert(size == sizeof(uint64_t));
                    const uint64_t moved = base + slot.target;
                    std::memcpy(dst, &moved, size);
                    return true;
                }
            }
            return read_disk(rva, dst, size);
        };
        assert(verify_profile_windows(retail_image_profile, base, read_relocated));
        auto os_header = [&](uint64_t address, void* dst, size_t size, bool executable) {
            if (!read_relocated(address, dst, size, executable)) return false;
            if (address == base + dos.e_lfanew)
                static_cast<IMAGE_NT_HEADERS64*>(dst)->OptionalHeader.ImageBase = base;
            if (address == base && size == pe.OptionalHeader.SizeOfHeaders) {
                auto* header = static_cast<char*>(dst) + dos.e_lfanew;
                std::memcpy(header + offsetof(IMAGE_NT_HEADERS64, OptionalHeader) +
                            offsetof(IMAGE_OPTIONAL_HEADER64, ImageBase), &base, sizeof base);
            }
            return true;
        };
        assert(verify_profile_windows(retail_image_profile, base, os_header));
        auto changed_code = [&](uint64_t address, void* dst, size_t size, bool executable) {
            if (!read_relocated(address, dst, size, executable)) return false;
            if (address == base + retail_windows[0].rva) static_cast<char*>(dst)[0] ^= 1;
            return true;
        };
        auto unreadable_code = [&](uint64_t address, void* dst, size_t size, bool executable) {
            return !executable && read_relocated(address, dst, size, executable);
        };
        auto wrong_header = [&](uint64_t address, void* dst, size_t size, bool executable) {
            if (!read_relocated(address, dst, size, executable)) return false;
            if (address == base + dos.e_lfanew)
                static_cast<IMAGE_NT_HEADERS64*>(dst)->OptionalHeader.SizeOfImage += 4096;
            return true;
        };
        auto inconsistent_header = [&](uint64_t address, void* dst, size_t size, bool executable) {
            if (!read_relocated(address, dst, size, executable)) return false;
            if (address == base && size == pe.OptionalHeader.SizeOfHeaders) {
                auto* header = static_cast<char*>(dst) + dos.e_lfanew;
                const uint64_t wrong = base + 0x10000;
                std::memcpy(header + offsetof(IMAGE_NT_HEADERS64, OptionalHeader) +
                            offsetof(IMAGE_OPTIONAL_HEADER64, ImageBase), &wrong, sizeof wrong);
            }
            return true;
        };
        assert(std::string_view(verify_profile_windows(retail_image_profile, base, changed_code).failure)
               == "mapped_window_digest");
        assert(std::string_view(verify_profile_windows(retail_image_profile, base, unreadable_code).failure)
               == "mapped_window_unreadable");
        assert(std::string_view(verify_profile_windows(retail_image_profile, base, wrong_header).failure)
               == "mapped_pe_header");
        assert(std::string_view(verify_profile_windows(retail_image_profile, base, inconsistent_header).failure)
               == "mapped_header_mismatch");
        if (base != retail_image_profile.preferred_base) {
            auto no_relocation = [&](uint64_t address, void* dst, size_t size, bool) {
                return read_disk(address - base, dst, size);
            };
            assert(std::string_view(verify_profile_windows(retail_image_profile, base, no_relocation).failure)
                   == "mapped_dir64_slot");
        }
    }
}

static void test_disposable_creation(const wchar_t* self, const wchar_t* other_file) {
    auto open = [](const wchar_t* path) {
        HANDLE file = CreateFileW(path, GENERIC_READ, FILE_SHARE_READ, nullptr, OPEN_EXISTING, 0, nullptr);
        assert(file != INVALID_HANDLE_VALUE);
        return file;
    };
    HANDLE image = open(self), wrong_image = open(other_file);
    profile_detail::FileStamp stamp{};
    assert(stamp.read(image));
    const auto digest = profile_detail::file_sha256(image, stamp.size);
    const auto local = reinterpret_cast<uint64_t>(GetModuleHandleW(nullptr));
    const auto dos = reinterpret_cast<const IMAGE_DOS_HEADER*>(local);
    const auto pe = reinterpret_cast<const IMAGE_NT_HEADERS64*>(local + dos->e_lfanew);
    const auto header_size = pe->OptionalHeader.SizeOfHeaders;
    std::ifstream disk(self, std::ios::binary);
    std::vector<char> disk_headers(header_size);
    assert(disk.read(disk_headers.data(), disk_headers.size()));
    IMAGE_NT_HEADERS64 disk_pe{};
    std::memcpy(&disk_pe, disk_headers.data() + dos->e_lfanew, sizeof disk_pe);
    const auto header_hash = sha256_memory(disk_headers.data(), disk_headers.size());
    const auto entry = reinterpret_cast<uint64_t>(marker);
    constexpr unsigned code_size = 8;
    const auto code_hash = sha256_memory(reinterpret_cast<const void*>(entry), code_size);
    const ImageWindow windows[]{
        {0, header_size, header_hash, false},
        {static_cast<uint32_t>(entry - local), code_size, code_hash, true},
    };
    const ImageSlot slots[]{
        {static_cast<uint32_t>(reinterpret_cast<uint64_t>(&moved_slot) - local),
         static_cast<uint32_t>(entry - local)},
    };
    const ImageProfile profile{digest, digest, stamp.size, disk_pe.OptionalHeader.ImageBase,
                              pe->OptionalHeader.SizeOfImage, windows, slots};
    STARTUPINFOW startup{};
    startup.cb = sizeof startup;
    PROCESS_INFORMATION child{};
    std::wstring command = L"\"" + std::wstring(self) + L"\" --profile-fixture-child";
    assert(CreateProcessW(self, command.data(), nullptr, nullptr, FALSE,
                          DEBUG_ONLY_THIS_PROCESS | CREATE_NO_WINDOW, nullptr, nullptr,
                          &startup, &child));
    CloseHandle(child.hThread);
    const auto born = profile_detail::process_birth(child.hProcess);
    DEBUG_EVENT event{};
    assert(WaitForDebugEvent(&event, INFINITE) && event.dwDebugEventCode == CREATE_PROCESS_DEBUG_EVENT);
    const auto& create = event.u.CreateProcessInfo;
    const auto valid = verify_stopped_mapping(child.hProcess, image, create, child.dwProcessId, born, profile);
    if (!valid) std::cerr << "disposable verification failed: " << valid.failure << '\n';
    assert(valid && valid.base == reinterpret_cast<uint64_t>(create.lpBaseOfImage));
    ImageProfile bad_digest = profile;
    bad_digest.image_sha256 = retail_image_profile.image_sha256;
    assert(std::string_view(verify_stopped_mapping(child.hProcess, image, create, child.dwProcessId,
                                                  born, bad_digest).failure) == "creation_image_file_digest");
    assert(std::string_view(verify_stopped_mapping(child.hProcess, wrong_image, create, child.dwProcessId,
                                                  born, profile).failure) == "creation_image_file_identity");
    assert(std::string_view(verify_stopped_mapping(child.hProcess, image, create, child.dwProcessId,
                                                  born + 1, profile).failure) == "creation_process_identity");
    assert(std::string_view(verify_retail_mapping(child.hProcess, image, create, child.dwProcessId,
                                                 born).failure) == "creation_image_file_identity");
    assert(!profile_detail::read_image(child.hProcess, valid.base, valid.base,
                                       &event, sizeof event, true)); // PE headers are data
    CloseHandle(create.hFile);
    assert(TerminateProcess(child.hProcess, 0x6006));
    assert(ContinueDebugEvent(event.dwProcessId, event.dwThreadId, DBG_CONTINUE));
    bool exited = false;
    while (!exited) {
        assert(WaitForDebugEvent(&event, INFINITE));
        assert(event.dwProcessId == child.dwProcessId);
        if (event.dwDebugEventCode == LOAD_DLL_DEBUG_EVENT && event.u.LoadDll.hFile)
            CloseHandle(event.u.LoadDll.hFile);
        if (event.dwDebugEventCode == EXIT_PROCESS_DEBUG_EVENT) {
            assert(event.u.ExitProcess.dwExitCode == 0x6006);
            exited = true;
        }
        const DWORD disposition = event.dwDebugEventCode == EXCEPTION_DEBUG_EVENT ?
                                  DBG_EXCEPTION_NOT_HANDLED : DBG_CONTINUE;
        assert(ContinueDebugEvent(event.dwProcessId, event.dwThreadId, disposition));
    }
    assert(WaitForSingleObject(child.hProcess, INFINITE) == WAIT_OBJECT_0);
    CloseHandle(child.hProcess);
    CloseHandle(image);
    CloseHandle(wrong_image);
    std::cout << "disposable creation verified at base " << std::hex << valid.base
              << ", preferred base " << profile.preferred_base << '\n';
}

int wmain(int argc, wchar_t** argv) {
    if (argc == 2 && std::wstring_view(argv[1]) == L"--profile-fixture-child")
        return moved_slot(0);
    if (argc != 2) return 2;
    test_retail_bytes(argv[1]);
    wchar_t self[32768]{};
    assert(GetModuleFileNameW(nullptr, self, static_cast<DWORD>(std::size(self))));
    test_disposable_creation(self, argv[1]);
    std::cout << "retail ASLR window/slot controls passed (data only)\n";
}
