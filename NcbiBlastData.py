from NcbiData import NcbiData
from RefDataInterface import RefDataInterface
import os, shutil
import ftplib
import re
import logging.config
import tarfile
import time

class NcbiBlastData(NcbiData, RefDataInterface):

    def __init__(self, config_file):
        #print('In NcbiBlastData. config file: {}'.format(os.path.abspath(config_file)))
        super(NcbiBlastData, self).__init__(config_file)

        self._download_ftp = self.config['ncbi']['blast_db']['ftp']
        self._ftp_dir = self.config['ncbi']['blast_db']['ftp_dir']
        self._ncbi_user = self.config['ncbi']['blast_db']['user']
        self._ncbi_passw = self.config['ncbi']['blast_db']['password']
        self._info_file_name = self.config['ncbi']['blast_db']['info_file_name']

        self.destination_dir = super(NcbiBlastData, self).destination_dir + self.config['ncbi']['blast_db']['destination_folder']
        if not os.path.exists(self.destination_dir):
            os.makedirs(self.destination_dir)
        os.chdir(self.destination_dir)

        self.backup_dir = super(NcbiBlastData, self).backup_dir + self.config['ncbi']['blast_db'][
            'destination_folder']
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


    # re-tries ftp connection. Returns connection handler or 0
    def ftp_connect(self):
        logging.info('Connecting to NCBI ftp: {} ...'.format(self._download_ftp))
        retry_num = self.connection_retry_num
        ftp = 0  # to make sure we don't get UnboundLocalError
        while not self.test_existing_connection(ftp) and retry_num != 0:
            try:
                ftp = ftplib.FTP(self._download_ftp)
                ftp.login(user=self._ncbi_user, passwd=self._ncbi_passw)
                ftp.cwd(self._ftp_dir)
            except Exception as e:
                print("Error connecting to FTP: {} Retrying...".format(e))
                time.sleep(1)
                retry_num -= 1

        return ftp



    def test_connection(self):
        connection_successful = False

        try:
            ftp = ftplib.FTP(self._download_ftp)
            ftp.login(user=self._ncbi_user, passwd=self._ncbi_passw)
            ftp.cwd(self._ftp_dir)

            # Just to check the connection. Does nothing
            response = ftp.voidcmd('NOOP')

            if response == '200 NOOP command successful':
                connection_successful = True

            ftp.quit()
        except:
            return False

        return connection_successful


    def test_existing_connection(self, ftp):
        connection_successful = False
        try:
            # Just to check the connection. Does nothing
            response = ftp.voidcmd('NOOP')

            if response == '200 NOOP command successful':
                connection_successful = True
        except:
            return False

        return connection_successful


    def update(self):
        logging.info("Running NCBI Blast update")
        # directory to do an intermediary download
        temp_dir = self.destination_dir + 'temp'
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

        # Download and unzip into an intermediate folder
        os.chdir(temp_dir)
        success = self.download(test_repeats=1)

        if not success:
            logging.error("Download failed. Update will not proceed.")
            return False

        backup_success = self.backup()

        if not backup_success:
            logging.error("Backup of reference data did not succeed. The update will not continue.")
            return False


        # Delete all data from the destination folder
        os.chdir(self.destination_dir)
        only_files = [f for f in os.listdir('.') if os.path.isfile(f)]
        for f in only_files:
            os.remove(f)

        # Copy data from intermediate folder to destination folder
        shutil.copytree(temp_dir, self.destination_dir)
        # Delete intermediate folder
        shutil.rmtree(temp_dir)


    def backup(self):
        # We will not keep a full copy of the directory
        #shutil.copytree(self.destination_dir, self.backup_dir)


        backup_folder = self.create_backup_dir()
        if not backup_folder:
            logging.error("Backup did not succeed.")
            return False

        # Copy only README files for future reference
        app_readme_file = self.config['readme_file']
        ncbi_readme_file = self._info_file_name
        try:
            all_files = os.listdir(self.destination_dir)

            if app_readme_file in all_files:
                shutil.copy2(app_readme_file, backup_folder)
            else:
                logging.info("{} file could not be backed-up because it is not found.".format(app_readme_file))

            if ncbi_readme_file in all_files:
                shutil.copy2(ncbi_readme_file, backup_folder)
            else:
                logging.info("{} file could not be backed-up because it is not found.".format(app_readme_file))
        except Exception as e:
            logging.exception("Backup did not succeed. Error: {}".format(e))
            return False

        return backup_folder


    # Deletes all blast database files. Directory structure will be preserved.
    def delete(self):
        all_files = os.listdir(self.destination_dir)

        for file in all_files:
            if os.path.isfile(file):
                print("File")
            else:
                print("DIr")

    def restore(self):
        # 2018.05.28: As agreed upon, this feature will not be implemented.
        # There is no backup functionality for blast databases, therefore there is no restore.
        pass


    # Download all nr / nt blast databases
    def download(self, test_repeats=0):
        download_start_time = time.time()

        #TODO: Check time, and if it is not after hours for ncbi, give a warning
        # Check out warning.warn(): https://docs.python.org/3/library/warnings.html#warnings.warn


        ftp = self.ftp_connect()

        if not ftp:
            logging.error("Could not connect to NCBI ftp {}. Download will not continue.")
            return False

        ### Download
        downloaded_files = []
        files_download_failed = []

        try:
            # Get list of files to download
            all_files = ftp.nlst()

            nr_nt_re = re.compile('(nr|nt)\.\d{2}\.tar\.gz$')

            nr_nt_files = [file_name for file_name in all_files if nr_nt_re.match(file_name)]


            ### Download NCBI README file
            #self.download_ftp_file(self._info_file_name, ftp)
            with open(self._info_file_name, 'wb') as f:
                ftp.retrbinary('RETR {}'.format(self._info_file_name), f.write, 1024)

            if test_repeats == 0:
                test_repeats = len(nr_nt_files) + 2
            for file in nr_nt_files:
                if test_repeats > 0:
                    test_repeats -= 1

                    downloaded = self.download_blast_file(file, ftp)

                    unzipped = False
                    if downloaded:
                        downloaded_files.append(file)
                        unzipped = self.unzip_file(file)

                    if unzipped:
                        os.remove(file)
                    else:
                        files_download_failed.append(file)


                else:
                    break

            ftp.quit()
        except Exception as e:
            logging.exception("Exception when trying to download and extract blast database from NCBI. Error: {}".format(e))
            try:
                ftp.quit()
            except:
                pass  # If connection was dead at this point, then it's fine

            return False

        if files_download_failed:
            logging.info("Following files failed to be downloaded and/or un-archived: {}".format(files_download_failed))

        # Write application's README+ file
        comment = 'This is full blast database (all of nr / nt datasets) downloaded from NCBI.'
        self.write_readme(download_url='{}/{}'.format(self._download_ftp, self._ftp_dir),
                          downloaded_files=downloaded_files, download_failed_files=files_download_failed,
                          comment=comment, execution_time=(time.time() - download_start_time))

        return True



    # Downloads a file and its corresponding .md5 file. Checks if md5 match.
    def download_blast_file(self, short_file_name, ftp_link):
        md5_file = '{}.md5'.format(short_file_name)
        '''
        md5_data = []
        try:
            ftp_link.retrbinary('RETR {}'.format(md5_file), md5_data.append)

        except ftplib.error_perm as e:
            logging.error("Can't download {} file from NCBI. Returned error: {}. \n Download will not continue".format(short_file_name, e))
            return False
        
        md5_str = md5_data[0].decode("utf-8") .split(' ')[0]
        '''

        success = self.download_ftp_file(md5_file, ftp_link)

        if not success:
            return False


        try:
            with open(md5_file, 'r') as f:
                md5_file_contents = f.read()
            md5_str = md5_file_contents.split(' ')[0]
            os.remove(md5_file)
        except Exception as e:
            logging.exception('Could not download or read MD5 file for file {}. Download of this file will not proceed.'.format(short_file_name))
            return False

        success = self.download_ftp_file(short_file_name, ftp_link)

        if not success:
            return False

        if not self.check_md5(short_file_name, md5_str):
            logging.warning("MD5 check did not pass. Attempting re-downloading again.")
            os.remove(short_file_name)
            success = self.download_ftp_file(short_file_name, ftp_link)
            if not success or not self.check_md5(short_file_name, md5_str):
                logging.error("MD5 check did not pass. The file {} will be destroyed.".format(short_file_name))
                return False

        return True



    def download_ftp_file(self, file_name, ftp_connection):

        download_success = False

        if not ftp_connection:
            ftp = self.ftp_connect()

        if ftp_connection:
            max_download_attempts = self.download_retry_num
            try:
                ftp_file_size = ftp_connection.size(file_name)
            except:
                logging.error("Failed to check the size of the download. The file {} will not be downloaded.".format(
                    file_name
                ))
                return False

            #print('Original ftp file size:   {}'.format(ftp_connection.size(file_name)))

            with open(file_name, 'wb') as file_obj:
                while ftp_file_size != file_obj.tell():
                    try:
                        if file_obj.tell() != 0:
                            #print('Downloaded local file size before re-try: {}'.format(file_obj.tell()))
                            ftp_connection.retrbinary('RETR {}'.format(file_name), file_obj.write, rest=file_obj.tell())
                        else:
                            ftp_connection.retrbinary('RETR {}'.format(file_name), file_obj.write)
                            #print('Downloaded local file size at end: {}'.format(file_obj.tell()))
                    except (ftplib.error_temp, IOError) as e:
                        print('Problems with ftp connection. Error: {}'.format(e))
                        logging.warning('Problems with ftp connection. Error: {}'.format(e))
                        if max_download_attempts != 0:
                            print('Re-trying the download of file: {}'.format(file_name))
                            logging.warning('Re-trying the download of file: {}'.format(file_name))
                            time.sleep(1)  # sleep one second before re-trying
                            ftp_connection = self.ftp_connect()
                            max_download_attempts -= 1
                            if not ftp_connection:
                                logging.error("Connection could not be established.")
                                return False
                        else:
                            logging.error('Failed to download file: {}'.format(file_name))
                            return False
                    except:
                        logging.exception(
                            'Something went wrong with the download of file: {} Re-download will not be attempted.'.format(
                                file_name))
                        os.remove(file_name)
                        return False

                if ftp_file_size == file_obj.tell():
                    download_success = True
                else:
                    logging.error("Downloaded file size does not match it's size on FTP server. The file will be deleted.")
                    os.remove(file_name)


        return download_success



    def unzip_file(self, filename):

        try:
            if (filename.endswith("tar.gz")):
                tar = tarfile.open(filename, "r:gz")
                tar.extractall()
                tar.close()
        except Exception as e:
            logging.exception("Failed to exctract file {}. Error: {}".format(filename, e))
            return False

        return True
