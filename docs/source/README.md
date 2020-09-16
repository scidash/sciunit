# Recipe for building the API docs from scratch:

updating .rst files with sphinx-apidoc
Assuming current working directory is `sciunit/docs/source`.

Linux Bash shell commands:
```
rm modules.rst sciunit.models.rst sciunit.rst sciunit.scores.rst sciunit.unit_test.rst
cd ..
sphinx-apidoc -o "./source" "../sciunit"
sphinx-build -b html ./source ./build
```
Windows PowerShell commands:
```
rm modules.rst, sciunit.models.rst, sciunit.rst, sciunit.scores.rst, sciunit.unit_test.rst
cd ..
sphinx-apidoc -o "./source" "../sciunit"
sphinx-build -b html ./source ./build
```
