## This file exports various utility functions

import os

## Given a path to a file
#  returns the contents of the file
def file_contents (fpath):

    fc = ""

    with open(fpath) as f:
        fc = f.read()

    return fc

## Given a path to a directory
#  returns a list of paths of files and folders inside the directory recursively
def rec_scandir(directory):

    scanlist = []

    assert (os.path.exists(directory))
    assert (os.path.isdir(directory))

    for f in os.listdir(directory):

        # path to f
        fpath = os.path.join(directory, f)

        if (os.path.isdir(fpath)):
            scanlist = scanlist + rec_scandir(fpath)
        else:
            scanlist.append(fpath)

    return scanlist

################################################################################
