import sys
import argparse
from brdm import brdm_root
from brdm.NcbiBlastData import NcbiBlastData
from brdm.NcbiSubsetData import NcbiSubsetData
from brdm.NcbiTaxonomyData import NcbiTaxonomyData
from brdm.NcbiWholeGenome import NcbiWholeGenome
from brdm.GreenGeneData import GreenGeneData
from brdm.UniteData import UniteData
from brdm.SilvaData import SilvaData


def parse_input_args(argv):
    """Parses command line arguments."""
    parser = argparse.ArgumentParser(
            description='Reference Data Manager (RDM) is used to download,'
            'update and backup bioinformatics reference data.'
            'Note that only one action is allowed each time to execute the'
            'program. For examples to download and to unzip nrnt blast,'
            'we have to run the program with option --update-ncbi-blast,'
            'and then run the program wit option --unzip-ncbi-blast restore.')
    # The path to the configuration file. If the path is ignored, then the
    # default config file will be loaded(./brdm/config.ini)
    parser.add_argument('--config-file',
                        help='Path to the configuration file.'
                        'Can be ignored if there is a config.ini file'
                        'in the brdm/ folder (the same folder as file'
                        ' config.ini.sample).',
                        dest='config_file',
                        required=False)
    # Required by database restore. restore_destination is the path to the
    # restored database. restore_date is the specific version(in date) of the
    # database you want to restore
    parser.add_argument('--restore-destination',
                        help='Required by all the database restore methods.'
                        'Path to your restored database.',
                        dest='restore_destination')
    parser.add_argument('--restore-date',
                        help='Required by all the database restore methods.'
                        'The version of the database to be restored;'
                        'format: yyyy-mm-dd.',
                        dest='restore_source')
    # Download NCBI nrnt blast database
    parser.add_argument('--update-ncbi-blast',
                        help='Download NCBI nr/nt blast database.',
                        dest='ncbi_blast_update', action='store_true',
                        required=False)
    # Unzip NCBI nrnt blast database
    parser.add_argument('--unzip-ncbi-blast',
                        help='Unzip NCBI nr/nt blast database.',
                        dest='ncbi_blast_unzip', action='store_true',
                        required=False)
    # Download NCBI taxonomy database
    parser.add_argument('--update-ncbi-taxonomy',
                        help='Update NCBI taxonomy database.',
                        dest='ncbi_taxonomy_update', action='store_true',
                        required=False)
    # Restore NCBI taxonomy database. Arguments --restore-destination and
    # --restore-source are required. See the help information of
    # --restore-destination and --restore-source for more info
    # An example python main.py --restore-ncbi-taxonomy --restore-destination
    # /path/to/a/folder  --restore-source 2018-09-10
    parser.add_argument('--restore-ncbi-taxonomy',
                        help='Restore NCBI taxonomy database.'
                        '--restore-destination and --restore-source'
                        'are required',
                        dest='ncbi_taxonomy_restore', action='store_true',
                        required=False)
    # NCBI subsets database(ITS, CO1, etc.). NCBI nrnt and NCBI taxonomy
    # database are required to complete the whole update process.
    parser.add_argument('--update-ncbi-subsets',
                        help='Update NCBI subsets (ITS, CO1, etc.)',
                        dest='ncbi_subsets_update', action='store_true',
                        required=False)
    parser.add_argument('--restore-ncbi-subsets',
                        help='Restore NCBI subsets (ITS, CO1, etc.)'
                        '--restore-destination and --restore-source'
                        'are required.',
                        dest='ncbi_subsets_restore', action='store_true',
                        required=False)
    # NCBI whole genomes (e.g. genome sequences for bacteria, fungi )
    parser.add_argument('--update-ncbi-wholegenomes',
                        help='Update NCBI whole genomes',
                        dest='ncbi_whole_genome_update', action='store_true',
                        required=False)
    parser.add_argument('--restore-ncbi-wholegenomes',
                        help='Restore NCBI whole genomes.'
                        '--restore-destination and --restore-source'
                        'are required',
                        dest='ncbi_whole_genome_restore',
                        action='store_true', required=False)
    # Green gene
    parser.add_argument('--update-greengene',
                        help='Update GreenGene data',
                        dest='greengene_update', action='store_true',
                        required=False)
    # Unite data
    parser.add_argument('--update-unite-data', help='Update unite data',
                        dest='unite_data_update', action='store_true',
                        required=False)
    # Silva data
    parser.add_argument('--update-silva-data', help='Update silva data',
                        dest='silva_data_update', action='store_true',
                        required=False)
    args = parser.parse_args(argv)
    # Count number of actions
    actions = []
    if args.ncbi_blast_update:
        actions.append('--update-ncbi-blast')
    if args.ncbi_blast_unzip:
        actions.append('--unzip-ncbi-blast')
    if args.ncbi_taxonomy_update:
        actions.append('--undate-ncbi-taxonomy')
    if args.ncbi_taxonomy_restore:
        actions.append('--restore-ncbi-taxonomy')
    if args.ncbi_subsets_update:
        actions.append('--update-ncbi-subsets')
    if args.ncbi_subsets_restore:
        actions.append('--restore-ncbi-subsets')
    if args.ncbi_whole_genome_update:
        actions.append('--update-ncbi-wholegenomes')
    if args.ncbi_whole_genome_restore:
        actions.append('--restore-ncbi-wholegenomes')
    if args.greengene_update:
        actions.append('--update-greengene')
    if args.unite_data_update:
        actions.append('--update-unite-data')
    if args.silva_data_update:
        actions.append('--update-silva_data')
    if len(actions) == 0:
        parser.error('No action requested. Please add one of the required \
                     \nactions (e.g. --update-ncbi-subsets)')
    if len(actions) > 1:
        parser.error('Only one action is allowed; there are {} actions in \
                    \nyour arguments {}'.format(len(actions), actions))
    return args


def execute_script(input_args):
    """Execute the script"""
    parsed_args = parse_input_args(input_args)
    config_file = '{}/config.yaml'.format(brdm_root.path())

    if parsed_args.config_file:
        config_file = parsed_args.config_file

    if parsed_args.ncbi_blast_update:
        print('Running NCBI nrnt blast database update')
        blast_data = NcbiBlastData(config_file)
        success = blast_data.update()
        if success:
            print('NCBI nrnt blast database were downloaded successfully. \
            \nIt is located at: {}'.format(blast_data.destination_dir))

    if parsed_args.ncbi_blast_unzip:
        print('Running NCBI nrnt blast database unzip')
        blast_data = NcbiBlastData(config_file)
        success = blast_data.unzip()
        if success:
            print('NCBI nrnt blast database were unzipped successfully.'
                  '\nIt is located at: {}'
                  .format(blast_data.destination_dir))

    if parsed_args.ncbi_taxonomy_update:
        print('Running NCBI Taxonomy update')
        taxonomy_data = NcbiTaxonomyData(config_file)
        success = taxonomy_data.update()
        if success:
            print('NCBI taxonomy data were updated successfully.'
                  '\nIt is located at: {}'
                  .format(taxonomy_data.destination_dir))

    if parsed_args.ncbi_taxonomy_restore:
        print('Running NCBI Taxonomy restore')
        if not parsed_args.restore_destination:
            print('Error: please provide the path of the destination for',
                  'restoring')
            exit(1)
        if not parsed_args.restore_source:
            print('Error: please provide the version (in date format',
                  'yyyy-mm-dd) of the database for restoring')
            exit(1)
        taxonomy_data = NcbiTaxonomyData(config_file)
        success = taxonomy_data.restore(
                                parsed_args.restore_source,
                                parsed_args.restore_destination)
        if success:
            print('NCBI taxonomy data were restored successfully.'
                  '\nIt is located at: {}'
                  .format(parsed_args.restore_destination))

    if parsed_args.ncbi_subsets_update:
        print('Running NCBI Subsets update')
        subset_data = NcbiSubsetData(config_file)
        success = subset_data.update()
        if success:
            print('NCBI subsets reference data were updated successfully.'
                  '\nIt is located at: {}'
                  .format(subset_data.destination_dir))

    if parsed_args.ncbi_subsets_restore:
        print('Restore NCBI subsets:')
        if not parsed_args.restore_destination:
            print('Error, please provide the path of the destination for ',
                  'restoring')
            exit(1)
        if not parsed_args.restore_source:
            print('Error, please provide the version (in date format ',
                  'yyyy-mm-dd) of the database for restoring')
            exit(1)
        subset_data = NcbiSubsetData(config_file)
        success = subset_data.restore(
                            parsed_args.restore_source,
                            parsed_args.restore_destination)
        if success:
            print('NCBI subsets reference data were restored successfully.'
                  '\nIt is located at: {}'
                  .format(parsed_args.restore_destination))

    if parsed_args.ncbi_whole_genome_update:
        print('Running NCBI whole genome update')
        whole_genome_data = NcbiWholeGenome(config_file)
        success = whole_genome_data.update()
        if success:
            print('NCBI whole genome data were updated successfully.'
                  '\nIt is located at: {}'
                  .format(whole_genome_data.destination_dir))

    if parsed_args.ncbi_whole_genome_restore:
        print('Restore NCBI whole genomes')
        if not parsed_args.restore_destination:
            print('Error, please provide the path of the destination for ',
                  'restoring')
            exit(1)
        if not parsed_args.restore_source:
            print('Error, please provide the version (in format ',
                  'yyyy-mm-dd) of the database for restoring')
            exit(1)
        whole_genome_data = NcbiWholeGenome(config_file)
        success = whole_genome_data.restore(
            parsed_args.restore_source, parsed_args.restore_destination)
        if success:
            print('NCBI wholeGenome data were restored successfully.'
                  '\nIt is located at: {}'
                  .format(parsed_args.restore_destination))

    if parsed_args.greengene_update:
        print('Running greengene update')
        greengene = GreenGeneData(config_file)
        success = greengene.update()
        if success:
            print('GreenGene data were updated successfully.'
                  '\nIt is located at: {}'.format(greengene.destination_dir))

    if parsed_args.unite_data_update:
        print('Running unite update')
        unitedata = UniteData(config_file)
        success = unitedata.update()
        if success:
            print('unite data were updated successfully.'
                  '\nIt is located at: {}'.format(
                                    unitedata.destination_dir)
                  )

    if parsed_args.silva_data_update:
        print('Running silva data update')
        silvadata = SilvaData(config_file)
        success = silvadata.update()
        if success:
            print('Silva data were updated successfully.'
                  '\nIt is located at: {}'.format(
                                    silvadata.destination_dir)
                  )


def main():
    execute_script(sys.argv[1:])


if __name__ == "__main__":
    main()
