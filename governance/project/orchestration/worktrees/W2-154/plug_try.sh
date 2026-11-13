set -u
P=$TMPDIR/proj; rm -rf $P; mkdir -p $P/tests/acceptance
cd $P
cat > tests/conftest.py <<'PY'
import pytest
def pytest_collection_modifyitems(config, items):
    left=[i for i in items if "ui_off" in i.nodeid and not config.getoption("--optin", default=None)]
    if left:
        items[:] = [i for i in items if i not in left]
        config.hook.pytest_deselected(items=left)
def pytest_addoption(parser):
    parser.addoption("--optin", action="store_true")
PY
printf 'def test_a():\n    pass\n' > tests/test_ui_off.py
printf 'def test_b():\n    pass\n' > tests/test_b.py
printf 'def test_c():\n    pass\n' > tests/test_c.py
PL=/home/usain/gov-os-worktrees/W2-154/src/gov/close/pytest_plugin
run() { env GOV_CLOSE_SERIAL_ONLY_OF=$P PYTHONPATH=$PL GOV_CLOSE_SERIAL_ONLY_OUT=$TMPDIR/out.txt "$@"; echo "exit=$?"; echo "out:"; cat $TMPDIR/out.txt; }
echo "== all out"; run env GOV_CLOSE_SERIAL_ONLY_GIVEN=tests/test_ui_off.py python3 -m pytest tests/test_ui_off.py -q -p no:cacheprovider -p gov_close_serial_only
echo "== one out one runs"; run env "GOV_CLOSE_SERIAL_ONLY_GIVEN=$(printf 'tests/test_ui_off.py\ntests/test_b.py')" python3 -m pytest tests/test_ui_off.py tests/test_b.py -q -p no:cacheprovider -p gov_close_serial_only
echo "== optin on"; run env GOV_CLOSE_SERIAL_ONLY_GIVEN=tests/test_ui_off.py python3 -m pytest tests/test_ui_off.py -q -p no:cacheprovider -p gov_close_serial_only --optin
echo "== no case"; printf 'def test_x():\n    pass\n' > tests/test_empty.py; sed -i 's/test_x/_x/' tests/test_empty.py
run env GOV_CLOSE_SERIAL_ONLY_GIVEN=tests/test_empty.py python3 -m pytest tests/test_empty.py -q -p no:cacheprovider -p gov_close_serial_only
