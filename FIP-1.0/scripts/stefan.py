#!/usr/bin/env python3
# One-phase melting analytic solution (Neumann) with steel_1045 liquid properties.
import numpy as np
from scipy.special import erf
from scipy.optimize import brentq

AL_L = 6.122e-6
CL = 700.0
L = 2.6e5
TM = 1743.0


def lam(Tw=1873.0):
    Ste = CL * (Tw - TM) / L
    f = lambda x: x * np.exp(x * x) * erf(x) - Ste / np.sqrt(np.pi)
    return brentq(f, 1.0e-6, 3.0)


def front(t, Tw=1873.0):
    return 2.0 * lam(Tw) * np.sqrt(AL_L * np.asarray(t, dtype=float))


def profile(x, t, Tw=1873.0):
    lm = lam(Tw)
    x = np.asarray(x, dtype=float)
    return Tw - (Tw - TM) * erf(x / (2.0 * np.sqrt(AL_L * t))) / erf(lm)


if __name__ == '__main__':
    print('Ste = %.4f   lambda = %.4f' % (CL * (1873.0 - TM) / L, lam()))
    for t in (0.1, 0.25, 0.5, 1.0):
        print('t = %.2f s   front = %.4f mm' % (t, front(t) * 1e3))
