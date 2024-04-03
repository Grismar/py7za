This package is called Py7za ('pizza'), `py7za` is the Python module, `Py7za` the class you can import to use it and `py7za-box` is the CLI tool that runs both the `box` and `unbox` commands.

Py7za was written to automate archival of individual files the open source 7-zip command line tool 7za from https://www.7-zip.org/. This is particularly useful for very large file collections that consist of files that compress reasonably well, and which you don't need to access most of the time, while still wanting these files to show up in searches and allowing for quick extraction.

The [source code](https://gitlab.com/Jaap.vanderVelde/py7za) is available on GitLab, and you can read the [change log](https://gitlab.com/Jaap.vanderVelde/py7za/-/blob/master/CHANGELOG.md) there as well.

The specific use case for which it was developed was compressing the outputs of modelling software, like the hydro-dynamic modelling software TUFLOW, but it is completely agnostic of what files it is operating on. It can be used as a Python library, but it is most useful through its command-line utility `py7za-box`, in particular its short aliases `box` and `unbox`.

- `py7za-box`, `box` and `unbox` run on Windows and Linux 
- Py7za makes optimal use of computing power of the machine it's running on by running compression on as many cores as it can get, or are specified by you
- Py7za is designed to be fairly robust to user mistakes - normal use should not cause irreversible trouble with your filesets

!!! note
    The word 'archival' can be tricky. For Py7za, when talking about 'archival', what is meant is "compression into an archive file format like `.7z` or `.zip`". Of course performing a bunch of 'archival' (i.e. boxing the files with Py7za) before 'archiving' a large file set, in the sense of filing it away for long term storage, can be a very good idea.

!!! warning
    Py7za is written and tested for free and feedback is welcome, but remember you use it at your own risk. Read the documentation carefully and even if you have, the responsibility for any problems arising from its use is entirely yours!