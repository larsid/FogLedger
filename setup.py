from setuptools import setup, find_packages


setup(
    name="fogLedger",
    version="2.0.2",
    description='Plugin to build DLTs in Fogbed.',
    long_description='Plugin to build DLT in Fogbed. Suport Hyperledger Indy',
    keywords=['networking', 'emulator', 'protocol', 'Internet', 'dlt', 'indy', 'fog'],
    url='https://github.com/larsid/FogLedger/tree/v2.0.0',
    author='Matheus Nascimento',
    author_email='matheusnascimentoti99@gmail.com',
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires = [
        'numpy>=1.24.2',
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False
)