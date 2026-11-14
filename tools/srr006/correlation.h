#pragma once

#include <array>
#include <cstdint>
#include <optional>

namespace srr006 {

using Address = uint64_t;

struct Layout {
    std::array<Address, 4> sites;
    Address vtable, guard, flag;
    std::array<Address, 2> sweep_returns;
    Address iterator_return, callback_return, adapter_return;
};

inline constexpr Layout retail{
    {0x9518FD, 0x5932EF, 0x77C470, 0x779760},
    0x4B3D9E8, 0x61E2288, 0x5EA6000, {0x94E57C, 0x94EF5C},
    0x5932F2, 0x77C487, 0x7796D7
};

struct Registers {
    Address rsp, rax, rcx, rdx, r14, rsi;
};

enum class Verdict { sample, nonfocal, unknown, iterator, invoked, allocator };

struct Result {
    Verdict verdict;
    uint64_t ingress = 0, callback = 0;
    unsigned sweep = 0;
    std::optional<Address> type;
};

// One instance belongs to one live process/module/coverage epoch and thread
// generation. The event pump destroys it on thread exit or a coverage gap.
class Correlation {
    struct Frame {
        Address rsp, receiver, form, source;
        uint64_t ingress, callback;
        unsigned sweep;
        std::optional<Address> type;
    };
    std::optional<Frame> frame;

public:
    void clear() { frame.reset(); }
    bool awaiting_callback() const { return frame && !frame->callback; }

    // read(address, width, stack) returns an exact checked little-endian value.
    template<class Reader>
    Result hit(unsigned site, const Layout& layout, Address base, Registers r,
               uint64_t sequence, Reader read) {
        auto operand = [&](Address address, Address offset, unsigned width, bool stack) {
            if (address > UINT64_MAX - offset) return std::optional<Address>{};
            return read(address + offset, width, stack);
        };
        auto stack = [&](Address offset) { return operand(r.rsp, offset, 8, true); };
        if (site == 0) {
            const auto guard = read(base + layout.guard, 8, false);
            return {guard ? Verdict::sample : Verdict::unknown};
        }
        read(base + layout.guard, 8, false);
        read(base + layout.flag, 1, false);
        if (site == 1) {
            // Invalidate even when a newer iterator proves nonfocal.
            const bool missing_callback = awaiting_callback();
            clear();
            if (missing_callback) return {Verdict::unknown};
            if (r.rax != base + layout.vtable || r.rcx != r.r14 || !r.rdx || !r.rcx)
                return {Verdict::nonfocal};
            const auto vptr = operand(r.rcx, 0, 8, false);
            const auto slot = operand(r.rax, 0x10, 8, false);
            const auto source = stack(0x38);
            if (!vptr || !slot || !source) return {Verdict::unknown};
            if (*vptr != r.rax || *slot != base + layout.sites[2])
                return {Verdict::unknown};
            unsigned sweep = *source == base + layout.sweep_returns[1];
            if (*source != base + layout.sweep_returns[sweep]) return {Verdict::nonfocal};
            frame = Frame{r.rsp, r.rcx, r.rdx, *source, sequence, 0, sweep, {}};
            return {Verdict::iterator, sequence, 0, sweep};
        }
        if (site == 2) {
            const auto prior = frame;
            clear();
            const auto ret = stack(0);
            if (!ret) return {Verdict::unknown};
            if (*ret != base + layout.iterator_return)
                return {prior && !prior->callback ? Verdict::unknown : Verdict::nonfocal};
            const auto source = stack(0x40);
            if (!source) return {Verdict::unknown};
            if (*source != base + layout.sweep_returns[0] &&
                *source != base + layout.sweep_returns[1])
                return {prior && !prior->callback ? Verdict::unknown : Verdict::nonfocal};
            if (!prior || prior->callback || prior->ingress >= sequence ||
                prior->rsp < 8 || prior->rsp - 8 != r.rsp || prior->source != *source ||
                r.rcx != prior->receiver || r.r14 != prior->receiver || r.rdx != prior->form)
                return {Verdict::unknown};
            const auto vptr = operand(r.rcx, 0, 8, false);
            const auto slot = read(base + layout.vtable + 0x10, 8, false);
            if (vptr != base + layout.vtable || slot != base + layout.sites[2])
                return {Verdict::unknown};
            frame = prior;
            frame->callback = sequence;
            frame->type = operand(r.rdx, 0x2e, 1, false);
            return {Verdict::invoked, frame->ingress, sequence, frame->sweep, frame->type};
        }
        const auto ret = stack(0);
        if (!ret) { clear(); return {Verdict::unknown}; }
        if (*ret != base + layout.adapter_return) return {Verdict::nonfocal};
        const auto prior = frame;
        clear();
        const auto adapter = stack(0x80);
        const auto iterator = stack(0xb0);
        const auto source = stack(0xf0);
        if (!adapter || !iterator || !source) return {Verdict::unknown};
        if (*adapter != base + layout.callback_return ||
            *iterator != base + layout.iterator_return ||
            (*source != base + layout.sweep_returns[0] &&
             *source != base + layout.sweep_returns[1]))
            return {prior && !prior->callback ? Verdict::unknown : Verdict::nonfocal};
        if (!prior || !prior->callback || prior->callback >= sequence ||
            prior->type != 0xba || prior->source != *source || prior->rsp < 0xb8 ||
            prior->rsp - 0xb8 != r.rsp || r.rsp > UINT64_MAX - 0xf8 ||
            r.rcx != r.rsp + 0x98 || r.rdx != r.rsp + 0x90 ||
            stack(0x98) != prior->form || stack(0x50) != prior->receiver)
            return {Verdict::unknown};
        return {Verdict::allocator, prior->ingress, prior->callback, prior->sweep, prior->type};
    }
};

} // namespace srr006
