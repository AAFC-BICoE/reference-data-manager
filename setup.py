from setuptools import setup, find_packages


setup(
    name="brdm",
    version="0.1",
    description='Bioinformatics Reference Data Manager for bioinformatics analysis',
    author='Oksana Korol',
    author_email='oksana.korol@agr.gc.ca',
    url='https://github.com/AAFC-BICoE/reference-data-manager',
    packages=find_packages(exclude=['tests', 'Test*', 'test*', '*.test', '*.test.*']),
    scripts=['main.py'],
    install_requires=[
        'numpy==1.14.0',
        'biopython==1.70',
        'PyYAML==3.12',
        'requests==2.18.4', ## This one also installs certifi, idna, urllib3, chardet and itself (requests)
      ],
    package_data={
        '': ['*.yaml*'],
      },
    entry_points={
          'console_scripts': [
              'brdm = main:main',
          ],
      },
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
      install_requires=[
          'numpy==1.14.0',
          'biopython==1.70',
          'PyYAML==3.12',
      ],
      entry_points={
          'console_scripts': [
              'rdm = main:main',
          ],
      },
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ),
      )
'''