import ftplib


class NcbiDownload:
    ncbi_ftp = "ftp://ftp.ncbi.nlm.nih.gov"
    genome_refseq_path = "/genomes/refseq/"
    genome_genbank_path = "/genomes/genbank/"
    listing_file_name = "assembly_summary.tx"

    @classmethod
    def download_refseq_genomes(ncbi_kingdom_keyword, disk_path):
        Ncbi.download_genomes('refseq', ncbi_kingdom_keyword)

    @classmethod
    def download_genomes(ncbi_db, ncbi_kingdom_keyword, disk_path):
        # TODO: Check / massage the coming data
        # Disk path ends with /
        # kingdoms are in accepted list

        ftp_url = Ncbi.ncbi_ftp
        if ncbi_db == 'refseq':
            ftp_url == "{0}{1}".format(ftp_url, Ncbi.genome_refseq_path)
        else:
            ftp_url == "{0}{1}".format(ftp_url, Ncbi.genome_genbank_path)

        with ftplib.FTP(ftp_url) as ftp:
            local_listing_file_path = "{0}{1}".format(disk_path, Ncbi.listing_file_name)
