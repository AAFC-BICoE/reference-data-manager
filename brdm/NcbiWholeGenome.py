from brdm.NcbiData import NcbiData
from brdm.RefDataInterface import RefDataInterface
import os, shutil
import tempfile
import logging
import time
from distutils.dir_util import copy_tree
import requests
from hashlib import md5

class NcbiWholeGenome(NcbiData, RefDataInterface):

    def __init__(self, config_file):
        super(NcbiWholeGenome, self).__init__(config_file)
        self.download_folder = self.config['ncbi']['whole_genome']['download_folder']
        self.download_file = self.config['ncbi']['whole_genome']['download_file']
        self.info_file_name = self.config['ncbi']['whole_genome']['info_file_name']
        self.assembly_level = self.config['ncbi']['whole_genome']['assembly_level']
        self.species = self.config['ncbi']['whole_genome']['species']
        try:
            self.destination_dir = os.path.join(super(NcbiWholeGenome, self).destination_dir, \
                                                self.config['ncbi']['whole_genome']['destination_folder'])
            if not os.path.exists(self.destination_dir):
                os.makedirs(self.destination_dir, mode = self.folder_mode)
            os.chdir(self.destination_dir)
            self.backup_dir = os.path.join(super(NcbiWholeGenome, self).backup_dir, \
                                           self.config['ncbi']['whole_genome']['destination_folder'])
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir, mode = self.folder_mode)
        except Exception as e:
            logging.error("Failed to create the destination_dir or backup_dir with error {}".format(e))
            
    
    def update(self):
        logging.info("Executing NCBI whole genomes update")
        # Download files into the intermediate folder
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
        # Backup the files a file with links of whole genomes 
        backup_success = self.backup()
        if not backup_success:
            logging.error("Backup of reference data did not succeed. The update will not continue.")
            return False
        
        # Delete old files from the destination folder
        # Copy new files from intermediate folder to destination folder
        clean_destination_ok = self.clean_destination_dir(self.destination_dir, True)
        if not clean_destination_ok:
            return False
        try:
            copy_tree(temp_dir, self.destination_dir)
            shutil.rmtree(temp_dir)
            for f in os.listdir("."):
                if os.path.isdir(f):
                    os.chmod(f,self.folder_mode)
        except Exception as e:
            logging.error("Failed to move files from temp_dir to destination folder, error{}".format(e))
            return False
        return True
        
    # Download taxonomy database
    def download(self, download_file_number = 3):
        logging.info("Executing NCBI whole genome download")
        download_start_time = time.time() 
        max_download_attempts = self.download_retry_num
        file_name = self.download_file
        readme_success = False
        attempt = 0
        while attempt < max_download_attempts and not readme_success:
            attempt += 1
            try:
                folder_url = os.path.join(self.login_url, self.download_folder)
                session_requests,connected = self.https_connect();
                file_name_readme = self.info_file_name
                file_url_readme = os.path.join(folder_url, file_name_readme)
                readme_success = self.download_a_file(file_name_readme, file_url_readme, session_requests)
                session_requests.close()
            except Exception as e:
                logging.error("Failed to download readme file on attempt {}: {}".format(attempt, e)) 
                time.sleep(self.sleep_time)
                
        if not readme_success:
            logging.error('Failed to download readme file after all attempts')
            return False
         
        downloaded_file = []       
        for a_set in self.species:
            folder_name = a_set
            try:
                if os.path.exists(folder_name):
                    shutil.rmtree(folder_name)
                os.makedirs(folder_name, mode = self.folder_mode)
                os.chdir(folder_name)
            except Exception as e:
                logging.error("Failed to create a folder {} : {}".format(folder_name, e)) 
            
            summary_success = False
            attempt = 0
            while attempt < max_download_attempts and summary_success == False:
                attempt += 1
                try:
                    session_requests,connected = self.https_connect(); 
                    summary_url = os.path.join(self.login_url, self.download_folder, a_set, self.download_file)
                    summary_success = self.download_a_file(self.download_file, summary_url, session_requests)
                    file_list = self.parse_assembly_summary(self.download_file)
                    session_requests.close()
                except Exception as e:
                    logging.info("Failed to download summary of {} on attempt {}: {}".format(a_set,attempt, e)) 
                    time.sleep(self.sleep_time)
            if not summary_success:
                logging.error("Failed to download summary of {} after all attempts: {}".format(a_set, e)) 
                return False
              
        
            attempt = 0
            
            
            if len(file_list) == 0:
                logging.error("Failed to get the file list to download")
                return False
        
            if download_file_number == 0:
                download_file_number = len(file_list)
            downloaded = 0 
            file_list_downloaded=[]  
            completed = False
            while attempt < max_download_attempts and completed == False:
                attempt += 1
                try:
                    session_requests,connected = self.https_connect(); 
                    for a_file in file_list:
                        if a_file not in file_list_downloaded:
                            #download  a genome zipped file
                            file_name = a_file.split('/')[-1]
                            file_url  = a_file.replace("ftp://","https://")
                            a_file = self.download_a_file(file_name, file_url, session_requests)
                            md5_name = 'md5checksums.txt'
                            md5_url = file_url.replace(file_name, md5_name)
                            md5_file = self.download_a_file(md5_name, md5_url, session_requests)
                            md5_code = self.read_md5(md5_name, file_name)
                            
                            a_file_success = self.check_md5(file_name, md5_code)
                            if a_file_success:
                                unzip_success = self.unzip_file(file_name)
                            if unzip_success:
                                downloaded += 1
                                downloaded_file.append(a_set+"\t"+file_url)
                                file_list_downloaded.append(a_file)
                            if downloaded == download_file_number:
                                completed = True
                                break;
                    session_requests.close()
                except Exception as e:
                    logging.error("Failed to download all file in {} on attempt {}: {}".format(a_set,attempt, e)) 
                    time.sleep(self.sleep_time)
                    
            if completed:
                try:
                    only_files = [f for f in os.listdir('.') if os.path.isfile(f)]
                    for f in only_files:
                        os.chmod(f, self.file_mode)
                    os.chdir('..')
                except Exception as e:
                    logging.error("Failed to change file mode")
                    return False
                
            
            if not completed:
                logging.info("Failed to download all file in {} after all attempts".format(a_set)) 
                return False
            
        files_download_failed = []
        # Write the README+ file 
        # downloaded_files.append(a_set+"/"+file_name)
        comment = 'This folder contains whole genome sequences that downloaded from NCBI.'
        self.write_readme(download_url='{}/{}/'.format(self.login_url, self.download_folder),
                          downloaded_files=downloaded_file, download_failed_files=files_download_failed,
                          comment=comment, execution_time=(time.time() - download_start_time))

        return True
    
    def read_md5(self, md5_file, file_name):
        try:
            with open(md5_file, 'r') as f:
                md5_file_contents = f.readlines()
                for line in md5_file_contents:
                    line_items = line.split('  ')
                    if file_name in line_items[1]:
                        md5_code = line_items[0]
            os.remove(md5_file)
        except Exception as e:
            logging.exception('Failed to get the md5_code {}.'.format(file_name))   
        return md5_code
    
    
    def parse_assembly_summary(self, assembly_file):
        '''
        Parses assembly_reference.txt file from NCBI and extracts full ftp files paths to download.
        :param assembly_file: full path to the assembly_summary.txt
        :param output_file: full path to the file which will contain the result of parsing
        :return: True if successfull, False otherwise
        '''
        file_list = list()
        try:
            with open(assembly_file, "r") as fp:
                content = fp.readlines()
                for line in content[3:]:
                    line_items = line.split('\t')
                    if line_items[11] == self.assembly_level:
                        dir_name = line_items[19]
                        dir_list = dir_name.split('/')
                        full_file_name = "{}/{}_genomic.fna.gz".format(dir_name, dir_list[-1])
                        file_list.append(full_file_name)
            
        except:
            logging.exception('Failed to download file {}.'.format(file_name))
            file_list = list()
            return file_list
        
        return file_list
    
    
    def backup(self):
        logging.info("Executing NCBI wholeGenome backup")

        backup_folder = self.create_backup_dir()
        if not backup_folder:
            logging.error("NCBI wholeGenome Backup did not succeed.")
            return False
        
        # Copy only README files for future reference
        app_readme_file = self.config['readme_file']
        ncbi_readme_file = self.info_file_name
        try:
            shutil.copy2(app_readme_file, backup_folder)
            shutil.copy2(ncbi_readme_file, backup_folder)  
        except Exception as e:
            logging.exception("NCBI wholegenome Backup did not succeed. Error: {}".format(e))
            return False
        
        return True

    
    def restore(self, proposed_folder_name, path_to_destination):
        logging.info("Executing NCBI wholegenome restore {}{} ".format(proposed_folder_name, path_to_destination))
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
                
                
            os.chdir(restore_destination)
            required_files = []   
            #session_requests,connected = self.https_connect()
            with open(self.config['readme_file'], "r") as fp:
                content = fp.readlines()
                for line in content[6:]:
                    required_files.append(line)   
            restore_download_ok = self.restore_download(required_files, restore_destination)
            if not restore_download_ok:
                return False
        except Exception as e:
            logging.exception("NCBI wholegenome restore did not succeed. Error: {}".format(e))
            return False
               
        return True        
                
    def restore_download(self, file_list, restore_destination):
        downloaded = 0 
        file_list_downloaded=[]  
        completed = False
        attempt = 0
        max_download_attempts = self.download_retry_num
        while attempt < max_download_attempts and completed == False:
            attempt += 1
            try:
                session_requests,connected = self.https_connect(); 
                for a_file in file_list:
                    if a_file not in file_list_downloaded:
                        subdir, link = a_file.split("\t")
                        #download  a genome zipped file
                        file_name = link.split('/')[-1].strip("\n")
                        file_url  = link.strip("\n")
                        path_to_subdir = os.path.join(restore_destination, subdir)
                        if not os.path.isdir(path_to_subdir):
                            os.makedirs(path_to_subdir,mode = self.folder_mode )
                        os.chdir(path_to_subdir)
                        a_file = self.download_a_file(file_name, file_url, session_requests)
                        md5_name = 'md5checksums.txt'
                        md5_url = file_url.replace(file_name, md5_name)
                        md5_file = self.download_a_file(md5_name, md5_url, session_requests)
                        md5_code = self.read_md5(md5_name, file_name)
                        a_file_success = self.check_md5(file_name, md5_code)
                        unzip_success = False
                        if a_file_success:
                            unzip_success = self.unzip_file(file_name)
                        if unzip_success:
                            downloaded += 1
                        if downloaded == len(file_list):
                            completed = True
                            break
                        os.chdir("..")
                session_requests.close()
            except Exception as e:
                logging.error("Failed to download all files on attempt {}: {}".format(attempt, e)) 
                time.sleep(self.sleep_time)
                    
        if completed:
            try:
                for root, dirs, files in os.walk(restore_destination):
                    for f in files:
                        os.chmod(os.path.join(root, f), self.file_mode)
            except Exception as e:
                logging.error("Failed to change file mode {}".format(e))
                return False
                
        return True
        
    