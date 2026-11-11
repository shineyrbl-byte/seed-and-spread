#!/usr/bin/env bash
# Bare-clone the 12 SWE-bench Lite test repositories (+6 dev repos with --dev) into cache/repos.
set -e
cd "$(dirname "$0")/.."
mkdir -p cache/repos
repos="django/django sympy/sympy matplotlib/matplotlib scikit-learn/scikit-learn pytest-dev/pytest sphinx-doc/sphinx astropy/astropy psf/requests pylint-dev/pylint pydata/xarray mwaskom/seaborn pallets/flask"
[ "$1" = "--dev" ] && repos="$repos sqlfluff/sqlfluff pvlib/pvlib-python pylint-dev/astroid pydicom/pydicom marshmallow-code/marshmallow pyvista/pyvista"
for r in $repos; do
  n=${r//\//__}
  [ -d "cache/repos/$n.git" ] || git clone -q --bare "https://github.com/$r.git" "cache/repos/$n.git" &
done
wait
