pip install coveralls
git clone -b cosmosuite http://github.com/scidash/scidash ../scidash
UNIT_TEST_SUITE="sciunit/unit_test/core_tests.py buffer"
# Fundamental Python bug prevents this latter method from allowing
# some notebook tests to pass.  
#UNIT_TEST_SUITE="setup.py test"
coverage run --source=. --omit=*unit_test*,setup.py,.eggs $UNIT_TEST_SUITE