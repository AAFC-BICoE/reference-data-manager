from brdm.NcbiData import NcbiData
from brdm.RefDataInterface import RefDataInterface
from Bio import Entrez
import os, shutil
import logging
from urllib.error import HTTPError
import time
from distutils.dir_util import copy_tree


class NcbiSubsetData(NcbiData, RefDataInterface):

    def __init__(self, config_file):
        #print('In NcbiBlastData. config file: {}'.format(os.path.abspath(config_file)))
        super(NcbiSubsetData, self).__init__(config_file)

        self._entrez_email = self.config['ncbi']['subsets']['entrez_email']
        Entrez.email = self._entrez_email
        self._query = self.config['ncbi']['subsets']['query_set']
        self._batch_size = self.config['ncbi']['subsets']['batch_size']
        self._info_file_name = self.config['ncbi']['subsets']['info_file_name']

        self.destination_dir = super(NcbiSubsetData, self).destination_dir + self.config['ncbi']['subsets']['destination_folder']
        if not os.path.exists(self.destination_dir):
            os.makedirs(self.destination_dir)
        os.chdir(self.destination_dir)
        self.backup_dir = super(NcbiSubsetData, self).backup_dir + self.config['ncbi']['subsets'][
            'destination_folder']
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

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
        # directory to do an intermediary download
        temp_dir = self.destination_dir + 'temp'
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        # Download files into an intermediate folder
        os.chdir(temp_dir)
        success = self.download()

        if not success:
            logging.error("Download failed. Update will not proceed.")
            return False
        
        #os.chdir(self.destination_dir)
        backup_success = self.backup()

        if not backup_success:
            logging.error("Backup of reference data did not succeed. The update will not continue.")
            return False

        # Delete all data from the destination folder
        os.chdir(self.destination_dir)
        only_files = [f for f in os.listdir(".") if os.path.isfile(f)]
        for f in only_files:
            os.remove(f)

        # Copy data from intermediate folder to destination folder
        copy_tree(temp_dir, self.destination_dir)
        # Delete intermediate folder
        shutil.rmtree(temp_dir)
        return True
        
    
    
    def backup(self):
        logging.info("Executing NCBI subsets backup")

        backup_folder = self.create_backup_dir()
        if not backup_folder:
            logging.error("NCBI subsets Backup did not succeed.")
            return False
        
        try:
            #copy_tree(self.destination_dir, backup_folder)
            src_files = [f for f in os.listdir('.') if os.path.isfile(f)]
            #src_files = os.listdir(self.destination_dir)
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

        #TODO: Check time, and if it is not after hours for ncbi, give a warning
        # Check out warning.warn(): https://docs.python.org/3/library/warnings.html#warnings.warn
        
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
                time.sleep(15)
                    
            if not download_success:
                files_download_failed.append(subset_file_name) 
                logging.error("failed to download %s after %s attempts" % (subset_file_name, max_download_attempts))
                return False
        # Write application's README+ file
        # CZ, create a file for accessionID, or record all IDs here?
        comment = 'This folder contains NCBI subset(CO1,ITS etc.) reference databases that downloaded from NCBI.'
        self.write_readme(download_url='{}{}'.format("NCBI nucleotide entrez database with queries:", self._query),
                          downloaded_files=downloaded_files, download_failed_files=files_download_failed,
                          comment=comment, execution_time=(time.time() - download_start_time))

        return True
    
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
                accid = aline.split(" ")[0]
                accID_file.write(accid+"\n")
        if confirm_count != count:
            logging.error("Error: downloaded %s sequences, while the number of sequences = %s" % (confirm_count, count))
            return False
        
        accID_file.close()
        return True
    
    def restore(self, folder_name):
        logging.info("Executing NCBI subsets restore %s " % folder_name)
        # check if the folder exist or not
        restore_folder = os.path.join(self.backup_dir, folder_name)
        if not os.path.exists(restore_folder):
            logging.error("could not restore, %s does not exist " % folder_name)
            return False
        # remove all the file in destination_dir
        if len(os.listdir(restore_folder) ) == 0:
            logging.error("could not restore, %s is an empty folder " % folder_name)
            return False
           
        current_files = [f for f in os.listdir(self.destination_dir) if os.path.isfile(f)]
        for filename in current_files:
            os.remove(filename)
            
        os.chdir(restore_folder)
        for filename in os.listdir(restore_folder):
            shutil.copy(filename, self.destination_dir)
        # copy the all the files in backup_dir/folder_name to destination_dir
        
