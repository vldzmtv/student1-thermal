#!/usr/bin/env python3
# Usage: python3 FIP-1.0/check/selfcheck_s3.py out/s3-r01-base-m02-v1
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fipcheck import Report, load_meta, has_keys, grid_matches
import make_grid as G


def run(d):
    r = Report()
    need = ['meta.json', 'grid_points.csv', 'grid_U.npz', 'final_fields.npz',
            'probes.csv', 'metrics_mech.csv', 'checksums.sha256', 'README.md']
    r.chk('C1 files', all(os.path.exists(os.path.join(d, f)) for f in need))
    m = load_meta(d)
    req = ['run_id', 'case_id', 'material_id', 'frame', 'units', 'grid_id',
           'grid_points', 'n_times', 'thermal_source', 'state', 'clamping',
           'physics', 'regime', 'stock', 'verification']
    r.chk('C2 meta', has_keys(m, req))
    r.chk('C3 units/frame', m.get('units') == 'SI' and
          m.get('frame') in ('plate_v1', 'part_axis_v1'))
    r.chk('C4 material', m.get('material_id') == 'steel_1045_v1')
    r.chk('C5 alpha type', m.get('physics', {}).get('alpha_type') == 'secant')

    ref, _ = G.ring_R01() if m.get('case_id') == 'R01' else G.plate_P01()
    ok, msg = grid_matches(d, ref)
    r.chk('C6 grid', ok, msg)

    z = np.load(os.path.join(d, 'grid_U.npz'))
    u, s = z['u_m'], z['sigmaEq_Pa']
    r.chk('C7 shape', u.shape == (m['n_times'], m['grid_points'], 3) and
          s.shape == (m['n_times'], m['grid_points']), str(u.shape))
    r.chk('C8 no NaN', not (np.isnan(u).any() or np.isnan(s).any()))
    r.chk('C9 u range', bool(np.abs(u).max() < 5.0e-3),
          '%.3e m' % np.abs(u).max())
    r.chk('C10 sigma range', bool(np.abs(s).max() < 3.0e9),
          '%.3e Pa' % np.abs(s).max())

    v = m['verification']
    r.chk('C11 bar', v.get('bar_rel_err', 9) < 0.01)
    r.chk('C12 bending', v.get('bending_rel_err', 9) < 0.02)
    r.chk('C13 ring', v.get('ring_rel_err', 9) < 0.03)
    r.chk('C14 free', v.get('free_rel_err', 9) < 0.01)
    r.chk('C15 mapping', v.get('mapping_roundtrip_rel_err', 9) < 0.02)
    r.chk('C16 mesh', v.get('mesh_convergence_rel_err', 9) < 0.05)
    r.chk('C17 ovality test', v.get('ovality_unit_test_ok') is True)
    r.chk('C18 status', v.get('status') == 'verified')

    mt = pd.read_csv(os.path.join(d, 'metrics_mech.csv'))
    r.chk('C19 K present', all(k in mt.columns for k in
                               ['K1', 'K2', 'K3', 'K4', 'K5', 'K6']))
    r.chk('C20 states', set(mt['state']) >= {'clamped', 'released'})
    if 'machined' in set(mt['state']):
        r.chk('C21 not fixture', m.get('thermal_source') != 'fixture')
    return r.finish()


if __name__ == '__main__':
    sys.exit(0 if run(sys.argv[1]) else 1)
