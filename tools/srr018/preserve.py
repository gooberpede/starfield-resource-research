"""Offline SRR-017 custody and compact comparison projection.

Run: python -E -B -m tools.srr018.preserve --source CAPTURE --output DIRECTORY
Reads original JSON/journal bytes; writes a private ZIP, CSV and manifests.
Never opens a process, changes game files or modifies a Ghidra project.
The CSV supports key/slot analysis, not native acquisition qualification.
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import shutil
import zipfile

ANCHORS = {
    'receipt.jsonl': '3a48b04479bf88a8821a704a77d684cd6941585c075323ce53c0d6a14a1efea3',
    'dataset.json': '15711109761112c3ce3b2f5bf2a03966ccdb26a277ea7ec0961f0147b16eedb4',
    'observation.json': '496ccd835e2e3de062aa07f812f15f406097c8f8948610a3f7952d6b08ae7c16',
    'result.json': 'df9fed288b61e6a5a48603b5b5e4497a001ef441562ed28f24f40a98c09f0bd4',
    'manifest.json': '3441ccf092bef63ed7c9046a21ae99bb343e303443f85b1064d8215b2e971357',
}
HEADER = ['pndt', 'biom', 'common', 'uncommon', 'rare', 'exotic', 'unique', 'special', 'everywhere']


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def preserve(source, output):
    # Includes room for original-size ZIP, restoration and CSV, without relying
    # on compression ratio. Input files are never modified.
    for drive in ('C:/', 'D:/'):
        if shutil.disk_usage(drive).free - 150_000_000 < 40_000_000_000:
            raise RuntimeError('insufficient available space: ' + drive)
    originals = {name: (source / name).read_bytes() for name in ANCHORS}
    if {name: digest(data) for name, data in originals.items()} != ANCHORS:
        raise ValueError('original acquisition anchor mismatch')
    manifest = json.loads(originals['manifest.json'])
    for name, expected in manifest['files'].items():
        if digest(originals[name]) != expected:
            raise ValueError('original manifest mismatch: ' + name)
    root = Path(__file__).resolve().parents[2]
    for name, expected in manifest['source']['files'].items():
        if digest((root / name).read_bytes()) != expected:
            raise ValueError('replay source mismatch: ' + name)
    d = json.loads(originals['dataset.json'])
    o = json.loads(originals['observation.json'])
    if d['acquisition'] != 'QUALIFIED' or o['acquisition'] != 'QUALIFIED':
        raise ValueError('unqualified original')
    rows = {}
    for row in d['rows']:
        key = tuple(row[k]['source']['comparator_id'] for k in ('pndt', 'biom'))
        if key in rows or [s['ordinal'] for s in row['slots']] != list(range(7)):
            raise ValueError('duplicate key or invalid ordinal sequence')
        values = []
        for slot in row['slots']:
            if slot['runtime_form_id'] == 0:
                if slot['source'] is not None or slot['native_status'] != 'ZERO':
                    raise ValueError('zero/source conflation')
                values.append('0')
            else:
                if slot['native_status'] != 'VERIFIED':
                    raise ValueError('unverified nonzero lane')
                values.append(slot['source']['comparator_id'])
        rows[key] = tuple(values)
    # Independent representation in the original comparator projection.
    projected = {}
    for row in o['rows']:
        key = tuple(row['key'])
        if key in projected or len(row['slots']) != 7 or len(row['raw_slots']) != 7:
            raise ValueError('invalid observation key/slots')
        values = []
        for value, raw in zip(row['slots'], row['raw_slots']):
            if (value is None) != (raw == 0):
                raise ValueError('observation null/raw mismatch')
            values.append('0' if value is None else value)
        projected[key] = tuple(values)
    if rows != projected or len(rows) != 3211:
        raise ValueError('dataset/observation disagreement')
    output.mkdir(parents=True, exist_ok=True)
    stem = 'SRR-017-2026-11-18'
    archive = output / (stem + '-original-evidence.zip')
    # Only original capture outputs are replay inputs. The directory's later
    # dossier-before.md/offline-summary.json are editorial derivatives.
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, data in sorted(originals.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 11, 18, 5, 13, 34))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data, compresslevel=9)
    with zipfile.ZipFile(archive) as z:
        if sorted(z.namelist()) != sorted(originals):
            raise ValueError('archive members differ')
        for name, data in originals.items():
            if z.read(name) != data:
                raise ValueError('archive restoration differs: ' + name)
    members = [{'name': name, 'bytes': len(data), 'sha256': digest(data)}
               for name, data in sorted(originals.items())]
    archive_info = {'schema': 'srr018-original-archive-v1', 'source_directory': str(source.resolve()),
                    'provenance': 'New archive from verified local originals, not the deleted upload ZIP',
                    'members': members, 'archive': archive.name, 'bytes': archive.stat().st_size,
                    'sha256': digest(archive.read_bytes()), 'restored_members_byte_equal': True,
                    'excluded_editorial_derivatives': ['dossier-before.md', 'offline-summary.json']}
    write_json(output / (stem + '-original-evidence.manifest.json'), archive_info)
    text = io.StringIO(newline='')
    writer = csv.writer(text, lineterminator='\n')
    writer.writerow(HEADER)
    for key, values in sorted(rows.items()):
        writer.writerow((*key, *values))
    compact = output / (stem + '-biome-slots.csv')
    compact.write_bytes(text.getvalue().encode('utf-8'))
    with compact.open(encoding='utf-8', newline='') as stream:
        reader = csv.reader(stream)
        if next(reader) != HEADER:
            raise ValueError('CSV header mismatch')
        decoded = {}
        for line in reader:
            key = tuple(line[:2])
            if key in decoded or len(line) != 9:
                raise ValueError('CSV duplicate or width mismatch')
            decoded[key] = tuple(line[2:])
    if decoded != rows:
        raise ValueError('CSV is not lossless')
    compact_info = {'schema': 'srr018-biome-slots-v1', 'file': compact.name,
                    'bytes': compact.stat().st_size, 'sha256': digest(compact.read_bytes()),
                    'columns': HEADER, 'ordering': 'lexicographic canonical PNDT, BIOM key; lane ordinal 0..6',
                    'identity': 'lowercase defining plugin:uppercase six-digit local FormID',
                    'zero': 'literal 0 means observed native zero, never missing/unknown',
                    'rows': len(rows), 'slot_words': len(rows) * 7,
                    'nonzero_words': sum(v != '0' for values in rows.values() for v in values),
                    'all_zero_rows': [list(key) for key, values in rows.items() if set(values) == {'0'}],
                    'source_directory': str(source.resolve()), 'source_sha256': ANCHORS,
                    'checks': ['all keys/slots equal original dataset and observation', 'CSV readback exact'],
                    'scope': d['scope'], 'retail_sha256': d['retail_sha256'],
                    'limitations': 'Key/slot analysis only; acquisition qualification requires original sealed journal and pinned reader. No runtime addresses, seeds or RSGD applicability fields retained.'}
    write_json(output / (stem + '-biome-slots.manifest.json'), compact_info)
    # Recheck protected original content after all outputs.
    for name, expected in ANCHORS.items():
        if digest((source / name).read_bytes()) != expected:
            raise ValueError('original changed: ' + name)
    return {'archive': archive_info, 'compact': compact_info}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(preserve(args.source, args.output), indent=2))
