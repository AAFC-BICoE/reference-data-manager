from brdm.BaseRefData import BaseRefData
from brdm.RefDataInterface import RefDataInterface
import os
import logging.config
import requests


class NcbiData(BaseRefData, RefDataInterface):

    def __init__(self, config_file):
        super(NcbiData, self).__init__(config_file)
        self.login_url = self.config['ncbi']['login_url']
        self.ncbi_user = self.config['ncbi']['user']
        self.ncbi_passw = self.config['ncbi']['password']
        self.chunk_size = self.config['ncbi']['chunk_size']
        try:
            self.destination_dir = os.path.join(super(NcbiData, self).destination_dir, self.config['ncbi']['destination_folder'])
            if not os.path.exists(self.destination_dir):
                os.makedirs(self.destination_dir, mode = self.folder_mode)
            os.chdir(self.destination_dir)

            self.backup_dir = os.path.join(super(NcbiData, self).backup_dir, self.config['ncbi']['destination_folder'])
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir, mode = self.folder_mode)
        except Exception as e:
            logging.error("Failed to create the destination or backup_dir with error {}".format(e))
   
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


    def download(self):
        logging.info("Downloading all of NCBI reference data ... Nothing to do.")
        pass

    def update(self):
        logging.info("Updating all of NCBI reference data ... Nothing to do.")
        pass

    def backup(self):
        logging.info("Backing up all of NCBI reference data ... Nothing to do.")
        pass

    def restore(self,folder_name):
        logging.info("Restoringing all of NCBI reference data ... Nothing to do.")
        pass

    # Login to NCBI
    def https_connect(self):
        logging.info('Connecting to NCBI https: {}'.format(self.login_url))
        login_data = {
                'username': self.ncbi_user,
                'password': self.ncbi_passw
                }
        retry_num = self.connection_retry_num
        session_requests = requests.Session()
        connected = False
        while not connected and retry_num != 0:
            try:
                session_requests.post(self.login_url, data=login_data)
                connected = True
            except Exception as e:
                logging.error("Error connecting to login_url {}: {} Retrying...".format(self.login_url, e))
                time.sleep(self.sleep_time)
                retry_num -= 1
        return session_requests, connected
    
    # Download a file 
    def download_a_file(self, file_name, file_address, session_requests):
        chunkSize = self.chunk_size
        totalSize = 0
        try:    
            res = session_requests.get(file_address, stream=True, verify=False)
            with open(file_name, 'wb') as output:
                chunknumber = 0
                for chunk in res.iter_content(chunk_size=chunkSize, decode_unicode=False):
                    if chunk:
                        totalSize = totalSize + chunkSize
                        chunknumber += 1
                        output.write(chunk)
            os.chmod(file_name, self.file_mode)
        except Exception as e:
            logging.exception('Failed to download file {}.{}'.format(file_name,e))
            return False
        
        return True