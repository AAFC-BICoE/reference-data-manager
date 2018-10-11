# Bioinformatics Reference Data Manager (BRDM)

## Description
BRDM is an application used to download, backup and update of 
reference data, required for bioinformatic analysis.

## Requirements

* python 3.5
* conda

## Deployment Procedures

* Download the latest release of this project from https://github.com/AAFC-BICoE/reference-data-manager
  OR check out this project by clone the git repository.
  > git clone https://github.com/AAFC-BICoE/reference-data-manager.git

* Set up the conda environment for the program
  > cd reference-data-manager

  > conda env create -n rdm_env --file rdn_env_setting.yaml 

## Run the program

* Copy the sample configuration and modify the config.yaml file
  > cp brdm/config.yaml.sample brdm/config.yaml

* View the options of the program
  > source activate rdm_env

  > python main.py -h

* Run the program
  > source activate rdm_env

  > python main.py [option]
  (an example: python main.py --update-ncbi-blast)

  

