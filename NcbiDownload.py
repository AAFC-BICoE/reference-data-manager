'''
Created on Feb 2, 2018

@author: korolo
'''
import ftplib


class NcbiDownload:
    ''' Downloads data from NCBI'''
    def __init__(self):
        self.ncbi_ftp = "ftp.ncbi.nlm.nih.gov"
        self.genome_refseq_path = "/genomes/refseq/"
        self.genome_genbank_path = "/genomes/genbank/"
        self.listing_file_name = "assembly_summary.txt"


    def download_refseq_genomes(self, ncbi_kingdom_keyword, disk_path):
        self.download_genomes('refseq', ncbi_kingdom_keyword, disk_path)


    def download_genomes(self, ncbi_db, ncbi_kingdom_keyword, disk_path):
        # TODO: Check / massage the coming data
        # Disk path ends with /
        if not disk_path.endswith("/"):
            disk_path = disk_path + "/"
        # kingdoms are in accepted list
        print("NCBIDownload diskpath: "+disk_path)

        #ftp_path = "{1}{2}".format(self.genome_refseq_path, ncbi_kingdom_keyword)
        ftp_path = self.genome_refseq_path + ncbi_kingdom_keyword
        if ncbi_db == 'genbank':
            ftp_path = "{1}{2}".format(self.genome_genbank_path, ncbi_kingdom_keyword)


        with ftplib.FTP(self.ncbi_ftp) as ftp:
            local_listing_file_path = "{0}{1}".format(disk_path, self.listing_file_name)
            lf = open(local_listing_file_path, "wb")
            #ftp.cwd(ftp_path)
            ftp.cwd("genomes")
            ftp.retrlines("RETR " + self.listing_file_name, lf.write)
            lf.close()


if __name__ == "__main__":
    #NcbiDownload.download_genomes('refseq','fungi','~/reference-data-manager/out/')
    #NcbiDownload().download_refseq_genomes("fungi","~/reference-data-manager/out/")
    pass