import unittest
from NcbiBlastData import NcbiBlastData
import os, shutil

class TestNcbiData(unittest.TestCase):


    def setUp(self):
        self.fixture = NcbiBlastData('test_config.yaml')


    def tearDown(self):
        if os.path.exists(self.fixture.destination_dir):
            shutil.rmtree(self.fixture.destination_dir)


    def testDownload(self):
        readme_file = self.fixture.destination_dir + "README+"
        print(readme_file)

        self.fixture.download()

        self.assertTrue(os.path.isfile(readme_file), "README+ file should be created with the download.")

        ncbi_readme = self.fixture.destination_dir + 'README'
        self.assertTrue(os.path.isfile(ncbi_readme), "NCBI README file is not found in the download directory.")