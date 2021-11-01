# Changelog

## [Unreleased]

No changes since last release.

## [0.0.8] - 2021-11-01

### Added
  - default now prints status underneath list, and `list` output mode only lists completed results (as default previously did)
  - comments on several functions and classes

### Fixed
  - ANSI codes for clearing a line when updating status

## [0.0.7] - 2021-10-28

### Added
  - support for multiple glob expressions, e.g. `py7za-box *.txt *.csv`

### Fixed
  - outdated and broken examples in help text corrected;
  - (major) extracting with 'x' instead of 'e' (previously, zipped directories would incorrectly extract)

## [0.0.6] - 2021-10-26

### Fixed
  - small mistakes in help text corrected;
  - with `--output verbose`, py7za-box now correctly prints INFO lines with the full 7za command.

## [0.0.5] - 2021-10-25

### Fixed
  - relative import of version (running script in development as package.module, instead of full script path name);
  - (non-functional:) refactoring and suppression of irrelevant warnings.

## [0.0.4] - 2021-10-24

### Added
  - `nice_size` for pretty-printing file sizes;
  - output modes default, verbose, status and quiet (previous default);
  - overwrite modes all, skip (default), rename_new, rename_existing.

### Fixed
  - passing `-y` as a default option, previously 7za could get stuck in interactive mode;
  - passing cli options to 7za when unboxing, previously only passed scripted options, ignoring `-7 <options>`.

## [0.0.3] - 2021-10-22

First PyPI release.

### Fixed
  - Unboxing with `--delete` now correctly removes archives after unboxing.<br>Note: if you pass options to 7za that would prevent (part of) the archive to not be extracted, but still result in a return code of 0, the archive would be removed and its contents lost!

## [0.0.2] - 2021-10-22

First release in the wild.

### Added
  - Core Py7za class wrapping 7za.exe;
  - AsyncIOPool CPU pooling;
  - `py7za-box` CLI tool;
  - Use of pre-installed 7za on Linux;
  - Unit tests.

## [0.0.1] - 2021-08-04

### Added
  - Cloned and adapted from python_package_template.

[Unreleased]: /../../../
[0.0.8]: /../../../tags/0.0.8
[0.0.7]: /../../../tags/0.0.7
[0.0.6]: /../../../tags/0.0.6
[0.0.5]: /../../../tags/0.0.5
[0.0.4]: /../../../tags/0.0.4
[0.0.3]: /../../../tags/0.0.3
[0.0.2]: /../../../tags/0.0.2
[0.0.1]: /../../../tags/0.0.1
