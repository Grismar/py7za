## Getting started

Although you don't need to know any Python to use Py7za, you do need Python installed. Also, `pip` is recommended for installing Py7za and keeping it up to date. Standard installations of Python include `pip`.

### Installation

It is strongly recommended you install Py7za in its own virtual environment, or an environment that you reserve for system-wide command-line tools, but outside of environments you need for development that don't rely on Py7za. If you do create a separate virtual environment, remember that it will need to be (re)activated prior to using Py7za. 

You can install Py7za from PyPI using `pip` like this:
```commandline
python -m pip install py7za[box]
```

If you already have Treewalker installed and just need the latest version:
```commandline
python -m pip install py7za[box] --upgrade
```

If you just want to use the Python library `py7za` and don't need the command-line tool `py7za-box`, you can install it with: 
```commandline
python -m pip install py7za
```
This also does not install the only external package `py7za-box` depends on, `conffu`.

To uninstall:
```commandline
python -m pip uninstall py7za
```

After installation, you can check that `py7za-box` runs with:
```commandline
py7za-box --help
box --help
unbox --help
```
All three commands should show you the help for `py7za-box` on the command-line.

### Boxing and unboxing

To avoid confusion with normal 'zipping' and 'archiving', which would take many or all the files in a location and package them in a single archive, archiving and unarchiving with Py7za is called 'boxing' and 'unboxing'. If you 'box' a location, every file (or directories if you match them specifically) in it will be archived into its own archive file, a `.7z` file by default (for speed and size), but you can specify other supported formats, like `.zip` as well. The reverse operation is 'unboxing'.

Example:
```commandline
box **/* -r C:\Temp
```
The `box` command takes a series (at least one) of so-called 'glob pattern' as its first argument(s), and in most cases you will want to specify a root directory to run the command from, unless you want `box` to run in the current working directory (in which case `box **/*` would have been enough).

To undo that `box` command, you'd use this `unbox` command:
```commandline
unbox **/*.7z -r C:\Temp
```
This will run in the same root directory, but only matches the 7-zip files that were created by the `box` command (as 7-zip is the default format used). You could still use `**/*` but this would also match any new non-archive files that have since been created and that's undesirable.

Much can be said about glob patterns, but the important one to remember is `**/*`, which means every file in every subfolder of the root and in root itself; and `**/*.7z`, which means every `.7z` file in every subfolder of the root and in root itself. [More about glob patterns in the Configuration section](../configuration/#glob-patterns).

### Typical use

Typical use in a modelling setting, would be: either after completing a model run, or perhaps after parts of a project become less actively used by a team, the relevant folders are boxed. If a user needs access to boxed files later, quickly unboxing a subdirectory, or even a specific file or group of files (see also [File Groups](../configuration/#glob-patterns)) is just a quick operation on the command line - files do not have to be boxed or unboxed all together.

It's probably worth it to assess which file types save the most space when compressed for your type of project and to write some scripts or configuration files that only box those file types. For example, for TUFLOW modelling projects, we've found that boxing `.wrr`, `.2dm`, `.flt`, `.asc`, `.dfs2`, `.csv`, `.shp`, `.eof`, `.xf4`, `.txt`, `.tlf`, `.xf8`, `.sy2`, `.res11`, `.loc`, `.tot`, `.xp`, `.tsf`, `.ts1`, and `.mif` files (and the files some of them are grouped with, see also [File Groups](../configuration/#file-groups)) is most effective.

Most effective would be to write a simple batch file or shell script that contains a reusable command for boxing and unboxing files in your project. For example, a TUFLOW project will often contain files relevant to a run in several folders, but all of them will start with the same prefix. So a simple boxing batch file `mybox.bat` for such a project could look something like:
```commandline
@echo off
box **/%1*.wrr **/%1*.2dm **/%1*.flt **/%1*.asc **/%1*.dfs2 **/%1*.csv **/%1*.shp **/%1*.eof **/%1*.xf4 **/%1*.txt **/%1*.tlf **/%1*.xf8 **/%1*.sy2 **/%1*.res11 **/%1*.loc **/%1*.tot **/%1*.xp **/%1*.tsf **/%1*.ts1 **/%1*.mif -r "C:/my model/"
```
Then, to box all the files for a run for which the files start with `some_prefix`, you'd just run `mybox.bat some_prefix`.

Of course, this is just a simple example, but some scripting can really improve efficiency and avoid mistakes which may cause people to have trouble finding or using files.

Just remember that, as long as you have the space for all the files to expand into, you can always just run `unbox **/*.7z -r C:/my_project_location` to unbox everything.

!!! note
    To avoid accidentally exploding existing archives that happen to have been created with 7-zip as well, `unbox` will only extract archives that match the provided pattern if they only contain a single, matching file or folder. So you should not have to worry about accidentally extracting more than you bargained for. 