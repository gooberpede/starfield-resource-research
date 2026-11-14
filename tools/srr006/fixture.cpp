#include <cstdint>
#include <cwchar>
#include <filesystem>
#include <fstream>
#include "fixture.h"

extern "C" {
volatile LONG fixture_count = 0;
uint64_t fixture_guard = 0;
unsigned char fixture_flag = 1;
const void* const fixture_vtable[3]{nullptr, &callback_site, &callback_site};
}
static const void* const other_vtable[3]{nullptr, nullptr, fixture_other_callback};
static const void* receiver = fixture_vtable;
static const void* other_receiver = other_vtable;
static unsigned char wrong_form[0x30]{}, right_form[0x30]{};
static HANDLE gate;
static bool busy, callback_only, stop_burst;

static void NTAPI early_tls(void*, DWORD reason, void*) {
    if (reason == DLL_PROCESS_ATTACH) {
        wchar_t mode[32]{};
        if (GetEnvironmentVariableW(L"SRR006_FIXTURE_MODE", mode, 32) &&
            (wcscmp(mode, L"quiet") == 0 || wcscmp(mode, L"delay") == 0 ||
             wcscmp(mode, L"slot-loss") == 0))
            return;
        sample_guard();
    }
}
#pragma section(".CRT$XLB", long, read)
extern "C" __declspec(allocate(".CRT$XLB")) PIMAGE_TLS_CALLBACK srr006_tls = early_tls;
#pragma comment(linker, "/INCLUDE:_tls_used")
#pragma comment(linker, "/INCLUDE:srr006_tls")

static DWORD WINAPI worker(void*) {
    // This is the first fixture operation performed by a new worker.
    sample_guard();
    if (WaitForSingleObject(gate, INFINITE) != WAIT_OBJECT_0) return 81;
    if (stop_burst) {
        for (unsigned i = 0; i < 512; ++i) sample_guard();
        return 0;
    }
    for (unsigned i = 0; i < (busy ? 512u : 16u); ++i)
        sweep_early(&other_receiver, wrong_form);
    sweep_early(&receiver, wrong_form);
    if (!callback_only) sweep_later(&receiver, right_form);
    return 0;
}

static int guarded_exception() {
    __try { RaiseException(0xe1230042, 0, 0, nullptr); }
    __except (GetExceptionCode() == 0xe1230042 ? EXCEPTION_EXECUTE_HANDLER : EXCEPTION_CONTINUE_SEARCH) {
        return 0;
    }
    return 82;
}

static int unreadable_form() {
    __try { sweep_early(&receiver, reinterpret_cast<void*>(1)); }
    __except (GetExceptionCode() == EXCEPTION_ACCESS_VIOLATION ?
              EXCEPTION_EXECUTE_HANDLER : EXCEPTION_CONTINUE_SEARCH) {
        return 0;
    }
    return 92;
}

static int unowned_step() {
    __try { RaiseException(EXCEPTION_SINGLE_STEP, 0, 0, nullptr); }
    __except (GetExceptionCode() == EXCEPTION_SINGLE_STEP ?
              EXCEPTION_EXECUTE_HANDLER : EXCEPTION_CONTINUE_SEARCH) {
        return 0;
    }
    return 96;
}

static void wait_for(const std::filesystem::path& path) {
    while (GetFileAttributesW(path.c_str()) == INVALID_FILE_ATTRIBUTES) Sleep(20);
}

int fixture_child(const wchar_t* scenario, const wchar_t* directory) {
    const std::filesystem::path folder(directory);
    auto is = [&](const wchar_t* name) { return wcscmp(scenario, name) == 0; };
    if (is(L"quiet") || is(L"delay") || is(L"slot-loss")) {
        if (is(L"delay")) Sleep(2300);
        wait_for(folder / "quit");
        return fixture_count == 0 ? 0 : 83;
    }
    if (is(L"continue-persistent")) {
        wait_for(folder / "fault");
        sample_guard();
        wait_for(folder / "unissued-release");
        return 84;
    }
    if (is(L"emergency-denied")) {
        wait_for(folder / "quit");
        return 0;
    }
    if (is(L"emergency") || is(L"abrupt-observer") ||
        is(L"wait-persistent") || is(L"combined-failure")) {
        wait_for(folder / "unissued-release");
        return 84;
    }
    if (is(L"handoff")) {
        wchar_t self[32768]{};
        if (!GetModuleFileNameW(nullptr, self, ARRAYSIZE(self))) return 93;
        auto command = L"\"" + std::wstring(self) + L"\" --child quiet \"" + folder.wstring() + L"\"";
        std::ofstream(folder / "quit").put('\n');
        STARTUPINFOW startup{};
        startup.cb = sizeof startup;
        PROCESS_INFORMATION successor{};
        if (!CreateProcessW(self, command.data(), nullptr, nullptr, FALSE, CREATE_NO_WINDOW,
                            nullptr, nullptr, &startup, &successor)) return 94;
        CloseHandle(successor.hThread);
        const auto wait = WaitForSingleObject(successor.hProcess, INFINITE);
        DWORD status = 0;
        GetExitCodeProcess(successor.hProcess, &status);
        CloseHandle(successor.hProcess);
        // The successor has its own TLS hit, proving that this marker belongs
        // to a real child outside DEBUG_ONLY_THIS_PROCESS coverage.
        if (wait != WAIT_OBJECT_0 || status != 83) return 95;
        std::ofstream(folder / "handoff-pid") << successor.dwProcessId << '\n';
        return 0;
    }
    if (is(L"crash")) {
        wait_for(folder / "crash-now");
        RaiseException(0xe1230043, 0, 0, nullptr);
        return 85;
    }
    if (is(L"unreadable")) {
        if (unreadable_form()) return 92;
        std::ofstream(folder / "ready").put('\n');
        wait_for(folder / "quit");
        return 0;
    }
    if (is(L"foreign-step")) {
        if (unowned_step()) return 96;
        std::ofstream(folder / "ready").put('\n');
        wait_for(folder / "quit");
        return 0;
    }
    if (is(L"unexpected-module")) {
        auto module = LoadLibraryExW(L"version.dll", nullptr, LOAD_LIBRARY_SEARCH_SYSTEM32);
        if (!module) return 98;
        std::ofstream(folder / "ready").put('\n');
        wait_for(folder / "quit");
        FreeLibrary(module);
        return 0;
    }
    right_form[0x2e] = 0xba;
    if (is(L"cross-window")) {
        sweep_later(&receiver, right_form);
        std::ofstream(folder / "ready").put('\n');
        wait_for(folder / "quit");
        return fixture_count == 3 ? 0 : 97;
    }
    busy = is(L"busy") || is(L"overflow") || is(L"write-error");
    callback_only = is(L"callback-only");
    stop_burst = is(L"stop-burst");
    gate = CreateEventW(nullptr, TRUE, FALSE, nullptr);
    if (!gate) return 86;
    HANDLE workers[8]{};
    for (auto& thread : workers) {
        thread = CreateThread(nullptr, 0, worker, nullptr, 0, nullptr);
        if (!thread) return 87;
    }
    if (!SetEvent(gate) || WaitForMultipleObjects(8, workers, TRUE, INFINITE) != WAIT_OBJECT_0)
        return 88;
    for (auto thread : workers) {
        DWORD code = 0;
        if (!GetExitCodeThread(thread, &code) || code != 0) return 89;
        CloseHandle(thread);
    }
    CloseHandle(gate);
    if (guarded_exception()) return 90;
    constexpr LONG workers_count = 8;
    const LONG expected = stop_burst ? 513 : (1 + (busy ? 512 : 16) + (callback_only ? 1 : 3));
    if (fixture_count != 1 + workers_count * expected)
        return 91;
    std::ofstream(folder / "ready").put('\n');
    // This hit is gated on operator STOP, proving event service after STOP.
    wait_for(folder / "quit");
    sample_guard();
    return 0;
}
