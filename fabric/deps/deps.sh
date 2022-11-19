#!/bin/bash 

COMMAND=$1

function printHelp() {
    echo_bold "Usage: "
    echo "run.sh <mode> "
    echo "    <mode> - one of 'install' or 'uninstall'"
    echo "      - 'install' - install Fabric dependencies - i.e., containernet (and dependencies) for Fabric-scenario"
    echo "      - 'uninstall' - uninstall Fabric dependencies - i.e., containernet dependencies for Fabric-scenario"
    echo "  deps.sh -h (print this message)"

}


function install() {

    echo "###################################"
    echo "Installing Fabric Dependencies"
    echo "###################################"

    sudo apt update && sudo apt install -y curl wget ansible git aptitude python3-pip
    sudo python3.8 -m pip install -U "docker<=4.1.0" cffi pexpect

    # sudo usermod -aG docker $USER

    echo "###################################"
    echo "Downloading Images for Monitoring Fabric: influxdb and graphana"
    echo "###################################"

    docker pull influxdb:latest
    docker pull grafana/grafana:latest

}

function uninstall() {

    echo "###################################"
    echo "Uninstalling Fabric Dependencies"
    echo "###################################"

}


case "$COMMAND" in
    install)
        install
        exit 0
        ;;  

    uninstall)
        uninstall
        exit 0
        ;;
    *)
        printHelp
        exit 1
esac
