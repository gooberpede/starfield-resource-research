#pragma once

#include <windows.h>
#include <atomic>
#include <cstdio>
#include <cstdint>
#include <filesystem>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>
#include "retail_profile.h"

namespace srr006 {

inline bool space_available() {
    constexpr uint64_t minimum = 40000000000ULL + 134217728;
    ULARGE_INTEGER c{}, d{};
    return GetDiskFreeSpaceExW(L"C:\\", &c, nullptr, nullptr) &&
           GetDiskFreeSpaceExW(L"D:\\", &d, nullptr, nullptr) &&
           c.QuadPart >= minimum && d.QuadPart >= minimum;
}

inline bool publish_record(const std::filesystem::path& path, const std::string& bytes) {
    auto temporary = path;
    temporary += L".partial";
    HANDLE handle = CreateFileW(temporary.c_str(), GENERIC_WRITE, 0, nullptr, CREATE_ALWAYS,
                                FILE_ATTRIBUTE_NORMAL, nullptr);
    if (handle == INVALID_HANDLE_VALUE) return false;
    DWORD written = 0;
    const bool flushed = WriteFile(handle, bytes.data(), static_cast<DWORD>(bytes.size()),
                                   &written, nullptr) && written == bytes.size() &&
                         FlushFileBuffers(handle);
    const bool closed = CloseHandle(handle) != 0;
    if (!flushed || !closed) return false;
    // An external reader can briefly hold the prior watermark without
    // delete sharing. Retry only that transient publication failure.
    for (unsigned attempt = 0; attempt != 5; ++attempt) {
        if (MoveFileExW(temporary.c_str(), path.c_str(),
                        MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH)) return true;
        const DWORD error = GetLastError();
        if (error != ERROR_SHARING_VIOLATION && error != ERROR_ACCESS_DENIED) return false;
        Sleep(10);
    }
    return false;
}

// One producer (debug loop), one consumer. Producer never waits for storage.
// Publish a watermark only after flushing the contiguous journal prefix.
class Journal {
    std::vector<std::string> queue;
    HANDLE file;
    std::filesystem::path watermark, seal_path;
    std::atomic<bool> done{false};
    std::atomic<uint64_t> head{0}, tail{0}, checkpoint{0};
    std::atomic<uint64_t> stop_requested{0}, stop_published{0};
    std::thread writer;
    bool inject_failure, slow_writer, abrupt_fixture;
    uint64_t peak = 0;

    void write_loop() {
        uint64_t written = 0, offset = 0;
        profile_detail::Sha256 prefix_hash;
        while (!failed) {
            const bool finishing = done.load();
            const uint64_t limit = head.load();
            if (written == limit) {
                if (finishing) break;
                Sleep(1);
                continue;
            }
            if (!space_available()) { failed = true; break; }
            if (slow_writer) Sleep(250);
            while (written < limit && written - durable.load() < 128) {
                auto& row = queue[written % queue.size()];
                const bool cut = inject_failure && written == 64;
                const bool interrupt = abrupt_fixture && row.find("\"kind\":\"abrupt_probe\"") != std::string::npos;
                const DWORD size = static_cast<DWORD>((cut || interrupt) ? row.size()/2 : row.size());
                DWORD count = 0;
                if (!WriteFile(file, row.data(), size, &count, nullptr) ||
                    count != size || cut) {
                    failed = true;
                    break;
                }
                if (interrupt) {
                    // The fixture supervisor terminates this disposable
                    // observer after reading its independently durable checkpoint.
                    std::puts("UNCOMMITTED_TAIL_WRITTEN");
                    std::fflush(stdout);
                    Sleep(INFINITE);
                }
                if (!prefix_hash.add(row.data(), count)) { failed = true; break; }
                offset += count;
                row.clear();
                tail = ++written;
                if (written == stop_requested.load() ||
                    (written >= checkpoint.load() && durable.load() < checkpoint.load()))
                    break;
            }
            if (!failed) {
                const auto prefix_digest = prefix_hash.snapshot();
                const std::string prefix = "{\"schema\":1,\"sequence\":" +
                    std::to_string(written) + ",\"bytes\":" + std::to_string(offset) +
                    ",\"sha256\":\"" + prefix_digest + "\"}\n";
                if (prefix_digest.empty() || !FlushFileBuffers(file) ||
                    !publish_record(watermark, prefix)) {
                    failed = true;
                    break;
                }
                durable.store(written);
                if (written == stop_requested.load()) {
                    if (!publish_record(seal_path, prefix)) {
                        failed = true;
                        break;
                    }
                    stop_published.store(written);
                }
            }
            if (finishing && written == head.load()) break;
        }
    }

public:
    std::atomic<bool> failed{false};
    std::atomic<uint64_t> durable{0};
    uint64_t attempted = 0, accepted = 0, first_lost = 0;
    uint64_t high_water() const { return peak; }
    bool stop_sealed(uint64_t sequence) const { return sequence && sequence == stop_published.load(); }

    Journal(const std::filesystem::path& path, unsigned capacity, bool cut, bool slow, bool abrupt,
            const wchar_t* seal_name = L"stop-prefix.json")
        : queue(capacity), file(CreateFileW(path.c_str(), GENERIC_WRITE, FILE_SHARE_READ,
                               nullptr, CREATE_NEW, FILE_ATTRIBUTE_NORMAL, nullptr)),
          watermark(path.parent_path() / "durable-prefix.json"),
          seal_path(path.parent_path() / seal_name), inject_failure(cut),
          slow_writer(slow), abrupt_fixture(abrupt) {
        if (file == INVALID_HANDLE_VALUE) throw std::runtime_error("create journal");
        try { writer = std::thread(&Journal::write_loop, this); }
        catch (...) { CloseHandle(file); throw; }
    }
    ~Journal() { finish(); }

    bool append(std::string fields, bool seal_stop = false) {
        ++attempted;
        const uint64_t next = head.load();
        const auto depth = next - tail.load();
        // A Stage B STOP includes the bounded per-window verdicts in the seal.
        if (first_lost || failed || depth >= queue.size() || fields.size() > (seal_stop ? 16384u : 4096u)) {
            if (!first_lost) first_lost = attempted;
            return false;
        }
        queue[next % queue.size()] =
            "{\"schema\":1,\"seq\":" + std::to_string(attempted) + ',' + fields + "}\n";
        if (seal_stop) stop_requested = attempted;
        head = ++accepted;
        if (peak < depth + 1) peak = depth + 1;
        return true;
    }
    void request_flush() { checkpoint = accepted; }
    void finish() {
        if (!writer.joinable()) return;
        done = true;
        writer.join();
        CloseHandle(file);
    }
};

} // namespace srr006
