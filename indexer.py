# This program creates an inverted index from the source code various document
# folders as mentioned in the params.cfg

from text_processing   import process_text, word_ngrams
from global_statistics import GlobalStatistics, GSFILE
from config            import Config
from index             import *
from docid_mapper      import DocIDMapper

from utils             import file_contents, rec_scandir

import argparse
from   argparse import RawTextHelpFormatter
import os
import shutil

## Globals #####################################################################
# Print to terminal about what the program is doing
# this is set by input to the program
verbose = False

## Help strings ################################################################

program_help = '''

    indexer.py tokenizes source code and constructs an index file (.idx)

    Argument 1: configfile - Path to cofiguration file. Please refer to ./params.ini
                             for config file format

    Argument 2: indexstore  - Folder where the output index file along with
                              other information such as global statistics is
                              stored

    Argument 3: ngrams      - Number of ngrams to index. Defaults to 1

    Argument 4: verbose     - Print progress of the program to the stdout.
                              This argument is optional.

    EXAMPLES:

        python indexer.py --configfile=./params.ini --indexstore=cacm.index --ngrams=1 --verbose
    '''

configfile_help = '''
    Path to cofiguration file. Please refer to ./params.ini for config file format
    '''

indexstore_help = '''
    Folder where the output index file along with other information such as
    global statistics is stored
    '''

ngrams_help = '''
    Number of ngrams to index. defaults to 1
    '''

verbose_help = '''
    Print progress of the program to the stdout. This argument is optional.
    '''
## Setup argument parser #######################################################

argparser = argparse.ArgumentParser(description = program_help,
                                    formatter_class = RawTextHelpFormatter)

argparser.add_argument("--configfile",
                       metavar  = "cf",
                       required = True,
                       type     = str,
                       help     = configfile_help)

argparser.add_argument("--indexstore",
                       metavar  = "o",
                       required = True,
                       type     = str,
                       help     = indexstore_help)

argparser.add_argument("--ngrams",
                       metavar = "n",
                       default = 1,
                       type    = int,
                       help    = ngrams_help)

argparser.add_argument("--verbose",
                       dest    = 'verbose',
                       action  = 'store_true',
                       help    = verbose_help)

## Utilities ##################################################################

# String -> Print output to terminal
# Given a string, print it to terminal if verbose is set in input arguments
def print_verbose(s):
    if verbose:
        print (s)

# Store global statistics
# Given the path to a folder where to store the global stats information and
#       the #terms per document dictionary whose (key, value) pair is
#       (docid, #terms in doc)
#
# Store all global statistics information to the global statistics file
#
def store_global_stats(indexstore, terms_per_document):

    # Total number of docs indexed
    N = len(terms_per_document)

    # Corpus size
    cs = reduce(lambda cs, doc_tf: cs + doc_tf[1], \
                terms_per_document.items(),        \
                0)

    # Corpus size is the sum of all document lenghts. avdl is cs/N
    # Average doclength
    avdl = (float(cs) / float(N))

    # doclengths is nothing be terms_per_document

    # create global stats
    gs = GlobalStatistics(os.path.join(indexstore, GSFILE))
    # load global stats
    gs.load(N, cs, avdl, terms_per_document)
    # store stats
    gs.write()

    return

# Given a path to a file and
#       a list of file extensions
# Return true iff the file ends with any extension in the input list
def has_extn(fpath, extns):
    return any(map(lambda extn: fpath.endswith(extn), extns))

# Given an object of the Config class, that contains information on what files
#       in what folders to index
# Returns a list of paths to all files, that are expected to be indexed
def files_to_index (pconfig):

    # Initialize return list
    files = []

    # docfolders
    docfolders = pconfig.docfolders()

    # valid file extensions
    docfileextns = pconfig.docfileextns()

    # blacklisted file extensions
    blacklistextns = pconfig.blacklistedextns()

    # for every docfolder
    for docfolder in docfolders:

        assert (os.path.exists(docfolder))

        fpaths = rec_scandir(docfolder)

        # filter paths with blacklisted file extns
        fpaths = filter(lambda fpath: not has_extn(fpath, blacklistextns), fpaths)

        files = files + filter(lambda fpath: has_extn(fpath, docfileextns), fpaths)

    return files

## Indexer functions ###########################################################

# given an object of the Config class, that holds information on what folders and
#       and files to parse and index,
#       a folder where the constructed index should be stored,
#       the number of words consisting a term,
# then create the output index file
def indexer(pconfig, indexstore, n):

    # create an empty index
    invidx = Index(indexstore)

    # global statistics information
    terms_per_document = {}

    # Files to index
    docfiles = files_to_index(pconfig)

    # docid mapper; Maps documentID to a tuple of (corpus_file_path, document_path);
    # We dont have corpus file path we have only the document file path
    docid_map = {}

    # For every file
    for docf in docfiles:

        # docid of file f
        docid = docfiles.index(docf)

        # update docid map
        assert (docid_map.get(docid) is None)
        docid_map[docid] = ("NO-CORPUS-FILE", docf)

        # progress
        print_verbose("Adding document"  + " (" +  str(docid + 1) + "/" + \
                      str(len(docfiles)) + ") " + docf + " to index")

        # docfile contents
        content = file_contents(docf)

        # text process content
        content = process_text(content)

        # assert that content has no whitespace other than '\n'
        assert(all(map(lambda w: w.strip() == w, content.split(" "))))

        # get word ngrams
        terms = word_ngrams(content, n)

        # assert word ngrams
        assert(all(map(lambda ng: len(ng.split(" ")) == n, terms)))

        # store global statistic, terms_per_document
        terms_per_document[docid] = len(terms)

        # store terms
        for posidx in range(0, len(terms)):
            # term and term position
            term = terms[posidx]
            tpos = posidx
            invidx.update(term, tpos, docid)

    # store index to a file inside corpusstore
    invidx.store()

    # Copy the document map file from corpusstore to indexstore
    DocIDMapper().store(indexstore, docid_map)

    # store global statistics
    store_global_stats(indexstore, terms_per_document)

    print "\nSuccess : Index created - ", indexstore


## Main ########################################################################

## Get arguments
args = vars(argparser.parse_args())

## Inputs
configfile  = args['configfile']
indexstore  = args['indexstore']
ngrams      = args['ngrams']
verbose     = args['verbose']

## Input check
if (not os.path.exists(configfile)):
    print ("FATAL: Cannot find config file ", configfile)
    exit(-1)
if (ngrams <= 0):
    print ("FATAL: ngrams should be > 0")
    exit(-1)

## Config file sanity check. If we are able to make a Config class object. We r set
pconfig = Config(configfile)

## Delete any indexstore previously present
if (os.path.exists(indexstore)):
    print ("DELETING EXISTING INDEXSTORE  ", indexstore)
    shutil.rmtree(indexstore)

# Create index
indexer(pconfig, indexstore, ngrams)

# print the index
#Index(indexfile).print_index()
