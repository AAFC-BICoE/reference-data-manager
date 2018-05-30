from BaseRefData import BaseRefData
from RefDataInterface import RefDataInterface
import os
import logging.config
import ftplib
import re

class NcbiData(BaseRefData, RefDataInterface):

    def __init__(self, config_file):
        super(NcbiData, self).__init__(config_file)

        self.destination_dir = super(NcbiData, self).destination_dir + self.config['ncbi']['destination_folder']
        if not os.path.exists(self.destination_dir):
            os.makedirs(self.destination_dir)
        os.chdir(self.destination_dir)


    @property
    def destination_dir(self):
        return self._destination_dir

    @destination_dir.setter
    def destination_dir(self, value):
        self._destination_dir = value


    def getDownloadUrl(self):
        pass
    '''
    def getDestinationFolder(self):
        return super(NcbiData, self).getDestinationFolder() + self.config['ncbi']['destination_folder']
    '''

    def testConnection(self):
        logging.info("Testing connection to NCBI... Nothing to do.")
        pass

    def download(self):
        logging.info("Downloading all of NCBI reference data ... Nothing to do.")
        pass

    def update(self):
        logging.info("Updating all of NCBI reference data ... Nothing to do.")
        pass

    def backup(self):
        logging.info("Backing up all of NCBI reference data ... Nothing to do.")
        pass

    def restore(self):
        logging.info("Restoringing all of NCBI reference data ... Nothing to do.")
        pass

