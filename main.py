import sys
import argparse

from NcbiBlastData import NcbiBlastData


def parse_input_args(argv):
    ''' Parses command line arguments '''

    parser = argparse.ArgumentParser(description=
            "Reference Data Manager (RDM) is used to download, update and backup bioinformatics reference data.")
    parser.add_argument('--update-ncbi-blast', help="Update entire nr/nt Blast reference data from NCBI.", dest="ncbi_blast_update",
                        action='store_true', required=False)
    parser.add_argument('--update-ncbi-subsets', help="Update NCBI's subsets (ITS, CO1, etc.)", dest="ncbi_subsets_update",
                        action = 'store_true', required=False)

    args = parser.parse_args(argv)

    if not (args.ncbi_blast_update or args.ncbi_subsets_update):
        parser.error('No action requested. Please add one of the required actions.')

    return args



def execute_script(input_args):

    config_file = "config/config.yaml"
    parsed_args = parse_input_args(input_args)


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
        print("Subsets update: not yet implemented.")


def main():
    execute_script(sys.argv[1:])

if __name__ == "__main__":
    main()