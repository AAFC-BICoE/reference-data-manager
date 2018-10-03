import unittest
import os, shutil
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)
from brdm.NcbiData import NcbiData

class TestNcbiData(unittest.TestCase):


    def setUp(self):
        self.fixture = NcbiData('test_config.yaml')


    def tearDown(self):
        if os.path.exists(self.fixture.destination_dir):
            shutil.rmtree(self.fixture.destination_dir)


    def test_getProperties(self):
        expected_dir = os.path.abspath('../../../out/test/ncbi/')+'/'
        self.assertEqual(self.fixture.destination_dir, expected_dir)

if __name__ == '__main__':
    unittest.main()
