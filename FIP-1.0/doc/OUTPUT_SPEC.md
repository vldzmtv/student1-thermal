# OUTPUT_SPEC -- the contract (identical for S1, S2, S3)

## 1 Units and frames
SI everywhere: m, s, K, kg, W, Pa. Key/column names carry units.
frame = plate_v1 (origin at bottom-face corner, z up, irradiated face z = 0.016)
frame = part_axis_v1 (origin on axis at bottom face, z along axis, phi = atan2(y,x))
t = 0 is laser ON of the first track. Preheat is an initial state, not "time zero".
u_r > 0 is outward from the axis. For bore cladding it REDUCES the remaining layer.

## 2 run_id
^s[123]-(p01|r01)-[a-z0-9]+-m[0-9]{2}-v[0-9]+$
New material card, regime or mesh -> NEW run_id. Old runs are never deleted.

## 3 Pack contents
S1: meta.json probes.csv grid_points.csv grid_T.npz metrics.csv checksums.sha256 README.md fields/ figures/ selfcheck.log
S2: + grid_mask.csv, metrics_pool.csv, npz also carries point_id and liquidFraction
S3: grid_U.npz final_fields.npz metrics_mech.csv probes.csv

## 4 Canonical grids / times / masks
G-P01 = 72900 points (81 x 25 x 36), C-order, x slow, z fast
G-R01 = 37800 points (25 x 72 x 21), C-order, r slow, z fast
times S1 = 71, S2 = 56 (prefix allowed, >= 51), S3-ring = 66
POOL2D = 2015 points, POOL3D = 26195 points
Generated ONLY by grid/make_grid.py. Editing them breaks cross-module assembly.

## 5 NPZ keys
thermal: times_s (nt,), T_K (nt,np) float32 [KELVIN]
pool:    + point_id (np,), liquidFraction (nt,np)
mech:    times_s, u_m (nt,np,3), sigmaEq_Pa (nt,np); final_fields.npz: epsPlEq, f_M, HV, sigma1_Pa

## 6 Composition rule (week 8, no negotiation)
Inside POOL mask -> S2. Outside -> S1. Time: linear interpolation of S2 onto S1
times; beyond S2 t_end -> S1 (pool already solidified). Script: thermal/compose_thermal.py

## 7 Definition of Done
schema-valid meta; range checks pass; verification numbers filled; checksums;
one-command README; git commit + tag recorded; selfcheck all PASS.
S3 additionally: engineering conclusions only with thermal_source != fixture,
and comparison with tolerance only in state = machined at 293.15 K.

## 8 Rejection
Open an issue naming the failed check code, actual and expected numbers.
Fix within 3 working days or justify in writing. Silent fixes are forbidden.
