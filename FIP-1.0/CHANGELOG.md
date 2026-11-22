# CHANGELOG

## FIP-1.0 (initial frozen release)
- Material unified: steel_1045_v1 for all three modules. No cast iron anywhere.
- Canonical grids fixed: G-P01 = 72900 points, G-R01 = 37800 points.
- Canonical times fixed: S1 = 71, S2 = 56, S3-ring = 66.
- POOL masks fixed: POOL2D = 2015 points, POOL3D = 26195 points.
- Two deliberate refinements vs the draft TZ texts (authoritative values are the files):
  1) ring fixture cooling time constant tau_c = 25.0 s (draft said 40 s).
     Rationale: with 40 s the fixture does not reach ambient by t_end = 200 s,
     which breaks the "cooled to ambient" interface check. 25 s gives T_final ~ 294.2 K.
  2) Ms declared as 595.15 K (322 degC). Andrews formula on the FIP composition
     gives 321.9 degC; the rounded declared value is used for reproducibility.
- Fixture peak is capped at 1.2*(Tm - T0) = 1584 K above preheat, i.e. T_max = 2007.15 K.
  The cap removes the Rosenthal singularity. The fixture is NOT physics.
