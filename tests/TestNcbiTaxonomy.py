import unittest
import os
from time import gmtime, strftime
from brdm.NcbiTaxonomyData import NcbiTaxonomyData


class TestNcbiTaxonomyData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        cls.fixture = NcbiTaxonomyData('{}/test_config.yaml'
                                       .format(dir_path))

    '''
    @classmethod
    def tearDownClass(self):

        if os.path.exists(self.fixture.destination_dir):
            shutil.rmtree(self.fixture.destination_dir)
        if os.path.exists(self.fixture.backup_dir):
            shutil.rmtree(self.fixture.backup_dir)

        pass
    '''

    def test_1_https_connect(self):
        print('Check https connection...')
        session_requests, status = self.fixture.https_connect()
        session_requests.close()
        self.assertTrue(status, 'connection Failed')

    def test_2_download(self):
        print('Check method download...')
        success = self.fixture.download(test=True)
        self.assertTrue(success, 'Failed in NCBI taxonomy download.')

    def test_3_update(self):
        print('Update ncbi taxonomy...')
        success = self.fixture.update()
        self.assertTrue(success, 'Failed in NCBI update.')

    def test_4_readme(self):
        print('Check readme files...')
        ncbi_readme = os.path.join(self.fixture.destination_dir,
                                   self.fixture.info_file_name)
        self.assertTrue(os.path.isfile(ncbi_readme),
                        'Cannot find NCBI taxonomy README file.')
        readme_file = os.path.join(self.fixture.destination_dir,
                                   self.fixture.config['readme_file'])
        self.assertTrue(os.path.isfile(readme_file),
                        'Cannot find RDM README+ file.')

    def test_5_restore(self):
        print('Restore ncbi taxonomy...')
        success = self.fixture.restore(strftime('%Y-%m-%d', gmtime()),
                                       os.path.join(
                                           self.fixture.destination_dir,
                                           'restoreTaxonomy')
                                       )
        self.assertTrue(success, 'Failed in NCBI taxonomy restore.')


if __name__ == '__main__':
    unittest.main()
