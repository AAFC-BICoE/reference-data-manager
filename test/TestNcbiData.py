import unittest
from NcbiData import NcbiData
import os, shutil

class TestNcbiData(unittest.TestCase):

    _test_yaml_file = 'config.yaml'

    def setUp(self):
        self.fixture = NcbiData(self._test_yaml_file)

    def tearDown(self):
        #shutil.rmtree(self.test_data_dir)
        pass


    def test_download_refseq_genomes(self):

        ncbiUpdateFrequency = self.fixture.getUpdateFrequency()
        self.assertTrue(ncbiUpdateFrequency == 30, "Expecting 30.")

