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
        #print(dir_path)
        self.fixture = NcbiBlastData('{}/test_config.yaml'.format(dir_path))

    @classmethod
    def tearDownClass(self):

        if os.path.exists(self.fixture.destination_dir):
            shutil.rmtree(self.fixture.destination_dir)
        if os.path.exists(self.fixture.backup_dir):
            shutil.rmtree(self.fixture.backup_dir)

        pass


    def test_testConnection(self):
        self.assertTrue(self.fixture.test_connection(), 'Could not connect to NCBI ftp: {}'.format(self.fixture._download_ftp))


    def testDownload(self):

        #success = self.fixture.download()
        success = self.fixture.download(test_repeats=1)

        self.assertTrue(success, "NCBI download did not return True.")

        ncbi_readme = self.fixture.destination_dir + 'README'
        self.assertTrue(os.path.isfile(ncbi_readme), "NCBI README file is not found in the download directory.")

        readme_file = self.fixture.destination_dir + "README+"
        self.assertTrue(os.path.isfile(readme_file), "RDM's's README+ file is not found in the download directory.")


        # Check few first files
        #self.assertTrue(os.path.isfile(self.fixture.destination_dir + 'nr.00.tar.gz'), "One of the expected ncbi blast files is not found in the download directory.")
        self.assertTrue(os.path.isfile(self.fixture.destination_dir + 'nr.00.phd'),
                        "Unarchived ncbi blast file was not found.")
        self.assertTrue(os.path.isfile(self.fixture.destination_dir + 'nr.00.phr'),
                        "Unarchived ncbi blast file was not found.")
        self.assertTrue(os.path.isfile(self.fixture.destination_dir + 'nr.00.psq'),
                        "Unarchived ncbi blast file was not found.")
        self.assertTrue(os.path.isfile(self.fixture.destination_dir + 'nr.pal'),
                        "Unarchived ncbi blast file was not found.")
        self.assertTrue(os.path.isfile(self.fixture.destination_dir + 'taxdb.btd'),
                        "Unarchived ncbi blast file was not found.")
        self.assertTrue(os.path.isfile(self.fixture.destination_dir + 'taxdb.bti'),
                        "Unarchived ncbi blast file was not found.")

        # files that shouldn't be there
        self.assertFalse(os.path.isfile(self.fixture.destination_dir + 'nr.00.tar.gz.md5'),
                        "md5 file should have been removed.")
        self.assertFalse(os.path.isfile(self.fixture.destination_dir + 'nr.00.tar.gz'),
                        "tar.gz file should have been removed.")

    '''
    def test_download_blast_file(self):
        # Small files to test with: nr.80, nt.53
        # Large files: nt.03, nr.05, nt.23
        file_name = 'nt.53.tar.gz'
        self.fixture.download_blast_file(file_name, self.ftp)
        self.assertTrue(os.path.isfile(self.fixture.destination_dir + file_name), "File was not downloaded.")

        #self.fixture.download_blast_file(file_name, 0)
        #self.assertTrue(os.path.isfile(self.fixture.destination_dir + file_name), "File was not downloaded.")

    '''

    def test_backup(self):
        self.fixture.download(test_repeats=1)
        self.fixture.backup()
        self.assertTrue(os.path.isfile(self.fixture.backup_dir + 'README'), "No README found.")
        self.assertTrue(os.path.isfile(self.fixture.backup_dir + 'README+'), "No README+ found.")

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
