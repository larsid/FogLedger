#!/bin/bash

# Script to deploy a Tangle Explorer component
# tangle-explorer.sh install .- Installs a new Tangle Exlorer
# tangle-explorer.sh start   .- Starts a new Tangle Exlorer
# tangle-explorer.sh update  .- Updates the Tangle Exlorer
# tangle-explorer.sh stop    .- Stops the Tangle Exlorer

set -e

help () {
  echo "usage: tangle-explorer.sh [install|update] [json-file-with-network-details.json] or [private-tangle-install-folder]"
}

if [ $#  -lt 1 ]; then
  echo "Illegal number of parameters"
  help
  exit 1
fi

### Initialization code

command="$1"
network_file="$2"
is_config_folder=false

EXPLORER_SRC="$2/explorer-src"
APP_DATA="$2/application-data"
DEFAULT_NETWORK_FILE="./private-network.json"

if [ "$command" == "install" ]; then
  if [ $# -lt 2 ]; then
    network_file="$DEFAULT_NETWORK_FILE"
  fi
fi

is_config_folder=true
folder_config="$2/config"
# The copy process will leave the network configuration under this file
network_file="$folder_config/my-network.json"
#fi

###################

clean () {

  if [ -d $EXPLORER_SRC ]; then
    rm -Rf $EXPLORER_SRC
  fi

  if [ -d $APP_DATA ]; then
    rm -Rf $APP_DATA
  fi
}

# Builds the network configuration file 
# in case only a folder with configuration files is given
buildConfig() {
  echo "Config api"
  
  echo $(cat $folder_config/../coo-milestones-public-key.txt)
  cp private-network.json $folder_config/my-network.json

  # Set the Coordinator Address
  sed -i 's/"coordinatorAddress": \("\).*\("\)/"coordinatorAddress": \1'$(cat $folder_config/../coo-milestones-public-key.txt)'\2/g' $folder_config/my-network.json

  # Set in the Front-End App configuration the API endpoint
  sed -i 's/"apiEndpoint": \("\).*\("\)/"apiEndpoint": \1http:\/\/localhost:4000\2/g' ./webapp.config.local.json
}

# Copies the configuration
copyConfig () {
  if ! [ -d $APP_DATA ]; then
    mkdir $APP_DATA
  fi

  if ! [ -d $APP_DATA/network ]; then
    mkdir $APP_DATA/network
  fi

  if ! [ -d $EXPLORER_SRC/api ]; then
    mkdir -p $EXPLORER_SRC/api/src/data
  fi

  cp -f $network_file $APP_DATA/network/private-network.json

  # Configuration of the API Server
  cp -f api.config.local.json $EXPLORER_SRC/api/src/data/config.local.json

  if ! [ -d $EXPLORER_SRC/client/src/assets/config ]; then
    mkdir -p "$EXPLORER_SRC/client/src/assets/config"
  fi
  
  # Configuration of the Web App
  cp -f webapp.config.local.json $EXPLORER_SRC/client/src/assets/config/config.local.json

  # TODO: Check why is it really needed
  if [ -f "$EXPLORER_SRC/client/package-lock.json" ]; then
    rm "$EXPLORER_SRC/client/package-lock.json"
  fi
}

installExplorer () {
  #clean
   
  #sudo git clone https://github.com/iotaledger/explorer $EXPLORER_SRC

  # If the input parameter is a folder with config then we need to build it
  if [ "$is_config_folder" = true ]; then
    buildConfig
  fi

  copyConfig
}


updateExplorer () {
  if ! [ -d "$EXPLORER_SRC" ]; then
    echo "Install the Tangle explorer first with './tangle-explorer.sh install'"
    exit 129
  fi

  stopExplorer

  cd $EXPLORER_SRC
  git pull

  startExplorer
}

case "${command}" in
	"help")
    help
    ;;
	"install")
    installExplorer
    ;;
  "update")
		updateExplorer
		;;
  *)
		echo "Command not Found."
		help
		exit 127;
		;;
esac
