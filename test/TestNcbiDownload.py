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
        print("Test output dir:   " + self.test_data_dir)
        os.makedirs(self.test_data_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_data_dir)
        pass


    def test_download_refseq_genomes(self):
        fixture = NcbiDownload.NcbiDownload()
        file_num = fixture.download_refseq_genomes('fungi', self.test_data_dir)
        print("Test RefSeq: {0}/{1}".format(self.test_data_dir, fixture.assembly_file_name))

        self.assertTrue(file_num >= 8, "Expecting more then 8 complete fungal genomes from RefSeq, but downloaded {}.".format(file_num))

        self.assertTrue(os.path.exists("{0}/{1}".format(self.test_data_dir, fixture.assembly_file_name)), \
                        "Assembly summary file was not downloaded.")

        self.assertTrue(os.path.exists("{0}/{1}".format(self.test_data_dir, fixture.ftp_file_names)), \
                        "Assembly ftp paths were not extracted.")

        # Test for downloaded fasta
        self.assertTrue(os.path.exists("{0}/{1}".format(self.test_data_dir, 'GCF_001417885.1_Kmar_1.0_genomic.fna.gz')), \
                        "Expected fasta file is not in the download directory.")

        self.assertTrue(os.path.exists("{0}/{1}".format(self.test_data_dir, 'GCF_001640025.1_ASM164002v2_genomic.fna.gz')), \
                        "Expected fasta file is not in the download directory.")



    def test_download_genbank_genomes(self):
        fixture = NcbiDownload.NcbiDownload()
        file_num = fixture.download_genbank_genomes('fungi', self.test_data_dir)
        print("Test Genbank: {0}/{1}".format(self.test_data_dir, fixture.assembly_file_name))

        self.assertTrue(file_num >= 30, "Expecting more then 30 complete fungal genomes from GenBank, but downloaded {}.".format(file_num))
        self.assertTrue(os.path.exists("{0}/{1}".format(self.test_data_dir, fixture.assembly_file_name)), \
                        "Assembly summary file was not downloaded.")

        self.assertTrue(os.path.exists("{0}/{1}".format(self.test_data_dir, fixture.ftp_file_names)), \
                        "Assembly ftp paths were not extracted.")

        # Test for downloaded fasta
        self.assertTrue(os.path.exists("{0}/{1}".format(self.test_data_dir, 'GCA_000002515.1_ASM251v1_genomic.fna.gz')), \
                        "Expected fasta file is not in the download directory.")

        self.assertTrue(os.path.exists("{0}/{1}".format(self.test_data_dir, 'GCA_900149175.1_Msy_KS004_June2015_genomic.fna.gz')), \
                        "Expected fasta file is not in the download directory.")


    def test_query_download(self):
        fixture = NcbiDownload.NcbiDownload()
        file_num = fixture.download_barcodes('blah')
        self.assertTrue(file_num >= 8,
                "Expecting more then 8 fungal ITS sequences from RefSeq, but downloaded {}.".format(file_num))