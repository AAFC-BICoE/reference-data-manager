from brdm.BaseRefData import BaseRefData
from brdm.RefDataInterface import RefDataInterface
import os
import logging.config
import ftplib


class NcbiData(BaseRefData, RefDataInterface):

    def __init__(self, config_file):
        super(NcbiData, self).__init__(config_file)

        self.destination_dir = super(NcbiData, self).destination_dir + self.config['ncbi']['destination_folder']
        if not os.path.exists(self.destination_dir):
            os.makedirs(self.destination_dir)
        os.chdir(self.destination_dir)

        self.backup_dir = super(NcbiData, self).backup_dir + self.config['ncbi']['destination_folder']
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)


    @property
    def destination_dir(self):
        return self._destination_dir

    @destination_dir.setter
    def destination_dir(self, value):
        self._destination_dir = value

    @property
    def backup_dir(self):
        return self._backup_dir

    @backup_dir.setter
    def backup_dir(self, value):
        self._backup_dir = value


    def getDownloadUrl(self):
        pass
    '''
    def getDestinationFolder(self):
        return super(NcbiData, self).getDestinationFolder() + self.config['ncbi']['destination_folder']
    '''

    def test_connection(self):
        connection_successful = False

        try:
            ftp = ftplib.FTP(self._download_ftp)
            ftp.login(user=self._ncbi_user, passwd=self._ncbi_passw)

            response = ftp.voidcmd('NOOP')

            if response == '200 NOOP command successful':
                connection_successful = True

            ftp.quit()
        except:
            return False

        return connection_successful


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

