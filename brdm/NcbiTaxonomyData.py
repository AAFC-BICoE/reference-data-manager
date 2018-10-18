from brdm.NcbiData import NcbiData
from brdm.RefDataInterface import RefDataInterface
import os, shutil
import tempfile
import logging
import time
from distutils.dir_util import copy_tree
import requests

class NcbiTaxonomyData(NcbiData, RefDataInterface):

    def __init__(self, config_file):
        super(NcbiTaxonomyData, self).__init__(config_file)
        self.download_folder = self.config['ncbi']['taxonomy']['download_folder']
        self.download_file = self.config['ncbi']['taxonomy']['download_file']
        self.taxonomy_file = self.config['ncbi']['taxonomy']['taxonomy_file']
        self.info_file_name = self.config['ncbi']['taxonomy']['info_file_name']
        # Create destination directory and backup directory
        try:
            self.destination_dir = os.path.join(super(NcbiTaxonomyData, self).destination_dir, \
                                                self.config['ncbi']['taxonomy']['destination_folder'])
            if not os.path.exists(self.destination_dir):
                os.makedirs(self.destination_dir, mode = self.folder_mode)
            os.chdir(self.destination_dir)
            self.backup_dir = os.path.join(super(NcbiTaxonomyData, self).backup_dir,
                                           self.config['ncbi']['taxonomy']['destination_folder'])
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir, mode = self.folder_mode)
        except Exception as e:
            logging.error("Failed to create the destination_dir or backup_dir with error {}".format(e))
            
    
    def update(self):
        logging.info("Executing NCBI taxonomy update")
        # Download files into the intermediate folder
        temp_dir = self.create_tmp_dir(self.destination_dir)
        if not temp_dir:
            logging.error("Failed to create the temp_dir: {}, error{}".format(temp_dir, e))
            return False
        success = self.download()
        if not success:
            logging.error("Download failed. Update will not proceed.")
            return False
        # Format the taxonomy file and remove unwanted files
        # and change file mode
        format_success = self.format_taxonomy(self.taxonomy_file) 
        if not format_success:
            logging.error("Failed to format taxonomy file")
            return False
        # Backup the files
        backup_success = self.backup()
        if not backup_success:
            logging.error("Backup of taxonomy data did not succeed. The update will not continue.")
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
        
        return True
    
    # Download taxonomy database
    def download(self, test = False):
        logging.info("Executing NCBI taxonomy download")
        download_start_time = time.time()
        downloaded_files = [] 
        files_download_failed = []
        max_download_attempts = self.download_retry_num
        file_name = self.download_file
        readme_success = False
        download_success = test
        unzip_success = False
        attempt = 0
        completed = False
        while attempt < max_download_attempts and not completed:
            attempt += 1
            try:
                file_url = os.path.join(self.login_url, self.download_folder)
                session_requests,connected = self.https_connect();
                if not readme_success:
                    #download readme file:
                    file_name_readme = self.info_file_name
                    file_url_readme = os.path.join(file_url, file_name_readme)
                    readme_success = self.download_a_file(file_name_readme, file_url_readme, session_requests)
                
                if not download_success:
                    #download md5 file:
                    file_name_md5 = self.download_file+".md5"
                    file_url_md5 = os.path.join(file_url, file_name_md5)
                    md5_success = self.download_a_file(file_name_md5, file_url_md5, session_requests)
                    #download taxdump zipped file
                    file_name_taxon = self.download_file
                    file_url_taxon = os.path.join(file_url, file_name_taxon)
                    taxon_success = self.download_a_file(file_name_taxon, file_url_taxon, session_requests)
                    #check md5
                    download_success = self.checksum(file_name_md5, file_name_taxon)
                if download_success and readme_success:
                    completed = True
                session_requests.close()
            except Exception as e:
                logging.info("Failed to download taxonomy file on attempt {}: {}".format(attempt, e)) 
                time.sleep(self.sleep_time)
              
        if completed:
            unzip_success = self.unzip_file(file_name_taxon)           
        if not unzip_success:
            files_download_failed.append(file_name) 
            logging.error("Failed to download {} after {} attempts".format(file_name, max_download_attempts))
            return False
        
        # Write the README+ file 
        downloaded_files.append(file_name)
        comment = 'This folder contains taxonomy reference databases that downloaded from NCBI.'
        self.write_readme(download_url='{}/{}/{}'.format(self.login_url, self.download_folder,self.download_file),
                          downloaded_files=downloaded_files, download_failed_files=files_download_failed,
                          comment=comment, execution_time=(time.time() - download_start_time))

        return True
   
    def checksum(self, md5_file, file_name):
        try:
            with open(md5_file, 'r') as f:
                md5_file_contents = f.read()
            md5_str = md5_file_contents.split(' ')[0]
            os.remove(md5_file)
        except Exception as e:
            logging.exception('Could not read MD5 file {}. Try to download the file again'.format(file_name))
            return False
        
        if not self.check_md5(file_name, md5_str):
            logging.warning("MD5 check did not pass. Try to download the file again.")
            return False

        return True
    
    # Write the taxonomy file in a specific format, redmine #12865-14
    def format_taxonomy(self,filename):
        dmp_file = filename+".dmp"
        taxonomy_file = filename+".txt"
        try:
            taxonomy = open(taxonomy_file,"w")
            taxonomy.write("taxon_id\ttaxon_name\td__domain; k__kingdom; p__phylum; c__class; o__order; f__family; g__genus; s__species\n")
            with open(dmp_file) as fp:
                content = fp.readlines()
                for line in content:
                    line = line[:-3]
                    x = line.split("\t|\t")
                    tax_id, tax_name, species, genus, family, order, taxon_class,  phylum, kingdom, superkingdom = x
                    taxonomy.write(tax_id+"\t"+tax_name+"\td__"+superkingdom+"; k__"+kingdom+"; p__"+phylum+"; c__"+taxon_class+"; o__"+order+"; f__"+family+"; g__"+genus+"; s__"+species+"\n")
            taxonomy.close()   
        except Exception as e:
            logging.exception('Failed to format taxonomy file')
            return False
        # remove unwanted file and change file mode
        app_readme_file = self.config['readme_file']
        ncbi_readme_file = self.info_file_name
        taxonomy_file = self.taxonomy_file+".txt"
        try:
            only_files = [f for f in os.listdir(".") if os.path.isfile(f)]
            for f in only_files:
                if not f==app_readme_file and not f==ncbi_readme_file and not f==taxonomy_file:
                    os.remove(f)
                else:
                    os.chmod(f, self.file_mode)
        except Exception as e:
            logging.error("Failed to remove unwanted files, error:{}".format(e))
            return False
        
        return True
    
    
    def backup(self):
        logging.info("Executing NCBI taxonomy backup")

        backup_folder = self.create_backup_dir()
        if not backup_folder:
            logging.error("NCBI taxonomy Backup did not succeed.")
            return False
        
        try:
            src_files = [f for f in os.listdir('.') if os.path.isfile(f)]
            for filename in src_files:
                shutil.copy(filename, backup_folder)
    
        except Exception as e:
            logging.exception("NCBI taxonomy Backup did not succeed. Error: {}".format(e))
            return False
        
        return True

    def restore(self, proposed_folder_name, path_to_destination):
        logging.info("Executing NCBI taxonomy restore {} to {}".format(proposed_folder_name,path_to_destination))
        # check the restore folder, return false if not exist or empty folder
        try:
            #restore_folder = os.path.join(self.backup_dir, proposed_folder_name)
            restore_folder = self.check_restore_date(self.backup_dir, proposed_folder_name)
            if not restore_folder:
                return False
            
            restore_destination = self.check_restore_destination(path_to_destination)
            if not restore_destination:
                return False 
            
            # create restore destination folder
            if not os.path.isdir(restore_destination):
                os.makedirs(restore_destination,mode = self.folder_mode)
                
            # copy the all the files in backup_dir/folder_name to restore destination  
            os.chdir(restore_folder)
            for filename in os.listdir(restore_folder):
                shutil.copy2(filename, restore_destination) 
        
        except Exception as e:
            logging.exception("NCBI taxonomy restore did not succeed. Error: {}".format(e))
            return False
        
        print("The restored database is located at " +restore_destination)
        logging.info("The restored database is located at {} ".format(restore_destination))
        
        return True