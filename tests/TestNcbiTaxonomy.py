import unittest
import os
from time import gmtime, strftime
from brdm.NcbiTaxonomyData import NcbiTaxonomyData

class TestNcbiTaxonomyData(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.fixture = NcbiTaxonomyData('{}/test_config.yaml'.format(dir_path))
    
    '''
    @classmethod
    def tearDownClass(self):

        if os.path.exists(self.fixture.destination_dir):
            shutil.rmtree(self.fixture.destination_dir)
        if os.path.exists(self.fixture.backup_dir):
            shutil.rmtree(self.fixture.backup_dir)

        pass
    '''
        
    def test_1_getConfig(self):
        print('Check config file...')
        self.assertEqual(self.fixture.login_url, "https://ftp.ncbi.nlm.nih.gov", "login_url OK" )
        self.assertEqual(self.fixture.download_file, 
                         "new_taxdump.tar.gz", 
                         "download_file address OK" )
    
      
    def test_2_update(self):
        print('Update ncbi taxonomy...')
        success = self.fixture.update()
        self.assertTrue(success, "NCBI update did not return True.")
        ncbi_readme = os.path.join(self.fixture.destination_dir, self.fixture.info_file_name)
        self.assertTrue(os.path.isfile(ncbi_readme), "NCBI README file is not found in the download directory.")
        readme_file = os.path.join(self.fixture.destination_dir, "README+")
        self.assertTrue(os.path.isfile(readme_file), "RDM's's README+ file is not found in the download directory.")
    
    
    def test_3_restore(self):
        print('Restore ncbi taxonomy...')
        success = self.fixture.restore(strftime("%Y-%m-%d", gmtime()), "restoreTaxonomy")
        self.assertTrue(success, "NCBI update did not return True.")
        
    
    '''
    def test_https_connect(self):
        session_requests, status = self.fixture.https_connect()
        session_requests.close()
        self.assertTrue(status, "connection OK")
       
    def test_download(self):
        success = self.fixture.download(test=True)
        self.assertTrue(success, "NCBI taxonomy download a file(readMe file).")
    
        
    def test_format_taxonomy(self):
        os.chdir("/home/chz001/myspace/reference-data-manager/output/ncbi/taxonomy/")
        success = self.fixture.format_taxonomy(self.fixture._taxonomy_file)
        self.assertTrue(success, "NCBI taxonomy format.")  
        
    def test_backup(self):
        self.fixture.download()
        backup = self.fixture.backup()
        self.assertTrue(backup, "backup OK")
    '''
   
if __name__ == '__main__':
    unittest.main() 
    