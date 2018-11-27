import os
import shutil
import tempfile
import logging
import time
import requests
import requests_ftp
from distutils.dir_util import copy_tree
from brdm.BaseRefData import BaseRefData
from brdm.RefDataInterface import RefDataInterface


class UniteData(BaseRefData, RefDataInterface):

    def __init__(self, config_file):
        super(UniteData, self).__init__(config_file)
        self.download_url = self.config['unite']['download_url']
        self.download_file = self.config['unite']['download_file']
        self.developer_folder = self.config['unite']['developer_folder']
        self.redundant_path = self.config['unite']['redundant_path']
        try:
            self.destination_dir = os.path.join(
                        super(UniteData, self).destination_dir,
                        self.config['unite']['destination_folder'])
            if not os.path.exists(self.destination_dir):
                os.makedirs(self.destination_dir, mode=self.folder_mode)
            os.chdir(self.destination_dir)
            self.backup_dir = os.path.join(
                        super(UniteData, self).backup_dir,
                        self.config['unite']['destination_folder'])
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir, mode=self.folder_mode)
        except Exception as e:
            logging.error('Failed to create destination_dir/backup_dir {}'
                          .format(e))

    def update(self):
        logging.info('Executing unite update')
        # Download files into the intermediate folder
        temp_dir = self.create_tmp_dir(self.destination_dir)
        if not temp_dir:
            logging.error('Failed to create the temp_dir: {}, error{}'
                          .format(temp_dir, e))
            return False
        # Download files into the intermediate folder
        success = self.download()
        if not success:
            logging.error('Failed to download. Quit the process.')
            return False
        # post process, remove developer folder
        # and change from  mothur/data/file_name to mothur/file_name
        clean_data_ok = self.post_process_data()
        if not clean_data_ok:
            logging.error('Failed to clean data. Quit the process.')
            return False
        # back up readme (qiime readme) and readme+ file
        # some irregular post_processes (remove developer dir,extra folder..)
        backup_success = self.backup()
        if not backup_success:
            logging.error('Failed to backup. Quit the process.')
            return False
        # Delete old files from the destination folder
        # Copy new files from intermediate folder to destination folder
        clean_ok = self.clean_destination_dir(self.destination_dir)
        if not clean_ok:
            return False
        try:
            copy_tree(temp_dir, self.destination_dir)
            shutil.rmtree(temp_dir)
        except Exception as e:
            logging.error('Failed to move files from temp_dir to \
            \ndestination folder, error{}'.format(e))
            return False
        return True

    def download(self):
        logging.info('Executing unite download')
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
                        os.makedirs(file_dir, mode=self.folder_mode)
                        os.chdir(file_dir)
                    file_success = self.download_a_file(file_name, file_url)
                    if file_success:
                        completed = self.unzip_file(file_name)
                    if file_dir:
                        os.chdir('..')
                except Exception as e:
                    logging.info('Failed to download {} on attempt {}: {}'
                                 .format(file_name, attempt, e))
                    time.sleep(self.sleep_time)
            if completed:
                downloaded_files.append(file_name)
            else:
                logging.info('Failed to download {} after all attempts'
                             .format(file_name))
                return False
        # Write the README+ file
        comment = 'This folder contains unite data.'
        self.write_readme(download_url='{}'.format(self.download_url),
                          downloaded_files=downloaded_files,
                          download_failed_files=files_download_failed,
                          comment=comment,
                          execution_time=(time.time() - download_start_time))
        return True

    # Download a file with provided file name and file address(link)
    def download_a_file(self, file_name, file_address):
        session_requests = requests.Session()
        try:
            res = session_requests.get(
                        file_address, stream=True)
            with open(file_name, 'wb') as output:
                shutil.copyfileobj(res.raw, output)
            session_requests.close()
        except Exception as e:
            logging.exception('Failed to download {}.'.format(file_name))
            return False
        return True

    def post_process_data(self):
        # Remove developer folder and remove Mothur/data folder
        try:
            pre_path = os.getcwd()
            for a_dev in self.developer_folder:
                if os.path.isdir(a_dev):
                    shutil.rmtree(a_dev)
                else:
                    logging.warning('Not folder: config.developer_folder {}'
                                    .format(a_dev))
            for a_remove in self.redundant_path:
                a_remove_path = os.path.join(os.getcwd(), a_remove)
                if os.path.isdir(a_remove_path):
                    os.chdir(a_remove_path)
                    for a_file in os.listdir('.'):
                        shutil.move(a_file, '../'+a_file)
                os.chdir(pre_path)
                shutil.rmtree(a_remove_path)
        except Exception as e:
            logging.exception('Failed to clean data: {}'
                              .format(e))
            return False
        blast = self.to_blast_format()
        if not blast:
            logging.error('Failed to get blast format')
            return False
        return True

    def to_blast_format(self):
        """Format the data for blast tool"""
        try:
            pre_path = os.getcwd()
            blast_folder = os.path.join(pre_path, 'Blast')
            if os.path.exists(blast_folder):
                shutil.rmtree(blast_folder)
            os.makedirs(blast_folder, mode=self.folder_mode)
            for f in os.listdir(pre_path):
                if os.path.isfile(f) and f.endswith('.fasta'):
                    sequence_input = f
                    blastdb_name = os.path.join(blast_folder, f[:-6])
                    command1 = 'makeblastdb -in ' + sequence_input \
                        + ' -dbtype nucl -out ' + blastdb_name
                    os.system(command1)
            for f in os.listdir(blast_folder):
                if os.path.isfile(f):
                    os.chmod(f, self.file_mode)
        except Exception as e:
            logging.error('failed to get blast format, error {}'.format(e))
            return False
        return True

    # Backup Qiime readme and readme+ file
    def backup(self):
        logging.info('Executing unite data backup')
        backup_folder = self.create_backup_dir()
        if not backup_folder:
            logging.error('Failed to create backup folder.')
            return False
        # Copy only README files for future reference
        app_readme_file = self.config['readme_file']
        try:
            shutil.copy2(app_readme_file, backup_folder)
        except Exception as e:
            logging.exception(' Failed to backup unite data: {}'.format(e))
            return False
        return True

    def restore(self, folder_name):
        """not necessary to restore unite database"""
        logging.info('Restoringing unite data ... Nothing to do.')
        pass
