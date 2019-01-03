import os
import shutil
import tempfile
import requests
import re
import logging.config
import tarfile
import time
from distutils.dir_util import copy_tree
from bs4 import BeautifulSoup
from brdm.NcbiData import NcbiData
from brdm.RefDataInterface import RefDataInterface


class NcbiBlastData(NcbiData, RefDataInterface):

    def __init__(self, config_file):
        """Initialize the object"""
        super(NcbiBlastData, self).__init__(config_file)
        self.download_folder = \
            self.config['ncbi']['blast_db']['download_folder']
        self.info_file_name = self.config['ncbi']['blast_db']['info_file_name']
        try:
            self.destination_dir = os.path.join(
                        super(NcbiBlastData, self).destination_dir,
                        self.config['ncbi']['blast_db']['destination_folder'])
            self.backup_dir = os.path.join(
                        super(NcbiBlastData, self).backup_dir,
                        self.config['ncbi']['blast_db']['destination_folder'])
            if not os.path.exists(self.destination_dir):
                os.makedirs(self.destination_dir, mode=self.folder_mode)
            os.chdir(self.destination_dir)
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir, mode=self.folder_mode)
        except Exception as e:
            logging.error('Failed to create destination/backup folder: {}'
                          .format(e))

    def update(self, file_number=0):
        """Update NCBI nrnt blast database"""
        logging.info('Executing NCBI Blast update')
        # Download nrnt data into an intermediate folder
        temp_dir = self.create_tmp_dir(self.destination_dir)
        if not temp_dir:
            logging.error('Failed to create the temp_dir: {}, error{}'
                          .format(temp_dir, e))
            return False
        success = self.download(download_file_number=file_number)
        if not success:
            logging.error('Failed to download nrnt files.')
            return False
        # Change the file mode
        try:
            only_files = [f for f in os.listdir('.') if os.path.isfile(f)]
            for f in only_files:
                os.chmod(f, self.file_mode)
        except Exception as e:
            logging.error('Failed to change file mode, error{}'.format(e))
            return False
        # Backup two readme files
        backup_success = self.backup()
        if not backup_success:
            logging.error('Failed to backup readme files.')
            return False
        # Delete all data from the destination folder
        clean_ok = self.clean_destination_dir(self.destination_dir)
        if not clean_ok:
            logging.error('Failed to remove old files in destination folder')
            return False
        # Copy data from intermediate folder to destination folder
        # Delete intermediate folder
        try:
            copy_tree(temp_dir, self.destination_dir)
            shutil.rmtree(temp_dir)
        except Exception as e:
            logging.error('Failed to copy file from temp to destination {}'
                          .format(e))
            return False
        return True

    # Backup readme and readme+ file
    def backup(self):
        """Backup readme and README+ files"""
        logging.info('Executing NCBI Blast backup')
        backup_folder = self.create_backup_dir()
        if not backup_folder:
            logging.error('Failed to create backup folder.')
            return False
        # Copy only README files for future reference
        app_readme_file = self.config['readme_file']
        ncbi_readme_file = self.info_file_name
        try:
            shutil.copy2(app_readme_file, backup_folder)
            shutil.copy2(ncbi_readme_file, backup_folder)
        except Exception as e:
            logging.exception('NCBI Blast Backup did not succeed. Error: {}'
                              .format(e))
            return False
        return True

    def restore(self):
        # 2018.05.28: As agreed upon, this feature will not be implemented.
        # There is no backup functionality for blast databases,
        # therefore there is no restore.
        pass

    # Unzip all of nrnt files
    def unzip(self):
        """Unzip all the nrnt files"""
        try:
            zipped_files = [f for f in os.listdir('.') if os.path.isfile(f)]
            for file in zipped_files:
                unzipped = self.unzip_file(file)
                if not unzipped:
                    logging.error('Failed to unzip {}'.format(file))
                    return False
            all_files = [f for f in os.listdir('.') if os.path.isfile(f)]
            for f in all_files:
                os.chmod(f, self.file_mode)
        except Exception as e:
            logging.error('Failed to unzip and change file mode {}'
                          .format(e))
            return False
        return True

    # Parse the webpage of ncbi blast to get the list of nrnt files
    def get_all_file(self, url):
        """Parse the webpage of ncbi blast to get the list of nrnt files

        Args:
            url (string): the link to ncbi blast database
        Return:
            A list of nrnt file names
        """
        result = []
        try:
            session_requests, connected = self.https_connect()
            html = session_requests.get(url)
            soup = BeautifulSoup(html.content, 'html.parser')
            nr_nt_re = re.compile(r'(nr|nt)\.\d{2,3}\.tar\.gz$')
            # nr_nt_re = re.compile('(nr|nt).d{2,3}.tar.gz$')
            links = soup.find_all('a')
            for a_link in links:
                file_name = a_link.string
                if nr_nt_re.match(file_name):
                    result.append(file_name)
            session_requests.close()
        except Exception as e:
            logging.info('Failed to get the list of nrnt files: {}'.format(e))
        print(len(result))
        return result

    # Download read me and all the nrnt files
    def download(self, download_file_number=0):
        """Download readme and all the nrnt files"""
        download_start_time = time.time()
        max_download_attempts = self.download_retry_num
        folder_url = os.path.join(self.login_url, self.download_folder)
        # Download read me
        readme_success = False
        attempt = 0
        while attempt < max_download_attempts and not readme_success:
            attempt += 1
            try:
                session_requests, connected = self.https_connect()
                file_name_readme = self.info_file_name
                file_url_readme = os.path.join(folder_url, file_name_readme)
                readme_success = self.download_a_file(
                        file_name_readme, file_url_readme, session_requests)
                session_requests.close()
            except Exception as e:
                logging.info('Failed to download readme on attempt {}:{}'
                             .format(attempt, e))
                time.sleep(self.sleep_time)
        if not readme_success:
            logging.error('Failed to download readme file')
            return False
        # Get the list of nrnt files
        all_file = self.get_all_file(folder_url)
        downloaded_file = []
        if len(all_file) == 0:
            logging.error('Failed to get the file list to download')
            return False
        if download_file_number == 0:
            download_file_number = len(all_file)
        # Download nrnt files
        attempt = 0
        while attempt < max_download_attempts and \
                len(downloaded_file) < download_file_number:
            try:
                session_requests, connected = self.https_connect()
                attempt += 1
                for file in all_file:
                    if file not in downloaded_file:
                        download_success = False
                        file_success = False
                        md5_success = False
                        file_name_nrnt = file
                        file_url_nrnt = os.path.join(
                                            folder_url, file_name_nrnt)
                        file_name_md5 = file+'.md5'
                        file_url_md5 = os.path.join(folder_url, file_name_md5)
                        file_success = self.download_a_file(
                            file_name_nrnt, file_url_nrnt, session_requests)
                        if file_success:
                            md5_success = self.download_a_file(
                                file_name_md5, file_url_md5, session_requests)
                        if md5_success:
                            download_success = self.checksum(file_name_md5,
                                                             file_name_nrnt)
                        if download_success:
                            downloaded_file.append(file)
                    if len(downloaded_file) == download_file_number:
                        break
                session_requests.close()

            except Exception as e:
                logging.exception('Errors in downloading nrnt files, \
                \nretry... {}'.format(e))
                time.sleep(self.sleep_time)

        if len(downloaded_file) < download_file_number:
            logging.error('Failed. downloaded {} out of {} files'
                          .format(len(downloaded_file), download_file_number))
            return False

        files_download_failed = []
        # Write application's README+ file
        comment = 'nr and nt blast datasets downloaded from NCBI.'
        self.write_readme(download_url='{}'.format(folder_url),
                          downloaded_files=downloaded_file,
                          download_failed_files=files_download_failed,
                          comment=comment,
                          execution_time=(time.time() - download_start_time))
        return True

    # Check the correctness of the downloaded file
    def checksum(self, md5_file, file_name):
        """Check the correctness of the downloaded file"""
        try:
            with open(md5_file, 'r') as f:
                md5_file_contents = f.read()
            md5_str = md5_file_contents.split(' ')[0]
            os.remove(md5_file)
        except Exception as e:
            logging.exception('Could not read MD5 file {}. \
            \nTry to download the file again'.format(file_name))
            return False
        if not self.check_md5(file_name, md5_str):
            logging.error('Failed in checksum. Download the file again.')
            return False
        return True
