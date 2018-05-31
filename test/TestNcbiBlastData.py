import unittest
from NcbiBlastData import NcbiBlastData
import os, shutil
import ftplib

class TestNcbiData(unittest.TestCase):


    def setUp(self):
        self.fixture = NcbiBlastData('test_config.yaml')

        self.ftp = ftplib.FTP(self.fixture._download_ftp)
        self.ftp.login(user=self.fixture._ncbi_user, passwd=self.fixture._ncbi_passw)
        self.ftp.cwd(self.fixture._ftp_dir)

    def tearDown(self):
        if os.path.exists(self.fixture.destination_dir):
            shutil.rmtree(self.fixture.destination_dir)

        self.ftp.quit()

    '''
    def testDownload(self):
        readme_file = self.fixture.destination_dir + "README+"
        print(readme_file)

        self.fixture.download(test_repeats=2)

        self.assertTrue(os.path.isfile(readme_file), "README+ file should be created with the download.")

        ncbi_readme = self.fixture.destination_dir + 'README'
        self.assertTrue(os.path.isfile(ncbi_readme), "NCBI README file is not found in the download directory.")

    '''

    def test_download_blast_file(self):
        # Some small files to test with: nr.80, nt.53
        file_name = 'nt.53.tar.gz'
        self.fixture.download_blast_file(file_name, self.ftp)
        self.assertTrue(os.path.isfile(self.fixture.destination_dir + file_name), "File was not downloaded.")


