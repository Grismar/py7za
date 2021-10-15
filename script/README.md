This folder contains scripts for writing, building, installing and maintaining your package project. Add additional scripts here.

Ideally, provide both Windows and Linux variants of scripts you add.

- [build_whl.bat](scripts/build_whl.bat) and [build_whl.sh](scripts/build_whl.sh)<br/>Builds a Python Wheel (.whl), so you can distribute a package as a single binary file (note that it still contains the source).
- [cleanup.bat](scripts/cleanup.bat) and [cleanup.sh](scripts/cleanup.sh)<br/>Cleans up files created by the build and deploy scripts.
- [deploy_to_pypi.bat](scripts/deploy_to_pypi.bat) and [deploy_to_pypi.sh](scripts/deploy_to_pypi.sh)<br/>Run tests, build and deploy to (test) PyPI. Pass `no_test` to deploy to the real index, or omit to deploy to the test index.
- [rename_package.bat](scripts/rename_package.bat) and [rename_package.sh](scripts/rename_package.sh)<br/>Uses [rename_package.py](scripts/rename_package.py) to rename relevant files in the project, updating the contents of files that were included in the template. Don't use this after you've started making actual code changes.
- [run_tests.bat](scripts/run_tests.bat) and [run_tests.sh](scripts/run_tests.sh)<br/>Runs unit tests in the [test](test) folder.

Any of these scripts can be started from other folders as well e.g., from the project root: `./script/rename_package.sh my_package` - the scripts will change their working directory to be the project root.
