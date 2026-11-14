#include <cassert>
#include <map>
#include "correlation.h"

using namespace srr006;

int main() {
    constexpr Address base = 0x140000000, rsp = 0x100000, receiver = 0x200000, form = 0x300000;
    constexpr Address callback_rsp = rsp - 8, allocator_rsp = rsp - 0xb8;
    Registers iterator{rsp, base + retail.vtable, receiver, form, receiver, 0};
    Registers callback{callback_rsp, iterator.rax, receiver, form, receiver, 0};
    Registers allocator{allocator_rsp, 0, allocator_rsp + 0x98, allocator_rsp + 0x90, receiver, 0};
    const Address source = base + retail.sweep_returns[0];
    std::map<Address, Address> memory{
        {receiver, iterator.rax}, {iterator.rax + 0x10, base + retail.sites[2]},
        {rsp + 0x38, source}, {callback_rsp, base + retail.iterator_return},
        {allocator_rsp, base + retail.adapter_return},
        {allocator_rsp + 0x80, base + retail.callback_return},
        {allocator_rsp + 0x50, receiver}, {allocator_rsp + 0x98, form}, {form + 0x2e, 0xba},
    };
    auto read = [&](Address address, unsigned, bool) -> std::optional<Address> {
        const auto entry = memory.find(address);
        if (entry == memory.end()) return {};
        return entry->second;
    };
    Correlation thread, other;
    auto hit = [&](unsigned site, Registers r, uint64_t seq) {
        return thread.hit(site, retail, base, r, seq, read);
    };
    assert(hit(1, iterator, 1).verdict == Verdict::iterator);
    assert(other.hit(2, retail, base, callback, 2, read).verdict == Verdict::unknown);
    const auto invocation = hit(2, callback, 3);
    assert(invocation.verdict == Verdict::invoked && invocation.ingress == 1);
    const auto arrival = hit(3, allocator, 4);
    assert(arrival.verdict == Verdict::allocator && arrival.callback == 3 && arrival.ingress == 1);
    assert(hit(3, allocator, 5).verdict == Verdict::unknown);

    assert(hit(1, iterator, 6).verdict == Verdict::iterator);
    assert(hit(1, iterator, 7).verdict == Verdict::unknown); // skipped callback
    assert(hit(2, callback, 8).verdict == Verdict::unknown);
    assert(hit(1, iterator, 9).verdict == Verdict::iterator);
    assert(hit(2, callback, 10).verdict == Verdict::invoked);
    assert(hit(2, callback, 11).verdict == Verdict::unknown);
    assert(hit(3, allocator, 12).verdict == Verdict::unknown);

    memory.erase(form + 0x2e);
    assert(hit(1, iterator, 13).verdict == Verdict::iterator);
    assert(hit(2, callback, 14).verdict == Verdict::invoked);
    assert(hit(3, allocator, 15).verdict == Verdict::unknown);
    assert(hit(1, iterator, 16).verdict == Verdict::iterator);
    thread.clear(); // coverage gap
    assert(hit(2, callback, 17).verdict == Verdict::unknown);
    assert(hit(1, iterator, 18).verdict == Verdict::iterator);
    thread = Correlation{}; // new generation for reused numerical TID
    assert(hit(2, callback, 19).verdict == Verdict::unknown);
    assert(hit(1, iterator, 20).verdict == Verdict::iterator);
    memory[callback_rsp] = base + retail.callback_return;
    assert(hit(2, callback, 21).verdict == Verdict::unknown);
    memory.erase(rsp + 0x38);
    assert(hit(1, iterator, 22).verdict == Verdict::unknown);
}
