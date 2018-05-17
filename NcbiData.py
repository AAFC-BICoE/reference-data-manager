from BaseRefData import BaseRefData
import os

class NcbiData(BaseRefData):

    def __init__(self, config_file):
        super(NcbiData, self).__init__(config_file)
        self.__update_feq = self.config['ncbi']['update_frequency']

    def getUpdateFrequency(self):
        return self.__update_feq

    def getDownloadUrl(self):
        pass

    def getDestinationFolder(self):
        pass


    def testConnection(self):
        pass


    def download(self):
        pass

