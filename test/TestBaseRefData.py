import unittest
from BaseRefData import BaseRefData
import os, shutil

class TestNcbiData(unittest.TestCase):

    def setUp(self):
        self.fixture = BaseRefData('test_config.yaml')
        self.local_write_dir = '../out/test/'


    def tearDown(self):
        if os.path.exists(self.fixture.destination_dir):
            shutil.rmtree(self.fixture.destination_dir)



    def test_download_delete_file(self):

        file_url = 'https://gist.github.com/oxyko/10798051fb9cf1e11f4baac2c6c49f3b/archive/44e343bfe87f56fbc8bb6fbf3a48294aa7b0a1b6.zip'

        local_file = self.fixture.download_file(file_url, self.local_write_dir)
        self.assertTrue(os.path.isfile(local_file), "Expecting file to be downloaded")

        self.fixture.delete_file(local_file)
        self.assertFalse(os.path.isfile(local_file), "Expecting file to be deleted")

    def test_write_readme(self):
        self.fixture.write_readme(download_url='http://some/url', files=['file1','file2', 'file3'], comment='This is a comment string.')
        expected_file_name = "{}{}".format(self.fixture.destination_dir, self.fixture.config['readme_file'])
        self.assertTrue(os.path.isfile(expected_file_name), "Expecting a readme file")