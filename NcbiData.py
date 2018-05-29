from BaseRefData import BaseRefData
from RefDataInterface import RefDataInterface
import os
import ftplib
import re

class NcbiData(BaseRefData, RefDataInterface):

    def __init__(self, config_file):
        super(NcbiData, self).__init__(config_file)

        self.destination_dir = super(NcbiData, self).destination_dir + self.config['ncbi']['destination_folder']
        if not os.path.exists(self.destination_dir):
            os.makedirs(self.destination_dir)


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
        pass

    def download(self):
        pass

    def update(self):
        pass

    def backup(self):
        pass

    def restore(self):
        pass

