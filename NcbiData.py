from BaseRefData import BaseRefData
from RefDataInterface import RefDataInterface
import os

class NcbiData(BaseRefData, RefDataInterface):

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

    def download(self):
        pass

    def update(self):
        pass

    def backup(self):
        pass

    def restore(self):
        pass


    ####################################
    ### Individual download methods  ###
    ####################################

    # Download all nr / nt blast databases
    def downloadBlastDB(self):
        blast_db_folder = self.getDestinationFolder() + self.config['ncbi']['blast_db']['destination_folder']
        blast_db_ftp = self.config['ncbi']['blast_db']['ftp']

        #TODO: Check time, and if it is not after hours for ncbi, give a warning
        # Check out warning.warn(): https://docs.python.org/3/library/warnings.html#warnings.warn

        # docs
        self.download_file(blast_db_ftp + "README", blast_db_folder)
        comment = 'This is all nr / nt datasets downloaded from ncbi.'
        self.write_readme(download_url=blast_db_ftp, files=['file1','file2', 'file3'], comment = comment)

        # List of download files


