## Configuration and CLI

Every option available on the command-line interface can also be provided using a configuration file.

### CLI Options

For any option that acts as a simple on/off switch, you can either just specify the option to imply turning it on, or explicitly pass `0` or `false` to turn it off, or `1` or `true` to turn it on. This may be useful if you want to be very clear in a batch file or log about what happens.

For example, the default is for [delete](#delete) to be on (`True`) and for [match_dir](#match_dir) to be off (`False`). So, this:
```commandline
box **/* -r C:\Temp --delete true --match_dir false
```
Would be the same as:
```commandline
box **/* -r C:\Temp
```


#### archive_ext 

```none
--archive_ext | -ae [<ext>]
```
If provided, globs will be interpreted as if matching the original file names, and matched files will be matched against any regular expressions provided without the archive extension.

Example:
```commandline
unbox **/*.csv -ae 7z -re "test.*\.csv"
```
This would proceed to find files ending in `.csv.7z` (i.e. previously boxed `.csv` files) and only archives with names like `test123.csv.7z` (i.e. starting with `test` and ending in `.csv`, ignoring the `.7z`) would be matched.

!!! Note 
    this is particularly useful if you have a complex set of globs and expressions to select files for boxing, perhaps defined in a configuration file. With the `--archive_ext` option, you can reuse that same configuration file without having to add archive extensions in many places.  


#### create_dirs

```none
--create_dirs | -cd
```

Switch for unboxing, determining whether to recreate the same directory structure in the target path. When a [target](#target) location is specified, files will not be boxed or unboxed in-place - if `create_dirs` is `False`, all the files in the target location will be created in the same directory. The default is `True`, which is the useful setting for in-place boxing and unboxing.

It's recommended you review [zip_structure and create_dirs](../gotchas/#zip_structure-and-create_dirs) before use.

!!! warning
    This can lead to undesirable results (files getting overwritten, or not boxed or unboxed) if there are files with the same name in different directories. Use with care! The default is safe, setting this option to `False` requires being careful.

#### delete

```none
--delete | -d
```

Remove the files that were boxed immediately after boxing (one file at a time) and remove the archive files that were unboxed immediately after unboxing. The default for this switch is `True`.

#### error_log

```none
--error_log | -el <path>
```

Write an error log file to the name and location specified by `<path>`. All warnings and error messages will be written (with a timestamp) to the file. The default is to write these messages on screen only.  

#### glob

```none
[--glob | -g] <pattern> [<pattern> [..]]
```

At least one pattern is required for a `box` or `unbox` command. The patterns provided will be processed in order.

!!! warning
    You should ensure that later patterns don't match files that are created by earlier patterns. For example, `box **/*.txt **/*` would first box every text file, but the created `.7z` files would then be matched by the second pattern - this would be an issue if [zip_archives](../configuration/#zip_archives) was also provided (since the new archives would then be archived again). Another example, `unbox project*.7z *.7z -md` would unbox boxed directories if [match_dir](../configuration/#match_dir) was also provided, which could contain further *.7z files which would then be matched by the second pattern - which could be undesirable, or at least not easily reversible with a `box` command.

#### group_match

```none
--group_match | -gm
```

Whether to match files that are grouped with other matched files. See also [File Groups](../configuration/#file-groups). The default is to match grouped files. In short, this means that any files that are normally grouped, like for example files that make up an ArcGIS shape file, will all be matched if at least one of them is matched by a glob pattern.

You can define additional groups using [group_add](../configuration/#group_add)

#### group_add

```none
--group_add | -ga <path>
```

In addition to default group definitions used by [group_match](../configuration/#group_match), you can define your own in a .json format that is structured the same as the `groups.json` file that accompanies the `py7za_box` script. 

The structure is straightforward:
```none
{
  "group name": [".suffix", ".suffix", ...],
  ...
}
```
Alternatively, this structure can be part of another .json file, in which case it should be the value of a `"groups"` key:
```none
{
  ...
  "groups: {
    "group name": [".suffix", ".suffix", ...],
    ...
  }
  ...
}
```
This allows including it into a configuration file that can be passed to box in addition to (or instead of) command-line options.

Example:
```commandline
unbox --group_add my_configuration.json
```
In this case, `my_configuration.json` would be expected to have a `"glob"` key, which would contain the glob patterns, since none are given on the command-line.

#### help

```none
--help | -h
```

Shows a help text for CLI parameters on the console (including the installed Treewalker version number at the top).

#### log

```none
--log | -l <path>
```
Write a log file to the name and location specified by `<path>`. For each boxing or unboxing operation, source file name, source file size, target file name, and target file size are written in .csv format. The default is not to log to file and to only report progress on the screen.

#### not_regex

```none
--not_regex | -nre <expr>
```
The opposite of [regex](../configuration/#regex). I.e: any objects with a full, absolute path that match the expression will be skipped. The default is that no regular expression matching is performed (`None`)

#### match_dir

```none
--match_dir | -md
```

Whether glob pattern(s) should match directories. By default only files are matched. If directories are matched, they will be archived as a whole, i.e. the entire directory will be archived as a single file when boxing, and unboxed all at once when unboxing.

!!! note
    7za itself supports multicore compression when compressing multiple files into a single archive. So if you're compressing many files into a few archives, which likely happens when compressing directories instead of single file, it may not be optimal to create a pool with as many tasks as you have cores. Look at [parallel](../configuration/#parallel)

!!! warning
    Since there are far more possible complications here, using this option requires some planning. It is recommended not to use this switch unless the implications are clear. Some experimentation before applying it to critical files is recommended.

#### match_file

```none
--match_file | -mf
```

Whether glob pattern(s) should match directories. By default files are matched, and directories are not. In case you want to box a series of directories and need to exclude any files that would otherwise be matched by the glob pattern, you can use this switch to avoid any files from being matched individually.

Example:
```commandline
box project/* -md -mf False
```
This command would box each directory in the `project` directory, but none of the individual files in the same directory. 

#### output

```none
--output | -o  d | default / l | list / q | quiet / s | status / v | verbose
```

What output to write to the screen. The default option is `default` which will print a line per archive processed with current status, updating lines as the application goes. 

The `list` option is largely the same, but does not print current status which gets updated like `default`, this mode is most useful if capturing the output in a file.

Using the `verbose` option will show each command to `7za.exe` as it is issued and enables logging at `info` level, which means that besides warnings and errors, messages of lesser importance are also logged to standard error.

With `status`, only live status for the ongoing processes are updated on screen, but there is no scrolling report of every archive as it completes processing. Information about what files have been processed is no registered, unless logged. This mode is most useful if a long runnig operation runs in the background and the user is only interested in overall progress, not what files have been processed.

When `quiet`, only essential messages like errors are written to the screen.

!!! Note
    The `default`, `list` and `verbose` modes all report some information on screen that may not be available when using archive formats that `7za` does not support (but Python does) If using these modes with more exotic formats causes error messages, consider using `quiet` and [log](../configuration/#log).

#### overwrite

```none
--overwrite | -w  a | all / s | skip / u | rename_new / t | rename_existing 
```

Controls what should happen if a file is unboxed when the target already exists. The default is to `skip` unboxing such files (to avoid overwriting changes that were made after boxing). When set to `all`, all files will be (over)written. When set to `rename_new`, files with existing targets will be renamed, adding a number to the name, to avoid overwriting the existing file(s). Similarly, the `rename_existing` option will cause the existing file to be renamed with a new number first, before unboxing the file that takes its place.

#### parallel

```none
--parallel | -p <n>[x]
```

How many parallel processes to run at a maximum. 

The default is `0`, which means all available cores on the system. This can exhaust compute resources on the system to the point of other programs having trouble getting their work done - for example, Remote Desktop sessions to the system may appear to hang or disconnect. If any interactivity with the desktop is required during the run, it is recommended to set `--parallel` to a lower value. A negative value is interpreted to mean the number of available cores minus that number, so `--parallel -2` may be suitable to retain more or less normal access to the system. 

You can also specify a multiple of the number of available cores on the system, by appending an `x` to the value, which can be a floating point value in that case.

Example:
```commandline
box **/* -p " -6"
box **/* -p 18
box **/* -p .75x
```
All three of these commands, on a system with 24 cores, would cause the operation to run on 18 cores.

!!! Note
    In rare cases you may want to kick off more parallel processes than there are cores, in particular when unboxing many large files that do not require a lot of computing power to decompress but when you do have a lot of bandwidth to saturate. However, in general a number at or below the number of available cores is optimal.

!!! Note
    Unless you have `psutil` installed in your environment, `py7za-box` currently won't be able to tell how many physical cores are available. You should be fine leaving several vCPU free, but if you want to be able to work comfortably, you may want to use an option like `-p .375x` to ensure your have at least a single physical core free on any 4 physical core (or more) system.

!!! Note
    If you use the [match_dir](../configuration/#match_dir) option, you may want to consider only allowing very few parallel operations, as 7za itself will make use of multiple cores to compress multiple files at once.

#### root

```none
--root | -r <path>
```

All file operations of `py7za-box` are relative to the given path. The default path is `"."`, i.e. the current working directory where `py7za-box` is started. UNC paths are supported.

Example
```commandline
unbox **/* -r \\server\some\path
```

#### regex

```none
--regex | -re <expr>
```

In case glob patterns don't allow you enough control over what files are processed, you can provide a regular expression to further limit what paths are matched. Note that the expression has to match the full, absolute path of the objects matched. The default is that no regular expression matching is performed (`None`)

Example:
```commandline
box **/* -re ".*\d{4}-\d{2} Report.docx?$"
```
Will match anything that ends in something like "2022-01 Report.docx$" and is an alternative for the glob pattern `**/*[0123456789][0123456789][0123456789][0123456789]-[0123456789][0123456789] Report.doc`, followed by the same pattern ending in an `x`. 

!!! note
    Regular expressions will likely perform worse than glob patterns, as the regular expression engine is more complex than the glob pattern matching engine. On the other hand, consider that archiving files in itself is not a very fast operation, so the overhead of the regular expression matching is likely negligible. 

#### si

```none
--si | -si 
```

When file sizes are printed (to screen or log files) in human-readable form, whether to use SI units for file sizes (or the default binary sizes). SI sizes are powers of 1,000 (KB, MB, GB, etc.) while binary sizes are powers of 1,024 (KiB, MiB, GiB, etc.)

#### target

```none
--target | -t <path>
```

By default, `py7za-box` commands work in-place on files in the [root](../configuration/#root) location. If you provide a path to `--target`, outputs will instead be written to that location.

This can be useful if you want to preserve the original and do not want to clutter it by adding archives, or when the root location does not have enough free space to contain the output. Note that options like [delete](../configuration/#delete) and [create_dirs](../configuration/#create_dirs) still work as usual.

Example:
```commandline
unbox **/*.7z --root \\archive\project\directory --target \\file_server\project\directory --delete false
```

#### test

```none
--test
```

Run `py7za-box` in 'test' mode - this will make the application run as it would otherwise, but it will not actually perform any (un)archiving, file deletion, etc. It will show the `7za.exe` commands as they would have been executed.

Example:
```commandline
box **/* -r D:\test\ --test 
```
This can output something like:
```none
TEST in ".": 7za.exe a "D:\test\test.mif.7z" "D:\0000\test.mif" -y -sdel
TEST in ".": 7za.exe a "D:\test\test.mid.7z" "D:\0000\test.mid" -y -sdel
TEST in ".": 7za.exe a "D:\test\test.txt.7z" "D:\0000\test.txt" -y -sdel
Matched 3 object(s), start processing in up to 16 parallel processes ...
Completed processing 0 B of files into 0 archives, totaling 0 B.
Took 0:00:00.010001. Skipped 0 files matching glob.
TEST: would have started boxing 3 matches.
```

#### test_match

```none
--test_match
```
Like [test](../configuration/#test), but instead of showing the full `7za.exe` commands, it only shows the files that were matched and the order in which the `7za.exe` commands for them would be started.
Example:
```commandline
box **/* -r D:\test\ --test_match 
```
This can output something like:
```none
D:\0000\test.mif
D:\0000\test.mid
D:\0000\test.txt
Matched 3 object(s), start processing in up to 16 parallel processes ...
Completed processing 0 B of files into 0 archives, totaling 0 B.
Took 0:00:00.010001. Skipped 0 files matching glob.
TEST: would have started boxing 3 matches.
```
Note: if both [test](../configuration/#test) and [test_match](../configuration/#test_match) are provided, [test_match](../configuration/#test) takes precedence.

#### unbox

```none
--unbox | unzip | -u
```

When you run `unbox`, you effectively run `py7za-box` with this option set to `True`, causing it to start unboxing and interpreting the other options accordingly. By default, this option is `False`, so running `py7za-box` without this option is nearly identical to running `box`.

#### unbox_multi

```none
--unbox_multi | -um
```

Whether to unzip multi-file archives. The default is `False`, unboxing will not extract archives that contain more than a single file. When you box a set of files with [match_dir](../configuration/#match_dir) you will likely want to unbox them using `--unbox_multi`.

!!! note
    If the archives were created by `py7za` this is likely a safe operation. However, if you apply this to archives that were created in some other fashion, moved around, or modified in some other way, you have to keep in mind that this can lead to conflicts. For example, extracting archives that contain files with the same names that would end up in the same place. 

#### zip_archives

```none
--zip_archives | -za
```

Whether to zip matched archives (again). By default, when an existing archive (`.7z`, `.zip`, etc.) gets matched by the glob pattern, it is skipped to avoid recompressing the archive. However, if you want this to happen, you can use this switch. A use case for that might be if a file format happens to be recognised as an archive, but is in fact some other more obscure or proprietary file type. 

#### zip_structure

```none
--zip_structure | -zs
 ```

When this option is specified, the subdirectory structure relative to the root directory is included in the archive (there is no effect when unboxing). By default, the directory structure from root is recreated (see [create_dirs](../configuration/#create_dirs)), and there is no need to include the directory structure. But if you set `--create_dirs` to False, you may want to preserve the original location of the files, even though you are creating a flat file structure.  

For example, if you start with two directories in a directory called `project`: `one` and `two`, and both contain a text file, `1.txt` and `2.txt` respectively, then running the following:
```commandline
box **/*.txt -zs -cd False
```
Will create 2 archives named `1.txt.7z` and `2.txt.7z`. However, normally these would simply contain `1.txt` and `2.txt` respectively. With `-zs` specified, they actually contain `project/one/1.txt` and `project/two/2.txt` and thus running:
```commandline
unbox *.7z
```
Will recreate the original directory structure and put the files in their correct locations.

It's recommended you review [zip_structure and create_dirs](../gotchas/#zip_structure-and-create_dirs) before use.

!!! note
    Although there are use cases where this may be desirable, using the in-place method of boxing and unboxing is far more convenient in most cases, since it allows for including parts of the directory structure in search queries and since directory structure incurs next to no overhead on storage, `--zip_structure` should only be used if a flat file structure has clear advantages.

#### 7za

```none
--7za | -7 <arguments>
```

The passed arguments will be passed as CLI arguments to `7za.exe`, after any scripted ones. Since arguments to `7za.exe` start with the same character as arguments to `py7za-box`, you should put double quotes around the arguments, and start with a space.

Example:
```commandline
box **/* -7 " -mx9 -tzip"
```
(Note the extra space after the opening quote) This would cause a normal boxing operation, but using `.zip` as the file format and using maximum compression. Look at the command-line options for 7-zip for a more complete overview:  https://sevenzip.osdn.jp/chm/cmdline/switches/index.htm

!!! Warning
    Options passed with `--7za` are applied after the options passed by `py7za-box` itself. As a result, they will likely override these options and may lead to faulty or unexpected behaviour. Please use this option with great care and look for a way to obtain your goals with `py7za-box` before tweaking things with `7za.exe` directly. 

### Glob patterns

There are many online guides on Unix path expansion with glob patterns, or glob expressions, but the key things to know are:

- You can use forward slashes / and backslashes \ interchangeably, but it is recommended to use forward slashes only to avoid unrelated problems with escaping, so prefer `model/log/*.txt` over `model\log\*.txt`
- A single asterisk `*` matches zero or more characters in part of a name, for example `abc-*.csv` would match every `.csv` file (or directory with a name that ends in `.csv`) with a name that starts with `abc-`.
- A double asterisk `**` matches any number of directories in a path, including subdirectories, for example `temp/**/model.log` would match every file called `model.log` in every subdirectory of the `temp` directory.
- If you just need to vary a single character, or a fixed number of characters, you can use the question mark `?`, for example `logs/2022-01-??.log` could be useful to match every log file from January 2022.
- If you need to vary a single character, but only want to match something specific, you can use brackets `[]`, for example `output/[AB]*.csv` would match any `.csv` file in the `output` directory that starts with `A` or `B`.

So: `*/*.txt` would match every `.txt` file in every directory of the root directory (but none of their subdirectories, and also none of the `.txt` files that sit directly in the root directory), while `**/*.txt` would match every `.txt` file in the root directory itself *and* all of its subdirectories. `*.txt` would just match all the `.txt` files in the root directory itself and nothing else.

!!! warning 
    The command-line tools accept a series of glob patterns, one or more. Instead of writing very complicated pattern to try and match a varied group of files, it can often be simpler to repeat the same pattern with a few variations. However: because the glob patterns are processed in order, you need to avoid matching the created archives in later patterns, for example `box **/*.txt **/*` would first box `.txt` files, but then match the created `.7z` files again. Luckily, boxing will skip over these files as they are recognised as archives by default (see [zip_archives](../configuration/#zip_archives)), but an error message may show if the file was still locked.

!!! note
    Although files and directories may be matches by glob patterns, `py7za-box` may ignore matched files and directories based on [match_dir](../configuration/#match_dir) and [match_file](../configuration/#match_file). This may sound complicated, but in most cases you just want to match files, and the default for `match_dir` is `False`.

!!! warning
    Because `[` and `]` are allowed characters in file and directory names, you can get into trouble with these if you want to use them in a glob pattern, as they are used to define character classes, like `[AB]` above. To indicate a literal `[` in a name, you would use `[[]` and similarly, `[]]` indicates a single literal `]`. So, to match `test[1].txt` literally, you would use `test[[]1[]].txt` and to match any `test[*].txt`, you'd use `test[[]*[]].txt`. There are no such problems with `*`, `**` and `?` because they are typically not allowed characters on most file systems.

### File Groups

Certain types of files are essentially useless or lose essential context if they are separated from their companion files. One such example are ArcGIS shape files. These consist of a `.shp`, but also require an accompanying `.dbf` and several other files, some of which are optional.

`py7za-box` supports automatically boxing and unboxing these files together, so that you can still have the benefit of good compression on some of them, without having to keep track of what part of the set you compressed or decompressed.

By default, there are very few groups defined in a `groups.json` that sits in the folder where `py7za-box.py` is installed (a `py7za` subfolder of your Python `site-packages` folder) - the default contents are currently:
```json
{
  "arcgis shape files": [".shp", ".shx", ".dbf", ".sbn", "sbx", ".fbn", ".fbx", ".ain", ".aih", ".atx", "ixs", ".mxs", ".prj", ".xml", ".cpg"],
  "mapinfo tab files": [".tab", ".dat", ".ind", ".map", ".id"],
  "mapinfo mid/mif files": [".mid", ".mif"]
}
```
You can add your own groups to that file, but that is not recommended as this may cause issues when upgrading or uninstalling the tool. Instead, use the [group_add](../group_add/#add_groups) option to point `py7za-box` to your own `.json` with a same structure. You can even override the existing groups, if you need, by including the same keys in the dictionary.

Alternatively, you can add a `"groups"` key to your main `.json` configuration with settings to drive `py7za`, which would have to have a dictionary value that's the exacty same as the entire `groups.json` file.

The behaviour when boxing or unboxing a file that falls into a group is straightforward. For example:
```commandline
box **/*.shp
```
This will start boxing all shape files, but include all the group files with the same name (but a different suffix) as well.

!!! note
    If a single suffix is part of multiple groups, it will only be matched for the first group it is part of. If you require both groups to be fully matched, you should write glob patterns that match one of the other suffixes, that are sufficiently distinct. For example, shape files include `.xml` as a suffix, which is a very common suffix. It will work, but if you have some other group that also includes it (and you need to match that in other cases), you could pick `.shp` to glob and the `.xml` would be collected for both. 