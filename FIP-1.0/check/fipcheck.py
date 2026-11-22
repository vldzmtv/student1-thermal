#!/usr/bin/env python3
# Shared helpers for the three selfchecks. Not a standalone test.
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
FIP = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(FIP, 'grid'))
import make_grid as G


class Report:
    def __init__(self):
        self.rows = []

    def chk(self, code, ok, msg=''):
        self.rows.append((code, 'PASS' if ok else 'FAIL', str(msg)))

    def finish(self):
        for c, s, m in self.rows:
            print('%-22s %-4s %s' % (c, s, m))
        ok = all(s == 'PASS' for _, s, _ in self.rows)
        print('')
        print('RESULT:', 'ACCEPTED' if ok else 'REJECTED')
        return ok


def load_meta(d):
    with open(os.path.join(d, 'meta.json'), encoding='utf-8') as f:
        return json.load(f)


def has_keys(m, keys):
    return all(k in m for k in keys)


def grid_matches(d, ref, tol=1.0e-7):
    g = pd.read_csv(os.path.join(d, 'grid_points.csv'))
    if len(g) != len(ref):
        return False, 'count %d != %d' % (len(g), len(ref))
    err = np.max(np.abs(g[['x_m', 'y_m', 'z_m']].values - ref))
    return bool(err < tol), 'max coord err %.2e' % err


def probes_ok(d, want):
    p = pd.read_csv(os.path.join(d, 'probes.csv'))
    got = sorted(p['probe_id'].unique())
    return got == sorted(want), str(got)


def fip_path(*parts):
    return os.path.join(FIP, *parts)
