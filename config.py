# Defines class that presents parameter configuration

import configparser # parse config file

## Config ######################################################################

class Config:

    # Configuration file path
    config_file      = ""
    # Path to folders containing source code
    document_folders = []
    # List of source code file extensions
    file_extns       = []

    # reset
    def reset(self):
        config_file      = ""
        document_folders = []
        file_extns       = []

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

    # return document folder list
    def docfolders (self):
        return self.document_folders

    # return valid file extension list
    def docfileextns (self):
        return self.file_extns

################################################################################
