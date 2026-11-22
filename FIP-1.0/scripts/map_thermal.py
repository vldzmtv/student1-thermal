#!/usr/bin/env python3
# Canonical slot -> mechanical mesh. Rectilinear interpolators (fast, exact).
# Also: OpenFOAM scalar field reader/writer and round-trip check helper.
import numpy as np
import pandas as pd
from scipy.interpolate import RegularGridInterpolator

X = np.arange(0.0, 0.0400001, 0.0005)
Y = np.arange(0.0, 0.0120001, 0.0005)
ZP = np.concatenate([np.arange(0.0, 0.0100, 0.002),
                     np.arange(0.010, 0.0160001, 0.0002)])
RR = np.arange(0.275, 0.2810001, 0.00025)
PHI = np.deg2rad(np.arange(0.0, 355.0001, 5.0))
ZR = np.arange(0.0, 0.0400001, 0.002)


def load_slot(slot):
    z = np.load(slot + '/grid_T.npz')
    p = pd.read_csv(slot + '/grid_points.csv')
    return z['times_s'], z['T_K'], p


def plate_interp(Trow):
    return RegularGridInterpolator((X, Y, ZP),
                                   np.asarray(Trow).reshape(81, 25, 36),
                                   bounds_error=False, fill_value=None)


def ring_interp(Trow):
    A = np.asarray(Trow).reshape(25, 72, 21)
    A = np.concatenate([A, A[:1, :, :]], axis=1)
    phi_ext = np.append(PHI, 2 * np.pi)
    it = RegularGridInterpolator((RR, phi_ext, ZR), A,
                                 bounds_error=False, fill_value=None)

    def f(pts):
        pts = np.asarray(pts, dtype=float)
        r = np.hypot(pts[:, 0], pts[:, 1])
        p = np.mod(np.arctan2(pts[:, 1], pts[:, 0]), 2 * np.pi)
        return it(np.column_stack([r, p, pts[:, 2]]))
    return f


def read_of_scalar(path):
    txt = open(path, encoding='utf-8', errors='ignore').read()
    i = txt.index('internalField')
    j = txt.index('(', i)
    k = txt.index(')', j)
    head = txt[i:j].split()
    if 'uniform' in head:
        return float(txt[j + 1:k].strip().rstrip(';'))
    n = int(head[-1])
    v = np.fromstring(txt[j + 1:k].replace('\n', ' '), sep=' ')
    assert v.size == n, (v.size, n)
    return v


def write_of_scalar(path, vals, obj='T', dims='[0 0 0 1 0 0 0]',
                    boundaries=None):
    vals = np.asarray(vals, dtype=float)
    with open(path, 'w', encoding='utf-8') as f:
        f.write('FoamFile\n{\n version 2.0;\n format ascii;\n'
                ' class volScalarField;\n object %s;\n}\n' % obj)
        f.write('dimensions %s;\n\n' % dims)
        f.write('internalField nonuniform List<scalar>\n%d\n(\n' % vals.size)
        np.savetxt(f, vals, fmt='%.8g')
        f.write(')\n;\n\nboundaryField\n{\n')
        f.write(boundaries or '    ".*" { type zeroGradient; }\n')
        f.write('}\n')


def roundtrip_error(T_in, T_back):
    a = np.asarray(T_in, dtype=float)
    b = np.asarray(T_back, dtype=float)
    den = max(np.max(np.abs(a - 293.15)), 1.0)
    return float(np.max(np.abs(a - b)) / den)


if __name__ == '__main__':
    print('import this module; see TZ S3 section on the thermal slot')
