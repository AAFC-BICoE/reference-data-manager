from BaseRefData import BaseRefData
from RefDataInterface import RefDataInterface
import os

class NcbiData(RefDataInterface, BaseRefData):

    def __init__(self, config_file):
        super(NcbiData, self).__init__(config_file)
        self.__update_feq = self.config['ncbi']['update_frequency']

    def getUpdateFrequency(self):
        return self.__update_feq

    def getDownloadUrl(self):
        pass

    def getDestinationFolder(self):
        return super(NcbiData, self).getDestinationFolder() + self.config['ncbi']['destination_folder']


    def testConnection(self):
        pass


    # Aggregate method that will call all download methods for ncbi
    def download(self):
        pass


    ####################################
    ### Individual download methods  ###
    ####################################

    # Download all nr / nt blast databases
    def downloadBlastDB(self):
        blast_db_folder = ''
        blast_db_ftp = ''
