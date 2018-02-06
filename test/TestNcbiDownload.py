'''
Created on Feb 2, 2018

@author: korolo
'''

import unittest
import NcbiDownload
import os, shutil

class TestNcbiDownload(unittest.TestCase):

    test_data_dir = "{0}/{1}".format(os.getcwd(),"testdata")

    def setUp(self):
        print("dir:   " + self.test_data_dir)
        os.makedirs(self.test_data_dir, exist_ok=True)

    def tearDown(self):
        #shutil.rmtree("{0}/{1}".format(working_dir,self.test_data_dir))
        pass

    def test_download_refseq_genomes(self):
        fixture = NcbiDownload.NcbiDownload()
        fixture.download_refseq_genomes('fungi', self.test_data_dir)
        print("{0}/{1}".format(self.test_data_dir, fixture.listing_file_name))
        self.assertTrue(os.path.exists("{0}/{1}".format(self.test_data_dir, fixture.listing_file_name)), \
                        "Assembly summary file was not downloaded.")

        self.assertTrue(os.path.exists("{0}/{1}".format(self.test_data_dir, 'ftpdirpaths')), \
                        "Assembly ftp paths were not extracted.")

        self.assertTrue(os.path.exists("{0}/{1}".format(self.test_data_dir, 'ftpfilepaths')), \
                        "Assembly list file were not created.")
