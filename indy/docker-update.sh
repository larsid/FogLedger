#!/bin/bash 

COMMAND=$1

function printHelp() {
    echo "$COMMAND - $@"
    echo_bold "Usage: "
    echo "run.sh <mode> "
    echo "    <mode> - one of 'update'"
    echo "      - 'update IMAGE_NAME' - updat docker dependencies - i.e., containernet (and dependencies) for fogbed"
    echo "  docker-update.sh -h (print this message)"

}





upgradeDockerImages() {
  IMAGE_NAME=$1
  echo "========================================================="
        echo "==> Upgrading Docker Images to run in containernet: $IMAGE_NAME"
        echo "========================================================="
        echo
        docker run -ti --name $IMAGE_NAME $IMAGE_NAME /bin/sh -c 'apk add --no-cache iputils bash'
        docker commit $IMAGE_NAME $IMAGE_NAME
        docker commit --change "CMD /bin/bash" $IMAGE_NAME $IMAGE_NAME
        echo "-- Committed docker image: $IMAGE_NAME --"
        # docker stop -t0 $IMAGE_NAME
        docker rm $IMAGE_NAME 

}



function update() {
  echo "$1"
  upgradeDockerImages $1 
   
}


case "$COMMAND" in
    update)
        update $2
        exit 0
        ;;
    *)
        printHelp
        exit 1
esac