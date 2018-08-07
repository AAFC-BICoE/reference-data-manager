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
        # Parse configuration values
        super(NcbiTaxonomyData, self).__init__(config_file)
        
        self._download_folder = self.config['ncbi']['taxonomy']['download_folder']
        self._download_file = self.config['ncbi']['taxonomy']['download_file']
        self._taxonomy_file = self.config['ncbi']['taxonomy']['taxonomy_file']
        self._info_file_name = self.config['ncbi']['taxonomy']['info_file_name']
        self._chunk_size = self.config['ncbi']['taxonomy']['chunk_size']
        # Create destination directory and backup directory
        try:
            self.destination_dir = super(NcbiTaxonomyData, self).destination_dir + self.config['ncbi']['taxonomy']['destination_folder']
            if not os.path.exists(self.destination_dir):
                os.makedirs(self.destination_dir)
            os.chdir(self.destination_dir)
            self.backup_dir = super(NcbiTaxonomyData, self).backup_dir + self.config['ncbi']['taxonomy']['destination_folder']
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir)
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
        logging.info("Executing NCBI taxonomy update")
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
        # Download files into the intermediate folder
        success = self.download()
        if not success:
            logging.error("Download failed. Update will not proceed.")
            return False
        '''
        # Backup the files
        backup_success = self.backup()
        if not backup_success:
            logging.error("Backup of reference data did not succeed. The update will not continue.")
            return False
        '''
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
        
        #format the taxonomy file and remove unwanted files
        self.format_taxonomy(self._taxonomy_file) 
        app_readme_file = self.config['readme_file']
        ncbi_readme_file = self._info_file_name
        taxonomy_file = self._taxonomy_file+".txt"
        try:
            only_files = [f for f in os.listdir(".") if os.path.isfile(f)]
            for f in only_files:
                if not f==app_readme_file and not f==ncbi_readme_file and not f==taxonomy_file:
                    os.remove(f)
        except Exception as e:
            logging.error("Failed to remove unwanted files, error{}".format(e))
            return False
        
        return True
        
    
    def https_connect(self):
        logging.info('Connecting to NCBI https: {}'.format(self._login_url))
        login_data = {
                'username': self._ncbi_user,
                'password': self._ncbi_passw
                }
        retry_num = self.connection_retry_num
        session_requests = requests.Session()
        connected = False
        while not connected and retry_num != 0:
            try:
                session_requests.post(self._login_url, data=login_data)
                connected = True
            except Exception as e:
                print("Error connecting to login_url {}: {} Retrying...".format(self._login_url, e))
                time.sleep(self.sleep_time)
                retry_num -= 1
        return session_requests, connected
    
    
    # Download taxonomy database
    def download(self, test = False):
        logging.info("Executing NCBI taxonomy download")
        download_start_time = time.time()
        downloaded_files = [] 
        files_download_failed = []
        max_download_attempts = self.download_retry_num
        file_name = self._download_file
        readme_success = False
        download_success = test
        attempt = 0
        completed = False
        while attempt < max_download_attempts and not completed:
            attempt += 1
            try:
                file_url = os.path.join(self._login_url, self._download_folder)
                session_requests,connected = self.https_connect();
                if not readme_success:
                    #download readme file:
                    print("download readme")
                    file_name_readme = self._info_file_name
                    file_url_readme = os.path.join(file_url, file_name_readme)
                    readme_success = self.download_a_file(file_name_readme, file_url_readme, session_requests)
                
                if not download_success:
                    #download md5 file:
                    print("download md5 and taxonomy")
                    file_name_md5 = self._download_file+".md5"
                    file_url_md5 = os.path.join(file_url, file_name_md5)
                    md5_success = self.download_a_file(file_name_md5, file_url_md5, session_requests)
                    #download taxdump zipped file
                    file_name_taxon = self._download_file
                    file_url_taxon = os.path.join(file_url, file_name_taxon)
                    taxon_success = self.download_a_file(file_name_taxon, file_url_taxon, session_requests)
        
                    download_success = self.checksum(file_name_md5, file_name_taxon)
                if download_success and readme_success:
                    completed = True
                session_requests.close()
            except Exception as e:
                logging.info("failed to download taxonomy file on attempt {}: {}".format(attempt, e)) 
                time.sleep(self.sleep_time)
               
        if completed:
            unzip_success = self.unzip_file(file_name_taxon)           
        if not unzip_success:
            files_download_failed.append(file_name) 
            logging.error("failed to download %s after %s attempts" % (file_name, max_download_attempts))
            return False
        
        # Write the README+ file 
        downloaded_files.append(file_name)
        comment = 'This folder contains taxonomy reference databases that downloaded from NCBI.'
        self.write_readme(download_url='{}/{}/{}'.format(self._login_url, self._download_folder,self._download_file),
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
    
    # Download a file with provided file name and file address(link)
    def download_a_file(self, file_name, file_address, session_requests):
        chunkSize = self._chunk_size
        totalSize = 0
        try:    
            res = session_requests.get(file_address, stream=True, verify=False)
            with open(file_name, 'wb') as output:
                chunknumber = 0
                for chunk in res.iter_content(chunk_size=chunkSize, decode_unicode=False):
                    if chunk:
                        totalSize = totalSize + chunkSize
                        chunknumber += 1
                        output.write(chunk)
        except Exception as e:
            logging.exception('Failed to download file {}.'.format(file_name))
            return False
        
        return True
    
    # Write the taxonomy file in a specific format, redmine #12865-14
    def format_taxonomy(self,filename):
        dmp_file = filename+".dmp"
        taxonomy_file = filename+".txt"
        try:
            taxonomy = open(taxonomy_file,"w")
            taxonomy.write("taxon_id\ttaxon_name\td_domain; k_kingdom; p_phylum; c_class; o_order; f_family; g_genus; s_species\n")
            with open(dmp_file) as fp:
                content = fp.readlines()
                for line in content:
                    line = line[:-3]
                    x = line.split("\t|\t")
                    tax_id, tax_name, species, genus, family, order, taxon_class,  phylum, kingdom, superkingdom = x
                    taxonomy.write(tax_id+"\t"+tax_name+"\td_"+superkingdom+"; k_"+kingdom+"; p_"+phylum+"; c_"+taxon_class+"; o_"+order+"; f_"+family+"; g_"+genus+"; s_"+species+"\n")
            taxonomy.close()   
        except Exception as e:
            logging.exception('Failed to format taxonomy file')
            return False
        
        return True
    
    
    '''
    def backup(self):
        logging.info("Executing NCBI taxonomy backup")

        backup_folder = self.create_backup_dir()
        if not backup_folder:
            logging.error("NCBI taxonomy Backup did not succeed.")
            return False
        
        try:
            #copy_tree(self.destination_dir, backup_folder)
            src_files = [f for f in os.listdir('.') if os.path.isfile(f)]
            #src_files = os.listdir(self.destination_dir)
            for filename in src_files:
                shutil.copy(filename, backup_folder)
    
        except Exception as e:
            logging.exception("NCBI taxonomy Backup did not succeed. Error: {}".format(e))
            return False
        
        return True


    def restore(self, folder_name):
        logging.info("Executing NCBI taxonomy restore %s " % folder_name)
        # check the restore folder, return false if not exist or empty folder
        restore_folder = os.path.join(self.backup_dir, folder_name)
        if not os.path.exists(restore_folder):
            logging.error("could not restore, %s does not exist " % folder_name)
            return False
        if len(os.listdir(restore_folder) ) == 0:
            logging.error("could not restore, %s is an empty folder " % folder_name)
            return False
        # remove all the file in destination_dir  
        current_files = [f for f in os.listdir(self.destination_dir) if os.path.isfile(f)]
        for filename in current_files:
            os.remove(filename)
        # copy the all the files in backup_dir/folder_name to destination_dir    
        os.chdir(restore_folder)
        for filename in os.listdir(restore_folder):
            shutil.copy(filename, self.destination_dir) 
    '''   
