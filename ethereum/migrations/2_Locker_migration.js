const NFTLocker = artifacts.require("NFTLocker");
// const configuration = require("../config.js");

module.exports = function (deployer, network) {
  // const config = configuration[network];
  deployer.deploy(
    NFTLocker
    // config.subscriptionId,
    // config.vrfCoordinator,
    // config.keyHash
  );
};
