import unittest
import os
from time import gmtime, strftime
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)

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
    
    def test_1_getSubsetList(self):
        self.assertEqual(self.fixture.query[0], "CO1p | COI and Phyllocnistis citrella", "query1 OK" )
        self.assertEqual(self.fixture.query[1], "ITSD | Internal Transcribed Spacer[All Fields] and Diplodia seriata", "query2 OK" )
        
    def test_2_update(self):
        success = self.fixture.update()
        self.assertTrue(success, "NCBI update did not return True.")
        readme_file = os.path.join(self.fixture.destination_dir,"README+")
        self.assertTrue(os.path.isfile(readme_file), "RDM's's README+ file is not found in the download directory.")
        
    def test_3_restore(self):
        success = self.fixture.restore(strftime("%Y-%m-%d", gmtime()), "restoreTaxonomy")
        self.assertTrue(success, "NCBI update did not return True.")
    
    '''
    
    def testDownload_a_subset(self):
        
        success = self.fixture.download_a_subset( "CO1p", "COI and Phyllocnistis citrella")
        self.assertTrue(success, "NCBI subset return False.")
        self.assertTrue(os.path.isfile(self.fixture.destination_dir + 'CO1p.accID'),
                        "CO1p.accID was not found.")
        lines = 0
        with open('CO1p.accID') as f:
            for line in f:
                lines = lines + 1
        self.assertEqual(lines, 46, "different CO1p.accID number")
    
    def test_accID_to_info(self):
        success = self.fixture.accID_to_info()
        self.assertTrue(success, "NCBI subset accID_to_info return False.")
        
    def test_backup(self):
        self.fixture.download()
        backup = self.fixture.backup()
        self.assertTrue(backup, "backup OK")
    '''
    
   
if __name__ == '__main__':
    unittest.main() 
    