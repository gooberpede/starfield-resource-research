#pragma once
#include <windows.h>

extern "C" {
extern unsigned char guard_site, iterator_site, callback_site, allocator_site;
extern unsigned char early_return, later_return, iterator_return, callback_return, adapter_return;
extern unsigned char fixture_end;
void sample_guard();
void sweep_early(const void*, const void*);
void sweep_later(const void*, const void*);
void fixture_other_callback(const void*, const void*);
extern volatile LONG fixture_count;
extern uint64_t fixture_guard;
extern unsigned char fixture_flag;
extern const void* const fixture_vtable[3];
}

int fixture_child(const wchar_t* scenario, const wchar_t* folder);
