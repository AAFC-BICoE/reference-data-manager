import unittest
import os
import shutil
from time import gmtime, strftime
from brdm.SilvaData import SilvaData


class TestSilvaData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        cls.fixture = SilvaData('{}/test_config.yaml'.format(dir_path))

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.fixture.destination_dir):
            shutil.rmtree(cls.fixture.destination_dir)
        if os.path.exists(cls.fixture.backup_dir):
            shutil.rmtree(cls.fixture.backup_dir)
        pass

    def test_1_download(self):
        print('Check method download...')
        success = self.fixture.download(test=True)
        self.assertTrue(success, 'Failed in silva download.')

    def test_2_update(self):
        print('Update silva Data...')
        success = self.fixture.update()
        self.assertTrue(success, 'Failed in silva update.')

    def test_3_readme(self):
        print('Check readme files...')
        readme_file = os.path.join(self.fixture.destination_dir,
                                   self.fixture.config['readme_file'])
        self.assertTrue(os.path.isfile(readme_file),
                        'Cannot find RDM README+ file.')

    def test_4_backup(self):
        print('Check silva data backup ...')
        backup_folder = os.path.join(self.fixture.backup_dir,
                                     strftime('%Y-%m-%d', gmtime()))
        readme_file = os.path.join(backup_folder,
                                   self.fixture.config['readme_file'])
        self.assertTrue(os.path.isfile(readme_file),
                        'Failed in backup: Cannot find RDM README+ file.')


if __name__ == '__main__':
    unittest.main()
