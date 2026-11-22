PY ?= python3

verify:
	$(PY) check/verify_fip.py

grid:
	$(PY) grid/make_grid.py P01
	$(PY) grid/make_grid.py R01
	$(PY) grid/make_grid.py mask POOL2D
	$(PY) grid/make_grid.py mask POOL3D

fixture:
	$(PY) thermal/make_thermal_ref.py P01 --out thermal_input/stage1_fixture_P01
	$(PY) thermal/make_thermal_ref.py R01 --out thermal_input/stage1_fixture_R01

manifest:
	$(PY) check/verify_fip.py --rebuild-manifest

all: verify grid fixture
