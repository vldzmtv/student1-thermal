#!/usr/bin/env python3
# Usage: python3 FIP-1.0/check/selfcheck_s1.py out/s1-p01-base-m02-v1
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fipcheck import Report, load_meta, has_keys, grid_matches, probes_ok
import make_grid as G


def run(d):
    r = Report()
    need = ['meta.json', 'probes.csv', 'grid_points.csv', 'grid_T.npz',
            'metrics.csv', 'checksums.sha256', 'README.md']
    r.chk('C1 files', all(os.path.exists(os.path.join(d, f)) for f in need))
    m = load_meta(d)
    req = ['run_id', 'fip_version', 'case_id', 'material_id', 'frame', 'units',
           'grid_id', 'grid_points', 'n_times', 'symmetry_factor', 'regime',
           'verification', 'solver', 'mesh', 'time']
    r.chk('C2 meta', has_keys(m, req))
    r.chk('C3 units/frame', m.get('units') == 'SI' and
          m.get('frame') in ('plate_v1', 'part_axis_v1'))
    r.chk('C4 material', m.get('material_id') == 'steel_1045_v1')

    if m.get('case_id') == 'R01':
        ref, _ = G.ring_R01()
        ct = G.times_ring()
    else:
        ref, _ = G.plate_P01()
        ct = G.times_s1()
    ok, msg = grid_matches(d, ref)
    r.chk('C5 grid', ok, msg)

    z = np.load(os.path.join(d, 'grid_T.npz'))
    tt, T = z['times_s'], z['T_K']
    r.chk('C6 shape', T.shape == (len(ct), len(ref)), str(T.shape))
    r.chk('C7 times', np.allclose(np.round(tt, 4), ct, atol=1.0e-6))
    r.chk('C8 no NaN', not np.isnan(T).any())
    r.chk('C9 T range', bool(T.min() > 250 and T.max() < 4000),
          '%.1f..%.1f K' % (T.min(), T.max()))
    r.chk('C10 cooled', float(T[-1].max()) <= m['regime']['ambient_K'] + 2.0,
          'final max %.2f K' % T[-1].max())

    ok, msg = probes_ok(d, ['P%02d' % i for i in range(1, 13)])
    r.chk('C11 probes', ok, msg)
    v = m['verification']
    r.chk('C13 cube', v.get('cube_slope_rel_err', 9) < 0.005)
    r.chk('C14 norm', v.get('source_norm_rel_err', 9) < 0.02)
    r.chk('C15 energy', v.get('energy_balance_rel_err', 9) < 0.03)
    r.chk('C16 mesh', v.get('mesh_convergence_rel_err', 9) < 0.03)
    r.chk('C17 status', v.get('status') == 'verified')
    return r.finish()


if __name__ == '__main__':
    sys.exit(0 if run(sys.argv[1]) else 1)
