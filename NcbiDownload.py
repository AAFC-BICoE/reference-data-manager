'''
Created on Feb 2, 2018

@author: korolo
'''
import wget, ftplib, subprocess
import re

# TODO:
# check download integrity

class NcbiDownload:
    ''' Downloads data from NCBI'''
    def __init__(self):
        self.ncbi_ftp = "ftp.ncbi.nlm.nih.gov"
        self.genome_refseq_ftp_dir = "/genomes/refseq/"
        self.genome_genbank_ftp_dir = "/genomes/genbank/"
        self.assembly_file_name = "assembly_summary.txt"
        self.ftp_file_names = 'ftp_file_names.txt'

    def test_connection(self):
        '''Test if NCBI ftp is available.'''

        try:
            ftp_connection = ftplib.FTP(self.ncbi_ftp)
            ftp_connection.connect()
            ftp_connection.voidcmd("NOOP")
            ftp_connection.quit()
            return True
        except:
            return False

    def parse_assembly_file(self, assembly_file, output_file):
        '''
        Parses assembly_reference.txt file from NCBI and extracts full ftp files paths to download.
        :param assembly_file: full path to the assembly_summary.txt
        :param output_file: full path to the file which will contain the result of parsing
        :return: True if successfull, False otherwise
        '''
        try:
            with open(assembly_file, "r") as in_obj, open(output_file, 'w') as out_obj:
                in_obj.readline(), in_obj.readline()  # skip first 2 lines
                for line in in_obj:
                    # Parse and write to file
                    line_items = re.split(r'\t', line)
                    #print("{}\t{}".format(line_items[11], line_items[19]))

                    if line_items[11] == 'Complete Genome':
                        dir_name = line_items[19]
                        dir_list = re.split('/', dir_name)
                        full_file_name = "{}/{}_genomic.fna.gz".format(dir_name, dir_list[-1])
                        out_obj.write(full_file_name + '\n')
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

        '''
        if not self.test_connection():
            print("No connection to NCBI.")
            exit(0)
        '''

        ftp_url = "ftp://{0}/genomes/{1}/{2}/{3}".format(self.ncbi_ftp, ncbi_db, ncbi_kingdom_keyword, self.assembly_file_name)
        print("NcbiDownload ftp: " + ftp_url)

        filename = wget.download(ftp_url, out=disk_path)


        if self.parse_assembly_file(disk_path+self.assembly_file_name, disk_path + self.ftp_file_names):
            print("Parsed successfully")

        else:
            print("Failed to parse.")

        '''
        try:
            # The commands below are copied from NCBI help page on data download https://www.ncbi.nlm.nih.gov/genome/doc/ftpfaq/#allcomplete
            # awk -F "\t" '$12=="Complete Genome" && $11=="latest"{print $20}' assembly_summary.txt > ftpdirpaths
            list_paths_cmd = 'awk -F "\\t" \'$12=="Complete Genome" && $11=="latest"{print $20}\' assembly_summary.txt > ftpdirpaths'
            print(list_paths_cmd)

            output = subprocess.check_output('ls', shell=True)
            print(output)
            list_result = subprocess.check_output(list_paths_cmd, shell=True)

            # awk 'BEGIN{FS=OFS="/";filesuffix="genomic.gbff.gz"}{ftpdir=$0;asm=$10;file=asm"_"filesuffix;print ftpdir,file}' ftpdirpaths > ftpfilepaths
            add_file_names_cmd = 'awk \'BEGIN{FS=OFS="/";filesuffix="genomic.gbff.gz"}{ftpdir=$0;asm=$10;file=asm"_"filesuffix;print ftpdir,file}\' ftpdirpaths > ftpfilepaths'
            add_names_result = subprocess.check_output(add_file_names_cmd, shell=True)
        except subprocess.CalledProcessError as e:
            print("Error processing assembly file for {}".format(ncbi_kingdom_keyword))
        '''

if __name__ == "__main__":
    #NcbiDownload.download_genomes('refseq','fungi','~/reference-data-manager/out/')
    #NcbiDownload().download_refseq_genomes("fungi","~/reference-data-manager/out/")
    pass