#!/usr/bin/env python3
# Week-8 composition: inside POOL mask use S2, outside use S1.
# Time: linear interpolation of S2 onto S1 canonical times; beyond S2 t_end use S1.
#   compose_thermal.py --s1 <dir> --s2 <dir> --out <dir>
import argparse
import json
import os
import shutil

import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--s1', required=True)
    ap.add_argument('--s2', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    z1 = np.load(os.path.join(a.s1, 'grid_T.npz'))
    z2 = np.load(os.path.join(a.s2, 'grid_T.npz'))
    t1, T1 = z1['times_s'], z1['T_K'].astype('float64')
    t2, T2 = z2['times_s'], z2['T_K'].astype('float64')
    ids = z2['point_id']
    n_over = 0
    for k, t in enumerate(t1):
        if t2[0] <= t <= t2[-1]:
            T1[k, ids] = np.array([np.interp(t, t2, T2[:, j])
                                   for j in range(len(ids))])
            n_over += 1
    np.savez_compressed(os.path.join(a.out, 'grid_T.npz'),
                        times_s=t1, T_K=T1.astype('float32'))
    shutil.copy(os.path.join(a.s1, 'grid_points.csv'),
                os.path.join(a.out, 'grid_points.csv'))
    for name in ('grid_mask.csv',):
        p = os.path.join(a.s2, name)
        if os.path.exists(p):
            shutil.copy(p, os.path.join(a.out, name))
    meta = {'schema_version': '2.0.0', 'source': 'composed',
            'thermal_source': 'composed', 'units': 'SI',
            'rule': 'inside POOL mask -> S2, outside -> S1; linear time interpolation',
            's1_run': os.path.basename(a.s1.rstrip('/')),
            's2_run': os.path.basename(a.s2.rstrip('/')),
            'n_times': int(len(t1)), 'grid_points': int(T1.shape[1]),
            'overwritten_times': n_over, 'mask_points': int(len(ids))}
    with open(os.path.join(a.out, 'meta.json'), 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print('composed:', T1.shape, 'overwritten times:', n_over,
          'mask points:', len(ids))


if __name__ == '__main__':
    main()
