#pragma once

#include <algorithm>
#include <array>
#include <cstdint>
#include <iomanip>
#include <optional>
#include <ostream>
#include "correlation.h"

namespace srr006 {

enum class Coverage { invocation, allocator, both };

// Receipts describe three named windows separated by two operator markers.
// A marker closes one window and opens the next. Event membership is
// [begin, end), but the closing marker must itself be durable.
class WindowEvidence {
    struct Join {
        uint64_t ingress = 0, callback = 0, allocator = 0;
        unsigned ingress_window = 0, callback_window = 0;
    };

    struct Window {
        uint64_t begin = 0, end = 0;
        uint64_t invocation_through = 0, allocator_through = 0;
        bool verified_begin = false, verified_end = false;
        bool invocation_gap = false, allocator_gap = false;
        uint64_t pending_callback = 0, pending_allocator = 0;
        std::array<uint64_t, 4> sites{};
        uint64_t rejected = 0, ambiguous = 0;
        std::array<Join, 2> first_invocation{}, first_allocator{};
    };

    // Only constant sizes depend on the experiment's named phases and sweeps.
    // The event-pump correlator owns active per-thread tokens. These counters
    // retain unresolved effects when a token is overwritten or discarded.
    std::array<Window, 3> windows{};
    std::array<const char*, 3> labels;
    unsigned current = 0;
    bool started = false, ended = false, stop_seen = false;

    std::optional<unsigned> find(uint64_t seq) const {
        if (!seq) return {};
        for (unsigned i = 0; i <= current; ++i) {
            const auto& window = windows[i];
            const bool unclosed = i == current && !ended;
            if (window.begin && window.begin <= seq && (unclosed || seq < window.end))
                return i;
        }
        return {};
    }

    static void mark(Window& window, Coverage coverage) {
        if (coverage != Coverage::allocator) window.invocation_gap = true;
        // An invocation gap can also hide a complete allocator chain.
        window.allocator_gap = true;
    }

    static bool durable_at(uint64_t sequence, uint64_t durable) {
        return sequence != 0 && sequence <= durable;
    }

    static void emit_joins(std::ostream& out, const std::array<Join, 2>& joins, uint64_t durable) {
        out << '[';
        bool comma = false;
        for (unsigned sweep = 0; sweep < joins.size(); ++sweep) {
            const auto& join = joins[sweep];
            if (!durable_at(join.allocator ? join.allocator : join.callback, durable)) continue;
            if (comma) out << ',';
            comma = true;
            out << "{\"sweep\":" << sweep << ",\"ingress\":" << join.ingress
                << ",\"callback\":" << join.callback << ",\"allocator\":" << join.allocator
                << ",\"ingress_window\":" << join.ingress_window
                << ",\"callback_window\":" << join.callback_window << '}';
        }
        out << ']';
    }

public:
    explicit WindowEvidence(std::array<const char*, 3> names = {"startup", "title_card", "main_menu"})
        : labels(names) {}

    unsigned index() const { return current; }

    void open(uint64_t sequence, bool checked) {
        if (started || ended || current) return;
        started = true;
        windows[0].begin = sequence;
        windows[0].verified_begin = checked && sequence;
    }

    bool phase(uint64_t sequence, bool checked) {
        if (ended || current + 1 >= windows.size()) return false;
        auto& closing = windows[current];
        closing.end = sequence;
        closing.verified_end = checked && sequence && sequence > closing.begin;
        auto& opening = windows[++current];
        opening.begin = sequence;
        opening.verified_begin = closing.verified_end;
        return true;
    }

    void stop(uint64_t sequence, bool checked) {
        if (ended) return;
        auto& window = windows[current];
        window.end = sequence;
        window.verified_end = checked && sequence && sequence > window.begin;
        ended = stop_seen = true;
    }

    void interrupt(uint64_t sequence) {
        if (ended) return;
        windows[current].end = sequence;
        gap();
        ended = true;
    }

    void gap(Coverage coverage = Coverage::both) {
        if (ended) return;
        mark(windows[current], coverage);
        // A later loss can obscure resolution of an earlier open chain.
        for (unsigned i = 0; i < current; ++i) {
            auto& prior = windows[i];
            if (prior.pending_callback && coverage != Coverage::allocator)
                mark(prior, Coverage::both);
            if (prior.pending_allocator || prior.pending_callback)
                mark(prior, Coverage::allocator);
        }
    }

    void gap_all(Coverage coverage = Coverage::both) {
        for (unsigned i = 0; i <= current; ++i) mark(windows[i], coverage);
    }

    // Call only after exact ownership, continuation and journal acceptance.
    // The correlator validates same-thread/frame/process ancestry. Fail closed
    // on unresolved receipt references independently of that validation.
    void observe(unsigned site, const Result& result, uint64_t seq) {
        if (ended || !seq || site >= 4) return;
        if (find(seq) != current) { gap(); return; }
        auto& arrival = windows[current];
        ++arrival.sites[site];
        switch (result.verdict) {
        case Verdict::sample:
            return;
        case Verdict::nonfocal:
            ++arrival.rejected;
            return;
        case Verdict::unknown:
            ++arrival.ambiguous;
            gap(site == 3 ? Coverage::allocator : Coverage::both);
            return;
        case Verdict::iterator:
            if (site == 1 && result.ingress == seq) ++arrival.pending_callback;
            else gap();
            return;
        case Verdict::invoked:
        case Verdict::allocator:
            break;
        }

        const bool invoked = result.verdict == Verdict::invoked;
        const auto ingress_window = find(result.ingress);
        const auto callback_window = find(result.callback);
        const auto coverage = invoked ? Coverage::both : Coverage::allocator;
        if (site != (invoked ? 2u : 3u) || result.sweep >= 2 ||
            !ingress_window || !callback_window || result.ingress >= result.callback ||
            (invoked ? result.callback != seq : result.callback >= seq || result.type != 0xba)) {
            gap(coverage);
            return;
        }
        auto& ingress = windows[*ingress_window];
        auto& callback = windows[*callback_window];
        const Join join{result.ingress, result.callback, invoked ? 0 : seq,
                        *ingress_window, *callback_window};
        if (invoked) {
            if (!ingress.pending_callback) { gap(); return; }
            --ingress.pending_callback;
            for (unsigned i = *ingress_window; i <= current; ++i) {
                auto& covered = windows[i];
                covered.invocation_through = std::max(covered.invocation_through, seq);
                covered.allocator_through = std::max(covered.allocator_through, seq);
            }
            auto& first = arrival.first_invocation[result.sweep];
            if (!first.callback) first = join;
            if (!result.type) {
                mark(ingress, Coverage::allocator);
                mark(arrival, Coverage::allocator);
            } else if (result.type == 0xba) {
                ++callback.pending_allocator;
                if (*ingress_window != *callback_window) ++ingress.pending_allocator;
            }
        } else {
            if (!callback.pending_allocator || !ingress.pending_allocator) { gap(coverage); return; }
            --callback.pending_allocator;
            if (*ingress_window != *callback_window) --ingress.pending_allocator;
            for (unsigned i = *ingress_window; i <= current; ++i)
                windows[i].allocator_through = std::max(windows[i].allocator_through, seq);
            auto& first = arrival.first_allocator[result.sweep];
            if (!first.allocator) first = join;
        }
    }

    void write_json(std::ostream& out, uint64_t durable) const {
        out << '[';
        bool callback_unresolved = false, allocator_unresolved = false;
        for (unsigned i = 0; i <= current; ++i) {
            const auto& window = windows[i];
            const bool closed = i < current || ended;
            const bool verified = closed && window.verified_begin && window.verified_end;
            const bool durable_window = durable_at(window.begin, durable) &&
                                        durable_at(window.end, durable);
            const bool incoming_callback = callback_unresolved;
            const bool incoming_allocator = allocator_unresolved;
            callback_unresolved |= window.pending_callback != 0;
            allocator_unresolved |= window.pending_allocator != 0;
            const bool callback_coverage = verified && !window.invocation_gap && !callback_unresolved;
            const bool allocator_coverage = callback_coverage && !window.allocator_gap && !allocator_unresolved;
            const bool invocation_complete = durable_window && callback_coverage &&
                                             window.invocation_through <= durable;
            const bool allocator_complete = durable_window && allocator_coverage &&
                                            window.allocator_through <= durable;
            bool invoked = false, reached = false;
            for (unsigned sweep = 0; sweep < 2; ++sweep) {
                invoked |= durable_at(window.first_invocation[sweep].callback, durable);
                reached |= durable_at(window.first_allocator[sweep].allocator, durable);
            }
            if (i) out << ',';
            out << "{\"index\":" << i << ",\"name\":" << std::quoted(labels[i])
                << ",\"begin\":" << window.begin << ",\"end\":" << window.end
                << ",\"closed\":" << (closed ? 1 : 0) << ",\"stop_boundary\":"
                << (i == current && stop_seen ? 1 : 0)
                << ",\"start_verified\":" << (window.verified_begin ? 1 : 0)
                << ",\"end_verified\":" << (window.verified_end ? 1 : 0)
                << ",\"journal_complete\":" << (durable_window ? 1 : 0)
                << ",\"invocation_coverage\":" << (callback_coverage ? 1 : 0)
                << ",\"allocator_coverage\":" << (allocator_coverage ? 1 : 0)
                << ",\"invocation_complete\":" << (invocation_complete ? 1 : 0)
                << ",\"allocator_complete\":" << (allocator_complete ? 1 : 0)
                << ",\"invocation_gap\":" << (window.invocation_gap ? 1 : 0)
                << ",\"allocator_gap\":" << (window.allocator_gap ? 1 : 0)
                << ",\"pending_callback\":" << window.pending_callback
                << ",\"pending_allocator\":" << window.pending_allocator
                << ",\"incoming_unresolved_callback\":" << (incoming_callback ? 1 : 0)
                << ",\"incoming_unresolved_allocator\":" << (incoming_allocator ? 1 : 0)
                << ",\"invocation_requires_through\":" << window.invocation_through
                << ",\"allocator_requires_through\":" << window.allocator_through
                << ",\"accepted_site_hits\":["
                << window.sites[0] << ',' << window.sites[1] << ','
                << window.sites[2] << ',' << window.sites[3] << ']'
                << ",\"accepted_nonfocal\":" << window.rejected
                << ",\"accepted_ambiguous\":" << window.ambiguous
                << ",\"outcome_scope\":\"site_arrival_window\""
                << ",\"invocation\":\""
                << (invoked ? "OBSERVED_INVOKED" :
                    invocation_complete ? "NOT_OBSERVED" : "INSTRUMENTATION_INCOMPLETE")
                << "\",\"allocator\":\""
                << (reached ? "OBSERVED_REACHED_ALLOCATOR" :
                    allocator_complete ? "NOT_OBSERVED" : "INSTRUMENTATION_INCOMPLETE")
                << "\",\"first_invocations\":";
            emit_joins(out, window.first_invocation, durable);
            out << ",\"first_allocator_chains\":";
            emit_joins(out, window.first_allocator, durable);
            out << '}';
        }
        out << ']';
    }
};

} // namespace srr006
