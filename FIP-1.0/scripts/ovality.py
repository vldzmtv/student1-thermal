#!/usr/bin/env python3
# Bore roundness harmonics. u_r(phi) = a0 + sum(an cos n phi + bn sin n phi)
# ovality = D_max - D_min = 4*sqrt(a2^2+b2^2)
import numpy as np


def harmonics(phi, ur, n_harm=6):
    phi = np.asarray(phi, dtype=float)
    ur = np.asarray(ur, dtype=float)
    cols = [np.ones(phi.size)]
    for n in range(1, n_harm + 1):
        cols.append(np.cos(n * phi))
        cols.append(np.sin(n * phi))
    A = np.column_stack(cols)
    c, *_ = np.linalg.lstsq(A, ur, rcond=None)
    out = {'dD_mean_m': 2.0 * c[0],
           'ecc_m': 2.0 * float(np.hypot(c[1], c[2]))}
    for n in range(2, n_harm + 1):
        out['A%d_m' % n] = 2.0 * float(np.hypot(c[2 * n - 1], c[2 * n]))
    out['ovality_m'] = 2.0 * out['A2_m']
    out['coeffs'] = c.tolist()
    return out


def from_vtk(vtk_file, z_target, n_harm=6, z_tol=0.5e-3):
    import pyvista as pv
    m = pv.read(vtk_file)
    p = m.points
    d = m.point_data['D']
    sel = np.abs(p[:, 2] - z_target) < z_tol
    phi = np.arctan2(p[sel, 1], p[sel, 0])
    ur = d[sel, 0] * np.cos(phi) + d[sel, 1] * np.sin(phi)
    return harmonics(phi, ur, n_harm)


def unit_test():
    phi = np.linspace(0, 2 * np.pi, 720, endpoint=False)
    A = 3.0e-5
    h = harmonics(phi, A * np.cos(2 * phi))
    ok = abs(h['ovality_m'] - 4 * A) < 1e-12
    print('unit test ovality: %.3e expected %.3e -> %s'
          % (h['ovality_m'], 4 * A, 'PASS' if ok else 'FAIL'))
    return ok


if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        sys.exit(0 if unit_test() else 1)
    print(from_vtk(sys.argv[1], float(sys.argv[2])))
