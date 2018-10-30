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
        
    def test_1_update(self, files = 2):
        print("Update ncbi nrnt blast...")
        success = self.fixture.update(file_number =  files)
        self.assertTrue(success, "NCBI update did not return True.")
        
    
    def test_2_unzip(self):
        print("Unzip ncbi nrnt blast...")
        success = self.fixture.unzip()
        self.assertTrue(success, "NCBI unzip did not return True.")
    
    
    def test_3_readme(self):
        print("Check readme files...")
        ncbi_readme = os.path.join(self.fixture.destination_dir, self.fixture.info_file_name)
        self.assertTrue(os.path.isfile(ncbi_readme), "NCBI README file is not found in the download directory.")
        readme_file = os.path.join(self.fixture.destination_dir, "README+")
        self.assertTrue(os.path.isfile(readme_file), "RDM's's README+ file is not found in the download directory.")
           
if __name__ == '__main__':
    unittest.main() 