pip install coveralls
git clone -b cosmosuite http://github.com/scidash/scidash ../scidash
coverage run --source=. --omit=*unit_test*,setup.py,.eggs setup.py test
