pip -q install coveralls
if [ ! -d "../scidash" ]; then
  git clone -b cosmosuite http://github.com/scidash/scidash ../scidash
fi
# All tests listed in sciunit/unit_test/active.py will be run
UNIT_TEST_SUITE="sciunit.unit_test buffer"
coverage run -m --source=. --omit=*unit_test*,setup.py,.eggs $UNIT_TEST_SUITE
