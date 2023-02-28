![](https://img.shields.io/badge/python-3.8+-blue.svg)
# FogLedger

FogLedger is tool based on Fogbed. It is framework and toolset integration for rapid prototyping of fog components in virtual-ized environments using a desktop approach for DLTs. Its design meets the postulated requirements of low cost, flexible setup and compatibility with real world technologies. The components are based on Mininet network emulator with Docker container instances as fog virtual nodes.

## Install

Before installing Fogbed it is necessary to install some dependencies and Containernet, as shown in the steps below:


#### 1. Install Containernet
```
sudo apt-get install ansible
```

```
git clone https://github.com/containernet/containernet.git
```

```
sudo ansible-playbook -i "localhost," -c local containernet/ansible/install.yml
```

#### 2. Install Fogbed
```
sudo pip install -U git+https://github.com/EsauM10/fogbed.git
```


## Get Started
## Preparing Blockchain Test 


#### Build DLTs Images
```
cd dlts/images
```

```
chmod +x build_images.sh
```

```
./build_images.sh
```

## Run example

```
cd dlts 
```

```
sudo python3 test-distributed-network
```