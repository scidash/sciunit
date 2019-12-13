# Recipe for building the API docs from scratch:

updating .rst files with sphinx-apidoc

shell commands:
```
rm -rf source
sphinx-apidoc -o "./source" "../sciunit"
sphinx-quickstart
```

Copy conf.py from the oringinal sciunit repo. Then:

```
sphinx-build -b html ./source ./build
```
