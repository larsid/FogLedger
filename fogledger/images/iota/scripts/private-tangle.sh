#!/bin/bash

# Script to run a new Private Tangle
# private-tangle.sh install .- Installs a new Private Tangle
# private-tangle.sh start   .- Starts a new Private Tangle
# private-tangle.sh stop    .- Stops the Tangle

set -e

chmod +x ./utils.sh
source ./utils.sh

help () {
  echo "Installs Private Tangle based on Hornet"
  echo "usage: private-tangle.sh [install]"
}

if [ $#  -lt 1 ]; then 
  echo "Illegal number of parameters"
  help
  exit 1
fi

command="$1"

ip_address=$(echo $(dig +short myip.opendns.com @resolver1.opendns.com))
COO_BOOTSTRAP_WAIT=10

nodes="$2"
# Split the node details string
extra_nodes=($(echo "$nodes" | tr ':' ' '))



clean () {
  if [ -d ./snapshots/private-tangle ]; then
    sudo rm -Rf ./snapshots/private-tangle/*
  fi

  # We need to do this so that initially the permissions are user's permissions
  resetPeeringFile config/peering-spammer.json
  resetPeeringFile config/peering-coo.json
  if [ -n "${extra_nodes}" ]; then
      for node in "${extra_nodes[@]}"; do
        peering_path="config/peering-${node}.json"
        echo "Resetting ${peering_path}"
        resetPeeringFile "${peering_path}"
      done
  fi
}

# Sets up the necessary directories if they do not exist yet
volumeSetup () {
  ## Directories for the Tangle DB files
  cd ../../../iota

  if ! [ -d ./config ]; then
    mkdir ./config
  else
    cd ./config
    for node in "${extra_nodes[@]}"; do
      echo "Copying config-node.json to config-${node}.json"
      cp config-node.json config-${node}.json
      sed -i 's/node1/'$node'/g' config-${node}.json
    done
    cd ..
  fi

  # Snapshots
  if ! [ -d ./snapshots ]; then
    mkdir ./snapshots
  fi
  
  if ! [ -d ./snapshots/private-tangle ]; then
    mkdir ./snapshots/private-tangle
  fi

  ## Change permissions so that the Tangle data can be written (hornet user)
  ## TODO: Check why on MacOS this cause permission problems
  if ! [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Setting permissions for Hornet..."
    sudo chown -R 65532:65532 snapshots 
  fi 
}

### 
### Generates the initial snapshot
### 
generateSnapshot () {
  echo "Generating an initial snapshot..."

  # First a key pair is generated
  docker run -t -i --rm iotaledger/hornet tool ed25519-key > key-pair.txt
  
  # Extract the public key use to generate the address
  local public_key="$(getPublicKey key-pair.txt)"

  # Generate the address
  cat key-pair.txt | awk -F : '{if ($1 ~ /ed25519 address/) print $2}' \
  | sed "s/ \+//g" | tr -d "\n" | tr -d "\r" > address.txt

  # Generate the snapshot
  cd snapshots/private-tangle
  docker run --rm -v "$PWD:/output_dir" -w /output_dir iotaledger/hornet tool snap-gen \
   --networkID "private-tangle" --mintAddress "$(cat ../../address.txt)" \
   --treasuryAllocation 1000000000 --outputPath /output_dir/full_snapshot.bin

  echo "Initial Ed25519 Address generated. You can find the keys at key-pair.txt and the address at address.txt"

  cd .. && cd ..
}

updateContainers () {
  docker pull iotaledger/hornet
}


installTangle () {
  # First of all volumes have to be set up
  volumeSetup
  
  clean

  # When we install we ensure container images are updated
  updateContainers

  # Initial snapshot
  generateSnapshot
}

case "${command}" in
	"help")
    help
    ;;
	"install")
    installTangle
    ;;
  *)
		echo "Command not Found."
		help
		exit 127;
		;;
esac
