#!/usr/bin/env python3
# CANONICAL generator. DO NOT EDIT. Identical for S1, S2, S3.
# Usage:
#   make_grid.py P01 | R01
#   make_grid.py mask POOL2D | POOL3D
import sys
import numpy as np
import pandas as pd

TOL = 1.0e-9


def plate_P01():
    x = np.arange(0.0, 0.0400001, 0.0005)
    y = np.arange(0.0, 0.0120001, 0.0005)
    z = np.concatenate([np.arange(0.0, 0.0100, 0.002),
                        np.arange(0.010, 0.0160001, 0.0002)])
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
    P = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()])
    return P, (len(x), len(y), len(z))


def ring_R01():
    r = np.arange(0.275, 0.2810001, 0.00025)
    phi = np.deg2rad(np.arange(0.0, 355.0001, 5.0))
    z = np.arange(0.0, 0.0400001, 0.002)
    R, PHI, Z = np.meshgrid(r, phi, z, indexing='ij')
    P = np.column_stack([(R * np.cos(PHI)).ravel(),
                         (R * np.sin(PHI)).ravel(), Z.ravel()])
    return P, (len(r), len(phi), len(z))


def times_s1():
    t = np.concatenate([np.arange(0.0, 2.0001, 0.05),
                        np.arange(2.1, 3.0001, 0.10),
                        np.arange(3.5, 6.0001, 0.50),
                        np.arange(7.0, 20.0001, 1.00)])
    return np.round(t, 4)


def times_s2():
    t = np.concatenate([np.arange(0.0, 2.0001, 0.05),
                        np.arange(2.1, 3.0001, 0.10),
                        np.arange(3.2, 4.0001, 0.20)])
    return np.round(t, 4)


def times_ring():
    t = np.concatenate([np.arange(0.0, 15.0001, 0.5),
                        np.arange(16.0, 30.0001, 1.0),
                        np.arange(35.0, 60.0001, 5.0),
                        np.arange(70.0, 200.0001, 10.0)])
    return np.round(t, 4)


def mask_pool(P, mode='POOL2D'):
    x, y, z = P[:, 0], P[:, 1], P[:, 2]
    b = ((x >= 0.004 - TOL) & (x <= 0.036 + TOL) &
         (y <= 0.006 + TOL) & (z >= 0.010 - TOL))
    if mode == 'POOL2D':
        b &= (np.abs(y) <= TOL)
    return b


def write_points(P, path):
    with open(path, 'w') as f:
        f.write('%d\n(\n' % len(P))
        for p in P:
            f.write('(%.7f %.7f %.7f)\n' % (p[0], p[1], p[2]))
        f.write(')\n')


def write_csv(P, path):
    df = pd.DataFrame(P, columns=['x_m', 'y_m', 'z_m'])
    df.insert(0, 'point_id', np.arange(len(df)))
    df.to_csv(path, index=False, float_format='%.7f')


def main():
    if len(sys.argv) < 2:
        print(__doc__ if __doc__ else 'see header')
        print('usage: make_grid.py P01|R01 | mask POOL2D|POOL3D')
        return 1
    if sys.argv[1] == 'mask':
        mode = sys.argv[2] if len(sys.argv) > 2 else 'POOL2D'
        P, _ = plate_P01()
        ids = np.where(mask_pool(P, mode))[0]
        df = pd.DataFrame({'point_id': ids, 'x_m': P[ids, 0],
                           'y_m': P[ids, 1], 'z_m': P[ids, 2]})
        df.to_csv('mask_%s.csv' % mode, index=False, float_format='%.7f')
        write_points(P[ids], 'points_mask_%s' % mode)
        print(mode, 'points:', len(ids))
        return 0
    which = sys.argv[1]
    if which == 'P01':
        P, shape = plate_P01()
        write_csv(P, 'grid_P01_points.csv')
        write_points(P, 'points_P01')
        np.savetxt('times_s1.csv', times_s1(), fmt='%.4f',
                   header='time_s', comments='')
        np.savetxt('times_s2.csv', times_s2(), fmt='%.4f',
                   header='time_s', comments='')
    elif which == 'R01':
        P, shape = ring_R01()
        write_csv(P, 'grid_R01_points.csv')
        write_points(P, 'points_R01')
        np.savetxt('times_ring.csv', times_ring(), fmt='%.4f',
                   header='time_s', comments='')
    else:
        print('unknown argument:', which)
        return 1
    print(which, 'points:', len(P), 'shape:', shape)
    return 0


if __name__ == '__main__':
    sys.exit(main())
