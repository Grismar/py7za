# Changelog

This package is currently in 'beta', in that it is in use by several users, but you may run into situations that simply haven't come up in use or testing so far. Feel free to submit an issue (and preferably suggest a solution).

## [Unreleased]

## [0.4.2] - 2025-07-22

### Added
  - add `--ansi 0` switch to disable use of ANSI codes to overwrite lines (for redirected output) 

### Fixed
  - add ANSI bit on console instead of overwriting 

## [0.4.1] - 2025-05-13

### Fixed
  - fix warning regarding legacy `bdist_wheel` 

## [0.4.0] - 2025-05-13

### Added
  - detect unknown operator in date test
  - add help text for configuration and catch errors for non-existent configuration files
  - catch exceptions when running in CLI, except when debugging

## [0.3.2] - 2024-04-03

### Added
  - add date to version output on CLI
  - include link to change log in readthedocs documentation

## [0.3.1] - 2024-03-21

### Fixed
  - fix async unit test that wasn't awaited

## [0.3.0] - 2024-03-21

### Added
  - add shorter help message after an error to avoid obscuring the error message.
  - check to avoid options being passed to box/unbox that are not supported.

### Changed
  - (breaking) replace short option for `--target` with `-tp` instead of `-t`.
  - (breaking) add `-t` the short option for `--test`, and `-tm` for `--test_match`.

## [0.2.14] - 2024-03-21

### Added
  - add `--datetime_created` and `--datetime_modified` to `py7za-box` to match files by their creation or modification date, respectively.

### Fixed
  - re-enable direct run of `py7za_box.py` CLI application with fixed package import.

## [0.2.13] - 2023-11-23

### Fixed
  - fix serious issue that would cause all tasks to start instantly, instead of respecting pool size, with all manor of disastrous results for large jobs.

## [0.2.12] - 2023-11-22

### Fixed
  - update `readthedocs.io` configuration.

## [0.2.11] - 2023-11-22

### Changed
  - have `Py7za.run()` return Py7za class with return code and errors, instead of just a return code. 

### Fixed
  - update `AsyncIOPool` to deal with the deprecation of awaitable classes since Python 3.10.
  - fix several comment typos.
  - fix `subprocess` imports to fully qualified references.
  
## [0.2.10] - 2023-07-24

### Changed
 - as of version 0.2.5 not compatible with Python 3.11 and beyond, pending updates of asynchronous handling

## [0.2.10] - 2023-07-26

### Changed
  - pass -mmt2 to each 7za process to force max 2 threads per process, unless another value was passed explicitly<br>this avoids py7za taking up all processing power when a specific number of parallel processes was passed

## [0.2.9] - 2023-07-24

### Changed
  - require Python 3.10 or previous<br>due to  "Changed in version 3.11: Passing coroutine objects to wait() directly is forbidden." (https://docs.python.org/3/library/asyncio-task.html#asyncio.wait )

## [0.2.8] - 2022-08-04

### Fixed
  - build `mkdocs` documentation without errors 

## [0.2.7] - 2022-08-04

### Fixed
  - correctly match names with `--regex` when using `--archive_ext`

## [0.2.6] - 2022-08-04

### Added
  - match file names without archive extension when unboxing with `--archive_ext`
  - only output matched filenames for a test run with `--test_match`
  - changes to readthedocs index to fix some broken links

## [0.2.4] - 2022-01-18

### Added
  - check negative regex `--not_regex`, i.e. an option to *not* match anything matching a regex

## [0.2.3] - 2022-01-14

### Changed
  - move most content from README.md to documentation.

### Added
  - update project documentation links on PyPI;
  - add documentation on common gotchas.

### Fixed
  - catch `CancelledError` in `arun_many` for `AsyncIOPool` when `cancel_all` is called; re-enable failing tests;
  - add missing version reference in changelog;
  - spellcheck documentation and fix broken links;
  - make git ignore created `site/` folder.

## [0.2.2] - 2022-01-13

### Added
  - add documentation with MkDocs on https://py7za.readthedocs.io;
  - add 'groups' option to configuration to allow group definition in application configuration file.

### Changed
  - rename `create_folders` to `create_dirs` for consistency; `create_folders` still works as an alias, but is phased out of the documentation as well.

### Fixed
  - avoid errors reporting missing files when files that are part of a group also match the main glob; this caused no actual mistakes in boxing, but the error messages themselves were in error.
  - build information for MkDocs 

## [0.2.0] - 2021-12-16

This version is intended for broader release and testing, however still in beta.

### Added
  - `box` as a standard alias for `py7za-box`;
  - `unbox` as a standard alias for `py7za-box` with `--unbox` as a forced option;
  - unit tests for `AsyncIOPool` and `nice_size`.

### Fixed
  - `AsyncIOPool.cancel_all()` would attempt to `close` tasks that hadn't started yet, instead of `cancel`.

## [0.1.9] - 2021-12-14

### Added
  - catch keyboard interrupt (Ctrl+C / Ctrl+Break) and terminate gracefully;
  - match grouping: for pre-defined groups, matching files will cause files in their groups to be matched as well; for example, when matching `*.shp` (part of the 'ArcGIS shape files' group), other files in that group like `*.shx`, `*.prj` etc. will also be matched;
  - alternate groups can be extended by providing an alternate `groups.json` `-ga` / `--group_add <path to .json>` - you can eliminate existing groups by redefining them as empty lists; 
  - pre-defined groups were defined for arcgis shape files, mapinfo tab files, and mapinfo mid/mif files.

## [0.1.8] - 2021-11-17

### Added
  - specify `--test` for a simple test mode, which won't actually start any archiving or unboxing, but will instead perform all matching and checking and report just the command it would run
  - specify `-re <expr>`/`--regex <expr>` for regular expression matching; this will attempt to match the path of globbed objects and skip them if they do not match; note that the path is not just the filename, but also not the absolute path, it is the path as generated by `Path().glob()` 

### Fixed
  - ANSI code support was assumed, but did not work correctly on Windows Command prompt; OS-specific check and fix are now applied at startup

## [0.1.7] - 2021-11-16

### Added
  - reporting finished instead of current (including running) and separately reporting running (dlv)

### Fixed
  - Misspelling in help, missing newline

## [0.1.6] - 2021-11-15

### Added
  - an `-el`/`--error_log` (alias `-el`/`--error_log`) option now allows error (and info and warning) messages to be captured in a file, instead of writing them to the console. Of course, you can also just redirect standard error, but this option is there for convenience
  - `--unzip_multi` alias for `--unbox_multi`, analogous to the `--unzip` alias for `--unbox`

### Changed
  - when specifying `--unbox_multi`, you no longer have to specify `--unbox`. However, if you specify `--unbox` specifically as False, `--unbox_multi` will be ignored (i.e. no contradiction allowed and `--unbox` is stronger).
  - when logging an error, the error message itself (from 7za.exe) will also be logged on the following lines

### Fixed
  - previously if all files being archived were locked, resulting in an empty archive, `py7za-box` would fail listing metadata on the archive 

## [0.1.5] - 2021-11-12

### Added
  - Support for other file formats in py7za-box, which previously would cause problems when using anything other than .zip (as ZipFile was used for metadata)
  - `Py7za.list_archive` class method to obtain metadata from any archive format supported by 7za, or obtain metadata and a list of archive content details. 

### Changed
  - (BREAKING) default file format is no longer .zip but .7z for py7za-box; pass a 7zip parameter like `-7 "-tzip"` to revert to previous behaviour  

### Fixed
  - previously, py7za-box would crash if options were passed to 7za to write 7z or another archive format that wasn't .zip

## [0.1.4] - 2021-11-12

### Added
  - `-p`/`--parallel` (formerly `-c`/`--cores`) now accepts '<n>x' as a multiplier to the number of cores, e.g. with 8 available cores, if `2x` is passed, 16 processes will be spawned in parallel.
  - `-l`/`--log` is a new option to which you can pass a path to a log file and every completed operation will be logged to that file with a timestamp, name of the associated archived and the size of both the contents and the archive, in both human-readable format (string, e.g. 1.2 KiB) and bytes (integer). 

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
  - relative import of version (running script in development as `package.module`, instead of full script path name);
  - (non-functional) refactoring and suppression of irrelevant warnings.

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
[0.3.2]: /../../../tags/0.3.2
[0.3.1]: /../../../tags/0.3.1
[0.3.0]: /../../../tags/0.3.0
[0.2.14]: /../../../tags/0.2.14
[0.2.13]: /../../../tags/0.2.13
[0.2.12]: /../../../tags/0.2.12
[0.2.11]: /../../../tags/0.2.11
[0.2.10]: /../../../tags/0.2.10
[0.2.9]: /../../../tags/0.2.9
[0.2.8]: /../../../tags/0.2.8
[0.2.7]: /../../../tags/0.2.7
[0.2.6]: /../../../tags/0.2.6
[0.2.4]: /../../../tags/0.2.4
[0.2.3]: /../../../tags/0.2.3
[0.2.2]: /../../../tags/0.2.2
[0.2.1]: /../../../tags/0.2.1
[0.2.0]: /../../../tags/0.2.0
[0.1.9]: /../../../tags/0.1.9
[0.1.8]: /../../../tags/0.1.8
[0.1.7]: /../../../tags/0.1.7
[0.1.6]: /../../../tags/0.1.6
[0.1.5]: /../../../tags/0.1.5
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
