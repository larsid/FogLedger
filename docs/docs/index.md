# FogLedger

It's important to be familiar with [Fogbed](https://github.com/larsid/fogbed). Fogbed is a framework for rapid prototyping of fog components in virtualized environments. It's based on Mininet network emulator with Docker container instances as fog virtual nodes. Fogbed is designed to meet the postulated requirements of low cost, flexible setup and compatibility with real world technologies.

The FogLedger is a plugin for Fogbed. It allows you to emulate a fog network with distributed ledgers.

Currently, FogLedger has suport for Hyperledger Indy. It's a distributed ledger, purpose-built for decentralized identity. It provides tools, libraries, and reusable components for creating and using independent digital identities rooted on blockchains or other distributed ledgers so that they are interoperable across administrative domains, applications, and any other silo. Indy is interoperable with other blockchains or can be used standalone powering the decentralization of identity.

With FogLedger you can create a network of nodes running Hyperledger Indy. You can also create a network of nodes running Hyperledger Indy. A emulation can have multiple networks of nodes running different distributed ledgers. FogLedger is a plugin for Fogbed, so you can use all the features of Fogbed to emulate your fog network, such as in the Figure below.


Future work includes support for other distributed ledgers, such as Hyperledger Fabric, Hyperledger Besu, IOTA Tangle.

The project code is available at [Github](https://github.com/larsid/FogLedger). 

Docker images are available at [Docker Hub](https://hub.docker.com/r/larsid).
