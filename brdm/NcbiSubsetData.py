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
        # parse settings from config_file
        super(NcbiSubsetData, self).__init__(config_file)

        self._entrez_email = self.config['ncbi']['subsets']['entrez_email']
        Entrez.email = self._entrez_email
        self._query = self.config['ncbi']['subsets']['query_set']
        self._batch_size = self.config['ncbi']['subsets']['batch_size']
        #self._info_file_name = self.config['ncbi']['subsets']['info_file_name']
        self._path_to_taxonomy = self.config['ncbi']['subsets']['taxonomy_file']
        self._path_to_nt = self.config['ncbi']['subsets']['nt_file']
        self._ext_accID = self.config['ncbi']['subsets']['ext_accID']
        self._ext_sequence = self.config['ncbi']['subsets']['ext_sequence']
        self._ext_taxonomy = self.config['ncbi']['subsets']['ext_taxonomy']
        self._line_width = self.config['ncbi']['subsets']['line_width']
        self.destination_dir = super(NcbiSubsetData, self).destination_dir + self.config['ncbi']['subsets']['destination_folder']
        self.backup_dir = super(NcbiSubsetData, self).backup_dir + self.config['ncbi']['subsets'][
            'destination_folder']
        try:
            if not os.path.exists(self.destination_dir):
                os.makedirs(self.destination_dir)
                os.chmod(self.destination_dir, int(folder_mode,8))
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir)
                os.chmod(self.backup_dir, int(folder_mode,8))
            os.chdir(self.destination_dir)
        except Exception as e:
            logging.error("Failed to create the destination_dir or backup_dir with error {}".format(e))
            
    @property
    def destination_dir(self):
        return self._destination_dir

    @destination_dir.setter
    def destination_dir(self, value):
        self._destination_dir = value

    @property
    def backup_dir(self):
        return self._backup_dir

    @backup_dir.setter
    def backup_dir(self, value):
        self._backup_dir = value
    
    
    def update(self):
        logging.info("Executing NCBI subsets update")
        # Create a temp directory to do an intermediate download
        try:
            #temp_dir = tempfile.mkdtemp(dir = self.destination_dir )
            temp_dir = self.destination_dir + 'temp'
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)
            os.chdir(temp_dir)
        except Exception as e:
            logging.error("Failed to create the temp_dir: {}, error{}".format(temp_dir, e))
            return False
        
        # Download files into the temp folder
        success = self.download()
        if not success:
            logging.error("Download failed. Update will not proceed.")
            return False
        
        try:
            only_files = [f for f in os.listdir('.') if os.path.isfile(f)]
            for f in only_files:
                os.chmod(f, int(file_mode,8))   
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
        try:
            os.chdir(self.destination_dir)
            only_files = [f for f in os.listdir(".") if os.path.isfile(f)]
            for f in only_files:
                os.remove(f)
            copy_tree(temp_dir, self.destination_dir)
            shutil.rmtree(temp_dir)
        except Exception as e:
            logging.error("Failed to move files from temp_dir to destination folder, error{}".format(e))
            return False
        
        # Get fasta file and taxonomy file for each subsets based on accID
        subsets_list = self.get_subset_list()
        retrieve_success = self.accID_to_info(subsets_list)
        if not retrieve_success:
            logging.error("Failed: accID to fasta and taxonomy ")
            return False
        
        return True
        
    
    
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
        ### Download
        downloaded_files = []
        files_download_failed = []
        max_download_attempts = self.download_retry_num
        for a_set in self._query:
            subset_file_name = a_set.split("|")[0].strip()
            subset_query = a_set.split("|")[1].strip()
            download_success = False
            attempt = 0
            while attempt < max_download_attempts and download_success == False:
                logging.info("download attempt %s" % attempt)
                attempt += 1
                download_success = self.download_a_subset(subset_file_name, subset_query);
                if download_success:
                    downloaded_files.append(subset_file_name)
                time.sleep(self.sleep_time)
                    
            if not download_success:
                files_download_failed.append(subset_file_name) 
                logging.error("failed to download %s after %s attempts" % (subset_file_name, max_download_attempts))
                return False
        # Write application's README+ file
        comment = 'This folder contains NCBI subset(CO1,ITS etc.) reference databases that downloaded from NCBI.'
        self.write_readme(download_url='{}{}'.format("NCBI nucleotide entrez database with queries:", self._query),
                          downloaded_files=downloaded_files, download_failed_files=files_download_failed,
                          comment=comment, execution_time=(time.time() - download_start_time))

        return True
    
    """
    # method to download sequences and the get the accID from the sequence files
    def download_a_subset(self, file_name, query):
        
        fasta_file_name = file_name+".fasta"
        accID_file_name = file_name+".accID"
        fasta_file = open(fasta_file_name,"w")
        accID_file = open(accID_file_name, "w")
        try:
            search_handle = Entrez.esearch(db="nucleotide", term=query, usehistory="y", idtype="acc")
            search_results = Entrez.read(search_handle)
            search_handle.close()
        except HTTPError as err:
            logging.error("Connection could not be established.")
            print("Connection could not be established.")
            return False
        
        webenv = search_results["WebEnv"]
        query_key = search_results["QueryKey"]
        count = int(search_results["Count"])
       
        batch_size = self._batch_size  
        max_attemp = self.connection_retry_num
        for start in range(0, count, batch_size):
            end = min(count, start+batch_size)
            logging.info("Going to download record %i to %i" % (start+1, end))
            print("Going to download record %i to %i" % (start+1, end))
            attempt = 0
            while attempt < max_attemp:
                attempt += 1
                try:
                    fetch_handle = Entrez.efetch(db="nucleotide",
                                         rettype="fasta", retmode="text",
                                         retstart=start, retmax=batch_size,
                                         webenv=webenv, query_key=query_key,
                                         idtype="acc")
                except HTTPError as err:
                    if 500 <= err.code <= 599:
                        logging.error("Received error from server %s" % err)
                        logging.error("Attempt %i of %s" % (attempt,max_attemp))
                        time.sleep(15)
                    else:
                        raise
            data = fetch_handle.read()
            fetch_handle.close()
            
            fasta_file.write(data)   
        fasta_file.close()
        
        confirm_count = 0
        for aline in open(fasta_file_name, "r"):
            if ">" in aline:
                confirm_count += 1
                accid = aline.split(" ")[0][1:]
                accID_file.write(accid+"\n")
        if confirm_count != count:
            logging.error("Error: downloaded %s sequences, while the number of sequences = %s" % (confirm_count, count))
            return False
        
        accID_file.close()
        return True
    """
    
    # Download accID file for a subset
    def download_a_subset(self, file_name, query):
        
        accID_file_name = file_name+self._ext_accID
        try:
            accID_file = open(accID_file_name, "w")
        except Exception as e:
            logging.error("Cannot open file {}. Error: {}".format(accID_file,e))
            return False 
        batch_size = self._batch_size  
        max_attemp = self.connection_retry_num
        try:
            search_handle = Entrez.esearch(db="nucleotide", term=query, usehistory="y", idtype="acc")
            search_results = Entrez.read(search_handle)
            search_handle.close()
        except HTTPError as err:
            logging.error("Connection could not be established %s " % err)
            print("Connection could not be established.")
            return False
        
        count = int(search_results["Count"])
        webenv = search_results["WebEnv"]
        query_key = search_results["QueryKey"]
        totalID = 0
        for start in range(0, count, batch_size):
            end = min(count, start+batch_size)
            logging.info("Going to download record %i to %i" % (start+1, end))
            print("Going to download record %i to %i" % (start+1, end))
            attempt = 0
            again = True
            while attempt < max_attemp and again:
                attempt += 1
                try:
                    search_handle = Entrez.esearch(db="nucleotide",term=query,
                                         retstart=start, retmax=batch_size,
                                         webenv=webenv, query_key=query_key,
                                         idtype="acc")
                    again = False
                except HTTPError as err:
                    if 500 <= err.code <= 599:
                        logging.error("Received error from server %s" % err)
                        logging.error("Attempt %i of %s" % (attempt,max_attemp))
                        time.sleep(15)
                    else:
                        raise  
            search_results = Entrez.read(search_handle)
            acc_list = search_results["IdList"]
            totalID = totalID + len(acc_list)
            acc_str = "\n".join(acc_list)
            try:
                accID_file.write(acc_str+"\n")
            except Exception as e:
                logging.error("Cannot write to file {}. Error: {}".format(accID_file,e))
                return False 
        try:
            accID_file.close()
        except Exception as e:
            logging.error("Cannot close file {}. Error: {}".format(accID_file,e))
            return False
        
        if totalID != count:
            logging.error("downloaded  %i out of to %i accIDs" % (totalID, count))
            print("downloaded  %i out of to %i accIDs" % (totalID, count))
            return False
        
        return True
    
    
    def restore(self, folder_name):
        logging.info("Executing NCBI subsets restore %s " % folder_name)
        # Check the restore folder, return false if not exist or empty folder
        try:
            restore_folder = os.path.join(self.backup_dir, folder_name)
            if not os.path.exists(restore_folder):
                logging.error("could not restore, %s does not exist " % folder_name)
                return False
            if len(os.listdir(restore_folder) ) == 0:
                logging.error("could not restore, %s is an empty folder " % folder_name)
                return False
        except Exception as e:
            logging.error("Failed to check the restore folder. Error: {}".format(e))
            return False 
        
        # Remove all the file in destination_dir
        # Copy the all the files in backup_dir/folder_name to destination_dir
        try:
            current_files = [f for f in os.listdir(self.destination_dir) if os.path.isfile(f)]
            for filename in current_files:
                os.remove(filename)    
            os.chdir(restore_folder)
            for filename in os.listdir(restore_folder):
                shutil.copy(filename, self.destination_dir)
            os.chdir(self.destination_dir)
        except Exception as e:
            logging.error("Failed to copy files. Error: {}".format(e))
            return False 
        
        
        subsets_list = self.get_accID_file()
        if len(subset_list) == 0 :
            logging.error("Failed to get accID_file ")
            return False
        
        retrieve_success = self.accID_to_info(subsets_list)
        if not retrieve_success:
            logging.error("Failed: accID to fasta and taxonomy ")
            return False
        
        return True
        
    def get_accID_file(self):
        list = []
        try:
            current_files = [f for f in os.listdir(self.destination_dir) if os.path.isfile(f)]
            for filename in current_files:
                print(filename)
                if filename.endswith(self._ext_accID):
                    subset_file_name = filename.split(".")[0]
                    list.append(subset_file_name)
        except Exception as e:
            logging.error("Failed to get a list of accID_file for restoring. Error: {}".format(e))
            list = []
            return list
        
        return list
        
    def get_subset_list(self):
        list = []
        for a_set in self._query:
            subset_file_name = a_set.split("|")[0].strip()
            list.append(subset_file_name)
        return list
    
    
    # from accID  to sequence file and taxonomy 
    def accID_to_info(self, set_list):
        for a_set in set_list:
            subset_file_name = a_set
            accID_file = subset_file_name+self._ext_accID
            sequence_file = subset_file_name+ self._ext_sequence
            taxon_file = subset_file_name+ self._ext_taxonomy       
            try:
                command = "blastdbcmd -db "+self._path_to_nt+ "  -target_only  -entry_batch " + accID_file + " -outfmt \"%a %T %s\" -out "+sequence_file+".tmp"
                os.system(command)
            except Exception as e:
                logging.error("Failed to retrieve %s fasta sequence from nt " % subset_file_name)
                return False
            try:
                self.get_taxonomy(sequence_file,taxon_file)
                os.chmod(sequence_file, int(file_mode,8))
                os.chmod(taxon_file, int(file_mode,8))
            except Exception as e:
                logging.error("Failed to retrieve %s taxonomy " % subset_file_name)
                return False
        return True
    
    
    # load the rankslinkage.txt
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
                    taxid_to_names[taxid] = (tax_name, level_8)
        except Exception as e:
                logging.error("failed to load taxonomyRank file, error {} ".format(e))
                raise
        #print(taxid_to_names)
        return taxid_to_names
     
    # get taxonomy from accID and rankslinkage.txt         
    def get_taxonomy(self, sequence_file_name, taxon_file_name):
        sequence_file = open(sequence_file_name, "w")
        try:
            taxon_file = open(taxon_file_name, "w")
            taxid_to_rank = self.parse_ranks(self._path_to_taxonomy)
        except Exception as e:
                logging.error("failed to load taxonomyRank file, error {} ".format(e))
                raise
        
        try:    
            taxId_no_name = 0
            with open(sequence_file_name+".tmp") as f:
                content = f.readlines()
                for line in content:
                    accID, taxID, sequence = line.split()
                    sequence_file.write(">"+accID+"  taxonID"+taxID+"\n")
                    sequence_file.write(textwrap.fill(sequence, width=self._line_width)+"\n")
                    if int(taxID) in taxid_to_rank:
                        #taxon_file.write(accID+"  "+",".join(taxid_to_rank[int(taxID)])+"\n")
                        taxon_file.write(accID+"\t"+taxid_to_rank[int(taxID)]["levle_8"])+"\n")
                        #print(accID+"\t"+taxID) 
                    else:
                        logging.info("CANNOT find taxonomy\t"+ accID+"\t"+taxID)
                        print("CANNOT find taxonomy\t"+ accID+"\t"+taxID)
                        taxId_no_name+=1
            logging.info("total taxID without taxonInfo:\t"+taxId_no_name)   
            print("total taxID without taxonInfo:\t"+taxId_no_name)
            sequence_file.close()
            taxon_file.close()
            os.remove(sequence_file_name+".tmp")   
        except Exception as e:
                logging.error("failed to get taxonomy, error {} ".format(e))
                raise
            