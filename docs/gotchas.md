## Gotchas

Py7za and its CLI tools are fairly easy to use, but there are some options that can get tricky. The sections below describe some common mistakes and gotchas. It is recommended for anyone using `py7za-box` in anger to at least have a quick read of this, before doing irreversible damage to important file collections. **You use Py7za at your own risk.**

### zip_structure and create_dirs

There is a clear distinction between the `--zip_structure` ([zip_structure](../configuration/#zip-structure)) and `--create_dirs` ([create_dirs](../configuration/#create_dirs)) options for `py7za-box`, which may not be immediately obvious.

Compare this set of statements:
```commandline
box **/*.csv --zip_structure 0 --create_dirs 0 --target output
box **/*.csv --zip_structure 0 --create_dirs 1 --target output   # this is the default!
box **/*.csv --zip_structure 1 --create_dirs 0 --target output
```
All three will try and find all .csv files in the current directory (because no alternative `--root` was provided) and all of its subdirectories, and create individual archives for each.

The first will create all those archives directly in `output` (`--create_dirs 0`), and the archives will only contain the .csv itself, no directory structure (`--zip_structure 0`). So, if the current directory contains a file `files/data.csv`, an archive called `output/data.csv.zip` will be created, containing only `data.csv`.

The second will recreate the directory structure relative to the root directory, putting each archive in subdirectories created in `output` (`--create_dirs 1`), but the archives will still only contain the .csv itself (`--zip_structure 0`). Again, if the current directory contains a file `files/data.csv`, an archive called `output/files/data.csv.zip` will be created, containing only `data.csv`. This is the default and works most naturally when not providing a `--target`, but performing the archival in place, and having `py7za-box` delete the originals, which is also the default (see [delete](../configuration/#delete)).

The third will create all the archives directly in `output` (`--create_dirs 0`), but the archives will contain the subdirectory structure as well as the .csv itself. Again, if the current directory contains a file `files/data.csv`, an archive called `output/data.csv.zip` will be created, containing `files/data.csv`. 

This third option is useful if you require the flat file structure, but want to retain the information about where the files are to go. Another typical use case is if you only archive a few files from a complex folder structure and don't want to create a labyrinth of folders for just a few files. However, keep in mind that this only works if the original files themselves have different names. For example `files/dir1/file.txt` and `files/dir2/file.txt` would both be compressed as `file.txt.7z`, the second overwriting the first (depending on the [overwrite](../configuration/#overwrite) option, which you could set to `rename_new`).

!!! Note
    you could also set *both* `--zip_structure` and `--create_dirs` to be true, but that would create an archive `output/files/data.csv`, which would contain `files/data.csv`; when extracting the resulting files, care would need to be taken to avoid files ending up in double subdirectory structures, so a warning is issued if you combine these options. There is no common use case for this combination.

!!! Note
    `py7za-box **/*.csv --zip_structure 1 --create_dirs 0 --target output` is not the same as `7za.exe a output/archive.zip *.csv -r`. The latter creates a single archive, not one archive for each file, which is the purpose of `py7za-box`.  

### Directories that already have archives

If a directory already contains archives (.7z, .zip, .gz, etc.) and you run `py7za-box` using some filter that would (also) match these files, these will not get zipped again, unless you also provide the [zip_archives](../configuration/#zip_archives) option. However, if you then proceed to unzip all archives, these original archives may also be matched and unzipped. 

That is:
```commandline
box **/*                  # everything gets matched, but matched archives get ignored
unbox **/*.7z             # after this, .7z files in the original directory, may have been extracted

box **/* --zip_archives   # this option will get py7za-box to re-zip the archives
unbox **/*.7z             # after this, the directory will be identical to the original directory, with any archives
```

Based on the above, you might expect `--zip_archives` to be the default, after all it makes it easier to restore a directory to its original state. However, a more common use case is where a user boxes files in a directory, then proceeds to add new files, and then want to box these new files, without having to explicitly exclude the previously boxed files. 

For example:
```commandline
box **/*                  # box everything
copy newfile.txt .        # add some new content
box **/*                  # box everything new (but leave the archives created before)
```

To make life a little easier, if an archive contains more than one file, it will not be extracted by `unbox`. Since most existing archives likely contain more than one file, that means that in the first example above, only `.7z` files that originally contained a single file would have been extracted by:
```commandline
unbox **/*.7z             # after this, .7z files **with a single file in them ** 
                          # in the original directory, will have been extracted
```

But of course there are cases where you use `py7za-box` to zip directories, which may contain multiple files, so you need some way to tell it to do that still. 

For example:
```commandline
box **/sub-* --match_dir                  # box directories starting with "sub-"
unbox **/sub-*.7z --unbox --unbox_multi   # unbox .7z files, regardless of number of files contained 
```

As with any major file operation, you need to be careful, but hopefully the above helps with avoiding some common mistakes that can make a mess. `py7za-box` has been designed with defaults that keep the most common use cases in mind, but you can override those defaults as needed.

### Matching directories

Consider this command:
```commandline
box **/* --match_dir
```
Looks innocent, but note that this matches all files and directories it can find, and will try to archive **all** of them separately. This almost certainly will lead to a directory being archived before its matched contents, causing `py7za-box` to fail (or at least generate errors) because after the directory is archived, the file can no longer be found and thus cannot be archived.

So, how about:
```commandline
box **/* --match_dir --match_file false
```
Better, but matched subdirectories can still cause the same problem. When using `--match_dir`, you yourself should make sure there won't be matches inside matches. `py7za-box` does *not* currently offer a `--safe` option, though it may in the future (which could check for these situations before running). Typically, this means you either only match directories that have specific names or match patterns where you know they won't be nested, or you do something like this:
```commandline
box */temp --match_dir --match_file false
```
This would match and directory named `temp` exactly one level from the current directory, so accidental nesting is impossible. However, it would of course miss `./dir1/dir2/temp` while `**/temp` would match both `./dir1/temp` and `./dir1/temp/temp`, and thus be problematic. There is no glob expression that allows you to only match the first or last occurrance. Similar to `--safe`, `py7za-box` currently does *not* have a `--regex_match` option where you could provide more powerful (but slower) matching, but may in future versions. 

If you needed to match `temp` one, two or three levels in:
```commandline
box */temp */*/temp */*/*/temp --match_dir --match_file false
```
This works because it first gets everything at the first level out of the way, then anything remaining two levels in, and finally the same for three levels in.

!!! Note
    When matching directories: unless you happen to know every directory you're matching only contains a single file, you should most likely use [unbox_multi](../configuration/#unbox_multi) when unboxing archived directories, so that directories with multiple files also get unboxed correctly.<br/><br/>
    However, this may also unzip multi-file archives that were present before boxing. To avoid that, you could opt to use [zip_archives](../configuration/#zip_archives).

```commandline
py7za-box */* --match_dir --match_file false
py7za-box */*.7z --unbox --unbox_multi
```

### Matching groups of files


Please read the documentation for [File Groups](../configuration/#file-groups) first. It's mentioned there, but grouping doesn't put the files together in single archives, it just archives all of them individually in one run and with a single glob pattern.

If you boxed shape files, to then unbox all shape files and their siblings, you would:
```commandline
unbox *.shp.7z
```
Here `py7za-box` will match files in the group - *as long as they have been boxed up using the same format*. If you were to mix `.7z` and `.zip` when boxing them up for some reason, only the matching ones will be unboxed. A situation where this can easily happen is if you box files, keep working on the project, some new files that match the group pattern get created, and you then box files using the other format.

!!! tip
    In general, pick one archive format for a project, and stick to it. Don't abuse formats for something that should be solved with more distinctive file names.

Once you have a .json with custom groups defined, you can get `py7za-box` to apply them using [group_add](../configuration/#group_add):
```commandline
box *.ext1 -ga my_groups.json
```

Just be aware that you need to use unique keys and that reusing existing keys from `groups.json` would override the original groups. Also, if multiple groups contain the same extension, only the first group that has the extension of a matched file will be used. If you want to list predefined keys in `groups.json` from the package, you can run:
```commandline
notepad <path to your site-packages>\py7za\groups.json
```
(this on Windows, use << your vastly superior text editor here >> on Linux)

### Locked files

If you have files open in a program that locks the file for reading or writing, `py7za-box` may file to archive them, or remove them after archiving. A warning or error will be logged (and it's recommended you log to file with `--log_error <path>` for easy review). 

However, consider this scenario: a file is locked when archiving, so no file is archived and an error is logged. However, an (empty) archive will still be created. From the presence of the archive (and ignoring the error log), you may falsely conclude that your file is safe and remove the original - but you've just removed the only copy of the file!

If you notice these warnings and errors, simply close the program locking the files and *rerun* the boxing operation - under normal settings, it will proceed to box these files and ignore the other previously created archives. This works because the original files are still there and will be matched on the second boxing run, overwriting the previously created empty archive. All the other previously created archives will be ignored.

!!! warning
    If you were using [zip_archives](../configuration/#zip_archives) the above advice does not work! In that case, if you run into locked files, you'll either need to specifically box the missed files after getting rid of the lock, or unbox everything before retrying the `box` operation. Otherwise, all the previously created archives would get archived themselves. 


### Interrupting vs. Killing runs

If you need to interrupt a long run of boxing or unboxing, you can hit `Ctrl+C` or `Ctrl+Break` and `py7za-box` will continue to finish up running tasks before terminating.

However, if your run gets terminated in some other way (by killing the task, closing the console window it was running in, shutting down the computer it was running on, power failure, etc.) you may end up in a situation where an incomplete archive or file was created. In that situation there will be two files, one with the boxed version of the file name and one with the original file name.

As it is impossible for `py7za-box` to know what exactly is being recovered from, there are no CLI options to deal with this, and you may `py7za-box` throwing errors as it encounters corrupt archive files. Even worse would be assuming a file was correctly unboxed, when it was only partially unboxed.

You will have to proceed with care, but a suggestion for Windows user is to use the following command in PowerShell to list files that were probably affected:
```powershell
Get-ChildItem *.7z -recurse | ForEach-Object {if(Test-Path (Join-Path $_.directoryname $_.basename) -Type leaf) {$_} }
```
This command runs in the current working directory and finds all files that have the `.7z` extension (change as needed) in there and in all subdirectories. It only prints those file names for which there is a matching file without that extension.

If you were feeling particularly adventurous (or perhaps after first running and verifying the above), you could run this command to get rid of the surplus .7z files after a killed **boxing** run: 
```powershell
Get-ChildItem *.7z -recurse | ForEach-Object {if(Test-Path (Join-Path $_.directoryname $_.basename) -Type leaf) {Remove-Item $_} }
```

If you need to recover from a killed **unboxing** run, you could make use of the [overwrite](../configuration/#overwrite) CLI option, but keep in mind that this will apply to *all* operations. The default behaviour for [overwrite](../configuration/#overwrite) is to *skip* with a warning.

If you instead opt to remove files that still have a matching boxed version sitting next to them, you could used the following command:
```powershell
Get-ChildItem *.7z -recurse | ForEach-Object {if(Test-Path (Join-Path $_.directoryname $_.basename) -Type leaf) {Remove-Item (Join-Path $_.directoryname $_.basename)} }
```

!!! warning 
    None of these options should be taken lightly. `py7za-box` was written with default  settings that aim to avoid accidentally overwriting or deleting files and allowing you to recover from mistakes. However, the suggestions given here *will* cause files to be deleted and you and only you are responsible for choosing to use them. 
!!! tip
    In general: **don't kill runs, interrupt runs** using `Ctrl+C`.