'''
Created on Feb 2, 2018

@author: korolo
'''
import wget, ftplib, subprocess


class NcbiDownload:
    ''' Downloads data from NCBI'''
    def __init__(self):
        self.ncbi_ftp = "ftp://ftp.ncbi.nlm.nih.gov"
        self.genome_refseq_path = "/genomes/refseq/"
        self.genome_genbank_path = "/genomes/genbank/"
        self.listing_file_name = "assembly_summary.txt"

    def test_connection(self):
        '''Test if NCBI ftp is available.'''

        try:
            ftp_connection = ftplib.FTP(self.ncbi_ftp)
            ftp_connection.connect()
            ftp_connection.voidcmd('NOOP')
            ftp_connection.close()
            return True
        except:
            return False


    def download_refseq_genomes(self, ncbi_kingdom_keyword, disk_path):
        self.download_genomes('refseq', ncbi_kingdom_keyword, disk_path)


    def download_genomes(self, ncbi_db, ncbi_kingdom_keyword, disk_path):
        # TODO: Check / massage the coming data
        # Disk path ends with /
        if not disk_path.endswith("/"):
            disk_path = disk_path + "/"
        # kingdoms are in accepted list
        print("NCBIDownload diskpath: "+disk_path)

        if not self.test_connection():
            print("No connection to NCBI.")
            exit(0)

        ftp_url = "{0}{1}{2}/{3}".format(self.ncbi_ftp, self.genome_refseq_path, ncbi_kingdom_keyword, self.listing_file_name)
        if ncbi_db == 'genbank':
            ftp_url = "{0}{1}{2}/{3}".format(self.ncbi_ftp, self.genome_genbank_path, ncbi_kingdom_keyword, self.listing_file_name)

        filename = wget.download(ftp_url, out=disk_path)

        try:
            # The commands below are copied from NCBI help page on data download https://www.ncbi.nlm.nih.gov/genome/doc/ftpfaq/#allcomplete
            # awk -F "\t" '$12=="Complete Genome" && $11=="latest"{print $20}' assembly_summary.txt > ftpdirpaths
            list_paths_cmd = 'awk -F "\\t" \'$12=="Complete Genome" && $11=="latest"{print $20}\' assembly_summary.txt > ftpdirpaths'

            list_result = subprocess.check_output(list_paths_cmd, shell=True)

            # awk 'BEGIN{FS=OFS="/";filesuffix="genomic.gbff.gz"}{ftpdir=$0;asm=$10;file=asm"_"filesuffix;print ftpdir,file}' ftpdirpaths > ftpfilepaths
            add_file_names_cmd = 'awk \'BEGIN{FS=OFS="/";filesuffix="genomic.gbff.gz"}{ftpdir=$0;asm=$10;file=asm"_"filesuffix;print ftpdir,file}\' ftpdirpaths > ftpfilepaths'
            add_names_result = subprocess.check_output(add_file_names_cmd, shell=True)
        except subprocess.CalledProcessError as e:
            print("Error processing assembly file for {}".format(ncbi_kingdom_keyword))

if __name__ == "__main__":
    #NcbiDownload.download_genomes('refseq','fungi','~/reference-data-manager/out/')
    #NcbiDownload().download_refseq_genomes("fungi","~/reference-data-manager/out/")
    pass