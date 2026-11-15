# SPDX-License-Identifier: GPL-3.0-or-later
"""Prospective save classes from the pinned native filename grammar/designations.

Reads names, optional explicit classifications and immutable inventory rows.
No header save-kind claim, target operation, restoration or source write.
"""

import sys

# Safety checks below require assertions, including when imported as a helper.
if not __debug__ or sys.flags.optimize != 0:
    raise RuntimeError('Python optimization is forbidden; invoke with -E -B and no -O/-OO')
import datetime
import hashlib
import json
import re

NAME = re.compile(
    r'(?P<kind>Save|Autosave|Exitsave|Quicksave)(?P<slot>0|[1-9][0-9]*)_'
    r'(?P<profile>[0-9A-F]{8})(?P<flags>SM|S|M|_)(?P<character>(?:[0-9A-F]{2})+)_'
    r'(?P<elapsed>[0-9]{6,})_(?P<utc>[0-9]{14})_'
    r'(?P<level>0|[1-9][0-9]*)_(?P<counter>0|[1-9][0-9]*)_4\.sfs', re.IGNORECASE)
KINDS = {'save': 'MANUAL', 'autosave': 'AUTO', 'exitsave': 'EXIT', 'quicksave': 'QUICK'}


def policy_hash(policy):
    return hashlib.sha256(json.dumps(policy, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def classify(name, policy):
    """Explicit research designation wins; unsupported names stay unclassified."""
    if '/' in name or chr(92) in name or ':' in name:
        return dict(kind='UNKNOWN', protection='UNCLASSIFIED', basis='NESTED_OR_NONBASENAME')
    folded = name.casefold()
    designated = {n.casefold(): v for n, v in policy['designated'].items()}
    if folded in designated:
        assert designated[folded]['evidence'].strip(), 'Research designation requires provenance'
        return dict(kind='DESIGNATED', protection='PROTECTED', basis='EXPLICIT_RESEARCH_DESIGNATION')
    kinds = {n.casefold(): v for n, v in policy['classified'].items()}
    if folded in kinds:
        entry = kinds[folded]
        assert entry['evidence'].strip() and entry['kind'] in ('MANUAL', 'AUTO', 'EXIT', 'QUICK')
        kind = entry['kind']
        basis = 'EXPLICIT_MAINTAINER_CLASSIFICATION'
    else:
        match = NAME.fullmatch(name)
        if not match:
            return dict(kind='UNKNOWN', protection='UNCLASSIFIED', basis='UNSUPPORTED_NAME')
        try:
            kind = KINDS[match['kind'].lower()]
            assert 0 not in bytes.fromhex(match['character'])
            elapsed = match['elapsed']
            assert f'{int(elapsed[:-4]):02d}' == elapsed[:-4]
            assert int(elapsed[:-4]) <= 0xffffffff
            assert int(elapsed[-4:-2]) < 24 and int(elapsed[-2:]) < 60
            assert int(match['slot']) <= 0xffffffff and int(match['counter']) <= 0xffffffff
            assert int(match['level']) <= 0xffff
            if kind in ('QUICK', 'EXIT'):
                assert match['slot'] == '0'
            datetime.datetime.strptime(match['utc'], '%Y%m%d%H%M%S')
        except (AssertionError, ValueError):
            return dict(kind='UNKNOWN', protection='UNCLASSIFIED', basis='INVALID_NATIVE_FIELDS')
        basis = 'NATIVE_FULL_FILENAME_GRAMMAR_1.16.244.0'
    return dict(kind=kind, protection='TRANSIENT' if kind in ('AUTO', 'EXIT') else 'PROTECTED', basis=basis)
