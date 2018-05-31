from NcbiData import NcbiData
from RefDataInterface import RefDataInterface
import os
import ftplib
import re
import logging.config

class NcbiBlastData(NcbiData, RefDataInterface):

    def __init__(self, config_file):
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


    def testConnection(self):
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
        except IOError as e:
            # Connection issues
            logging.error('FTP access error. Error: {}'.format(e))
        except ftplib.error_perm as e:
            # App issues
            logging.error("FTP error. {}".format(e))
            ftp.quit()
        except:
            # Catch all
            logging.error("Something went wrong when connecting to ftp.")
            ftp.quit()

        return connection_successful

    def update(self):
        pass

    def backup(self):
        # NCBI does not archive old nr/nt databases. Since we do not have the capacity to store this as a redundant db,
        # this function will not be implemented. If there is a need to restore the old versions of nr/nt datasets,
        # then the requirements need to be re-evaluated.
        pass

    def restore(self):
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
            with open(short_file_name, 'wb') as f:
                ftp_link.retrbinary('RETR {}'.format(short_file_name), f.write, 1024)

        except ftplib.error_perm as e:
            logging.error("Can't download {} file from NCBI. Returned error: {}".format(short_file_name, e))
            ## Retry?

        md5_str = md5_data[0].decode("utf-8") .split(' ')[0]
        if not self.check_md5(self.destination_dir + short_file_name, md5_str):
            # Delete and re-download the file?

        return True





