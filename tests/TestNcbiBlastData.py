import unittest
import os
from brdm.NcbiBlastData import NcbiBlastData


class TestNcbiBlastData(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.fixture = NcbiBlastData('{}/test_config.yaml'.format(dir_path))

    '''
    @classmethod
    def tearDownClass(self):

        if os.path.exists(self.fixture.destination_dir):
            shutil.rmtree(self.fixture.destination_dir)
        if os.path.exists(self.fixture.backup_dir):
            shutil.rmtree(self.fixture.backup_dir)

        pass
    '''

    def test_1_get_all_file(self):
        print('Get ncbi nrnt blast file list...')
        folder_url = os.path.join(self.fixture.login_url,
                                  self.fixture.download_folder)
        all_file = self.fixture.get_all_file(folder_url)
        print('number of nrnt files :', len(all_file))
        self.assertGreater(len(all_file), 100, 'Missing some nrnt files.')

    def test_2_update(self, files=2):
        print('Update ncbi nrnt blast...')
        success = self.fixture.update(file_number=files)
        self.assertTrue(success, 'NCBI nrnt update did not return True.')

    def test_3_unzip(self):
        print('Unzip ncbi nrnt blast...')
        success = self.fixture.unzip()
        self.assertTrue(success, 'NCBI nrnt unzip did not return True.')

    def test_4_readme(self):
        print('Check readme files...')
        ncbi_readme = os.path.join(self.fixture.destination_dir,
                                   self.fixture.info_file_name)
        self.assertTrue(os.path.isfile(ncbi_readme),
                        'Cannot find NCBI README file.')
        readme_file = os.path.join(self.fixture.destination_dir,
                                   self.fixture.config['readme_file'])
        self.assertTrue(os.path.isfile(readme_file),
                        'Cannot find RDM README+ file.')


if __name__ == '__main__':
    unittest.main()
