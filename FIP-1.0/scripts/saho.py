#!/usr/bin/env python3
# Sahoo-DebRoy-McNallan surface tension, Fe-S. Coefficients: see material card.
import numpy as np

R = 8314.4
SIG_M = 1.943
A = 4.3e-4
GAMMA = 1.3e-8
K1 = 3.18e-3
DH0 = -1.66e8
TM = 1743.0


def K(T):
    return K1 * np.exp(-DH0 / (R * np.asarray(T, dtype=float)))


def sigma(T, aS):
    T = np.asarray(T, dtype=float)
    return SIG_M - A * (T - TM) - R * T * GAMMA * np.log(1.0 + K(T) * aS)


def dsdT(T, aS):
    T = np.asarray(T, dtype=float)
    k = K(T)
    return (-A - R * GAMMA * np.log(1.0 + k * aS)
            - GAMMA * aS * k * DH0 / (T * (1.0 + k * aS)))


def reversal_T(aS, Tlo=TM, Thi=TM + 900.0, n=2000):
    T = np.linspace(Tlo, Thi, n)
    d = dsdT(T, aS)
    idx = np.where(np.diff(np.sign(d)))[0]
    return float(T[idx[0]]) if idx.size else float('nan')


if __name__ == '__main__':
    for aS in (0.002, 0.006, 0.015, 0.025, 0.030):
        print('S = %.3f wt%%  dsdT(Tm) = %+.3e  reversal T = %.0f K'
              % (aS, dsdT(TM, aS), reversal_T(aS)))
