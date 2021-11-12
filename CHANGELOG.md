# Changelog

## [Unreleased]

No changes since last release.

## [0.1.4] - 2021-11-12

### Added
  - `-p`/`--parallel` (formerly `-c`/`--cores`) now accepts '<n>x' as a multiplier to the number of cores, e.g. with 8 available cores, if `2x` is passed, 16 processes will be spawned in parallel.
  - `-l`/`--log` is a new option to which you can pass a path to a log file and every completed operation will be logged to that file with a timestamp, name of the associated archived and the size of both the contents and the archive, in both human readable format (string, e.g. 1.2KiB) and bytes (integer). 

### Changed
  - (BREAKING) renamed `-c`/`--cores` to `-p`/`--parallel`, to be more accurate and avoid confusion about how this actually works. The default 0 still uses the number of available cores.

### Fixed
  - Previously, FileNotFoundErrors and failed 7za execution (return code > 0) would not be caught and cause the operation to fail; now an error is reported, but the process continues. 

## [0.1.3] - 2021-11-11

### Added
  - during startup, py7za-box reports the number of matched files as they are found, before actually starting archiving; previously, the application would appear to be hanging while collecting large numbers of matched files

### Changed
  - default, list and verbose updates now include a timestamp at the start; py7za-box also reports total time taken once it completes.
  - running status updated to be more clear "current / total \[file size from/into archive size\]"

## [0.1.2] - 2021-11-11

### Added
  - when reporting completion, py7za-box now also reports the number of skipped files.

### Fixed
  - using UNC paths could cause py7za-box to fail, due to shlex.split() issues; a workaround to `shlex.split` is `py7za.arg_split`, [arg_split](py7za/_py7za.py).

## [0.1.1] - 2021-11-10

### Fixed
  - help text formatting
  - refactoring errors, invalidating 0.1.0

## [0.1.0] - 2021-11-10

### Changed
  - (breaking) by default, py7za-box unboxing will now not unzip matched archives that contain multiple files
  - (breaking) by default, py7za-box single file boxing will no longer match and archive existing archives (.zip, .7z, .gz, etc.)  

### Added
  - an option to unbox multiple files `-um` / `--unbox_multi` to override the new standard behaviour for py7za-box
  - an option to match and archive existing archives `-za` / `--zip_archives` to override the new standard behaviour for py7za-box

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
[0.1.4]: /../../../tags/0.1.4
[0.1.3]: /../../../tags/0.1.3
[0.1.2]: /../../../tags/0.1.2
[0.1.1]: /../../../tags/0.1.1
[0.1.0]: /../../../tags/0.1.0
[0.0.8]: /../../../tags/0.0.8
[0.0.7]: /../../../tags/0.0.7
[0.0.6]: /../../../tags/0.0.6
[0.0.5]: /../../../tags/0.0.5
[0.0.4]: /../../../tags/0.0.4
[0.0.3]: /../../../tags/0.0.3
[0.0.2]: /../../../tags/0.0.2
[0.0.1]: /../../../tags/0.0.1
