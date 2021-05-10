# Contributing to SciUnit

## Reporting issues

When reporting issues please include as much detail as possible about your
operating system, `sciunit` version, and python version. Whenever possible, please
also include a brief, self-contained code example that demonstrates the problem.

## Contributing code

Thanks for your interest in contributing code to SciUnit!
Our developers aim to adhere to Python Enhancement Proposals (PEP) standards to ensure that code is readable, usable, and maintainable.

+ If this is your first time contributing to a project on GitHub, please consider reading
this [example guide](https://numpy.org/devdocs/dev/index.html) to contributing code provided by the developers of numpy.
+ If you have contributed to other projects on GitHub you may open a pull request directly against the `dev` branch.

Either way, please be sure to provide informative commit messages
and ensure that each commit contains code addressing only one development goal.

Writing unit tests to cover new code is encouraged but not required.
Your changes can be tested using the current set of units tests by executing `test.sh` in the root directory.

The python packages `isort`, `black`, and `autoflake` are being used with the `pre-commit` framework to auto-format code.
If you install `pre-commit`, you can run `pre-commit run --all-files` before a pull request or commit in your shell to apply this formatting yourself.
