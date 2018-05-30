from NcbiData import NcbiData
from RefDataInterface import RefDataInterface
import os
import ftplib
import re
import logging.config

class NcbiBlastData(NcbiData, RefDataInterface):

    def __init__(self, config_file):
        super(NcbiBlastData, self).__init__(config_file)

        self.destination_dir = super(NcbiBlastData, self).destination_dir + self.config['ncbi']['blast_db']['destination_folder']
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
        return super(NcbiBlastData, self).getDestinationFolder() + self.config['ncbi']['blast_db']['destination_folder']
    '''

    def testConnection(self):
        pass

    def update(self):
        pass

    def backup(self):
        # NCBI does not archive old nr/nt databases. Since we do not have the capacity to store this as a redundant db,
        # this function will not be implemented. If there is a need to restore the old versions of nr/nt datasets,
        # then the requirements need to be re-evaluated.
        pass

    def restore(self):
        # There is not backup functionality for blast databases, therefore there is no restore.
        pass


    # Download all nr / nt blast databases
    def download(self, test_number=0):

        blast_db_ftp = self.config['ncbi']['blast_db']['ftp']
        ftp_dir = self.config['ncbi']['blast_db']['ftp_dir']

        #TODO: Check time, and if it is not after hours for ncbi, give a warning
        # Check out warning.warn(): https://docs.python.org/3/library/warnings.html#warnings.warn

        ftp = ftplib.FTP(blast_db_ftp)
        ftp.login(user='anonymous', passwd='anonymous')

        try:
            ftp.cwd(ftp_dir)

            # Get list of files to download
            all_files = ftp.nlst()

            nr_nt_re = re.compile('(nr|nt)\.\d{2}\.tar\.gz$')

            nr_nt_files = [file_name for file_name in all_files if nr_nt_re.match(file_name)]

            # Write docs
            comment = 'This is full blast database (all of nr / nt datasets) downloaded from ncbi.'
            self.write_readme(download_url=blast_db_ftp, files=nr_nt_files, comment=comment)


            #self.download_file(blast_db_ftp + "README", blast_db_folder)
            readme_file = 'README'
            with open(readme_file, 'wb') as f:
                ftp.retrbinary('RETR ' + readme_file, f.write, 1024)

        except:
            logging.exception("Exception when trying to download blast database from NCBI.")
            ftp.quit()

        ftp.quit()


