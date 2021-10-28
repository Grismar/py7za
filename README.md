# Py7za ("pizza")

Python wrapper for running the 7za.exe utility from https://www.7-zip.org/

The wrapper simply runs the application in a separate process and provides the following added functionality:
- capture and parse output (overriding any `-bs_` arguments)
- track progress and some basic metrics (size, files processed, etc.)

Other than providing that utility, the wrapper tries to provide users access to 7za in a way as simple, and as close to the original as possible. See some documentation for the command line options here https://sevenzip.osdn.jp/chm/cmdline/index.htm (no affiliation).

Additionally, the package contains the `AsyncIOPool` class, which allows you to queue up a large number of asynchronous tasks, and it will keep a certain number of them running at all times, until all tasks are done. This works for any `asyncio` `Task`, but can be handily combined with `Py7za` (see below).

Finally, a command line utility `py7za-box` is included, which allows you to quickly replace individual files with their zipped equivalent in-place and vice versa, without writing any code. The idea is that a user may want to zip many files in a large project, without removing them from their original location, and still be able to find them by name and easily extract them individually.

## Install

Install the package:
```commandline
pip install py7za
```

Of if you want to use the command-line interface `py7za-box`, make sure the dependencies for it are installed like this: 
```commandline
pip install py7za[box]
py7za-box --help
```

On Linux, you will have to have `p7zip` installed, as there is no Linux binary included in the package. For example:
```commandline
sudo yum install -y p7zip
```

## Example

With the package installed, try running this script:
```
from py7za import Py7za

# zip all .txt files in c:\temp and subdirectories to texts.zip
Py7za.run(r'a c:\temp\*.txt texts.zip -r')
```

A simple example use of `AsyncIOPool`, to run multiple copies of 7za in parallel:
```python
from py7za import AsyncIOPool, Py7za
from pathlib import Path
from asyncio import run

async def zip_many(root, glob, target='.'):
    async for task_result in AsyncIOPool(pool_size=4).arun_many(
            [Py7za(f'a {target}/{fn.name}.zip {fn}') for fn in Path(root).glob(glob)]):
        print(task_result.arguments, task_result.return_code)

run(zip_many('c:/documents', '*.bak', target='c:/temp'))
```
This function would find a bunch of files and create zip files for each in another location, with 4 copies of 7za running at any time, until it's done.

Note: 7za supports multicore compression when compressing multiple files into a single archive. So if you're compressing many files into a few archives, it may not be optimal to create a pool with as many tasks as you have cores.

### Command line py7za-box

To quickly replace every .csv file in a folder and all its sub-folders with a zip-file containing that .csv:
```commandline
py7za-box **/*.csv
```

And the reverse:
```commandline
py7za-box **/*.csv.zip --unbox
```

A more elaborate example:
```commandline
py7za-box **/*.csv **/*.txt --root c:/temp --folders --verbose -7 "-mx=9 -psecret" 
```

This would run `py7za-box` with `c:/temp` as the working directory, matching all .csv and .txt files in it and its sub-folders, printing the command line for each execution of 7za as it happens. The `--folders` ensures that the sub-folder structure relative to `c:/temp` is preserved in the archives. The extra options passed to 7za ensure maximum compression and set a password on the archive.

### Structure and Folders

There is a clear distinction between the `--structure` and `--folders` options for `py7za-box`, which may not be immediately obvious.

Compare these sets of statements:
```commandline
py7za-box **/*.csv --structure 0 --folders 0 --target output
py7za-box **/*.csv --structure 1 --folders 0 --target output  # this is the default!
py7za-box **/*.csv --structure 0 --folders 1 --target output
```
All three will try and find all .csv files in the current folder (because no alternative `--root` was provided) and all sub-folders, and create individual archives for each.

The first will create all those archives directly in `output`, and the archives will only contain the .csv itself, no folder structure. So, if the current folder contains a file `files/data.csv`, an archive called `output/data.csv.zip` will be created, containing only `data.csv`.

The second will recreate the folder structure relative to the source folder, putting each archive in sub-folders created in `output`, but the archives will still only contain the .csv itself. Again, if the current folder contains a file `files/data.csv`, an archive called `output/files/data.csv.zip` will be created, containing only `data.csv`. This is the default and works most naturally when not providing a `--target`, but performing the archival in place, and deleting the originals, which is also the default.

The third will create all the archives directly in `output`, but the archives will contain the sub-folder structure as well as the .csv itself. Again, if the current folder contains a file `files/data.csv`, an archive called `output/data.csv.zip` will be created, containing `files/data.csv`.

Note that you could also set both `--structure` and `--folders` to be true, but that would create an archive `output/files/data.csv`, which would contain `files/data.csv`; when extracting the resulting files, care would need to be taken to avoid files ending up in double sub-folder structures, so a warning is issued if you combine these options.

Also note that `py7za-box **/*.csv --structure 0 --folders 1 --target output` is not the same as `7za.exe a output/archive.zip *.csv -r`. The latter creates a single archive, not one archive for each file, which is the purpose of `py7za-box`.  

## Dependencies

The only external dependency is on `conffu` for the configuration of the command-line tool. If you only want to use the Py7za class, and just use `pip install py7za`, this dependency won't be installed. 

## License

This package is licensed under the MIT license. See [LICENSE.txt](https://gitlab.com/Jaap.vanderVelde/py7za/-/blob/master/LICENSE.txt).

## Changelog

See [CHANGELOG.md](https://gitlab.com/Jaap.vanderVelde/py7za/-/blob/master/CHANGELOG.md).
