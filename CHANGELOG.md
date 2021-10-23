# Changelog

## [Unreleased]

No changes since last release.

## [0.0.4] - 2021-10-23

### Added
  - `nice_size` for pretty-printing file sizes
  - output modes default, verbose, status and quiet (previous default) 

## [0.0.3] - 2021-10-22

First PyPI release.

### Fixed
  - Unboxing with `--delete` now correctly removes archives after unboxing.<br>Note: if you pass options to 7za that would prevent (part of) the archive to not be extracted, but still result in a return code of 0, the archive would be removed and its contents lost!

## [0.0.2] - 2021-10-22

First release in the wild.

### Added
  - Core Py7za class wrapping 7za.exe
  - AsyncIOPool CPU pooling
  - `py7za-box` CLI tool
  - Use of pre-installed 7za on Linux
  - Unit tests

## [0.0.1] - 2021-08-04

### Added
  - Cloned and adapted from python_package_template

[Unreleased]: /../../../
[0.0.3]: /../../../tags/0.0.3
[0.0.2]: /../../../tags/0.0.2
[0.0.1]: /../../../tags/0.0.1
