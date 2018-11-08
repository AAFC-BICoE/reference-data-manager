import unittest
import os
from time import gmtime, strftime
from brdm.NcbiSubsetData import NcbiSubsetData


class TestNcbiSebsetData(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.fixture = NcbiSubsetData('{}/test_config.yaml'.format(dir_path))

    '''
    @classmethod
    def tearDownClass(self):

        if os.path.exists(self.fixture.destination_dir):
            shutil.rmtree(self.fixture.destination_dir)
        if os.path.exists(self.fixture.backup_dir):
            shutil.rmtree(self.fixture.backup_dir)

        pass
    '''

    def test_1_get_subset(self):
        print('Check config file...')
        self.assertTrue(self.fixture.query, 'No query in test_config.yaml')

    def test_2_download_a_subset(self):
        print('Download a subset...')
        subset_file_name = self.fixture.query[0].split('|')[0].strip()
        subset_query = self.fixture.query[0].split('|')[1].strip()
        success = self.fixture.download_a_subset(
                                    subset_file_name, subset_query)          
        self.assertTrue(success, 'Failed in download.')

    def test_3_accID_to_info(self):
        print('Retrieve sequences and taxonomy...')
        success = self.fixture.accID_to_info(self.fixture.destination_dir)
        self.assertTrue(success, 'Failed in NCBI subset accID_to_info.')

    def test_4_update(self):
        print('Update ncbi subsets...')
        success = self.fixture.update()
        self.assertTrue(success, 'Failed in NCBI update.')

    def test_5_readme(self):
        print('Check readme files...')
        readme_file = os.path.join(self.fixture.destination_dir,
                                   self.fixture.config['readme_file'])
        self.assertTrue(os.path.isfile(readme_file),
                        'Cannot find RDM README+ file.')

    def test_6_restore(self):
        print('Restore ncbi subsets...')
        success = self.fixture.restore(strftime("%Y-%m-%d", gmtime()),
                                       os.path.join(
                                            self.fixture.destination_dir,
                                            'restoreSubsets')
                                       )
        self.assertTrue(success, 'NCBI restore did not return True.')
    

if __name__ == '__main__':
    unittest.main()
    