import abc
import yaml
import requests
import os
from RefDataInterface import RefDataInterface

class BaseRefData(RefDataInterface):

    def __init__(self, config_file):
        self._config = self.load_config(config_file)
        self._root_dir = self._config['root_folder']

    @property
    def config(self):
        return self._config

    @config.setter
    def setConfig(self, config):
        self._config = config


    def getUpdateFrequency(self):
        raise NotImplementedError('Need to define getUpdateFrequency method to use this base class.')


    def getDownloadUrl(self):
        raise NotImplementedError('Need to define getDownloadUrl method to use this base class.')


    def getDestinationFolder(self):
        return self._root_dir


    def testConnection(self):
        raise NotImplementedError('Need to define testConnection method to use this base class.')


    def download(self):
        raise NotImplementedError('Need to define download method to use this base class.')


    def load_config(self, config_file):

        with open(config_file, 'r') as stream:
            try:
                config = yaml.load(stream)
            except yaml.YAMLError as exc:
                print("Error in configuration file:", exc)
            except Exception as msg:
                print("Could not load configuration file: %s" % os.path.abspath(config_file))
                print("Current working script is: %s" % os.path.abspath(__file__))

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
        return local_file_name

    def unzip_file(self):
        pass

    def delete_file(self, full_file_name):
        os.remove(full_file_name)