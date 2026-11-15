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
             (wcscmp(mode, L"slot-loss") == 0 &&
              !GetEnvironmentVariableW(L"SRR007_DISPOSABLE_ATTACH", nullptr, 0))))
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

static bool competing_breakpoint() {
    const auto address = reinterpret_cast<void(*)()>(
        GetProcAddress(GetModuleHandleW(L"ntdll.dll"), "DbgBreakPoint"));
    __try { address(); }
    __except (GetExceptionCode() == EXCEPTION_BREAKPOINT ? EXCEPTION_EXECUTE_HANDLER : EXCEPTION_CONTINUE_SEARCH) {
        return true;
    }
    return false;
}

static void wait_for(const std::filesystem::path& path) {
    while (GetFileAttributesW(path.c_str()) == INVALID_FILE_ATTRIBUTES) Sleep(20);
}

int fixture_child(const wchar_t* scenario, const wchar_t* directory) {
    std::filesystem::path folder(directory);
    auto is = [&](const wchar_t* name) { return wcscmp(scenario, name) == 0; };
    const bool late_attach = !is(L"quiet") &&
        GetEnvironmentVariableW(L"SRR007_DISPOSABLE_ATTACH", nullptr, 0) != 0;
    if (late_attach) {
        // One actual worker predates the attach census. It executes a site
        // only after the initial break-in and the operator's title marker.
        const auto parked = CreateThread(nullptr, 0, [](void* arg) -> DWORD {
            const auto& output = *static_cast<const std::filesystem::path*>(arg);
            wait_for(output / "advance");
            sample_guard();
            return 0;
        }, &folder, 0, nullptr);
        if (!parked || fixture_count != 1) return 99;
        if (is(L"admission-overlay-drift") || is(L"admission-overlay-lookalike")) {
            // Materialize a simulated Steam root before the attach census. The
            // drift control loads the origin-verified copy; the lookalike
            // control loads a same-named image from outside that origin.
            const std::filesystem::path source(L"C:/Windows/System32/version.dll");
            std::error_code copy_error;
            std::filesystem::create_directory(folder / L"steam-root", copy_error);
            copy_error.clear();
            const auto loaded = is(L"admission-overlay-drift") ?
                folder / L"steam-root" / L"gameoverlayrenderer64.dll" :
                folder / L"gameoverlayrenderer64.dll";
            if (!std::filesystem::copy_file(source, loaded,
                    std::filesystem::copy_options::overwrite_existing, copy_error) && copy_error)
                return 105;
            if (!LoadLibraryW(loaded.c_str())) return 106;
        }
        std::ofstream(folder / "attach-ready").put('\n');
        if (is(L"competing-breakpoint") || is(L"admission-competitor")) {
            wait_for(folder / "compete");
            if (!competing_breakpoint()) return 100;
            std::ofstream(folder / "competitor-handled").put('\n');
        }
        wait_for(folder / "advance");
        if (WaitForSingleObject(parked, INFINITE) != WAIT_OBJECT_0) return 99;
        CloseHandle(parked);
        // The previous guard hit served the attach census control. Existing
        // fixture cases use their original expected counts from this point.
        InterlockedDecrement(&fixture_count);
        if (is(L"crash")) {
            right_form[0x2e] = 0xba;
            sweep_later(&receiver, right_form);
            std::ofstream(folder / "ready").put('\n');
        }
        if (std::wstring_view(scenario).starts_with(L"recover-")) {
            right_form[0x2e] = 0xba;
            sweep_later(&receiver, right_form);
            std::ofstream(folder / "ready").put('\n');
            wait_for(folder / "quit");
            BOOL debugged = TRUE;
            if (!CheckRemoteDebuggerPresent(GetCurrentProcess(), &debugged)) return 101;
            const bool expected_attached = is(L"recover-refusal") || is(L"recover-partial") ||
                                           is(L"recover-detach-error");
            if (bool(debugged) != expected_attached) return 102;
            auto worker = CreateThread(nullptr, 0, [](void*) -> DWORD {
                sample_guard();
                return 0;
            }, nullptr, 0, nullptr);
            if (!worker || WaitForSingleObject(worker, INFINITE) != WAIT_OBJECT_0) return 103;
            CloseHandle(worker);
            sample_guard();
            return fixture_count == 5 ? 0 : 104;
        }
        if (is(L"anomalous-return")) {
            // Visit the callback directly with the wrong return path. The
            // real call chain that follows must remain independently usable.
            reinterpret_cast<void(*)(void*, void*)>(fixture_vtable[2])(&receiver, wrong_form);
            InterlockedDecrement(&fixture_count);
        }
    }
    if (is(L"quiet") || is(L"delay") || is(L"slot-loss")) {
        if (is(L"delay")) Sleep(2300);
        if (late_attach) std::ofstream(folder / "ready").put('\n');
        wait_for(folder / "quit");
        return fixture_count == int(late_attach) ? 0 : 83;
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
    if (is(L"admission-critical") || is(L"admission-quiet") || is(L"admission-slot-replaced")) {
        std::ofstream(folder / "ready").put('\n');
        wait_for(folder / "quit");
        return 0;
    }
    if (is(L"admission-overlay-drift") || is(L"admission-overlay-lookalike") ||
        is(L"admission-drift-arrival")) {
        if (is(L"admission-drift-arrival")) {
            // One durable positive in the pre-menu window, then the updated
            // overlay arrives mid-observation as a real module transition.
            right_form[0x2e] = 0xba;
            sweep_later(&receiver, right_form);
            std::ofstream(folder / "ready").put('\n');
            wait_for(folder / "menu-done");
            const auto overlay = folder / L"steam-root" / L"gameoverlayrenderer64.dll";
            std::error_code copy_error;
            std::filesystem::create_directory(folder / L"steam-root", copy_error);
            copy_error.clear();
            if (!std::filesystem::copy_file(L"C:/Windows/System32/version.dll", overlay,
                    std::filesystem::copy_options::overwrite_existing, copy_error) && copy_error)
                return 105;
            if (!LoadLibraryW(overlay.c_str())) return 107;
            std::ofstream(folder / "arrived").put('\n');
        } else {
            // The origin-verified but updated overlay predates arming; the
            // chain must still produce a full scientific positive.
            if (is(L"admission-overlay-drift")) {
                right_form[0x2e] = 0xba;
                sweep_later(&receiver, right_form);
            }
            std::ofstream(folder / "ready").put('\n');
        }
        wait_for(folder / "quit");
        return 0;
    }
    if (is(L"unexpected-module") || is(L"admission-fixture")) {
        const bool admission = is(L"admission-fixture");
        const auto source = std::filesystem::path(L"C:/Windows/System32/version.dll");
        const auto alias = folder / "optional-fixture.dll";
        if (admission) std::filesystem::copy_file(source, alias);
        auto module = admission ? LoadLibraryW(alias.c_str()) :
                                  LoadLibraryExW(L"version.dll", nullptr, LOAD_LIBRARY_SEARCH_SYSTEM32);
        if (!module) return 98;
        if (late_attach) {
            FreeLibrary(module);
            right_form[0x2e] = 0xba;
            sweep_later(&receiver, right_form);
        }
        std::ofstream(folder / "ready").put('\n');
        wait_for(folder / "quit");
        if (!late_attach) FreeLibrary(module);
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
