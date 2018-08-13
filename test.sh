pip install coveralls
if [ ! -d "../scidash" ]; then
  git clone -b cosmosuite http://github.com/scidash/scidash ../scidash
fi
UNIT_TEST_SUITE="sciunit.unit_test buffer"
# Fundamental Python bug prevents this latter method from allowing
# some notebook tests to pass.
#UNIT_TEST_SUITE="setup.py test"
coverage run -m --source=. --omit=*unit_test*,setup.py,.eggs $UNIT_TEST_SUITE
