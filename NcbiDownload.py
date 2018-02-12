'''
Created on Feb 2, 2018

@author: korolo
'''
import wget, ftplib, subprocess
import re
# biopython
import Bio.Entrez as Entrez

# TODO:
## Time and throttle (if needed) ftp download
## Socket problem: Briefly looked into it. It happens during the unittest run. Seems to be a bug with urllib and unittest.
'''
When running TestNcbiDownload, get this error:
/usr/local/Cellar/python3/3.6.4_1/Frameworks/Python.framework/Versions/3.6/lib/python3.6/socket.py:657: ResourceWarning: unclosed <socket.socket fd=5, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=6, laddr=('192.168.0.109', 54039), raddr=('130.14.250.10', 21)>
  self._sock = None

Could be because of not finishing debugging of the unit test properly
'''
## check download integrity
##

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
        file_list = list()
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
                        file_list.append(full_file_name)
                        out_obj.write(full_file_name + '\n')
            return file_list
        except:
            # TODO log
            return None


    def download_refseq_genomes(self, ncbi_kingdom_keyword, disk_path):
        return self.download_genomes('refseq', ncbi_kingdom_keyword, disk_path)

    def download_genbank_genomes(self, ncbi_kingdom_keyword, disk_path):
        return self.download_genomes('genbank', ncbi_kingdom_keyword, disk_path)

    def download_genomes(self, ncbi_db, ncbi_kingdom_keyword, disk_path):
        '''

        :param ncbi_db:
        :param ncbi_kingdom_keyword:
        :param disk_path:
        :return: number of records that were downloaded
        '''
        # TODO: Check / massage the coming data
        # Disk path ends with /
        if not disk_path.endswith("/"):
            disk_path = disk_path + "/"
        # kingdoms are in accepted list
        print("NCBIDownload diskpath: "+disk_path)

        if not self.test_connection():
            print("No connection to NCBI.")
            return 0

        ftp_url = "ftp://{0}/genomes/{1}/{2}/{3}".format(self.ncbi_ftp, ncbi_db, ncbi_kingdom_keyword, self.assembly_file_name)
        print("NcbiDownload ftp: " + ftp_url)

        filename = wget.download(ftp_url, out=disk_path)


        ftp_file_list = self.parse_assembly_file(disk_path+self.assembly_file_name, disk_path + self.ftp_file_names)
        if ftp_file_list is not None:
            for f in ftp_file_list:
                wget.download(f, out=disk_path)


        return len(ftp_file_list)

    def download_fungal_ITS(self):
        return self.download_barcodes('some ncbi query')


    def download_barcodes(self, ncbi_query):
        '''
        Perform a query on NCBI and download resulting sequences
        :param ncbi_query:
        :return:
        '''
        Entrez.email = 'oksana.korol@agr.gc.ca'
        Entrez.tool = 'AAFC Reference Data Manager'

        handle = Entrez.einfo()
        result = handle.read()
        handle.close()

        print(result)

        return 0



if __name__ == "__main__":
    #NcbiDownload.download_genomes('refseq','fungi','~/reference-data-manager/out/')
    #NcbiDownload().download_refseq_genomes("fungi","~/reference-data-manager/out/")
    pass