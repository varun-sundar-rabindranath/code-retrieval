# Defines class that presents parameter configuration

import configparser # parse config file
import os

## Config ######################################################################

class Config:

    # Configuration file path
    config_file          = ""
    # Path to folders containing source code
    document_folders     = []
    # List of source code file extensions
    file_extns           = []
    # List of file extensions that are blacklisted
    file_extns_blacklist = []

    # reset
    def reset(self):
        config_file          = ""
        document_folders     = []
        file_extns           = []
        file_extns_blacklist = []

    # Constructor
    def __init__(self, config_file_):

        # reset
        self.reset()

        # input check
        assert (os.path.exists(config_file_))

        self.config_file = config_file_

        # Set up config parser
        config_parser = configparser.ConfigParser()
        config_parser.read(self.config_file)

        # Parse document folders info from config file
        self.document_folders = map(lambda x: x.strip(), \
                                    config_parser.get("DOCUMENTS", "DOCLIST").split(","))
        # Parse src file extensions info from config file
        self.file_extns = map(lambda x: x.strip(), \
                              config_parser.get("EXTN", "EXTNLIST").split(","))
        # Parse blacklisted src file extensions info from config file
        self.file_extns_blacklist = map(lambda x: x.strip(), \
                                        config_parser.get("EXTN", "EXTNBLACKLIST").split(","))

        # Config sanity check
        assert(all(map(lambda folder: os.path.exists(folder), self.document_folders)))

    # return document folder list
    def docfolders (self):
        return self.document_folders

    # return valid file extension list
    def docfileextns (self):
        return self.file_extns

    # return blacklisted file extensions
    def blacklistedextns (self):
        return self.file_extns_blacklist

################################################################################
