# ASSUMPTIONS -- what is model, what is open, what is forbidden

## Forbidden
Customer drawings, process sheets, measurement reports, material certificates,
enterprise reports. Do not request them, do not cite them, do not store them.
If a number is missing: take the FIP value and run a sensitivity study.

## Model (synthetic) by construction
Geometry P01 (40x24x16 plate) and R01 (bore 550 / outer 582, H 40).
Regimes REG-01 / REG-02 / REG-SERIES. Tolerance class IT7 on a MODEL bore 550 H7.
Undercut 0.5 mm per side, t_min 0.2 mm, h_clad 0.8 mm (sensitivity 0.6/0.8/1.0).
Absorptivity 0.35 (open range for steel 0.30-0.50). Spot convention 1/e2, d = 2w.

## Open literature, to be verified by each student (criterion A0)
lambda(T), cp(T) of steel 45 / AISI 1045; CCT diagrams; Andrews Ms;
Koistinen-Marburger alpha = 0.011 1/K; Sahoo Fe-S coefficients;
gallium benchmark properties; ISO 286 IT grades.
Deliver a table: parameter | FIP value | literature value | source | deviation.
Deviation > 20 percent -> written question to the supervisor, but COMPUTE ON FIP.

## Known model limitations (must be discussed in every report)
1. Sahoo coefficients are for pure Fe-S; oxygen is a second surfactant.
   Model reversal threshold lands near 20-30 ppm, literature for real steels
   quotes ~50-60 ppm. Explain, do not "fix".
2. Boussinesq with constant nu/Pr gives the same alpha in solid and liquid;
   alpha_s/alpha_l = 2.13 for this steel. Level A accepts the error, level B fixes it.
3. 2D pool: transverse flow absent, W is not measurable; only L and D are valid.
4. Rigid lid: no free-surface deformation, no keyhole, no evaporation.
5. Level A mechanics: clad layer not modeled geometrically; elasticity is
   path-independent, so per-snapshot static solves are legitimate; plasticity is not.
6. The analytic thermal fixture is a TEST STAND. Its Rosenthal peak is capped and
   its cooling is a single exponential. No engineering conclusion may rely on it.

## Composition of the model clad
316L-type austenitic steel: no martensite, alpha ~ 16.5e-6 vs 11.5e-6 of the
substrate. The mismatch is intentional and is part of the exercise.
