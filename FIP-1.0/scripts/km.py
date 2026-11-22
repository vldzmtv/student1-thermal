#!/usr/bin/env python3
# Phase fractions, hardness, carbon equivalent, Andrews Ms.
# Temperatures in KELVIN in all public functions except ce_and_ms (degC output).
import numpy as np

AC1_K = 1000.15
AC3_K = 1053.15
MS_K = 595.15
ALPHA_KM = 0.011
BETA_TR = 4.0e-3
HV_BASE = 230.0
HV_M = 630.0
TEMPER_LO_K = 773.15
TEMPER_FACTOR = 0.9


def austenite(T_peak_K):
    return np.clip((T_peak_K - AC1_K) / (AC3_K - AC1_K), 0.0, 1.0)


def martensite(T_peak_K, T_min_after_Ms_K):
    fg = austenite(np.asarray(T_peak_K, dtype=float))
    T = np.asarray(T_min_after_Ms_K, dtype=float)
    return fg * np.where(T < MS_K, 1.0 - np.exp(-ALPHA_KM * (MS_K - T)), 0.0)


def transformation_strain(f_M):
    return BETA_TR * np.asarray(f_M, dtype=float)


def hardness(f_M, T_peak_K):
    f = np.asarray(f_M, dtype=float)
    Tp = np.asarray(T_peak_K, dtype=float)
    hv = HV_BASE * (1.0 - f) + HV_M * f
    temper = np.where((Tp > TEMPER_LO_K) & (Tp < AC1_K), TEMPER_FACTOR, 1.0)
    return hv * temper


def ce_and_ms(comp_wt_percent):
    c = comp_wt_percent
    C, Mn = c['C'], c['Mn']
    Cr, Mo, V = c.get('Cr', 0), c.get('Mo', 0), c.get('V', 0)
    Ni, Cu = c.get('Ni', 0), c.get('Cu', 0)
    ce = C + Mn / 6.0 + (Cr + Mo + V) / 5.0 + (Ni + Cu) / 15.0
    ms = 539.0 - 423.0 * C - 30.4 * Mn - 17.7 * Ni - 12.1 * Cr - 7.5 * Mo
    return ce, ms


if __name__ == '__main__':
    import json
    import os
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     '..', 'material', 'steel_1045_v1.json')
    with open(p, encoding='utf-8') as f:
        st = json.load(f)
    ce, ms = ce_and_ms(st['composition_wt_percent'])
    print('CE_IIW = %.4f   Ms_Andrews = %.1f degC' % (ce, ms))
    for Tp in (900.0, 1053.15, 1200.0):
        fm = martensite(np.array([Tp]), np.array([293.15]))[0]
        print('T_peak = %7.1f K -> f_M = %.3f  HV = %.0f'
              % (Tp, fm, hardness(fm, Tp)))
