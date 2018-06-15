import unittest
from NcbiData import NcbiData
import os, shutil

class TestNcbiData(unittest.TestCase):


    def setUp(self):
        self.fixture = NcbiData('test_config.yaml')


    def tearDown(self):
        if os.path.exists(self.fixture.destination_dir):
            shutil.rmtree(self.fixture.destination_dir)


    def test_getProperties(self):
        expected_dir = os.path.abspath('../../../out/test/ncbi/')+'/'
        self.assertEqual(self.fixture.destination_dir, expected_dir)

