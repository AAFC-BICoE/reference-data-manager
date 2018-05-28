import unittest
from NcbiData import NcbiData
import os, shutil

class TestNcbiData(unittest.TestCase):


    def setUp(self):
        self.fixture = NcbiData('test_config.yaml')


    def tearDown(self):
        #shutil.rmtree(self.fixture.getDestinationFolder())
        pass


    def test_download_refseq_genomes(self):

        ncbiUpdateFrequency = self.fixture.getUpdateFrequency()
        self.assertTrue(ncbiUpdateFrequency == 30, "Expecting 30.")

        destination_folder = self.fixture.getDestinationFolder()
        self.assertEqual(destination_folder, '../out/test/ncbi/')


    def testDownloadBlastDB(self):
        readme_file = self.fixture.getDestinationFolder() + "README+"
        print(readme_file)

        self.fixture.downloadBlastDB()

        self.assertTrue(os.path.isfile(readme_file), "README+ file should be created with the download.")