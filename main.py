import sys
import argparse

from brdm.NcbiBlastData import NcbiBlastData
from brdm.NcbiSubsetData import NcbiSubsetData
from brdm import brdm_root


def parse_input_args(argv):
    ''' Parses command line arguments '''

    parser = argparse.ArgumentParser(description=
            "Reference Data Manager (RDM) is used to download, update and backup bioinformatics reference data.")
    parser.add_argument('--test', help="Test BRDM's execution: check connection to NCBI.", dest="test",
                        action='store_true', required=False)
    parser.add_argument('--update-ncbi-blast', help="Update entire nr/nt Blast reference data from NCBI.", dest="ncbi_blast_update",
                        action='store_true', required=False)
    parser.add_argument('--update-ncbi-subsets', help="Update NCBI's subsets (ITS, CO1, etc.)", dest="ncbi_subsets_update",
                        action = 'store_true', required=False)
    parser.add_argument('--restore-ncbi-subsets', help="Restore NCBI's subsets (ITS, CO1, etc.)", dest="ncbi_subsets_restore_folder",
                        required=False)
    args = parser.parse_args(argv)

    if not (args.ncbi_blast_update or args.ncbi_subsets_update or args.test or args.ncbi_subsets_restore_folder):
        parser.error('No action requested. Please add one of the required actions.')

    return args



def execute_script(input_args):

    config_file = "{}/config.yaml".format(brdm_root.path())
    parsed_args = parse_input_args(input_args)

    
        
    if parsed_args.test:
        print("Testing NCBI ftp connection.")
        blastData = NcbiBlastData(config_file)
        success = blastData.test_connection()
        if success:
            print("Test successful!")
            print("For NCBI's nr/nt download, destination directory will be {} and backup folder will be {}.".format(
                blastData.destination_dir, blastData.backup_dir
            ))
        else:
            print("Test did not succeed.")

    if parsed_args.ncbi_blast_update:
        print("Running NCBI Blast update")
        blastData = NcbiBlastData(config_file)
        #success = blastData.test_connection()
        success = blastData.update()
        if success:
            print("NCBI Blast reference data were updated successfully. It is located at: {}".format(
                blastData.destination_dir
            ))

    if parsed_args.ncbi_subsets_update:
        print("Running NCBI Subsets update")
        subsetData = NcbiSubsetData(config_file)
        success = subsetData.update()
        if success:
            print("NCBI subsets reference data were updated successfully. It is located at: {}".format(
                subsetData.destination_dir
            ))
     
    if parsed_args.ncbi_subsets_restore_folder:
        print("Restore NCBI subsets: %s " % parsed_args.ncbi_subsets_restore_folder)
        subsetData = NcbiSubsetData(config_file)
        success = subsetData.restore(parsed_args.ncbi_subsets_restore_folder)
        if success:
            print("NCBI subsets reference data were restored successfully. It is located at: {}".format(
                subsetData.destination_dir
            ))   
def main():
    execute_script(sys.argv[1:])

if __name__ == "__main__":
    main()