from NcbiData import NcbiData
from RefDataInterface import RefDataInterface
import os
import ftplib
import re
import logging.config

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



    @property
    def destination_dir(self):
        return self._destination_dir

    @destination_dir.setter
    def destination_dir(self, value):
        self._destination_dir = value


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
                os.sleep(1)
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
        pass

    def backup(self):
        # 2018.05.28: As agreed upon, this feature will not be implemented.
        pass

    def restore(self):
        # 2018.05.28: As agreed upon, this feature will not be implemented.
        # There is no backup functionality for blast databases, therefore there is no restore.
        pass


    # Download all nr / nt blast databases
    def download(self, test_repeats=0):

        #TODO: Check time, and if it is not after hours for ncbi, give a warning
        # Check out warning.warn(): https://docs.python.org/3/library/warnings.html#warnings.warn

        if not self.testConnection():
            logging.critical(
                'Problems connecting to NCBI ftp {}. Download of NCBI BLAST nr/nt databases will not proceed.'.format(
                self._download_ftp
            ))
            return False


        try:
            ftp = ftplib.FTP(self._download_ftp)
            ftp.login(user=self._ncbi_user, passwd=self._ncbi_passw)
            ftp.cwd(self._ftp_dir)


            # Get list of files to download
            all_files = ftp.nlst()

            nr_nt_re = re.compile('(nr|nt)\.\d{2}\.tar\.gz$')

            nr_nt_files = [file_name for file_name in all_files if nr_nt_re.match(file_name)]

            # Write docs
            comment = 'This is full blast database (all of nr / nt datasets) downloaded from NCBI.'
            self.write_readme(download_url='{}/{}'.format(self._download_ftp, self._ftp_dir), files=nr_nt_files,
                              comment=comment)

            with open(self._info_file_name, 'wb') as f:
                ftp.retrbinary('RETR {}'.format(self._info_file_name), f.write, 1024)

            self.download_blast_file(nr_nt_files[0], ftp)

            ftp.quit()
        except:
            logging.exception("Exception when trying to download blast database from NCBI.")
            ftp.quit()




    def download_blast_file(self, short_file_name, ftp_link):
        md5_file = '{}.md5'.format(short_file_name)

        md5_data = []
        try:
            ftp_link.retrbinary('RETR {}'.format(md5_file), md5_data.append)

        except ftplib.error_perm as e:
            logging.error("Can't download {} file from NCBI. Returned error: {}".format(short_file_name, e))
            ## Retry?

        md5_str = md5_data[0].decode("utf-8") .split(' ')[0]

        with open(short_file_name, 'wb') as f:
            ftp_link.retrbinary('RETR {}'.format(short_file_name), f.write, 1024)

        if not self.check_md5(self.destination_dir + short_file_name, md5_str):
            # Delete and re-download the file?
            pass

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

            print('Original ftp file size:   {}'.format(ftp_connection.size(file_name)))

            with open(file_name, 'wb') as file_obj:
                while ftp_file_size != file_obj.tell():
                    try:
                        if file_obj.tell() != 0:
                            print('Downloaded local file size before re-try: {}'.format(file_obj.tell()))
                            ftp_connection.retrbinary('RETR {}'.format(file_name), file_obj.write, rest=file_obj.tell())
                        else:
                            ftp_connection.retrbinary('RETR {}'.format(file_name), file_obj.write)
                            print('Downloaded local file size at end: {}'.format(file_obj.tell()))
                    except (ftplib.error_temp, IOError) as e:
                        print('Problems with ftp connection. Error: {}'.format(e))
                        logging.warning('Problems with ftp connection. Error: {}'.format(e))
                        if max_download_attempts != 0:
                            print('Re-trying the download of file: {}'.format(file_name))
                            logging.warning('Re-trying the download of file: {}'.format(file_name))
                            os.sleep(1)  # sleep one second before re-trying
                            ftp_connection = self.ftp_connect()
                            max_download_attempts -= 1
                            if not ftp_connection:
                                logging.error("Connection could not be established.")
                                return False
                        else:
                            print('Failed to download file: {}'.format(file_name))
                            logging.error('Failed to download file: {}'.format(file_name))
                            return False
                    except:
                        print(
                            'Something went wrong with the download of file: {} Re-download will not be attempted.'.format(
                                file_name))
                        os.remove(file_name)
                        return False

                print('Downloaded file: {}'.format(self.destination_dir+file_name))
                if ftp_file_size == file_obj.tell():
                    download_success = True
                else:
                    #os.remove(file_name)
                    pass

        return download_success
