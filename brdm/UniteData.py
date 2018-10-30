from brdm.BaseRefData import BaseRefData
from brdm.RefDataInterface import RefDataInterface
import os, shutil
import tempfile
import logging
import time
from distutils.dir_util import copy_tree
import requests, requests_ftp


class UniteData(BaseRefData, RefDataInterface):

    def __init__(self, config_file):
        super(UniteData, self).__init__(config_file)
        self.download_url = self.config['unite']['download_url']
        self.download_file = self.config['unite']['download_file']
        self.info_file_name = self.config['unite']['info_file_name']
        self.developer_path = self.config['unite']['developer_path']
        self.remove_path = self.config['unite']['remove_path']
        try:
            self.destination_dir = os.path.join(super(UniteData, self).destination_dir, \
                                                self.config['unite']['destination_folder'])
            if not os.path.exists(self.destination_dir):
                os.makedirs(self.destination_dir, mode = self.folder_mode)
            os.chdir(self.destination_dir)
            self.backup_dir = os.path.join(super(UniteData, self).backup_dir, \
                                           self.config['unite']['destination_folder'])
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir, mode = self.folder_mode)
        except Exception as e:
            logging.error("Failed to create the destination_dir or backup_dir with error {}".format(e))
            

    def update(self):
        logging.info("Executing unite update")
        # Download files into the intermediate folder 
        temp_dir = self.create_tmp_dir(self.destination_dir)
        if not temp_dir:
            logging.error("Failed to create the temp_dir: {}, error{}".format(temp_dir, e))
            return False
        # Download files into the intermediate folder 
        success = self.download()
        if not success:
            logging.error("Download failed. Update will not proceed.")
            return False
         
        # back up readme(qiime readme) and readme+ file
        # some unregular post processes (remvoe developer dir, remove data folder..)
        backup_success = self.backup()
        if not backup_success:
            logging.error("Failed to backup readme files. The update will not continue.")
            return False
        # Delete old files from the destination folder
        # Copy new files from intermediate folder to destination folder
        try:
            os.chdir(self.destination_dir)
            only_files = [f for f in os.listdir(".") if os.path.isfile(f)]
            for f in only_files:
                os.remove(f)
            copy_tree(temp_dir, self.destination_dir)
            shutil.rmtree(temp_dir)
        except Exception as e:
            logging.error("Failed to move files from temp_dir to destination folder, error{}".format(e))
            return False
    
        return True
        
   
    def download(self, test = False):
        logging.info("Executing unite download")
        download_start_time = time.time()
        downloaded_files = [] 
        files_download_failed = []
        max_download_attempts = self.download_retry_num
        
        for a_file in self.download_file:
            
            attempt = 0
            file_dir = a_file.split("|")[0].strip()
            file_name = a_file.split("|")[1].strip()
            completed = False
            
            while attempt < max_download_attempts and not completed:
                attempt += 1
                try:
                    file_url = os.path.join(self.download_url, file_name)
                    if file_dir:
                        os.makedirs(file_dir, mode = self.folder_mode)
                        os.chdir(file_dir)
                    file_success = self.download_a_file(file_name, file_url)
                    if file_success :
                        completed = self.unzip_file(file_name)
                    if file_dir:
                        os.chdir("..")
                        
                except Exception as e:
                    logging.info("failed to download file {} on attempt {}: {}".format(file_name, attempt, e)) 
                    time.sleep(self.sleep_time)
        
            if completed:
                downloaded_files.append(file_name)
            else:
                logging.info("failed to download greengene file {} after all attempts".format(file_name))
                return False
        # Write the README+ file 
        comment = 'This folder contains greenGene data.'
        self.write_readme(download_url='{}'.format(self.download_url),
                          downloaded_files=downloaded_files, download_failed_files=files_download_failed,
                          comment=comment, execution_time=(time.time() - download_start_time))

        return True
    
    # Download a file with provided file name and file address(link)
    def download_a_file(self, file_name, file_address):
        print(file_name)
        #requests_ftp.monkeypatch_session()
        session_requests = requests.Session()
        try:   
            res = session_requests.get(file_address, stream=True, verify=False)
            with open(file_name, 'wb') as output:
                shutil.copyfileobj(res.raw, output)
            
            session_requests.close()
        except Exception as e:
            logging.exception('Failed to download file {}.'.format(file_name))
            return False
        return True
    
    # backup Qiime readme and readme+ file
    def backup(self):
        logging.info("Executing unite data backup")

        backup_folder = self.create_backup_dir()
        if not backup_folder:
            logging.error("Failed to create backup folder.")
            return False
        # Copy only README files for future reference
        app_readme_file = self.config['readme_file']
        try:
            shutil.copy2(app_readme_file, backup_folder)
            for a_readme in self.info_file_name:
                file_dir = a_readme.split("|")[0].strip()
                file_name = a_readme.split("|")[1].strip()
                shutil.copy2(file_dir+"/"+file_name, backup_folder)
        except Exception as e:
            logging.exception("unitedata Backup did not succeed. Error: {}".format(e))
            return False
        # Remove developer folder and remove Mothur/data folder
        try:
            pre_path = os.getcwd()
            print(pre_path)
            for a_dev in self.developer_path:
                print(a_dev)
                #a_path = os.path.join(pre_path, a_dev)
                #print(a_path)
                shutil.rmtree(a_dev)
                
            for a_remove in self.remove_path:
                a_remove_path = os.path.join(os.getcwd(), a_remove)
                os.chdir(a_remove_path)
                for a_file in os.listdir("."):
                    shutil.move(a_file, "../"+a_file)
                os.chdir(pre_path)
                print(a_remove_path)
                shutil.rmtree(a_remove_path)
        except Exception as e:
            logging.exception("Failed to remove developer folder. Error: {}".format(e))
            return False
        
        return True

    def restore(self,folder_name):
        logging.info("Restoringing unite data ... Nothing to do.")
        pass
   