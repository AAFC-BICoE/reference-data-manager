import yaml
import os
import shutil
import logging.config
import datetime
import tarfile
import gzip
import zipfile
from pathlib import Path
from hashlib import md5
from datetime import timedelta
from site import abs_paths


class BaseRefData():

    def __init__(self, config_file):
        """Initialize the object"""
        self.config = self.load_config(config_file)
        self.current_dir = os.getcwd()
        self.download_retry_num = self.config['download_retry_num']
        self.connection_retry_num = self.config['connection_retry_num']
        self.sleep_time = self.config['sleep_time']
        self.folder_mode = int(self.config['folder_mode'], 8)
        self.file_mode = int(self.config['file_mode'], 8)
        logging.config.dictConfig(self.config['logging'])
        try:
            self.destination_dir = os.path.abspath(self.config['root_folder'])
            if not os.path.exists(self.destination_dir):
                os.makedirs(self.destination_dir, mode=self.folder_mode)
            self.backup_dir = os.path.abspath(self.config['backup_folder'])
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir, mode=self.folder_mode)
        except Exception as e:
            logging.error('Failed to create the root_dir or backup_dir with \
            \nerror: {}'.format(e))

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
        """Load the parameters in config file."""
        try:
            with open(config_file, 'r') as stream:
                config = yaml.load(stream)
        except yaml.YAMLError as e:
            print('Could not load configuration file. Error: {}'.format(e))
            exit(1)
        except FileNotFoundError as e:
            print('Cannot find the configuration file {}'
                  .format(os.path.abspath(config_file)))
            print('Double check the config file in folder brdm/ or',
                  'provide a config file by --config-file.')
            exit(1)
        except Exception as msg:
            print('Error while loading configuration file: {}'.format(msg))
            exit(1)
        logging.info('RDM configuration file was successfully loaded. \
                     File name: {}'.format(config_file))
        return config

    def unzip_file(self, filename_in):
        """Unzip file"""
        if filename_in.endswith('.gz') and not filename_in.endswith('tar.gz'):
            try:
                filename_out = filename_in[:-3]
                with gzip.open(filename_in, 'rb') as f_in, \
                        open(filename_out, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
                self.delete_file(filename_in)
            except Exception as e:
                logging.exception('Failed to unzip file {}. Error: {}'
                                  .format(filename_in, e))
                return False

        if filename_in.endswith('tar.gz'):
            try:
                with tarfile.open(filename_in, 'r:gz') as tar:
                    tar.extractall()
                self.delete_file(filename_in)
            except Exception as e:
                logging.exception('Failed to exctract file {}. Error: {}'
                                  .format(filename_in, e))
                return False

        if filename_in.endswith('.zip'):
            try:
                with zipfile.ZipFile(filename_in, 'r') as zip:
                    zip.extractall()
                self.delete_file(filename_in)
            except Exception as e:
                logging.exception('Failed to exctract file {}. Error: {}'
                                  .format(filename_in, e))
                return False
        return True

    def delete_file(self, full_file_name):
        """Method to delete a file"""
        try:
            os.remove(full_file_name)
            #logging.info('File deleted: {}'.format(full_file_name))
        except Exception as e:
            logging.exception('Failed to delete a file {}. Error: {}'
                              .format(full_file_name, e))

    def write_readme(self, download_url, downloaded_files,
                     download_failed_files=[], comment='', execution_time=0):
        """Write information to application read me file"""
        file_name = self.config['readme_file']
        try:
            with open(file_name, 'w') as f:
                f.write('About: this an automatically generated description \
                        file for the data located in this folder.\n')
                if comment:
                    f.write('{}\n'.format(comment))
                f.write('Downloaded on: {}\n'.format(datetime.datetime.now()))
                f.write('Downloaded from: {}\n'.format(download_url))
                if execution_time:
                    msg = 'Download time: {} secs \n' \
                           .format(timedelta(seconds=round(execution_time)))
                    f.write(msg)
                f.write('List of downloaded files: \n')
                for file in downloaded_files:
                    f.write('{}\n'.format(file))

                if download_failed_files:
                    f.write('List of files that failed to be downloaded: \n')
                    for file in download_failed_files:
                        f.write('{}\n'.format(file))
            os.chmod(file_name, self.file_mode)
        except Exception as e:
            logging.exception('Failed to write_readme. Error: {}'
                              .format(file_name, e))
            return False

        logging.info('Finished writing an application README file: {}'
                     .format(file_name))
        return True

    def check_md5(self, file_name, md5_check):
        """Checksum md5"""
        if not md5_check:
            logging.error('Empty md5_code. Failed to check md5')
            return False
        try:
            with open(file_name, 'rb') as file_data:
                md5_real = md5(file_data.read()).hexdigest()
        except Exception as e:
            logging.exception('Failed to check_md5. Error: {}'
                              .format(file_name, e))
            return False
        return md5_check == md5_real

    # All backup dirs are named as date: yyyy-mm-dd.
    # They will be placed in appropriate sub-folder
    def create_backup_dir(self):
        """Create backup directory"""
        short_dir_name = datetime.datetime.now().strftime('%Y-%m-%d')
        full_dir_name = os.path.join(self.backup_dir, short_dir_name)
        try:
            if os.path.exists(full_dir_name):
                shutil.rmtree(full_dir_name)
            os.makedirs(full_dir_name, mode=self.folder_mode)
        except Exception as e:
            logging.exception('Could not create a backup directory: {}'
                              .format(full_dir_name))
            return False
        return full_dir_name + '/'

    # Create an intermediate dir for holding updated new data
    # The data will be move to destination dir if download successful
    def create_tmp_dir(self, destination_path):
        """Create an intermediate dir for holding new data"""
        try:
            # temp_dir = tempfile.mkdtemp(dir = self.destination_dir )
            temp_dir = os.path.join(destination_path, 'temp')
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)
            os.chdir(temp_dir)
        except Exception as e:
            logging.error('Failed to create the temp_dir: {}, error{}'
                          .format(temp_dir, e))
            return False
        return temp_dir

    # Clean old files in the destination dir; Temp folder CANNOT be removed
    def clean_destination_dir(self, destination_path):
        """Remove old files in destination directory"""
        try:
            os.chdir(destination_path)
            for f in os.listdir('.'):
                if os.path.isfile(f):
                    os.remove(f)
                if os.path.isdir(f) and f != 'temp':
                    shutil.rmtree(f)
        except Exception as e:
            logging.error('Failed to remove files in destination folder, \
            error{}'.format(e))
            return False
        return True

    # Check the gap between two dates; used by restore method to select
    # the right version of the database
    def count_gap_two_dates(self, target_date, date):
        """Check the gap between two dates

        Used by restore method to select the right version of the database
        Args:
            target_date (string): a date in format yyyy-mm-dd
            date (string): a date in format yyyy-mm-dd
        Return:
            number of days between two dates
        """
        try:
            target_items = target_date.split('-')
            date_items = date.split('-')
            year = int(target_items[0])-int(date_items[0])
            month = int(target_items[1])-int(date_items[1])
            day = int(target_items[2])-int(date_items[2])
        except Exception as e:
            logging.error('Failed to count the gap between two dates, \
            error{}'.format(e))
            return -1
        return (year*365+month*30+day)

    # Check the path of destination of the restored database
    # if relative path, then cwd/proposed_destination
    def check_restore_destination(self, proposed_destination):
        """Return the absolute path of restore destination"""
        abs_path = proposed_destination
        if not os.path.isabs(proposed_destination):
            abs_path = os.path.join(self.current_dir, proposed_destination)
            # return os.path.join(str(Path.home()), proposed_destination)
        if os.path.isdir(abs_path):
            print('Folder already exists; Select other restore destination')
            logging.error('{} already exists; Select other restore destination'
                          .format(abs_path))
            return False
        return abs_path
    
    # The format of the restore date has to be yyyy-mm-dd
    def check_restore_date_format(self, proposed_date):
        """Check the format of the restore date"""
        date_format = proposed_date.split('-')
        if len(date_format) != 3:
            return False
        for index in range(len(date_format)):
            if not date_format[index].isdigit():
                return False
        return True

    # Check the restore date and find the right date to be restored
    # the right date is the proposed_date if it exists in the backup folder;
    # otherwise the right date is the one just before the proposed_date that
    # available in the backup folder
    def check_restore_date(self, backup_dir, proposed_date):
        """Return the right date to be restored

        Check the restore date and find the right date to be restored
        the right date is the proposed_date if it exists in the backup folder;
        otherwise the right date is the one just before the proposed_date that
        available in the backup folder
        Args:
            backup_dir (string): a path to a directory
            proposed_date (string): date of database version to be restored
        Return:
            the date that available in backup_dir AND on or just before the
            proposed_date
        """
        restore_path = ''
        try:
            right_format = self.check_restore_date_format(proposed_date)
            if not right_format:
                print('Error: format of --restore-date has to be yyyy-mm-dd')
                logging.error('Format of --restore-date has to be yyyy-mm-dd')
                return False
            restore_date = ''
            minGap = -1
            for f in os.listdir(backup_dir):
                if os.path.isdir(os.path.join(backup_dir, f)) \
                        and self.check_restore_date_format(f):
                    gap = self.count_gap_two_dates(proposed_date, f)
                    if gap >= 0 and minGap == -1:
                        minGap = gap
                        restore_date = f
                    if gap >= 0 and minGap > 0 and gap < minGap:
                        minGap = gap
                        restore_date = f
            if restore_date:
                restore_path = os.path.join(backup_dir, restore_date)
            if not os.path.exists(restore_path):
                logging.error('could not restore, database created on/before \
                \nthe provided date does not exist.')
                return False
            if len(os.listdir(restore_path)) == 0:
                logging.error('could not restore, {} is an empty folder.'
                              .format(restore_path))
                return False
        except Exception as e:
            logging.error('Failed to check restore folder, error{}'.format(e))
            return False
        logging.info('Required --restore-date {}; Real --restore-date {}.'
                     .format(proposed_date, restore_date))
        print('Required --restore-date ' + proposed_date + ';\
              \nReal --restore-date ' + restore_date)
        return restore_path
