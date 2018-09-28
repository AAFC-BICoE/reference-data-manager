import yaml
import os, shutil
import logging.config
import datetime
from hashlib import md5
from datetime import timedelta
import tarfile
import gzip


class BaseRefData():

    def __init__(self, config_file):
        self.config = self.load_config(config_file)
        self.download_retry_num = self.config['download_retry_num']
        self.connection_retry_num = self.config['connection_retry_num']
        self.sleep_time =  self.config['sleep_time']
        self.folder_mode = int(self.config['folder_mode'],8)
        self.file_mode = int(self.config['file_mode'],8)
        logging.config.dictConfig(self.config['logging'])
        try:
            self.destination_dir = os.path.abspath(self.config['root_folder'])
            if not os.path.exists(self.destination_dir):
                os.makedirs(self.destination_dir, mode = self.folder_mode)
            self.backup_dir = os.path.abspath(self.config['backup_folder'])
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir, mode = self.folder_mode)
        except Exception as e:
            logging.error("Failed to create the root_dir or backup_dir with error: {}".format(e))
         
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
     
                   
    def unzip_file(self, filename_in):
        if filename_in.endswith('.gz') and not filename_in.endswith('tar.gz'):
            try:
                filename_out = filename_in[:-3]
                with gzip.open(filename_in, 'rb') as f_in, open(filename_out, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
                self.delete_file(filename_in)
            except Exception as e:
                logging.exception("Failed to unzip file {}. Error: {}".format(filename_in, e))
                return False
            
        if filename_in.endswith("tar.gz"):
            try:
                tar = tarfile.open(filename_in, "r:gz")
                tar.extractall()
                tar.close()
                self.delete_file(filename_in)
            except Exception as e:
                logging.exception("Failed to exctract file {}. Error: {}".format(filename_in, e))
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
        try:
            with open(file_name, 'w') as f:
                f.write("About: this an automatically generated description file for the data located in this folder.\n")
                if comment:
                    f.write("{}\n".format(comment))
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
            os.chmod(file_name, self.file_mode)
        except Exception as e:
            logging.exception("Failed to write_readme. Error: {}".format(filename, e))
            return False

        logging.info("Finished writing an application README file: {}".format(file_name))
        return True


    def check_md5(self, file_name, md5_check):
        if not md5_check:
            logging.error('empty md5_code')
            return False
        try:
            file_data = open(file_name, 'rb')
            md5_real = md5(file_data.read()).hexdigest()
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

            os.makedirs(full_dir_name, mode = self.folder_mode)
        except:
            logging.exception("Could not create a backup directory: {}".format(full_dir_name))
            return False

        return full_dir_name + '/'
    
    def create_tmp_dir(self, destination_path):
        try:
            #temp_dir = tempfile.mkdtemp(dir = self.destination_dir )
            temp_dir = os.path.join(destination_path,'temp')
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)
            os.chdir(temp_dir)
        except Exception as e:
            logging.error("Failed to create the temp_dir: {}, error{}".format(temp_dir, e))
            return False
        return temp_dir
