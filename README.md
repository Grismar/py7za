# Name

Python wrapper for running the 7za.exe utility from https://www.7-zip.org/

The wrapper simply runs the application in a separate process and provides the following added functionality:
- capture and parse output (overriding any `-bs_` arguments)
- track progress and some basic metrics (size, files processed, etc.)

Other than providing that utility, the wrapper tries to allow users access to 7za in a way as simple, and as close to the original as possible.

## Install

Install the package:
```
pip install py7za
```

## Example

With the package installed, try running this script:
```
from py7za import Py7za

# zip all .txt files in c:\temp and subdirectories to texts.zip
Py7za.run(r'a c:\temp\*.txt texts.zip -r')
```

## License

This package is licensed under the MIT license. See [LICENSE.txt](https://gitlab.com/Jaap.vanderVelde/py7za/-/blob/master/LICENSE.txt).

## Changelog

See [CHANGELOG.md](https://gitlab.com/Jaap.vanderVelde/py7za/-/blob/master/CHANGELOG.md).
