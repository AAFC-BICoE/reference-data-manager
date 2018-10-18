from brdm.BaseRefData import BaseRefData
from brdm.RefDataInterface import RefDataInterface
import os, shutil
import tempfile
import logging
import time
from distutils.dir_util import copy_tree
import requests, requests_ftp


class GreenGeneData(BaseRefData, RefDataInterface):

    def __init__(self, config_file):
        super(GreenGeneData, self).__init__(config_file)
        self.download_url = self.config['greengene']['download_url']
        self.download_file = self.config['greengene']['download_file']
        self.format_file = self.config['greengene']['format_file']
        self.info_file_name = self.config['greengene']['info_file_name']
        self.qiime2_path = self.config['greengene']['qiime2_path']
        try:
            self.destination_dir = os.path.join(super(GreenGeneData, self).destination_dir, \
                                                self.config['greengene']['destination_folder'])
            if not os.path.exists(self.destination_dir):
                os.makedirs(self.destination_dir, mode = self.folder_mode)
            os.chdir(self.destination_dir)
            self.backup_dir = os.path.join(super(GreenGeneData, self).backup_dir, \
                                           self.config['greengene']['destination_folder'])
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir, mode = self.folder_mode)
        except Exception as e:
            logging.error("Failed to create the destination_dir or backup_dir with error {}".format(e))
            

    def update(self):
        logging.info("Executing greengene update")
        # Download files into the intermediate folder 
        temp_dir = self.create_tmp_dir(self.destination_dir)
        if not temp_dir:
            logging.error("Failed to create the temp_dir: {}, error{}".format(temp_dir, e))
            return False
        success = self.download()
        if not success:
            logging.error("Download failed. Update will not proceed.")
            return False
        # Back up readme+ file
        backup_success = self.backup()
        if not backup_success:
            logging.error("Failed to backup readme files. The update will not continue.")
            return False
        # Delete old files from the destination folder
        # Copy new files from intermediate folder to destination folder
        clean_destination_ok = self.clean_destination_dir(self.destination_dir, True)
        if not clean_destination_ok:
            return False
        try:
            copy_tree(temp_dir, self.destination_dir)
            shutil.rmtree(temp_dir)
        except Exception as e:
            logging.error("Failed to move files from temp_dir to destination folder, error{}".format(e))
            return False
        return True
        
   
    def download(self, test = False):
        logging.info("Executing greengene download")
        download_start_time = time.time()
        downloaded_files = [] 
        files_download_failed = []
        max_download_attempts = self.download_retry_num
        
        attempt = 0
        readme_success = False
        while attempt < max_download_attempts and not readme_success:
            attempt += 1
            try:
                readme_url = os.path.join(self.download_url, self.info_file_name)
                readme_success = self.download_a_file(self.info_file_name, readme_url)
            except Exception as e:
                logging.info("failed to download readme file on attempt {}: {}".format(attempt, e)) 
                time.sleep(self.sleep_time)
       
        if not readme_success:
            logging.info("failed to download readme file after {} attempts.".format(attempt))
            return False
    
        for a_file in self.download_file:
            attempt = 0
            completed = False
            file_name = a_file
            while attempt < max_download_attempts and not completed:
                attempt += 1
                try:
                    file_url = os.path.join(self.download_url, file_name)
                    file_success = self.download_a_file(file_name, file_url)
                    #if file_success:
                    #    completed = True
                    md5_url = file_url+".md5"
                    md5_name = file_name+".md5"
                    md5_success = self.download_a_file(md5_name, md5_url)
                    if file_success and md5_success:
                        checksum_success = self.checksum(md5_name, file_name)
                    if checksum_success: 
                        completed = self.unzip_file(file_name)
                   
                except Exception as e:
                    logging.info("failed to download greengene file {} on attempt {}: {}".format(file_name, attempt, e)) 
                    time.sleep(self.sleep_time)
        
            if completed:
                downloaded_files.append(file_name)
            else:
                logging.info("failed to download greengene file {} after all attempts".format(file_name))
                return False
        # Write the README+ file 
        comment = 'This folder contains greenGene data.'
        self.write_readme(download_url='{}'.format(self.download_url),
                          downloaded_files=downloaded_files, download_failed_files=files_download_failed,
                          comment=comment, execution_time=(time.time() - download_start_time))

        return True
    

    def checksum(self, md5_file, file_name):
        try:
            if file_name == 'gg_13_5.fasta.gz':
                with open(file_name+".md5", 'r') as f:
                    md5_file_contents = f.read()
                    md5_str = md5_file_contents.split(' ')[0] 
            else:
                with open(md5_file, 'r') as f:
                    md5_file_contents1 = f.read()
                    md5_file_contents = md5_file_contents1.strip('\n')
                    md5_str = md5_file_contents.split(' ')[3]      
            os.remove(file_name+".md5")
                    
        except Exception as e:
            logging.exception('Could not read MD5 file {} '.format(file_name))
            return False
        
        if not self.check_md5(file_name, md5_str):
            logging.warning("MD5 check did not pass.")
            return False

        return True

    # Download a file with provided file name and file address(link)
    def download_a_file(self, file_name, file_address):
        print(file_name)
        requests_ftp.monkeypatch_session()
        session_requests = requests.Session()
        try:   
            res = session_requests.get(file_address, stream=True)
            with open(file_name, 'wb') as output:
                shutil.copyfileobj(res.raw, output)
            
            session_requests.close()
        except Exception as e:
            logging.exception('Failed to download file {}.'.format(file_name))
            return False
        return True
    
    # backup readme and readme+ file
    def backup(self):
        logging.info("Executing Greengene backup")

        backup_folder = self.create_backup_dir()
        if not backup_folder:
            logging.error("Failed to create backup folder.")
            return False
        # Copy only README files for future reference
        app_readme_file = self.config['readme_file']
        ncbi_readme_file = self.info_file_name
        try:
            shutil.copy2(app_readme_file, backup_folder)
            shutil.copy2(ncbi_readme_file, backup_folder)
        except Exception as e:
            logging.exception("Greengene backup did not succeed. Error: {}".format(e))
            return False

        return True

    def restore(self,folder_name):
        logging.info("Restoringing Greengene data ... Nothing to do.")
        pass
    
    def get_format_file_list(self):
        sequence_file = []
        taxon_file = []
        output_file = []
        try:
            for a_file in self.format_file:
                f1 = a_file.split("|")[0].strip()
                f2 = a_file.split("|")[1].strip()
                f3 = a_file.split("|")[2].strip()
                if f1 and f2 and f3:
                    sequence_file.append(os.path.join(self.destination_dir, f1))
                    taxon_file.append(os.path.join(self.destination_dir, f2))
                    output_file.append(f3)
                else:
                    logging.error("the format file is not valid {}".format(a_file))
                    return False
        except Exception as e:
            logging.exception("Failed in get format file list. Error: {}".format(e))
            return False

        return sequence_file,taxon_file,output_file
            
    def format(self):
        sequence_file,taxon_file,output_file = self.get_format_file_list()
        qiime1 = self.to_qiime1_format(sequence_file, taxon_file, output_file)
        if not qiime1:
            logging.error("Failed to get qiime1 format.")
            return False
        mothur = self.to_mothur_format(sequence_file, taxon_file, output_file)
        if not mothur:
            logging.error("Failed to get mothur format.")
            return False
        qiime2 = self.to_qiime2_format(sequence_file, taxon_file, output_file)
        if not qiime2:
            logging.error("Failed to get qiime2 format.")
            return False
        q1_rdp = self.to_qiime1_rdp_format(sequence_file, taxon_file, output_file)
        if not q1_rdp:
            logging.error("Failed to get qiime1_rdp format.")
            return False
            
        return True
    
    
    def to_qiime1_format(self, sequence_file, taxon_file, output_file):
        try:
            qiime1_folder = os.path.join(self.destination_dir, 'Qiime1')
            if os.path.exists(qiime1_folder):
                shutil.rmtree(qiime1_folder)
            os.makedirs(qiime1_folder, mode = self.folder_mode)
            os.chdir(qiime1_folder)
            for index in range(len(sequence_file)):
                input_sequence = sequence_file[index]
                input_taxon = taxon_file[index]
                output_sequence = os.path.join(qiime1_folder, output_file[index])+".fasta"
                output_taxon = os.path.join(qiime1_folder, output_file[index])+".taxon"
                os.symlink(input_sequence, output_sequence)
                os.symlink(input_taxon, output_taxon)
                os.chmod(output_sequence, self.file_mode)
                os.chmod(output_taxon, self.file_mode)       
        except Exception as e:
            logging.error("Failed to get qiime1 format, error {} ".format(e))
            return False
        return True
    
    
    def to_qiime2_format(self,sequence_file, taxon_file, output_file):
        try:
            qiime2_folder = os.path.join(self.destination_dir, 'Qiime2')
            if os.path.exists(qiime2_folder):
                shutil.rmtree(qiime2_folder)
            os.makedirs(qiime2_folder, mode = self.folder_mode)
            os.chdir(qiime2_folder)
            export_path = 'export PATH="'+self.qiime2_path+':$PATH"'
            os.system(export_path)
            print(export_path)
            for index in range(len(sequence_file)):
                input_sequence = sequence_file[index]
                input_taxon = taxon_file[index]
                output_taxon = os.path.join(qiime2_folder, output_file[index])+"_taxon.qza"
                output_sequence = os.path.join(qiime2_folder, output_file[index])+"_fasta.qza"
                sklearn_classifier = os.path.join(qiime2_folder, output_file[index])+"_sklearn_classifier.qza"
                
                command1 = self.qiime2_path+"/qiime tools import \
                        --type 'FeatureData[Sequence]' \
                        --input-path "+input_sequence+ " \
                        --output-path "+ output_sequence
                os.system(command1)
                print(command1)
                command2 = self.qiime2_path+"/qiime tools import \
                        --type 'FeatureData[Taxonomy]' \
                        --source-format HeaderlessTSVTaxonomyFormat \
                        --input-path "+ input_taxon+ " \
                        --output-path "+ output_taxon
                        
                os.system(command2)
                print(command2)
                command3 = self.qiime2_path+"/qiime feature-classifier fit-classifier-naive-bayes \
                      --i-reference-reads "+output_sequence +" \
                      --i-reference-taxonomy "+output_taxon +" \
                      --o-classifier "+sklearn_classifier
                print(command3)
                os.system(command3)
                print("after command3")
                  
                os.chmod(output_taxon, self.file_mode)
                os.chmod(output_sequence, self.file_mode)
                os.chmod(sklearn_classifier, self.file_mode)
        except Exception as e:
            logging.error("Failed to get qiime2 format, error {} ".format(e))
            return False
        return True
    
      
    def to_qiime1_rdp_format(self,sequence_file, taxon_file, output_file):
        try:
            rdp_folder = os.path.join(self.destination_dir, 'Qiime1_rdp')
            if os.path.exists(rdp_folder):
                shutil.rmtree(rdp_folder)
            os.makedirs(rdp_folder, mode = self.folder_mode)
            os.chdir(rdp_folder)
            for index in range(len(sequence_file)):
                input_sequence = sequence_file[index]
                input_taxon = taxon_file[index]
                output_taxon = os.path.join(rdp_folder, output_file[index])+".taxon"
                output_sequence = os.path.join(rdp_folder, output_file[index])+".fasta"
                # symbolic link to the sequence file
                os.symlink(input_sequence, output_sequence)
                # remove spaces in qiime1 taxon file
                with open(input_taxon, 'r') as f_in, open(output_taxon, 'w') as f_out:
                    for line in f_in:
                        f_out.write(line.replace('; ', ';'))
                os.chmod(output_taxon, self.file_mode) 
                os.chmod(output_sequence, self.file_mode)    
        except Exception as e:
            logging.error("failed to get qiime1_rdp format, error {} ".format(e))
            return False
        return True
    
    
    def to_mothur_format(self, sequence_file, taxon_file, output_file):
        try:
            mothur_folder = os.path.join(self.destination_dir, 'Mothur')
            if os.path.exists(mothur_folder):
                shutil.rmtree(mothur_folder)
            os.makedirs(mothur_folder, mode = self.folder_mode)
            os.chdir(mothur_folder)
            for index in range(len(sequence_file)):
                input_sequence = sequence_file[index]
                input_taxon = taxon_file[index]
                output_taxon = os.path.join(mothur_folder, output_file[index])+".taxon"
                output_sequence = os.path.join(mothur_folder, output_file[index])+".fasta"
                # symbolic link to the sequence file
                os.symlink(input_sequence, output_sequence)
                
                mothur_taxon_file = open(output_taxon, "w")     
                with open(input_taxon) as fp:
                    content = fp.readlines()
                    for line in content:
                        line = line[:-1]
                        x = line.split("\t")
                        tax_id, level_8 = x
                        levels = level_8.split('; ')
                        a_line=""
                        for a_level in levels:
                            if a_level[3:] and not a_line:
                                a_line = a_level[3:]
                            elif a_level[3:] and a_line:
                                a_line = a_line+";"+a_level[3:]
                        a_line = a_line+";"
                        mothur_taxon_file.write(tax_id+"\t"+a_line.replace(" ","")+"\n")
                mothur_taxon_file.close()
                os.chmod(output_taxon, self.file_mode)  
                os.chmod(output_sequence, self.file_mode)     
        except Exception as e:
            logging.error("Failed to get mothur format, error {} ".format(e))
            return False
        return True
    
   