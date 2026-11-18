"""Offline SRR-018 comparison. Freeze predictions before opening observed inputs.

Run: python -B -m tools.srr018.compare REPRODUCER CAPTURE NEW_OUTPUT
Reads pinned four-input model and verified original observation; writes JSON reports.
No process, game, Ghidra or production-data mutations. Zero lanes use JSON null.
"""
import argparse
import csv
from collections import Counter, defaultdict
import json
from pathlib import Path
import subprocess
import sys

from tools.srr016 import oracle, compare
from tools.srr016.ledger import digest, file_digest, require


def canonical(word):
    # Extract namespace, independent of the captured runtime mapping. Both full
    # masters are explicitly named in the four canonical CSVs; never mask an
    # arbitrary unknown namespace into base-master identity.
    require(type(word) is int and 0 < word < 0x02000000, 'UNSUPPORTED_EXTRACT_NAMESPACE')
    plugin = ('starfield.esm', 'shatteredspace.esm')[word >> 24]
    return f'{plugin}:{word & 0xffffff:06X}'


def index(rows):
    out = {}
    for row in rows:
        key = tuple(row['key'])
        require(key not in out, 'DUPLICATE_KEY')
        require(len(row['slots']) == 7, 'INVALID_LANES')
        out[key] = row
    return out


def reconcile(observed, model):
    a, b = index(observed), index(model)
    differences = []
    for key in sorted(a.keys() & b.keys()):
        p = b[key]
        if p['applicability'] != 'CONDITIONAL':
            continue
        for lane, (actual, expected) in enumerate(zip(a[key]['slots'], p['slots'], strict=True)):
            if actual != expected:
                differences.append({'key': list(key), 'slot_ordinal': lane,
                                    'observed': actual, 'predicted': expected,
                                    'applicability': p['applicability'],
                                    'source': 'SRR-016 whole-owner screen / conditional control profile',
                                    'reason': 'ORDERED_NATIVE_LANE_DIFFERENCE'})
    return {'intersection': len(a.keys() & b.keys()),
            'retail_only': [list(k) for k in sorted(a.keys() - b.keys())],
            'model_only': [list(k) for k in sorted(b.keys() - a.keys())],
            'duplicates': 0, 'slot_differences': differences}


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n', encoding='utf-8', newline='\n')


def compact_rows(path):
    from tools.srr018.preserve import HEADER, ANCHORS
    manifest = compare.read_json(path.with_suffix('.manifest.json'))
    require(manifest['sha256'] == file_digest(path) ==
            '9675d3ac0335c98a17a636000075f76f3eb580944f510c95ff73738155a10bfb', 'COMPACT_HASH_DRIFT')
    require(manifest['source_sha256'] == ANCHORS, 'COMPACT_PROVENANCE_DRIFT')
    with path.open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        require(reader.fieldnames == HEADER, 'COMPACT_HEADER_DRIFT')
        rows = [{'key':[r['pndt'],r['biom']],
                 'slots':[None if r[h] == '0' else compare.identity(r[h]) for h in HEADER[2:]]}
                for r in reader]
    require(len(index(rows)) == 3211, 'COMPACT_POPULATION_DRIFT')
    return rows


def run(root, capture, output, compact=False):
    # Existing independent freeze validates clean HEAD and every canonical hash.
    ledger, qualified, receipt = oracle.freeze(root)
    pins = oracle.pinned_tree(root)
    from starfield_resource_reproducer.load_data import load_production_data
    from starfield_resource_reproducer.product import generate_all_planets
    from starfield_resource_reproducer.occurrences import build_enriched_occurrences
    project = load_production_data(root / 'data')
    require(not project.oracle, 'ORACLE_LEAKAGE')
    generations = generate_all_planets(project)
    q = index(qualified['rows'])
    predictions, planet_predictions, special = [], {}, []
    for fid, result in sorted(generations.items()):
        owner = canonical(fid.numeric)
        words, selected, flags = oracle.screen_owner(result, project.ires_nodes)
        planet_predictions[owner] = sorted(canonical(x.form_id.numeric) for x in result.predicted_resources)
        for biome in result.initial_biomes:
            key = [owner, canonical(biome.form_id.numeric)]
            applicability = 'CONDITIONAL' if tuple(key) in q else 'UNQUALIFIED_ORACLE'
            row = {'key': key, 'slots': [canonical(w) if w else None for w in words[biome.index]],
                   'applicability': applicability,
                   'reasons': sorted(flags) + ([] if applicability == 'CONDITIONAL' else ['EFFECTIVE_INPUTS_AND_WORKSET_UNATTESTED'])}
            predictions.append(row)
            s = selected[biome.index]
            if s['word'] and s['count_before'] == 8:
                special.append({'key': key, 'selected': canonical(s['word']), 'predicted_slot': row['slots'][5],
                                'applicability': applicability})
    atmosphere = defaultdict(set)
    for item in build_enriched_occurrences(project, generations):
        if item.location_type.value == 'ATMOSPHERE':
            atmosphere[canonical(item.planet_form_id.numeric)].add(canonical(item.resource_form_id.numeric))
    for owner in atmosphere.keys() - planet_predictions.keys():
        planet_predictions[owner] = sorted(atmosphere[owner])
    coverage = [{'owner': canonical(fid.numeric), 'reason': 'NO_TERRESTRIAL_MODEL_INPUT',
                 'atmosphere_model': sorted(atmosphere[canonical(fid.numeric)])}
                for fid in sorted(project.planet_directory) if fid not in generations]
    # Freeze all predictions, including diagnostics, before reading retail values.
    output.mkdir(parents=True, exist_ok=False)
    for name, value in [('ledger', ledger), ('oracle', qualified), ('freeze', receipt),
                        ('model-slots', predictions), ('model-planets', planet_predictions), ('unsupported-owners', coverage)]:
        write(output / (name + '.json'), value)
    expected = {'receipt.jsonl':'3a48b04479bf88a8821a704a77d684cd6941585c075323ce53c0d6a14a1efea3',
                'dataset.json':'15711109761112c3ce3b2f5bf2a03966ccdb26a277ea7ec0961f0147b16eedb4',
                'observation.json':'496ccd835e2e3de062aa07f812f15f406097c8f8948610a3f7952d6b08ae7c16',
                'result.json':'df9fed288b61e6a5a48603b5b5e4497a001ef441562ed28f24f40a98c09f0bd4',
                'manifest.json':'3441ccf092bef63ed7c9046a21ae99bb343e303443f85b1064d8215b2e971357'}
    if compact:
        observed_list = compact_rows(capture)
        observed = index(observed_list)
        strict = {'input':'UNQUALIFIED_COMPACT_DERIVATIVE', 'counts':{'comparable':0}}
    else:
        require({n:file_digest(capture/n) for n in expected} == expected, 'ORIGINAL_HASH_DRIFT')
        observation = compare.read_json(capture / 'observation.json')
        observed = compare.observed_rows(observation)
        require(observation['acquisition'] == 'QUALIFIED', 'UNQUALIFIED_CAPTURE')
        observed_list = observation['rows']
        strict = compare.compare(observation, ledger, qualified, receipt, receipt_sha256=digest(receipt))
    write(output / 'strict-comparator.json', strict)
    report = reconcile(observed_list, predictions)
    model = index(predictions)
    rows, terrestrial = [], defaultdict(set)
    diagnostic_diffs = []
    for key, row in sorted(observed.items()):
        terrestrial[key[0]].update(x for x in row['slots'] if x is not None)
        p = model.get(key)
        status = 'UNQUALIFIED_ORACLE' if p is None else p['applicability']
        if status == 'CONDITIONAL':
            status = 'MATCH' if row['slots'] == p['slots'] else 'DIFFERENCE'
        rows.append({'key':list(key), 'classification':status,
                     'reason': 'NO_TERRESTRIAL_MODEL_INPUT' if p is None else p['reasons']})
        if p:
            for lane, (actual, predicted) in enumerate(zip(row['slots'], p['slots'], strict=True)):
                if actual != predicted:
                    diagnostic_diffs.append({'key':list(key), 'slot_ordinal':lane, 'observed':actual,
                                             'predicted':predicted, 'applicability':p['applicability'],
                                             'reason':p['reasons'], 'source':'SRR-016 screened projection; frozen four-input model'})
    planets = []
    for owner, measured in sorted(terrestrial.items()):
        derived = measured | atmosphere[owner]
        predicted = planet_predictions.get(owner)
        result = ('UNQUALIFIED' if predicted is None else 'MATCH' if derived == set(predicted) else 'DIFFERENCE')
        planets.append({'owner':owner, 'terrestrial_observed':sorted(measured),
                        'atmosphere_model':sorted(atmosphere[owner]), 'derived':sorted(derived),
                        'predicted':predicted, 'derived_set_comparison':result,
                        'native_applicability':'CONDITIONAL' if any(k[0] == owner for k in q) else 'UNQUALIFIED',
                        'terrestrial_model_supported': any(k[0] == owner for k in model),
                        'observed_only': sorted(derived - set(predicted or [])),
                        'model_only': sorted(set(predicted or []) - derived)})
    for item in special:
        item['observed_slot'] = observed[tuple(item['key'])]['slots'][5]
    report.update({'row_classifications':dict(Counter(r['classification'] for r in rows)),
                   'observed_rows':len(observed), 'model_rows':len(model),
                   'observed_owners':len(terrestrial), 'model_owners':len(generations),
                   'qualified_owners':len({k[0] for k in q}),
                   'directory_owners_without_terrestrial_model':len(coverage),
                   'screen_failure_counts':receipt['screen_failure_counts'],
                   'strict_input':strict['input'], 'strict_comparable':strict['counts'].get('comparable',0),
                   'all_zero_rows':[list(k) for k,r in observed.items() if not any(r['slots'])],
                   'zero_lanes':sum(x is None for r in observed.values() for x in r['slots']),
                   'diagnostic_difference_lanes':len(diagnostic_diffs),
                   'planet_derived_comparisons':dict(Counter(p['derived_set_comparison'] for p in planets)),
                   'special_at_eight':special,
                   'provenance':{'research_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                                 'reproducer_head':oracle.REPRODUCER_COMMIT, 'model_pins':pins,
                                 'original_hashes':expected, 'comparison_source_sha256':file_digest(Path(__file__))}})
    for name, value in [('comparison',report), ('row-classifications',rows),
                        ('diagnostic-slot-differences',diagnostic_diffs), ('planet-comparisons',planets)]:
        write(output / (name + '.json'), value)
    require(oracle.pinned_tree(root) == pins, 'MODEL_CHANGED')
    print(json.dumps({k:v for k,v in report.items() if k != 'provenance'},indent=2))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('reproducer',type=Path); parser.add_argument('capture',type=Path); parser.add_argument('output',type=Path)
    parser.add_argument('--compact', action='store_true', help='CAPTURE is verified compact CSV; arithmetic only')
    args=parser.parse_args(); run(args.reproducer.resolve(),args.capture,args.output,args.compact)
