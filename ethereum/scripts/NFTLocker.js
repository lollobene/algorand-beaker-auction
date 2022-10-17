const { NFTLocker, NFT } = require("./web3");

async function approve(from, to, tokenId) {
  return await NFT.methods.approve(to, tokenId).send({ from: from });
}

async function lockNFT(from, nftAddress, tokenId, releaseTime) {
  try {
    return await NFTLocker.methods
      .lock(nftAddress, tokenId, releaseTime)
      .send({ from: from });
  } catch (error) {
    console.error(error);
    return undefined;
  }
}

async function setWinner(from, winnerAddres) {
  return await NFTLocker.methods.setWinner(winnerAddres).send({ from: from });
}

async function unlockNFT(from, nftAddress, tokenId) {
  return await NFTLocker.methods
    .unlock(nftAddress, tokenId)
    .send({ from: from });
}

module.exports = {
  approve,
  lockNFT,
  unlockNFT,
  setWinner,
};
