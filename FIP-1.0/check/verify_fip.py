#!/usr/bin/env python3
# Integrity + unit tests of the pack itself. Run before distributing / after cloning.
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FIP = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(FIP, 'grid'))
sys.path.insert(0, os.path.join(FIP, 'scripts'))
import make_grid as G

ROWS = []


def chk(name, ok, msg=''):
    ROWS.append((name, 'PASS' if ok else 'FAIL', str(msg)))


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(65536), b''):
            h.update(b)
    return h.hexdigest()


SKIP_DIRS = {'__pycache__', 'thermal_input', 'out', '.git'}


def rebuild_manifest():
    man = {}
    for root, dirs, files in os.walk(FIP):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in sorted(files):
            if fn.endswith('.pyc') or fn == 'manifest.json':
                continue
            p = os.path.join(root, fn)
            rel = os.path.relpath(p, FIP).replace(os.sep, '/')
            man[rel] = sha(p)
    with open(os.path.join(FIP, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump({'fip_version': 'FIP-1.0', 'sha256': man}, f, indent=2)
    print('manifest rebuilt:', len(man), 'files')


def main():
    if '--rebuild-manifest' in sys.argv:
        rebuild_manifest()
        return 0

    Pp, sp = G.plate_P01()
    Pr, sr = G.ring_R01()
    chk('plate count', len(Pp) == 72900, len(Pp))
    chk('plate shape', sp == (81, 25, 36), sp)
    chk('ring count', len(Pr) == 37800, len(Pr))
    chk('ring shape', sr == (25, 72, 21), sr)
    chk('times s1', len(G.times_s1()) == 71, len(G.times_s1()))
    chk('times s2', len(G.times_s2()) == 56, len(G.times_s2()))
    chk('times ring', len(G.times_ring()) == 66, len(G.times_ring()))
    m2 = np.where(G.mask_pool(Pp, 'POOL2D'))[0]
    m3 = np.where(G.mask_pool(Pp, 'POOL3D'))[0]
    chk('mask 2D', len(m2) == 2015, len(m2))
    chk('mask 3D', len(m3) == 26195, len(m3))
    chk('mask subset', np.all(np.isin(m2, m3)))
    chk('plate z max', abs(Pp[:, 2].max() - 0.016) < 1e-9)
    chk('ring r range', abs(np.hypot(Pr[:, 0], Pr[:, 1]).min() - 0.275) < 1e-9)

    with open(os.path.join(FIP, 'material', 'steel_1045_v1.json'),
              encoding='utf-8') as f:
        st = json.load(f)
    need = ['solid', 'liquid', 'phase_change', 'surface_tension',
            'mechanical', 'transformation', 'composition_wt_percent']
    chk('steel card keys', all(k in st for k in need))
    a_s = st['solid']['level_A_constant']['alpha_m2_s']
    a_l = st['liquid']['alpha_m2_s']
    chk('alpha ratio 2.13', abs(a_s / a_l - 2.13) < 0.02, '%.3f' % (a_s / a_l))
    nu, Pr_l = st['liquid']['nu_m2_s'], st['liquid']['Pr']
    chk('nu/Pr = alpha_l', abs(nu / Pr_l - a_l) / a_l < 0.01)

    try:
        import stefan
        lam = stefan.lam(1873.0)
        chk('stefan lambda', abs(lam - 0.397) < 0.005, '%.4f' % lam)
        chk('stefan front 1s', abs(stefan.front(1.0) * 1e3 - 1.96) < 0.05,
            '%.3f mm' % (stefan.front(1.0) * 1e3))
    except Exception as e:
        chk('stefan', False, e)

    try:
        import saho
        d20 = saho.dsdT(1743.0, 0.002)
        d60 = saho.dsdT(1743.0, 0.006)
        chk('sahoo sign 20ppm', d20 < 0, '%+.2e' % d20)
        chk('sahoo sign 60ppm', d60 > 0, '%+.2e' % d60)
    except Exception as e:
        chk('sahoo', False, e)

    try:
        import km
        fm = km.martensite(np.array([1200.0]), np.array([293.15]))[0]
        chk('km full martensite', 0.9 < fm <= 1.0, '%.3f' % fm)
        ce, ms = km.ce_and_ms(st['composition_wt_percent'])
        chk('CE 0.628', abs(ce - 0.6283) < 0.002, '%.4f' % ce)
        chk('Ms 322 C', abs(ms - 321.9) < 1.0, '%.1f C' % ms)
    except Exception as e:
        chk('km', False, e)

    try:
        import ovality
        phi = np.linspace(0, 2 * np.pi, 720, endpoint=False)
        A = 3.0e-5
        h = ovality.harmonics(phi, A * np.cos(2 * phi))
        chk('ovality unit test', abs(h['ovality_m'] - 4 * A) < 1e-9,
            '%.3e vs %.3e' % (h['ovality_m'], 4 * A))
    except Exception as e:
        chk('ovality', False, e)

    mp = os.path.join(FIP, 'manifest.json')
    if os.path.exists(mp):
        with open(mp, encoding='utf-8') as f:
            man = json.load(f)['sha256']
        bad = [k for k, v in man.items()
               if not os.path.exists(os.path.join(FIP, k))
               or sha(os.path.join(FIP, k)) != v]
        chk('manifest integrity', not bad, bad[:5])
    else:
        chk('manifest present', False, 'run --rebuild-manifest')

    for n, s, m in ROWS:
        print('%-24s %-4s %s' % (n, s, m))
    ok = all(s == 'PASS' for _, s, _ in ROWS)
    print('')
    print('FIP RESULT:', 'OK' if ok else 'BROKEN')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
