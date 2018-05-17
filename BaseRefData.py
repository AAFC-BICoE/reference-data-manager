import abc
import yaml

class BaseRefData(metaclass=abc.ABCMeta):

    def __init__(self, config_file):
        self._config = self.load_config(config_file)

    @property
    def config(self):
        return self._config

    @config.setter
    def setConfig(self, config):
        self._config = config

    @abc.abstractmethod
    def getUpdateFrequency(self):
        raise NotImplementedError('Need to define getUpdateFrequency method to use this base class.')

    @abc.abstractmethod
    def getDownloadUrl(self):
        raise NotImplementedError('Need to define getDownloadUrl method to use this base class.')

    @abc.abstractmethod
    def getDestinationFolder(self):
        raise NotImplementedError('Need to define getDestinationFolder method to use this base class.')

    @abc.abstractmethod
    def testConnection(self):
        raise NotImplementedError('Need to define testConnection method to use this base class.')

    @abc.abstractmethod
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