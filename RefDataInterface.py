import abc
import yaml
import requests
import os

class RefDataInterface(metaclass=abc.ABCMeta):

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
