"""Small SRR-018 comparator adversarial fixtures: python -B -m tools.srr018.qualify."""
from copy import deepcopy
import unittest
from tools.srr018.compare import reconcile, canonical
from tools.srr016.compare import input_decision

class ComparisonChallenge(unittest.TestCase):
    def setUp(self):
        self.row={'key':['starfield.esm:000001','starfield.esm:000002'], 'slots':[None]*7, 'applicability':'CONDITIONAL'}
    def test_missing_key(self):
        r=reconcile([], [self.row]); self.assertEqual(r['model_only'],[self.row['key']])
    def test_extra_key(self):
        r=reconcile([self.row],[]); self.assertEqual(r['retail_only'],[self.row['key']])
    def test_ordered_lane_difference(self):
        observed=deepcopy(self.row); observed['slots'][4]='starfield.esm:0057EA'
        r=reconcile([observed],[self.row]); self.assertEqual(r['slot_differences'][0]['slot_ordinal'],4)
        self.assertEqual(r['slot_differences'][0]['observed'],'starfield.esm:0057EA')
        self.assertIsNone(r['slot_differences'][0]['predicted'])
    def test_equal_union_different_lane_is_not_match(self):
        model=deepcopy(self.row); model['slots'][0]='starfield.esm:0057EA'
        observed=deepcopy(self.row); observed['slots'][1]='starfield.esm:0057EA'
        self.assertEqual(set(model['slots']),set(observed['slots']))
        self.assertEqual(len(reconcile([observed],[model])['slot_differences']),2)
    def test_unqualified_is_not_scored(self):
        model=deepcopy(self.row); model['applicability']='UNQUALIFIED_ORACLE'; model['slots'][0]='starfield.esm:0057EA'
        self.assertEqual(reconcile([self.row],[model])['slot_differences'],[])
    def test_duplicate_rejected(self):
        with self.assertRaisesRegex(ValueError,'DUPLICATE_KEY'): reconcile([self.row,self.row],[])
    def test_missing_input_attestation_refused(self):
        source={'retail_sha256':'a'*64, 'input_sha256':None}
        self.assertEqual(input_decision(source,source),'RETAIL_APPLICABILITY_UNRESOLVED')
    def test_different_input_source_refused(self):
        observed={'retail_sha256':'a'*64, 'input_sha256':'b'*64}
        expected={'retail_sha256':'a'*64, 'input_sha256':'c'*64}
        self.assertEqual(input_decision(observed,expected),'INPUT_PROVENANCE_MISMATCH')
    def test_unknown_namespace_refused(self):
        with self.assertRaisesRegex(ValueError,'UNSUPPORTED_EXTRACT_NAMESPACE'): canonical(0x02000001)
    def test_lane_count_refused(self):
        self.row['slots'].pop()
        with self.assertRaisesRegex(ValueError,'INVALID_LANES'): reconcile([self.row],[])

if __name__ == '__main__': unittest.main()
