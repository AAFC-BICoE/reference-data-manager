# Download, update and manage reference data for bioinformatics
#
# author: Oksana Korol
import os

start_dir = "out/reference"
wholegenomes_kingdoms = ["archaea", "bacteria", "fungi", "invertebrate"]
barcode_dirs = ["16S_Bacteria", "16S_Archea", "Fungi_ITS", "Insect_CO1"]
# Move the taxonomy out to the same level as WholeGenome
#ref_data_dirs = ['Taxonomy', 'Fasta', 'ToolDB']
ref_data_dirs = ['Fasta', 'ToolDB']
taxonomy_formats = ['qiime', 'mothur']


def main():
    try:
        for k in wholegenomes_kingdoms:
            kingdom_dir = "{0}/WholeGenome/{1}".format(start_dir, k)
            for d in ref_data_dirs:
                os.makedirs("{0}/ncbi/RefSeq/{1}".format(kingdom_dir, d), exist_ok=True)
                os.makedirs("{0}/ncbi/GenBank/{1}".format(kingdom_dir, d), exist_ok=True)
            os.makedirs("{0}/WholeGenome/ToolDB/Humann".format(start_dir), exist_ok=True)
            os.makedirs("{0}/WholeGenome/ToolDB/Metamos".format(start_dir), exist_ok=True)
            os.makedirs("{0}/WholeGenome/ToolDB/Kraken".format(start_dir), exist_ok=True)


        for k in barcode_dirs:
            barcode_dir = "{0}/DNA_Barcodes/{1}".format(start_dir, k)
            for d in ref_data_dirs:
                # This is probably too specific for barcodes
                # os.makedirs("{0}/ncbi/RefSeq/{1}".format(loci_dir, d), exist_ok=True)
                # os.makedirs("{0}/ncbi/GenBank/{1}".format(loci_dir, d), exist_ok=True)
                os.makedirs("{0}/ncbi/{1}".format(barcode_dir, d), exist_ok=True)

        for k in taxonomy_formats:
            taxonomy_dir = "{0}/Taxonomy/ncbi/ToolFormats/{1}".format(start_dir, k)
            os.makedirs(taxonomy_dir, exist_ok=True)

        # ncbi_nr_nt is not a very good name, think of a better one
        os.makedirs("{0}/ncbi_nr_nt".format(start_dir), exist_ok=True)

        # If we want proteins in the future, they should be at this level:
        #os.makedirs("{0}/Protein".format(start_dir), exist_ok=True)
        # refseq_protein database
        os.makedirs("{0}/Protein/ncbi/RefSeq/".format(start_dir), exist_ok=True)
        os.makedirs("{0}/Protein/ToolDB/Humann/".format(start_dir), exist_ok=True)

    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


if __name__ == "__main__":
    main()