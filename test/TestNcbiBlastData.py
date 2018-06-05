import unittest
from NcbiBlastData import NcbiBlastData
import os, shutil
import ftplib

class TestNcbiData(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        #print('In TestNcbiBlastData. config file: {}'.format(os.path.abspath('test_config.yaml')))
        # get current working dir:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        print(dir_path)
        self.fixture = NcbiBlastData('{}/test_config.yaml'.format(dir_path))

    @classmethod
    def tearDownClass(self):
        if os.path.exists(self.fixture.destination_dir):
            shutil.rmtree(self.fixture.destination_dir)



    def test_testConnection(self):
        self.assertTrue(self.fixture.test_connection(), 'Could not connect to NCBI ftp: {}'.format(self.fixture._download_ftp))

    '''
    def testDownload(self):
        readme_file = self.fixture.destination_dir + "README+"
        print(readme_file)

        self.fixture.download(test_repeats=2)

        self.assertTrue(os.path.isfile(readme_file), "README+ file should be created with the download.")

        ncbi_readme = self.fixture.destination_dir + 'README'
        self.assertTrue(os.path.isfile(ncbi_readme), "NCBI README file is not found in the download directory.")

    

    def test_download_blast_file(self):
        # Small files to test with: nr.80, nt.53
        # Large files: nt.03, nr.05, nt.23
        file_name = 'nt.53.tar.gz'
        self.fixture.download_blast_file(file_name, self.ftp)
        self.assertTrue(os.path.isfile(self.fixture.destination_dir + file_name), "File was not downloaded.")

        #self.fixture.download_blast_file(file_name, 0)
        #self.assertTrue(os.path.isfile(self.fixture.destination_dir + file_name), "File was not downloaded.")

    '''

    def test_download_ftp_file(self):
        # Small files to test with: nr.80, nt.53
        # Large files: nt.03, nr.05, nt.23

        ftp = self.fixture.ftp_connect()
        if ftp:
            file_name = 'nt.53.tar.gz'
            self.fixture.download_ftp_file(file_name, ftp)
            self.assertTrue(os.path.isfile(self.fixture.destination_dir + file_name), "File was not downloaded.")
            ftp.quit()
        else:
            print('Could not connect to NCBI. The test was not run.')
