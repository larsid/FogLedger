from setuptools import setup, find_packages


setup(
    name="fogLedger",
    version="2.0.0",
    description='Plugin to build DLTs in Fogbed.',
    long_description='Plugin to build DLT in Fogbed. Suport Hyperledger Indy',
    keywords=['networking', 'emulator', 'protocol', 'Internet', 'dlt', 'indy', 'fog'],
    url='https://github.com/larsid/FogLedger/tree/v2.0.0',
    author='Matheus Nascimento',
    author_email='matheusnascimentoti99@gmail.com',
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python 3.8',
        'Topic :: System :: Emulators'
        'Operating System :: Ubunbu OS',
        'Blockchain :: Hyperledger Indy',
    ],
    install_requires = [
        'fogbed @ https://github.com/EsauM10/fogbed',
        'numpy>=1.24.2',
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False
)