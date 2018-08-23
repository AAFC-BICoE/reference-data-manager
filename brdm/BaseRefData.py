import yaml
import requests
import os, shutil
import logging.config
import datetime
import hashlib
from datetime import timedelta
import tarfile


class BaseRefData():

    def __init__(self, config_file):
        
        self.config = self.load_config(config_file)
        self.download_retry_num = self.config['download_retry_num']
        self.connection_retry_num = self.config['connection_retry_num']
        self.sleep_time =  self.config['sleep_time']
        self.folder_mode = self.config['folder_mode']
        self.file_mode = self.config['file_mode']
        logging.config.dictConfig(self.config['logging'])
        
        try:
            self.destination_dir = os.path.abspath(self.config['root_folder']) + '/'
            if not os.path.exists(self.destination_dir):
                os.makedirs(self.destination_dir)
                os.chmod(self.destination_dir, int(folder_mode,8))
            self.backup_dir = os.path.abspath(self.config['backup_folder']) + '/'
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir)
                os.chmod(self.backup_dir, int(folder_mode,8))
        except Exception as e:
            logging.error("Failed to create the root_dir or backup_dir with error {}".format(e))
         
        

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        self._config = value

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

    @property
    def download_retry_num(self):
        return self._download_retry_num

    @download_retry_num.setter
    def download_retry_num(self, value):
        self._download_retry_num = value

    @property
    def connection_retry_num(self):
        return self._connection_retry_num

    @connection_retry_num.setter
    def connection_retry_num(self, value):
        self._connection_retry_num = value

    '''
    def getDestinationFolder(self):
        return self._root_dir + "/"
    '''


    def load_config(self, config_file):

        try:
            with open(config_file, 'r') as stream:
                config = yaml.load(stream)

        except yaml.YAMLError as e:
            print("Could not load configuration file. RDM will not run. Error: {}".format(e))
            exit(1)
        except FileNotFoundError as e:
            print('Configuration file full path: {}'.format(os.path.abspath(config_file)))
            print("Configuration file {} could not be found. RDM will not run. Error: {}".format(config_file, e))
            exit(1)
        except Exception as msg:
            print("Error while loading configuration file {}. RDM will not run. Error: {}".format(config_file))
            exit(1)

        logging.info("RDM's configuration file was successfully loaded. File name: {}".format(config_file))

        return config


    #file_url = 'https://gist.github.com/oxyko/10798051fb9cf1e11f4baac2c6c49f3b/archive/44e343bfe87f56fbc8bb6fbf3a48294aa7b0a1b6.zip'
    def download_file(self, file_url, destination_dir):
        '''
        local_file_name = destination_dir + file_url.split('/')[-1]
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)
        r = requests.get(file_url, stream=True)  # stream=True makes sure that python does not run out of memory when reading/writing
        with open(local_file_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=512 * 1024):
                if chunk:
                    f.write(chunk)

        logging.info("File downloaded: {}".format(local_file_name))
        return local_file_name
        '''
        pass
    
    def unzip_file(self, filename):
        try:
            if (filename.endswith("tar.gz")):
                tar = tarfile.open(filename, "r:gz")
                tar.extractall()
                tar.close()
                self.delete_file(filename)
        except Exception as e:
            logging.exception("Failed to exctract file {}. Error: {}".format(filename, e))
            return False

        return True


    def delete_file(self, full_file_name):
        try:
            os.remove(full_file_name)
            logging.info("File deleted: {}".format(full_file_name))
        except Exception as e:
            logging.exception("Failed to delete a file {}. Error: {}".format(full_file_name, e))


    def write_readme(self, download_url, downloaded_files, download_failed_files=[], comment='', execution_time=0):
        file_name = self.config['readme_file']
        #print("Readme file: {}\n".format(file_name))
        try:
            with open(file_name, 'w') as f:
                f.write("About: this an automatically generated description file for the data located in this folder.\n")
                if comment:
                    f.write("{}\n".format(comment))
                # now.strftime("%Y-%m-%d %H:%M")
                f.write("Downloaded on: {}\n".format(datetime.datetime.now()))
                f.write("Downloaded from: {}\n".format(download_url))
                if execution_time:
                    msg = "Download time: {} secs \n".format(timedelta(seconds=round(execution_time)))
                    f.write(msg)
                f.write("List of downloaded files: \n")
                for file in downloaded_files:
                    f.write("{}\n".format(file))

                if download_failed_files:
                    f.write("List of files that failed to be downloaded: \n")
                    for file in download_failed_files:
                        f.write("{}\n".format(file))
        except Exception as e:
            logging.exception("Failed to write_readme. Error: {}".format(filename, e))
            return False

        logging.info("Finished writing an application README file: {}".format(file_name))

    def parse_readme(self):
        # This one is for getting a list of files, recorded at the update/download time
        # Will be used in the restore backup
        pass


    def check_md5(self, file_name, md5_check):
        try:
            with open(file_name, 'rb') as file:
                file_data = file.read()
                md5_real = hashlib.md5(file_data).hexdigest()
        except Exception as e:
            logging.exception("Failed to check_md5. Error: {}".format(filename, e))
            return False

        return md5_check == md5_real


    # All backup dirs are named as date: yyyy-mm-dd. They will be placed in appropriate sub-folder
    def create_backup_dir(self):
        short_dir_name = datetime.datetime.now().strftime('%Y-%m-%d')
        full_dir_name = '{}{}'.format(self.backup_dir, short_dir_name)

        try:
            if os.path.exists(full_dir_name):
                shutil.rmtree(full_dir_name)

            os.makedirs(full_dir_name)
        except:
            logging.exception("Could not create a backup directory: {}".format(full_dir_name))
            return False

        return full_dir_name + '/'
