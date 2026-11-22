#!/usr/bin/env python3
# Usage: python3 FIP-1.0/check/selfcheck_s2.py out/s2-p01-base-m02-v1
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fipcheck import Report, load_meta, has_keys, grid_matches, probes_ok
import make_grid as G


def run(d):
    r = Report()
    need = ['meta.json', 'probes.csv', 'grid_points.csv', 'grid_mask.csv',
            'grid_T.npz', 'metrics_pool.csv', 'checksums.sha256', 'README.md']
    r.chk('C1 files', all(os.path.exists(os.path.join(d, f)) for f in need))
    m = load_meta(d)
    req = ['run_id', 'fip_version', 'material_id', 'frame', 'units', 'grid_id',
           'grid_mode', 'grid_points', 'n_times', 'slab_thickness_m',
           'regime', 'physics', 'verification', 'solver', 'mesh', 'time']
    r.chk('C2 meta', has_keys(m, req))
    r.chk('C3 units/frame', m.get('units') == 'SI' and m.get('frame') == 'plate_v1')
    r.chk('C4 material', m.get('material_id') == 'steel_1045_v1')

    P, _ = G.plate_P01()
    ok, msg = grid_matches(d, P)
    r.chk('C5 grid', ok, msg)
    ids = np.where(G.mask_pool(P, m['grid_mode']))[0]
    gm = pd.read_csv(os.path.join(d, 'grid_mask.csv'))
    r.chk('C6 mask', np.array_equal(gm['point_id'].values, ids), str(len(ids)))

    z = np.load(os.path.join(d, 'grid_T.npz'))
    tt, T, fl = z['times_s'], z['T_K'], z['liquidFraction']
    ct = G.times_s2()
    r.chk('C7 times', len(tt) >= 51 and
          np.allclose(np.round(tt, 4), ct[:len(tt)], atol=1.0e-6), str(len(tt)))
    r.chk('C8 shape', T.shape == (len(tt), len(ids)) and fl.shape == T.shape,
          str(T.shape))
    r.chk('C9 no NaN', not (np.isnan(T).any() or np.isnan(fl).any()))
    r.chk('C10 T range', bool(T.min() > 250 and T.max() < 3300),
          '%.0f..%.0f K' % (T.min(), T.max()))
    r.chk('C11 fl range', bool(fl.min() >= 0 and fl.max() <= 1))
    r.chk('C12 solidified', float(fl[-1].max()) == 0.0,
          'max fl = %.3g' % fl[-1].max())

    want = ['P01', 'P02', 'P03', 'P04', 'P05', 'P06', 'P07', 'P09', 'P10']
    ok, msg = probes_ok(d, want)
    r.chk('C13 probes', ok, msg)
    v = m['verification']
    r.chk('C14 stefan', v.get('stefan_front_rel_err', 9) < 0.03)
    r.chk('C15 gallium', v.get('gallium_front_rel_err', 9) < 0.10)
    r.chk('C16 energy', v.get('energy_balance_rel_err', 9) < 0.03)
    r.chk('C17 solid u', v.get('solid_velocity_max_m_s', 9) < 1.0e-6)
    r.chk('C18 sign', v.get('marangoni_sign_ok') is True)
    r.chk('C19 dz', v.get('dz_equivalence_rel_err', 9) < 0.05)
    r.chk('C20 mesh', v.get('mesh_convergence_rel_err', 9) < 0.05)
    r.chk('C21 status', v.get('status') == 'verified')
    return r.finish()


if __name__ == '__main__':
    sys.exit(0 if run(sys.argv[1]) else 1)
