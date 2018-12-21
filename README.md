# Bioinformatics Reference Data Manager (BRDM)

## Description
BRDM is an application used to automatically update, backup and restore the reference data that required for bioinformatic analysis.

## Requirements

* miniconda

## Deployment Procedures

* Download rdm_env_setting.yaml from github
```
  wget https://raw.githubusercontent.com/AAFC-BICoE/reference-data-manager/master/rdm_env_setting.yaml
```
* Create the conda environment for the program
```
  conda env create -n rdm_env --file rdm_env_setting.yaml 
```
## Run the program

* Set up the config file
  * The location of the sample configuration file config.yaml.sample
  ```
    /path/to/conda/envs/lib/python3.6/site-package/brdm
  ```
  * Default option to set up the config file: Copy the sample configuration to config.yaml and modify config.yaml
  ``` 
    cd /path/to/conda/envs/lib/python3.6/site-package/brdm
    cp config.yaml.sample config.yaml
    nano config.yaml
  ```
  * If the location or the name of your configuration file is different with that of default option, the path of your config file has to be provided by argument --config-file

* view the options of the program
```
  source activate rdm_env
  brdm -h
```
* Run the program
```
  source activate rdm_env
  brdm [option]
  (an example: brdm --update-ncbi-blast)
```

## Some suggestions for executing the program

* All the NCBI database should be updated outside of business hours. Abuse of the Entrez or NCBI services can lead to temporary
   loss of access.

* Construct the precise queries for NCBI subsets
   1. The purpose of the NCBI subsets is to construct database for specific markers in a group of taxa;
     it is suggested to provide information such as names of the markers, taxa and range of the sequence length in a query.
   2. Confirm and refine your queries by testing them on NCBI website.
   3. Due to the approach of constructing the subset database, sequences (e.g. wgs) that not exist in NCBI nt database cannot be included in subset database. The condition such as "and not wgs" is suggested to be added in your queries, in order to get the appropriate accession IDs and sequences.
    	1. The approach of constructing the subset database: Only accession IDs for each subsets are downloaded directly from NCBI; Sequences are retrieved from NCBI nt blast database;
    	2. Ncbi nt blast database consists of GenBank+EMBL+DDBJ+PDB+RefSeq sequences, but excludes EST, STS, GSS, WGS, TSA, patent sequences as well as phase 0, 1, and 2 HTGS sequences.

