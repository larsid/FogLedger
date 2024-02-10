#!/bin/bash

# Script to run a new Private Tangle
# private-tangle.sh install .- Installs a new Private Tangle
# private-tangle.sh start   .- Starts a new Private Tangle
# private-tangle.sh stop    .- Stops the Tangle

set -e

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

COO_BOOTSTRAP_WAIT=10

DIR=/tmp/iota/$USER



clean () {
  if [ -d ./snapshots/private-tangle ]; then
    rm -Rf ./snapshots/private-tangle/*
  fi

  # We need to do this so that initially the permissions are user's permissions
  #resetPeeringFile config/peering-spammer.json
  #resetPeeringFile config/peering-coo.json
}

# Sets up the necessary directories if they do not exist yet
volumeSetup () {
  mkdir -p "${DIR}/config"
  cp -r config-node.json "${DIR}/config/config-node.json"
  cp -r config-coo.json "${DIR}/config/config-coo.json"
  cp -r config-spammer.json "${DIR}/config/config-spammer.json"
  cp -r private-network.json "${DIR}/config/my-network.json"
  cp -r api.config.local.json "${DIR}/config/api.config.local.json"
  cp -r webapp.config.local.json "${DIR}/config/webapp.config.local.json"
  cd "${DIR}"

  # Snapshots
  if ! [ -d ./snapshots ]; then
    mkdir ./snapshots
  fi
  
  if ! [ -d ./snapshots/private-tangle ]; then
    mkdir ./snapshots/private-tangle
  fi
  
  chmod -R 777 "${DIR}"

}

### 
### Generates the initial snapshot
### 
generateSnapshot () {
  echo "Generating an initial snapshot..."

  # First a key pair is generated
  docker run -t -i --rm iotaledger/hornet:1.2.4 tool ed25519-key > key-pair.txt
  
  # Extract the public key use to generate the address
  local public_key="$(getPublicKey key-pair.txt)"

  # Generate the address
  cat key-pair.txt | awk -F : '{if ($1 ~ /ed25519 address/) print $2}' \
  | sed "s/ \+//g" | tr -d "\n" | tr -d "\r" > address.txt

  # Generate the snapshot
  cd snapshots/private-tangle
  docker run --rm -u "$(id -u):$(id -g)" -v "$PWD:/output_dir" -w /output_dir iotaledger/hornet:1.2.4 tool snap-gen \
   --networkID "private-tangle" --mintAddress "$(cat ../../address.txt)" \
   --treasuryAllocation 1000000000 --outputPath /output_dir/full_snapshot.bin

   chmod 777 ./full_snapshot.bin 

  echo "Initial Ed25519 Address generated. You can find the keys at key-pair.txt and the address at address.txt"

  cd .. && cd ..
}

updateContainers () {
  docker pull iotaledger/hornet:1.2.4
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
