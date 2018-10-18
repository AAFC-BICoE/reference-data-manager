from brdm.NcbiData import NcbiData
from brdm.RefDataInterface import RefDataInterface
from Bio import Entrez
import os, shutil
import tempfile
import logging
from urllib.error import HTTPError
import time
from distutils.dir_util import copy_tree
import textwrap


class NcbiSubsetData(NcbiData, RefDataInterface):

    def __init__(self, config_file):
        super(NcbiSubsetData, self).__init__(config_file)
        self.entrez_email = self.config['ncbi']['subsets']['entrez_email']
        Entrez.email = self.entrez_email
        self.query = self.config['ncbi']['subsets']['query_set']
        self.batch_size = self.config['ncbi']['subsets']['batch_size']
        self.path_to_taxonomy = self.config['ncbi']['subsets']['taxonomy_file']
        self.path_to_nt = self.config['ncbi']['subsets']['nt_file']
        self.ext_accID = self.config['ncbi']['subsets']['ext_accID']
        self.ext_sequence = self.config['ncbi']['subsets']['ext_sequence']
        self.ext_taxonomy = self.config['ncbi']['subsets']['ext_taxonomy']
        self.line_width = self.config['ncbi']['subsets']['line_width']
        try:
            self.destination_dir = os.path.join(super(NcbiSubsetData, self).destination_dir, \
                                                self.config['ncbi']['subsets']['destination_folder'])
            self.backup_dir = os.path.join(super(NcbiSubsetData, self).backup_dir, \
                                           self.config['ncbi']['subsets']['destination_folder'])
            if not os.path.exists(self.destination_dir):
                os.makedirs(self.destination_dir, mode = self.folder_mode)
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir, mode = self.folder_mode)
            os.chdir(self.destination_dir)
        except Exception as e:
            logging.error("Failed to create the destination_dir or backup_dir with error {}".format(e))
            
    
    def update(self):
        logging.info("Executing NCBI subsets update")
        # Download files into an intermediate folder
        temp_dir = self.create_tmp_dir(self.destination_dir)
        if not temp_dir:
            logging.error("Failed to create the temp_dir: {}, error{}".format(temp_dir, e))
            return False
        success = self.download()
        if not success:
            logging.error("Download failed. Update will not proceed.")
            return False
        # Change the mode of the files
        try:
            only_files = [f for f in os.listdir('.') if os.path.isfile(f)]
            for f in only_files:
                os.chmod(f, self.file_mode)   
        except Exception as e:
            logging.error("Failed to change file mode, error{}".format(e))
            return False
        # Backup the accID 
        backup_success = self.backup()
        if not backup_success:
            logging.error("Backup of reference data did not succeed. The update will not continue.")
            return False

        # Delete old files from the destination folder
        # Copy new files from intermediate folder to destination folder
        clean_destination_ok = self.clean_destination_dir(self.destination_dir)
        if not clean_destination_ok:
            return False
        try:
            copy_tree(temp_dir, self.destination_dir)
            shutil.rmtree(temp_dir)
        except Exception as e:
            logging.error("Failed to move files from temp_dir to destination folder, error{}".format(e))
            return False
        
        # Get fasta file and taxonomy file for each subsets based on accID
        #subsets_list = self.get_subset_list()
        #retrieve_success = self.accID_to_info(self.deatination_dirsubsets_list)
        retrieve_success = self.accID_to_info(self.destination_dir)
        if not retrieve_success:
            logging.error("Failed: accID to fasta and taxonomy ")
            return False
        
        format_success = self.format(self.destination_dir)
        if not format_success:
            logging.error("Failed: format subsets ")
            return False
        
        return True
     
    # Backup accID files and README+ file
    def backup(self):
        logging.info("Executing NCBI subsets backup")
        backup_folder = self.create_backup_dir()
        if not backup_folder:
            logging.error("NCBI subsets Backup did not succeed.")
            return False
        try:
            src_files = [f for f in os.listdir('.') if os.path.isfile(f)]
            for filename in src_files:
                shutil.copy(filename, backup_folder)
        except Exception as e:
            logging.exception("NCBI subsets Backup did not succeed. Error: {}".format(e))
            return False
        return True
    
    # Download all NCBI subsets
    def download(self):
        logging.info("Executing NCBI subsets download")
        download_start_time = time.time()
        downloaded_files = []
        files_download_failed = []
        max_download_attempts = self.download_retry_num
        for a_set in self.query:
            subset_file_name = a_set.split("|")[0].strip()
            subset_query = a_set.split("|")[1].strip()
            download_success = False
            attempt = 0
            while attempt < max_download_attempts and download_success == False:
                attempt += 1
                download_success = self.download_a_subset(subset_file_name, subset_query);
                if download_success:
                    downloaded_files.append(subset_file_name)
                time.sleep(self.sleep_time)
                    
            if not download_success:
                files_download_failed.append(subset_file_name) 
                logging.error("Failed to download {} after {} attempts".format(subset_file_name, max_download_attempts))
                return False
        # Write application's README+ file
        comment = 'This folder contains NCBI subset(CO1,ITS etc.) reference databases that downloaded from NCBI.'
        self.write_readme(download_url='{}{}'.format("NCBI nucleotide entrez database with queries:", self.query),
                          downloaded_files=downloaded_files, download_failed_files=files_download_failed,
                          comment=comment, execution_time=(time.time() - download_start_time))

        return True
    
    
    # Download accID file for a subset
    def download_a_subset(self, file_name, query):
        accID_file_name = file_name+self.ext_accID
        try:
            accID_file = open(accID_file_name, "w")
        except Exception as e:
            logging.error("Cannot open file {}. Error: {}".format(accID_file,e))
            return False
        batch_size = self.batch_size  
        max_attemp = self.connection_retry_num
        connection_again = True
        connection_attemp =0
        while connection_attemp < max_attemp and connection_again:
            connection_attemp += 1
            try:
                search_handle = Entrez.esearch(db="nucleotide", term=query, usehistory="y", idtype="acc")
                search_results = Entrez.read(search_handle)
                search_handle.close()
                connection_again = False
            except HTTPError as err:
                logging.error("Connection could not be established {} on attempt {} ".format(err,connection_attemp))
                time.sleep(self.sleep_time)
                
        if connection_again:
            logging.error("Connection could not be established {} after all attempts ".format(err))
            return False
        
        count = int(search_results["Count"])
        webenv = search_results["WebEnv"]
        query_key = search_results["QueryKey"]
        totalID = 0
        for start in range(0, count, batch_size):
            end = min(count, start+batch_size)
            logging.info("Going to download record {} to {}, total record {}".format(start+1, end, count))
            attempt = 0
            again = True
            while attempt < max_attemp and again:
                attempt += 1
                try:
                    search_handle = Entrez.esearch(db="nucleotide",term=query,
                                         retstart=start, retmax=batch_size,
                                         webenv=webenv, query_key=query_key,
                                         idtype="acc")
                    search_results = Entrez.read(search_handle)
                    acc_list = search_results["IdList"]
                    totalID = totalID + len(acc_list)
                    acc_str = "\n".join(acc_list)
                    accID_file.write(acc_str+"\n")
                    again = False
                except Exception as e:
                    logging.error("Received error in downloading  {}".format(e))
                    logging.error("Attempt {} of {}".format(attempt,max_attemp))
                    time.sleep(self.sleep_time)
            
            if again:
                logging.error("Failed to get the record {} to {}".format(start+1, end))
                return False
                
        try:
            accID_file.close()
        except Exception as e:
            logging.error("Cannot close file {}. Error: {}".format(accID_file,e))
            return False
        
        if totalID != count:
            logging.error("downloaded  {} out of to {} accIDs".format(totalID, count))
            return False
        
        return True

    
    # Restore accID file from a backup folder, 
    # Retrieve sequences and taxonomy from accID
    def restore(self, proposed_folder_name, path_to_destination):
        logging.info("Executing NCBI subsets restore {}{} ".format(proposed_folder_name, path_to_destination))
        try:
            restore_folder = self.check_restore_date(self.backup_dir, proposed_folder_name)
            if not restore_folder:
                return False
        
            restore_destination = self.check_restore_destination(path_to_destination)
            if not restore_destination:
                return False 
                
            if not os.path.isdir(restore_destination):
                os.makedirs(restore_destination,mode = self.folder_mode)
            # copy the all the files in backup_dir/folder_name to destination_dir    
            os.chdir(restore_folder)
            for filename in os.listdir(restore_folder):
                shutil.copy2(filename, restore_destination)
            
        except Exception as e:
            logging.error("Failed to copy files. Error: {}".format(e))
            return False 
        
        logging.info("retrieve sequence and taxonomy info from accID")
        retrieve_success = self.accID_to_info(restore_destination)
        if not retrieve_success:
            logging.error("Failed: accID to fasta and taxonomy ")
            return False
        format_success = self.format(restore_destination)
        if not format_success:
            logging.error("Failed: format subsets ")
            return False
        
        print("The restored database is located at " +restore_destination)
        logging.info("The restored database is located at {} ".format(restore_destination))
        
        return True
    
    # Get the list of subsets in the destination dir. Required in the method format
    def get_subset_list_format(self, path_destination):
        list = []
        try:
            current_files = [f for f in os.listdir(path_destination) 
                             if os.path.isdir(os.path.join(path_destination,f))]
            for filename in current_files:
                list.append(filename)
        except Exception as e:
            logging.error("Failed to get a list of accID_file for formatting. Error: {}".format(e))
            list = []
            return list
        
        return list   
        
    # Get the list of subsets in the destination_dir. Required in the method restore
    def get_subset_list(self, path_destination):
        list = []
        try:
            current_files = [f for f in os.listdir(path_destination)
                              if os.path.isfile(os.path.join(path_destination,f))]
            for filename in current_files:
                print(filename)
                if filename.endswith(self.ext_accID):
                    subset_file_name = filename.split(".")[0]
                    list.append(subset_file_name)
        except Exception as e:
            logging.error("Failed to get a list of accID_file for restoring. Error: {}".format(e))
            list = []
            return list
        
        return list
     
    # From accID to sequence file and taxonomy 
    def accID_to_info(self, path_to_destination):
        subsets_list = self.get_subset_list(path_to_destination)
        if len(subsets_list) == 0 :
            logging.error("Failed to get accID_file ")
            return False
        for a_set in subsets_list:
            subset_file_name = a_set
            accID_file = subset_file_name+self.ext_accID
            sequence_file = subset_file_name+ self.ext_sequence
            taxon_file = subset_file_name+ self.ext_taxonomy       
            try:
                a_subset_folder = os.path.join(path_to_destination, subset_file_name)
                if os.path.exists(a_subset_folder):
                    shutil.rmtree(a_subset_folder)
                os.makedirs(a_subset_folder, mode = self.folder_mode)
                shutil.move(os.path.join(path_to_destination,accID_file), os.path.join(a_subset_folder,accID_file))
                os.chdir(a_subset_folder)
                print(a_subset_folder)
                command = "blastdbcmd -db "+self.path_to_nt+ "  -target_only  -entry_batch " + accID_file + " -outfmt \"%a %T %s\" -out "+sequence_file+".tmp"
                os.system(command)
                print(command)
            except Exception as e:
                logging.error("Failed to retrieve {} fasta sequence from nt ".format(subset_file_name))
                return False
            
            try:
                self.get_taxonomy(sequence_file,taxon_file)
                os.chmod(sequence_file, self.file_mode)
                os.chmod(taxon_file, self.file_mode)
            except Exception as e:
                logging.error("Failed to retrieve {} taxonomy ".format(subset_file_name))
                return False
            
        return True
    
    
    # load the rankslineage.txt
    def parse_ranks(self,filename):
        taxid_to_names = dict()
        try:
            with open(filename) as fp:
                content = fp.readlines()
                for line in content[1:]:
                    line = line[:-1]
                    x = line.split("\t")
                    tax_id, tax_name, level_8 = x
                    taxid = int(tax_id)
                    taxid_to_names[taxid] = level_8
        except Exception as e:
                logging.error("failed to load taxonomyRank file, error {} ".format(e))
                raise
        #print(taxid_to_names)
        return taxid_to_names
     
    # Get taxonomy from accID and rankslinkage.txt
    # Wrap sequence file into fixed line width   
    def get_taxonomy(self, sequence_file_name, taxon_file_name):
        sequence_file = open(sequence_file_name, "w")
        try:
            taxon_file = open(taxon_file_name, "w")
            taxid_to_rank = self.parse_ranks(self.path_to_taxonomy)
        except Exception as e:
            logging.error("failed to load taxonomyRank file, error {} ".format(e))
            raise
        
        try:    
            taxId_no_name = 0
            with open(sequence_file_name+".tmp") as f:
                content = f.readlines()
                for line in content:
                    accID, taxID, sequence = line.split() 
                    if int(taxID) in taxid_to_rank:
                        taxon_file.write(accID+"\t"+taxid_to_rank[int(taxID)]+"\n")
                        sequence_file.write(">"+accID+"\n")
                        sequence_file.write(textwrap.fill(sequence, width=self.line_width)+"\n")
                    else:
                        logging.info("CANNOT find taxonomy\t"+ accID+"\t"+taxID)
                        taxId_no_name+=1
            logging.info("total taxID without taxonInfo:{}".format(taxId_no_name))   
            print("total taxID without taxonInfo:\t",taxId_no_name)
            sequence_file.close()
            taxon_file.close()
            os.remove(sequence_file_name+".tmp")   
        except Exception as e:
            logging.error("failed to get taxonomy, error {} ".format(e))
            raise
     
     
    def format(self, path_to_destination):
        print(path_to_destination)
        subsets_list = self.get_subset_list_format(path_to_destination)
        if len(subsets_list) == 0 :
            logging.error("Failed to get accID_file ")
            return False
        
        for a_set in subsets_list:
            subset_file_name = a_set
            sequence_file = subset_file_name+ self.ext_sequence
            taxon_file = subset_file_name+ self.ext_taxonomy      
            a_subset_folder = os.path.join(path_to_destination,subset_file_name)
            qiime1 = self.to_qiime1_format(a_subset_folder, sequence_file, taxon_file)
            if not qiime1:
                logging.error("Failed to get qiime1 format {} ".format(subset_file_name))
                return False
            mothur = self.to_mothur_format(a_subset_folder, sequence_file, taxon_file)
            if not mothur:
                logging.error("Failed to get mothur format {} ".format(subset_file_name))
                return False
            #qiime2 = self.to_qiime2_format(a_subset_folder, sequence_file, taxon_file, subset_file_name)
            #if not qiime2:
            #    logging.error("Failed to get qiime2 format {} ".format(subset_file_name))
            #    return False
            q1_rdp = self.to_qiime1_rdp_format(a_subset_folder, sequence_file, taxon_file)
            if not q1_rdp:
                logging.error("Failed to get qiime1_rdp format {} ".format(subset_file_name))
                return False
            blast = self.to_blast_format(a_subset_folder,sequence_file, taxon_file, subset_file_name)
            if not blast:
                logging.error("Failed to get blast format {} ".format(subset_file_name))
                return False
        return True
    
    
    def to_qiime1_format(self, a_subset_folder, sequence_file, taxon_file):
        try:
            qiime1_folder = os.path.join(a_subset_folder, 'Qiime1')
            qiime1_taxon_name = os.path.join(qiime1_folder, taxon_file)
            qiime1_sequence_name = os.path.join(qiime1_folder,sequence_file)
            if os.path.exists(qiime1_folder):
                shutil.rmtree(qiime1_folder)
            os.makedirs(qiime1_folder, mode = self.folder_mode)
            os.chdir(qiime1_folder)
            
            os.symlink(os.path.join(a_subset_folder,sequence_file), qiime1_sequence_name)
            qiime1_taxon_file = open(qiime1_taxon_name, "w")     
            with open(os.path.join(a_subset_folder,taxon_file)) as fp:
                content = fp.readlines()
                for line in content:
                    line = line[:-1]
                    x = line.split("\t")
                    acc_id, level_8 = x
                    levels = level_8.split('; ')
                    a_line = "; ".join(levels[1:])
                    qiime1_taxon_file.write(acc_id+"\t"+a_line+"\n")
            qiime1_taxon_file.close()
            os.chmod(qiime1_taxon_name, self.file_mode)
            os.chmod(qiime1_sequence_name, self.file_mode)       
        except Exception as e:
            logging.error("failed to get qiime1 format, error {} ".format(e))
            return False
        return True
    
    
    def to_qiime2_format(self,a_subset_folder, sequence_file, taxon_file, subset_file):
        try:
            qiime1_folder = os.path.join(a_subset_folder, 'Qiime1')
            qiime2_folder = os.path.join(a_subset_folder, 'Qiime2')
            if os.path.exists(qiime2_folder):
                shutil.rmtree(qiime2_folder)
            os.makedirs(qiime2_folder, mode = self.folder_mode)
            os.chdir(qiime2_folder)
            input_taxon_name = os.path.join(qiime1_folder, taxon_file)
            output_taxon_name = os.path.join(qiime2_folder, subset_file)+"_taxon.qza"
            input_sequence_name = os.path.join(a_subset_folder,sequence_file)
            output_sequence_name = os.path.join(qiime2_folder, subset_file)+"_fasta.qza"
            
            sklearn_classifier_name = os.path.join(qiime2_folder, subset_file)+"_sklearn_classifier.qza"
            command1 = "qiime tools import \
                        --type 'FeatureData[Sequence]' \
                        --input-path "+input_sequence_name+ " \
                        --output-path "+ output_sequence_name
            os.system(command1)
            command2 = "qiime tools import \
                        --type 'FeatureData[Taxonomy]' \
                        --source-format HeaderlessTSVTaxonomyFormat \
                        --input-path "+ input_taxon_name+ " \
                        --output-path "+ output_taxon_name
            os.system(command2)
            command3 = "qiime feature-classifier fit-classifier-naive-bayes \
                      --i-reference-reads "+output_sequence_name +" \
                      --i-reference-taxonomy "+output_taxon_name +" \
                      --o-classifier "+sklearn_classifier_name
            os.system(command3)     
            os.chmod(output_taxon_name, self.file_mode)
            os.chmod(output_sequence_name, self.file_mode)
            os.chmod(sklearn_classifier_name, self.file_mode)
        except Exception as e:
            logging.error("failed to get qiime2 format, error {} ".format(e))
            return False
        return True
    
      
    def to_qiime1_rdp_format(self,a_subset_folder, sequence_file, taxon_file):
        try:
            qiime1_folder = os.path.join(a_subset_folder, 'Qiime1')
            rdp_folder = os.path.join(a_subset_folder, 'Qiime1_rdp')
            if os.path.exists(rdp_folder):
                shutil.rmtree(rdp_folder)
            os.makedirs(rdp_folder, mode = self.folder_mode)
            os.chdir(rdp_folder)
            # symbolic link to the sequence file
            input_sequence_name = os.path.join(a_subset_folder,sequence_file)
            output_sequence_name = os.path.join(rdp_folder,sequence_file)
            os.symlink(input_sequence_name, output_sequence_name)
            # remove spaces in qiime1 taxon file
            input_taxon_name = os.path.join(qiime1_folder, taxon_file)
            output_taxon_name = os.path.join(rdp_folder,taxon_file)
            #os.symlink(input_taxon_name, output_taxon_name)
            with open(input_taxon_name, 'r') as f_in, open(output_taxon_name, 'w') as f_out:
                for line in f_in:
                    f_out.write(line.replace('; ', ';'))
            os.chmod(output_taxon_name, self.file_mode) 
            os.chmod(output_sequence_name, self.file_mode)    
        except Exception as e:
            logging.error("failed to get qiime1_rdp format, error {} ".format(e))
            return False
        return True
    
    
    def to_mothur_format(self, a_subset_folder, sequence_file, taxon_file):
        try:
            mothur_folder = os.path.join(a_subset_folder, 'Mothur')
            mothur_taxon_name = os.path.join(mothur_folder, taxon_file)
            if os.path.exists(mothur_folder):
                shutil.rmtree(mothur_folder)
            os.makedirs(mothur_folder, mode = self.folder_mode)
            os.chdir(mothur_folder)
            os.symlink(os.path.join(a_subset_folder,sequence_file), os.path.join(mothur_folder,sequence_file))
            mothur_taxon_file = open(mothur_taxon_name, "w")     
            with open(os.path.join(a_subset_folder,taxon_file)) as fp:
                content = fp.readlines()
                for line in content[1:]:
                    line = line[:-1]
                    x = line.split("\t")
                    tax_id, level_8 = x
                    levels = level_8.split('; ')
                    a_line=""
                    for a_level in levels[1:]:
                        if a_level[3:] and not a_line:
                            a_line = a_level[3:]
                        elif a_level[3:] and a_line:
                            a_line = a_line+";"+a_level[3:]
                    a_line = a_line+";"
                    mothur_taxon_file.write(tax_id+"\t"+a_line.replace(" ","")+"\n")
            mothur_taxon_file.close()
            os.chmod(mothur_taxon_name, self.file_mode)      
        except Exception as e:
            logging.error("failed to get mothur format, error {} ".format(e))
            return False
        return True
    
    
    def to_blast_format(self, a_subset_folder, sequence_file, taxon_file, subset_file):
        try:
            blast_folder = os.path.join(a_subset_folder, 'Blast')
            if os.path.exists(blast_folder):
                shutil.rmtree(blast_folder)
            os.makedirs(blast_folder, mode = self.folder_mode)
            os.chdir(blast_folder)
            sequence_input = os.path.join(a_subset_folder, sequence_file)
            blastdb_name = os.path.join(blast_folder, subset_file)
            command1 = "makeblastdb -in "+sequence_input+" -dbtype nucl -out "+blastdb_name
            os.system(command1)
            for f in os.listdir("."):
                if os.path.isfile(f):
                    os.chmod(f, self.file_mode)   
        except Exception as e:
            logging.error("failed to get blast format, error {} ".format(e))
            return False
        return True
                             