from brdm.NcbiData import NcbiData
from brdm.RefDataInterface import RefDataInterface
import os, shutil
import tempfile
import requests
import re
import logging.config
import tarfile
import time
from distutils.dir_util import copy_tree
from bs4 import BeautifulSoup


class NcbiBlastData(NcbiData, RefDataInterface):

    def __init__(self, config_file):
        super(NcbiBlastData, self).__init__(config_file)
        self.download_folder = self.config['ncbi']['blast_db']['download_folder']
        self.info_file_name = self.config['ncbi']['blast_db']['info_file_name']
        try:
            self.destination_dir = os.path.join(super(NcbiBlastData, self).destination_dir, \
                                                self.config['ncbi']['blast_db']['destination_folder'])
            self.backup_dir = os.path.join(super(NcbiBlastData, self).backup_dir, \
                                           self.config['ncbi']['blast_db']['destination_folder'])
            if not os.path.exists(self.destination_dir):
                os.makedirs(self.destination_dir, mode = self.folder_mode)
            os.chdir(self.destination_dir)
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir, mode = self.folder_mode)
        except Exception as e:
            logging.error("Failed to create destination/backup folder : {} {}".format(self.backup_dir, e))

    
    def update(self):
        logging.info("Executing NCBI Blast update")
        # Download nrnt data into an intermediate folder
        temp_dir = self.create_tmp_dir(self.destination_dir)
        if not temp_dir:
            logging.error("Failed to create the temp_dir: {}, error{}".format(temp_dir, e))
            return False
        success = self.download()
        if not success:
            logging.error("Failed to download nrnt files. Update will not proceed.")
            return False
        # Change the file mode
        try:
            only_files = [f for f in os.listdir('.') if os.path.isfile(f)]
            for f in only_files:
                os.chmod(f, self.file_mode)   
        except Exception as e:
            logging.error("Failed to change file mode, error{}".format(e))
            return False
        
        # Backup two readme files
        backup_success = self.backup()
        if not backup_success:
            logging.error("Failed to backup readme files. The update will not continue.")
            return False
        # Delete all data from the destination folder
        clean_destination_ok = self.clean_destination_dir(self.destination_dir)
        if not clean_destination_ok:
            logging.error("Failed to remove old files from destination folder")
            return False
        # Copy data from intermediate folder to destination folder
        # Delete intermediate folder
        try:
            copy_tree(temp_dir, self.destination_dir) 
            shutil.rmtree(temp_dir)
        except Exception as e:
            logging.error("Failed to copy file from temp to destination, error{}".format(e))
            return False
        
        return True
    
    # Backup readme and readme+ file
    def backup(self):
        logging.info("Executing NCBI Blast backup")
        backup_folder = self.create_backup_dir()
        if not backup_folder:
            logging.error("Failed to create backup folder.")
            return False
        # Copy only README files for future reference
        app_readme_file = self.config['readme_file']
        ncbi_readme_file = self.info_file_name
        try:
            shutil.copy2(app_readme_file, backup_folder)
            shutil.copy2(ncbi_readme_file, backup_folder)
        except Exception as e:
            logging.exception("NCBI Blast Backup did not succeed. Error: {}".format(e))
            return False
        return True


    def restore(self):
        # 2018.05.28: As agreed upon, this feature will not be implemented.
        # There is no backup functionality for blast databases, therefore there is no restore.
        pass
    
    # Unzip all of nrnt files
    def unzip(self):
        try:
            zipped_files = [f for f in os.listdir('.') if os.path.isfile(f)]
            for file in zipped_files:
                unzipped = self.unzip_file(file)
                if not unzipped:
                    logging.error("Failed to unzip {}".format(file))
                    return False
                
            all_files = [f for f in os.listdir('.') if os.path.isfile(f)]
            for f in all_files:
                os.chmod(f, self.file_mode)   
                
        except Exception as e:
            logging.error("Failed to unzip and change file mode, error{}".format(e))
            return False
        return True
    
    # Parse the webpage of ncbi blast to get the list of nrnt files
    def get_all_file(self, url):
        result = []
        try:
            session_requests,connected = self.https_connect();
            html = session_requests.get(url)
            soup = BeautifulSoup(html.content, "html.parser")
            nr_nt_re = re.compile('(nr|nt)\.\d{2}\.tar\.gz$')
            links = soup.find_all('a')
            for a_link in links:
                file_name = a_link.string
                if nr_nt_re.match(file_name):
                    result.append(file_name)
            session_requests.close()
        except Exception as e:
                logging.info("Failed to get the list of nrnt files: {}".format(e)) 
        return result


    # Download read me and all the nrnt files
    def download(self, download_file_number=0):
        download_start_time = time.time()
        max_download_attempts = self.download_retry_num
        folder_url = os.path.join(self.login_url, self.download_folder)
        # download read me
        readme_success = False
        attempt = 0
        while attempt < max_download_attempts and not readme_success:
            attempt += 1
            try:
                session_requests,connected = self.https_connect();
                file_name_readme = self.info_file_name
                file_url_readme = os.path.join(folder_url, file_name_readme)
                readme_success = self.download_a_file(file_name_readme, file_url_readme, session_requests)
                session_requests.close()
            except Exception as e:
                logging.info("Failed to download readme file on attempt {}: {}".format(attempt, e)) 
                time.sleep(self.sleep_time)
                
        if not readme_success:
            logging.error('Failed to download readme file')
            return False
        # get the list of nrnt files
        all_file = self.get_all_file(folder_url)
        downloaded_file = []
        
        if len(all_file) == 0:
            logging.error("Failed to get the file list to download")
            return False
        
        if download_file_number == 0:
            download_file_number = len(all_file)
        
        attempt = 0
        while attempt < max_download_attempts and len(downloaded_file) < download_file_number:
            try:
                session_requests,connected = self.https_connect();
                attempt += 1
                for file in all_file:
                    if file not in downloaded_file:
                        download_success = False
                        file_name_nrnt = file
                        file_url_nrnt = os.path.join(folder_url, file_name_nrnt)
                        file_name_md5 = file+".md5"
                        file_url_md5 = os.path.join(folder_url, file_name_md5)
                        file_success = self.download_a_file(file_name_nrnt, file_url_nrnt, session_requests)
                        md5_success = self.download_a_file(file_name_md5, file_url_md5, session_requests)
                        
                        download_success = self.checksum(file_name_md5, file_name_nrnt)
                        
                        if download_success:
                            downloaded_file.append(file)
                            
                    if len(downloaded_file) == download_file_number:
                        break;
                session_requests.close()    
                
            except Exception as e:
                logging.exception("Errors in downloading nrnt files, retry... {}".format(e))
                time.sleep(self.sleep_time)
                
        if len(downloaded_file) < download_file_number: 
            logging.error("Failed. downloaded {} out of {} files".format(len(downloaded_file),download_file_number)) 
            return False
        
        files_download_failed = []
        # Write application's README+ file
        comment = 'This folder contains a reference blast database (nr and nt datasets) downloaded from NCBI.'
        self.write_readme(download_url='{}'.format(folder_url),
                          downloaded_files=downloaded_file, download_failed_files=files_download_failed,
                          comment=comment, execution_time=(time.time() - download_start_time))

        return True
    
    # Check the correctness of the downloaded file
    def checksum(self, md5_file, file_name):
        try:
            with open(md5_file, 'r') as f:
                md5_file_contents = f.read()
            md5_str = md5_file_contents.split(' ')[0]
            os.remove(md5_file)
        except Exception as e:
            logging.exception('Could not read MD5 file {}. Try to download the file again'.format(file_name))
            return False
        
        if not self.check_md5(file_name, md5_str):
            logging.warning("MD5 check did not pass. Try to download the file again.")
            return False

        return True
    