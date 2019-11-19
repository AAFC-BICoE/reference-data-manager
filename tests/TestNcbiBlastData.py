import os
import re
import unittest
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
        file_list = self.fixture.get_all_file(folder_url)
        self.assertGreater(len(file_list), 0, 'File list is empty')

        file_match = []
        for i in file_list:
            nr_nt_re = re.match("n[r|t]", i)
            if nr_nt_re:
                file_match.append(i)
        self.assertEqual(len(file_list), len(file_match),
                         'Missing some nrnt files')

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

    def test_5_download(self):
        print("Check file download...")
        start_time = os.path.getctime(self.fixture.destination_dir)
        self.fixture.download(download_file_number=2)
        end_time = os.path.getctime(self.fixture.destination_dir)
        self.assertGreater(end_time, start_time, "No new files downloaded")

        directory_list = os.listdir(self.fixture.destination_dir)
        download_file_size = 0
        if not set(directory_list).isdisjoint(set(self.fixture.all_files)):
            for directory_file in directory_list:
                if directory_file in self.fixture.all_files:
                    download_file_size = os.path.getsize(directory_file)
                    self.assertGreater(download_file_size, 0,
                                       'Downloaded file is empty')
        else:
            print('Expected download files not found')


if __name__ == '__main__':
    unittest.main()
