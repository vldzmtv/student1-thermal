#!/usr/bin/env python3
# Analytic FIXTURE in canonical slot format. INTERFACE TESTING ONLY.
# Not physics. Engineering conclusions must use own_cfd or composed data.
#   make_thermal_ref.py P01|R01 --out <dir>
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'grid'))
import make_grid as G

LAM = 48.0
RHO = 7850.0
CP = 470.0
ALPHA = LAM / (RHO * CP)
ETA = 0.35
P_W = 1200.0
V = 0.010
T0 = 423.15
TAMB = 293.15
TM = 1743.15
CAP = 1.2 * (TM - T0)
TAU_C = {'P01': 0.5, 'R01': 25.0}
T_OFF = {'P01': 2.0, 'R01': 14.4}


def rosenthal_dT(xi, y, depth):
    R = np.sqrt(xi ** 2 + y ** 2 + depth ** 2)
    R = np.maximum(R, 1.0e-6)
    dT = ETA * P_W / (2.0 * np.pi * LAM * R) * np.exp(-V * (R + xi) / (2.0 * ALPHA))
    return np.minimum(dT, CAP)


def field_plate(pts, t):
    x, y, z = pts[:, 0], pts[:, 1], pts[:, 2]
    ts = min(t, T_OFF['P01'])
    xs = 0.010 + V * ts
    dT = rosenthal_dT(x - xs, y, 0.016 - z)
    if t <= T_OFF['P01']:
        return T0 + dT
    return TAMB + (T0 + dT - TAMB) * np.exp(-(t - T_OFF['P01']) / TAU_C['P01'])


def field_ring(pts, t):
    r = np.hypot(pts[:, 0], pts[:, 1])
    phi = np.arctan2(pts[:, 1], pts[:, 0])
    z = pts[:, 2]
    ts = min(t, T_OFF['R01'])
    omega = V / 0.275
    dphi = phi - omega * ts
    dphi = (dphi + np.pi) % (2.0 * np.pi) - np.pi
    xi = 0.275 * dphi
    dT = rosenthal_dT(xi, z - 0.020, r - 0.275)
    if t <= T_OFF['R01']:
        return T0 + dT
    return TAMB + (T0 + dT - TAMB) * np.exp(-(t - T_OFF['R01']) / TAU_C['R01'])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('case', choices=['P01', 'R01'])
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    if a.case == 'P01':
        pts, _ = G.plate_P01()
        times = G.times_s1()
        fun = field_plate
        gid, frame = 'G-P01', 'plate_v1'
        G.write_csv(pts, os.path.join(a.out, 'grid_points.csv'))
    else:
        pts, _ = G.ring_R01()
        times = G.times_ring()
        fun = field_ring
        gid, frame = 'G-R01', 'part_axis_v1'
        G.write_csv(pts, os.path.join(a.out, 'grid_points.csv'))
    T = np.empty((len(times), len(pts)), dtype='float32')
    for i, t in enumerate(times):
        T[i, :] = fun(pts, float(t)).astype('float32')
    np.savez_compressed(os.path.join(a.out, 'grid_T.npz'),
                        times_s=times, T_K=T)
    meta = {
        'schema_version': '2.0.0',
        'source': 'fixture',
        'thermal_source': 'fixture',
        'generator': 'FIP-1.0/thermal/make_thermal_ref.py',
        'case_id': a.case, 'grid_id': gid, 'frame': frame, 'units': 'SI',
        'grid_points': int(len(pts)), 'n_times': int(len(times)),
        'T_ref_K': T0, 'ambient_K': TAMB, 'preheat_K': T0,
        'cap_K_above_preheat': CAP, 'tau_cool_s': TAU_C[a.case],
        't_off_s': T_OFF[a.case],
        'symmetry_factor': 2.0 if a.case == 'P01' else 1.0,
        'WARNING': 'analytic fixture for interface testing only, NOT physics; engineering conclusions forbidden on this data'
    }
    with open(os.path.join(a.out, 'meta.json'), 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(a.case, 'fixture:', T.shape, 'T range %.1f..%.1f K' % (T.min(), T.max()),
          'final max %.2f K' % T[-1].max())


if __name__ == '__main__':
    main()
