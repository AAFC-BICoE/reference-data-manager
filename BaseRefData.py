import yaml
import requests
import os
import logging.config
import datetime


class BaseRefData():

    def __init__(self, config_file):
        self.config = self.load_config(config_file)
        # TODO: Check if config was loaded
        logging.config.dictConfig(self._config['logging'])

        #logging.critical("RDM application has started. Log file is here: {}.".format(self._config['logging']['handlers']['file']['filename']))

        self.destination_dir = os.path.abspath(self._config['root_folder']) + '/'
        if not os.path.exists(self.destination_dir):
            os.makedirs(self.destination_dir)

        #self._root_dir = os.path.abspath(self._config['root_folder'])
        #if not os.path.exists(self._root_dir):
        #    os.makedirs(self._root_dir)
        #TODO: catch all exceptions


    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        self._config = value

    @property
    def destination_dir(self):
        return self._destination_dir

    @destination_dir.setter
    def destination_dir(self, value):
        self._destination_dir = value


    def getUpdateFrequency(self):
        raise NotImplementedError('Need to define getUpdateFrequency method to use this base class.')


    def getDownloadUrl(self):
        raise NotImplementedError('Need to define getDownloadUrl method to use this base class.')

    '''
    def getDestinationFolder(self):
        return self._root_dir + "/"
    '''


    def load_config(self, config_file):

        with open(config_file, 'r') as stream:
            try:
                config = yaml.load(stream)
            except yaml.YAMLError as exc:
                print("Error in configuration file:", exc)
            except Exception as msg:
                print("Could not load configuration file: %s" % os.path.abspath(config_file))
                print("Current working script is: %s" % os.path.abspath(__file__))

        logging.info("RDM's configuration file was successfully loaded. File name: {}".format(config_file))

        return config


    #file_url = 'https://gist.github.com/oxyko/10798051fb9cf1e11f4baac2c6c49f3b/archive/44e343bfe87f56fbc8bb6fbf3a48294aa7b0a1b6.zip'
    def download_file(self, file_url, destination_dir):
        local_file_name = destination_dir + file_url.split('/')[-1]
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)
        r = requests.get(file_url, stream=True)  # stream=True makes sure that python does not run out of memory when reading/writing
        with open(local_file_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=512 * 1024):
                if chunk:
                    f.write(chunk)

        logging.info("File downloaded: {}".format(local_file_name))
        return local_file_name

    def unzip_file(self):
        pass

    def delete_file(self, full_file_name):
        os.remove(full_file_name)
        logging.info("File deleted: {}".format(full_file_name))


    def write_readme(self, download_url, files, comment=''):
        file_name = self.destination_dir + self.config['readme_file']
        print("Readme file: {}\n".format(file_name))
        with open(file_name, 'w') as f:
            f.write("About: this an automatically generated description file for the data located in this folder.\n")
            if comment:
                f.write("{}\n".format(comment))
            # now.strftime("%Y-%m-%d %H:%M")
            f.write("Downloaded on: {}\n".format(datetime.datetime.now()))
            f.write("Downloaded from: {}\n".format(download_url))
            f.write("List of downloaded files: \n")
            for file in files:
                f.write("{}\n".format(file))

        logging.info("Finished writing an application README file: {}".format(file_name))

    def parse_readme(self):
        # This one is for getting a list of files, recorded at the update/download time
        # Will be used in the restore backup
        pass