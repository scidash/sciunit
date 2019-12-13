Zhiwei made following change:

updating .rst files with sphinx-apidoc

shell commands:
$ rm -rf source
$ sphinx-apidoc -o "./source" "../sciunit"
$ sphinx-quickstart

Copy conf.py from the oringinal sciunit repo.

$ sphinx-build -b html ./source ./build


I have found something new about the attribute, and I will send you an email to explain it.