from setuptools import setup, find_packages
import os.path

readme_file = 'README.md'
readme = 'Cannot find the file:'+readme_file
if os.path.exists(readme_file):

    with open(readme_file) as f:

        readme = f.read()

license_file = 'LICENSE'
license = 'Cannot find the file:'+license_file
if os.path.exists(license_file):

    with open(license_file) as f:

        license = f.read()

requires_file = 'requirements.txt'
requires = 'Cannot find the file:'+requires_file
if os.path.exists(requires_file):

    with open(requires_file) as f:

        requires = f.read()


setup(
    name="reference-data-manager",
    version="0.8.3",

    description='''Bioinformatics Reference Data Manager is an application
    used to download, backup and update of reference data, required for
    various bioinformatics analysis''',

    long_description=readme,
    long_description_content_type='text/markdown',

    author='Chunfang Zheng, Oksana Korol',
    author_email='aafc.bice-ceib.aac@canada.ca',

    url='https://github.com/AAFC-BICoE/reference-data-manager',

    license='MIT License',

    classifiers=(
        "Programming Language :: Python :: 3",

        "License :: OSI Approved :: MIT License",

    ),

    packages=find_packages(exclude=['test*', 'Test*']),

    package_data={
        '': ['README.md', 'LICENSE'],

        'brdm': ['config.yaml.sample']

      },

    include_package_data=True,

    # install_requires = requires,

    scripts=['main.py', 'rdm_env_setting.yaml'],

    entry_points={
          'console_scripts': [
              'brdm = main:main',

          ],

      },


)
