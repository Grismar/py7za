Py7za was written to automate the archival of individual files the open source 7-zip command line tool 7za. This is particularly useful for very large file collections that consist of files that compress reasonably well and to which you don't need access most of the time, while still wanting these files to show up in searches and allowing for quick extraction.

The specific use case for which it was developed was compressing the outputs of modelling software, like the hydro-dynamic modelling software TUFLOW, but it is completely agnostic of what files it is operating on. It can be used as a Python library, but it is most useful through its command-line utility `py7za-box` ('pizza box'), or its short aliases `box` and `unbox`.

- `py7za-box` runs on Windows and Linux 
- `Py7za` makes optimal use of computing power of the machine it's running on by running compression on as many cores as it can get, or are specified by you
- `Py7za` is designed to be fairly robust to user mistakes - normal use should not cause irreversible trouble with your filesets

!!! note
    The word 'archival' can be tricky. For Py7za, when talking about 'archival', what is meant is "compression into an archive file format like `.7z` or `.zip`". Of course performing a bunch of 'archival' (i.e. boxing the files with Py7za) before 'archiving' a large file set, in the sense of filing it away for long term storage, can be a very good idea. 