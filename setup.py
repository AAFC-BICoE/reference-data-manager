from setuptools import setup, find_packages


setup(
    name="brdm",
    version="0.1",

    description='''Bioinformatics Reference Data Manager is an application used to download, backup and update of \
    reference data, required for various bioinformatics analysis''',

    author='Oksana Korol',
    author_email='oksana.korol@agr.gc.ca',

    url='https://github.com/AAFC-BICoE/reference-data-manager',

    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ),


    packages=find_packages(exclude=['test*', 'Test*']),

    package_data={
        '': ['README.md', 'LICENSE'],
        'brdm': ['config.yaml.sample']
      },


    scripts=['main.py'],

    entry_points={
          'console_scripts': [
              'brdm = main:main',
          ],
      },

    install_requires=[
        'PyYAML==3.13',
        'requests==2.19.1', ## This one also installs certifi, idna, urllib3, chardet and itself (requests)
      ],


)

'''
setup(name='rdm',
      version='0.1',
      description='Reference Data Manager for bioinformatics research',
      author='Oksana Korol',
      author_email='oksana.korol@agr.gc.ca',
      url='https://github.com/AAFC-BICoE/reference-data-manager',

      packages=find_packages(exclude=['test', '*.test', '*.test.*']),
      include_package_data=True,
      package_data={
        '': ['*.yaml.sample', 'README.md'],
        'config': ['*.yaml.sample, *.yaml'],
      },
      
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ),
      )
'''