import sys
import argparse
from brdm.NcbiBlastData import NcbiBlastData
from brdm.NcbiSubsetData import NcbiSubsetData
from brdm.NcbiTaxonomyData import NcbiTaxonomyData
from brdm.NcbiWholeGenome import NcbiWholeGenome
from brdm.GreenGeneData import GreenGeneData
#from brdm.UniteData import UniteData
from brdm import brdm_root

def parse_input_args(argv):
    ''' Parses command line arguments '''
    parser = argparse.ArgumentParser(description=
            "Reference Data Manager (RDM) is used to download, update and backup bioinformatics reference data.")
    # The path to the configuration file. If the path is ignored, then the default config file will be loaded(./brdm/config.ini)  
    parser.add_argument('--config-file', help="Path to the config file. Can be ignored if your config file \
                       is in the same folder as the sample config file (brdm/ folder)", dest="config_file",
                        required=False)
    # Required by database restore. restore_destination is the path to the restored database
    # restore_date is the specific version(in date) of the database you want to restore
    parser.add_argument('--restore-destination', help = "Required by all the database restore methods. \
                       Path to your restored database.", dest="restore_destination")
    parser.add_argument("--restore-date", help = "Required by all the database restore methods. \
                       The version of the database to be restored; format: yyyy-mm-dd", dest = "restore_source")
    # Download NCBI nrnt blast database
    parser.add_argument('--update-ncbi-blast', help="Download NCBI nr/nt blast database.", dest="ncbi_blast_update",
                        action='store_true', required=False)
    # Unzip NCBI nrnt blast database
    parser.add_argument('--unzip-ncbi-blast', help="Unzip NCBI nr/nt blast database.", dest="ncbi_blast_unzip",
                        action='store_true', required=False)
    # Download NCBI taxonomy database
    parser.add_argument('--update-ncbi-taxonomy', help="Update NCBI taxonomy database.", dest="ncbi_taxonomy_update",
                        action = 'store_true', required=False)
    # Restore NCBI taxonomy database. Arguments --restore-destination and --restore-source are required
    # See the help information of --restore-destination and --restore-source for more info 
    # An example python main.py --restore-ncbi-taxonomy --restore-destination /path/to/a/folder  --restore-source 2018-09-10
    parser.add_argument('--restore-ncbi-taxonomy', help="Restore NCBI taxonomy database. --restore-destination and \
                     --restore-source are required ", dest="ncbi_taxonomy_restore",
                        action = 'store_true',required=False)
    # NCBI subsets database(ITS, CO1, etc.). NCBI nrnt and NCBI taxonomy database are required to complete the whole update process. 
    parser.add_argument('--update-ncbi-subsets', help="Update NCBI subsets (ITS, CO1, etc.)", dest="ncbi_subsets_update",
                        action = 'store_true', required=False)
    parser.add_argument('--restore-ncbi-subsets', help="Restore NCBI's subsets (ITS, CO1, etc.) --restore-destination and \
                     --restore-source are required", dest="ncbi_subsets_restore", action = 'store_true', required=False)
    
    
    
    
    # NCBI whole genomes (e.g. genome sequences for bacteria, fungi )
    parser.add_argument('--update-ncbi-wholegenomes', help="Update NCBI whole genomes", dest="ncbi_whole_genome_update",
                        action = 'store_true', required=False)
    # Green gene
    parser.add_argument('--update-greengene', help="Update GreenGene data", dest="greengene_update",
                        action = 'store_true', required=False)
    parser.add_argument('--format-greengene', help="Format GreenGene data", dest="greengene_format",
                        action = 'store_true', required=False)
    # Unite data
    parser.add_argument('--update-unitedata', help="Update unite data", dest="unitedata_update",
                        action = 'store_true', required=False)
    args = parser.parse_args(argv)

    if not (args.ncbi_blast_update or \
            args.ncbi_blast_unzip or \
            args.ncbi_taxonomy_update or \
            args.ncbi_taxonomy_restore or \
            args.ncbi_subsets_update or \
            args.ncbi_subsets_restore or \
            args.ncbi_whole_genome_update or \
            args.greengene_update or \
            args.greengene_format or \
            args.unitedata_update):
        parser.error('No action requested. Please add one of the required actions.')

    return args


    
def execute_script(input_args):
    parsed_args = parse_input_args(input_args)
    config_file = "{}/config.yaml".format(brdm_root.path())
    
    if parsed_args.config_file:
        config_file = parsed_args.config_file;
       
    if parsed_args.ncbi_blast_update:
        print("Running NCBI nrnt blast database update")
        blastData = NcbiBlastData(config_file)
        success = blastData.update()
        if success:
            print("NCBI nrnt blast database were downloaded successfully. It is located at: {}".format(
                blastData.destination_dir
            ))
            
    if parsed_args.ncbi_blast_unzip:
        print("Running NCBI nrnt blast database unzip")
        blastData = NcbiBlastData(config_file)
        success = blastData.unzip()
        if success:
            print("NCBI nrnt blast database were unzipped successfully. It is located at: {}".format(
                blastData.destination_dir
            ))
        
    if parsed_args.ncbi_taxonomy_update:
        print("Running NCBI Taxonomy update")
        taxonomyData = NcbiTaxonomyData(config_file)
        success = taxonomyData.update()
        if success:
            print("NCBI taxonomy data were updated successfully. It is located at: {}".format(
                taxonomyData.destination_dir
            ))
            
    if parsed_args.ncbi_taxonomy_restore:
        print("Running NCBI Taxonomy restore ")
        if not parsed_args.restore_destination:
            print("Error: please provide the path of the destination for restoring")
            exit(1)
        if not parsed_args.restore_source:
            print("Error: please provide the version (in date format yyyy-mm-dd) of the database for restoring")
            exit(1)
        taxonomyData = NcbiTaxonomyData(config_file)
        success = taxonomyData.restore(parsed_args.restore_source, parsed_args.restore_destination)
        if success:
            print("NCBI taxonomy data were restored successfully. It is located at: {}".format(
                parsed_args.restore_destination
            ))
            
    if parsed_args.ncbi_subsets_update:
        print("Running NCBI Subsets update")
        subsetData = NcbiSubsetData(config_file)
        success = subsetData.update()
        if success:
            print("NCBI subsets reference data were updated successfully. It is located at: {}".format(
                subsetData.destination_dir
            )) 
    
    if parsed_args.ncbi_subsets_restore:
        print("Restore NCBI subsets:")
        if not parsed_args.restore_destination:
            print("Error, please provide the path of the destination for restoring")
            exit(1)
        if not parsed_args.restore_source:
            print("Error, please provide the version (in date format yyyy-mm-dd) of the database for restoring")
            exit(1)
        subsetData = NcbiSubsetData(config_file)
        success = subsetData.restore(parsed_args.restore_source, parsed_args.restore_destination)
        if success:
            print("NCBI subsets reference data were restored successfully. It is located at: {}".format(
                parsed_args.restore_destination
            ))
                          
    if parsed_args.ncbi_whole_genome_update:
        print("Running NCBI whole genome update")
        wholeGenomeData = NcbiWholeGenome(config_file)
        success = wholeGenomeData.update()
        if success:
            print("NCBI whole genome data were updated successfully. It is located at: {}".format(
                wholeGenomeData.destination_dir
            ))  
            
    if parsed_args.greengene_update:
        print("Running greengene update")
        greengene = GreenGeneData(config_file)
        success = greengene.update()
        if success:
            print("GreenGene data were updated successfully. It is located at: {}".format(
                greengene.destination_dir
            ))
            
    if parsed_args.greengene_format:
        print("Running greengene format")
        greengene = GreenGeneData(config_file)
        success = greengene.format()
        if success:
            print("GreenGene data were format successfully. It is located at: {}".format(
                greengene.destination_dir
            ))
    '''        
    if parsed_args.unitedata_update:
        print("Running unite update")
        unitedata = UniteData(config_file)
        success = unitedata.update()
        if success:
            print("unite data were updated successfully. It is located at: {}".format(
                unitedata.destination_dir
            )) 
    '''      
def main():
    execute_script(sys.argv[1:])

if __name__ == "__main__":
    main()