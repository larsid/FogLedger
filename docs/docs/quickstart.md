# FogLedger



## 1. Install

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

#### 3. Install FogLedger

```
sudo pip install fogLedger
```

## 2. Run example

```
mkdir example
cd example
```

### 1. Download example

```
wget https://raw.githubusercontent.com/larsid/FogLedger/main/examples/test-local-network.py
wget https://github.com/larsid/FogLedger/blob/main/examples/tmp/trustees.csv -o ./tmp/trustees.csv
```

### 2. Run local network

```
sudo python3 test-local-network.py
```
