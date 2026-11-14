#include <cassert>
#include <sstream>
#include <string>
#include <string_view>
#include "window_evidence.h"

using namespace srr006;

static std::string receipt(const WindowEvidence& evidence, uint64_t durable) {
    std::ostringstream out;
    evidence.write_json(out, durable);
    return out.str();
}

static std::string_view window(const std::string& json, unsigned i) {
    const auto begin = json.find("{\"index\":" + std::to_string(i));
    assert(begin != std::string::npos);
    const auto next = json.find("{\"index\":", begin + 1);
    return std::string_view(json).substr(begin, next - begin);
}

static void expect(std::string_view value, std::string_view substring) {
    assert(value.find(substring) != std::string_view::npos);
}

int main() {
    {
        WindowEvidence evidence;
        evidence.open(1, true);
        assert(evidence.phase(3, true));
        evidence.stop(8, true);
        const auto partial = receipt(evidence, 3);
        expect(window(partial, 0), "\"invocation\":\"NOT_OBSERVED\"");
        expect(window(partial, 1), "\"journal_complete\":0");
        expect(window(partial, 1), "\"invocation\":\"INSTRUMENTATION_INCOMPLETE\"");
        evidence.gap(); // Post-STOP pump failure has its own run-level receipt.
        const auto complete = receipt(evidence, 8);
        expect(window(complete, 1), "\"allocator\":\"NOT_OBSERVED\"");
        evidence.gap_all(); // Retrospective identity or handoff failure.
        const auto retroactive = receipt(evidence, 8);
        expect(window(retroactive, 0), "\"invocation_gap\":1");
        expect(window(retroactive, 1), "\"invocation_gap\":1");
    }
    {
        WindowEvidence evidence{{"fixture_startup", "fixture_title", "fixture_main_menu"}};
        evidence.open(1, true);
        evidence.observe(1, {Verdict::iterator, 2}, 2);
        assert(evidence.phase(3, true));
        evidence.observe(2, {Verdict::invoked, 2, 4, 1, 0xba}, 4);
        assert(evidence.phase(5, true));
        evidence.observe(3, {Verdict::allocator, 2, 4, 1, 0xba}, 6);
        evidence.stop(7, true);
        const auto partial = receipt(evidence, 5);
        expect(window(partial, 0), "\"invocation_complete\":1");
        expect(window(partial, 0), "\"allocator_requires_through\":6");
        expect(window(partial, 0), "\"allocator\":\"INSTRUMENTATION_INCOMPLETE\"");
        expect(window(partial, 1), "\"invocation\":\"OBSERVED_INVOKED\"");
        expect(window(partial, 2), "\"allocator\":\"INSTRUMENTATION_INCOMPLETE\"");
        const auto durable = receipt(evidence, 7);
        expect(window(durable, 2), "\"name\":\"fixture_main_menu\"");
        expect(window(durable, 2), "\"allocator\":\"OBSERVED_REACHED_ALLOCATOR\"");
        expect(window(durable, 2), "\"sweep\":1,\"ingress\":2,\"callback\":4,\"allocator\":6");
        expect(window(durable, 2), "\"ingress_window\":0,\"callback_window\":1");
    }
    {
        WindowEvidence evidence;
        evidence.open(1, true);
        evidence.observe(1, {Verdict::iterator, 2}, 2);
        evidence.observe(2, {Verdict::invoked, 2, 3, 0, {}}, 3);
        evidence.stop(4, true);
        const auto durable = receipt(evidence, 4);
        expect(window(durable, 0), "\"invocation\":\"OBSERVED_INVOKED\"");
        expect(window(durable, 0), "\"invocation_complete\":1");
        expect(window(durable, 0), "\"allocator\":\"INSTRUMENTATION_INCOMPLETE\"");
    }
    {
        WindowEvidence evidence;
        evidence.open(1, true);
        evidence.observe(1, {Verdict::iterator, 2}, 2);
        evidence.observe(2, {Verdict::invoked, 2, 3, 0, 0xba}, 3);
        assert(evidence.phase(4, true));
        evidence.gap(Coverage::allocator); // Lost downstream coverage while a chain still crosses the boundary.
        evidence.stop(5, true);
        const auto durable = receipt(evidence, 5);
        expect(window(durable, 0), "\"pending_allocator\":1");
        expect(window(durable, 0), "\"invocation_complete\":1");
        expect(window(durable, 0), "\"allocator_complete\":0");
        expect(window(durable, 1), "\"invocation\":\"NOT_OBSERVED\"");
        expect(window(durable, 1), "\"incoming_unresolved_allocator\":1");
    }
    {
        WindowEvidence evidence;
        evidence.open(1, true);
        evidence.observe(1, {Verdict::iterator, 2}, 2);
        assert(evidence.phase(3, true));
        evidence.interrupt(4);
        const auto durable = receipt(evidence, 4);
        expect(window(durable, 0), "\"pending_callback\":1");
        expect(window(durable, 0), "\"invocation\":\"INSTRUMENTATION_INCOMPLETE\"");
        expect(window(durable, 1), "\"end_verified\":0");
        expect(window(durable, 1), "\"incoming_unresolved_callback\":1");
    }
    {
        WindowEvidence evidence;
        evidence.open(1, true);
        evidence.observe(3, {Verdict::unknown}, 2);
        evidence.stop(3, true);
        const auto durable = receipt(evidence, 3);
        expect(window(durable, 0), "\"invocation\":\"NOT_OBSERVED\"");
        expect(window(durable, 0), "\"allocator\":\"INSTRUMENTATION_INCOMPLETE\"");
    }
    {
        WindowEvidence evidence;
        evidence.stop(1, true);
        expect(receipt(evidence, 1), "\"invocation\":\"INSTRUMENTATION_INCOMPLETE\"");
    }
}
