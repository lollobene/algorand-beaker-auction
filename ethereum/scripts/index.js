const NFTLocker = require("./NFTLocker");
const NFT = require("./NFT");
const { web3, addresses, NFTLockerAddress, NFTAddress } = require("./web3");
const { loadEvents } = require("./events");
const { setTimeout } = require("timers/promises");

const [governor, seller, winner] = addresses;

// setting the release time after 2 minutes (120 milliseconds)
const releaseTime = Math.floor(Date.now() / 1000 + 120);
async function main() {
  const chainId = await web3.eth.getChainId();
  console.log("Connected to Chain ", chainId);

  //const tokenId = await mint();

  let tokenId = 1;
  await approve(tokenId);

  await lock(tokenId);

  await setWinner();

  await unlock(tokenId);
}

async function mint() {
  // Minting the NFT and sending it to the seller.
  // Here we assume that the NFT contract is already deployed by the Governor
  console.log("Minting NFT");
  const tokenId = await NFT.mint(governor, seller);
  console.log("NFT ID: ", tokenId);
  return tokenId;
}

async function approve(tokenId) {
  console.log("Approving the Locker contract");
  await NFT.approve(seller, NFTLockerAddress, tokenId);
  console.log("Locker contract approved");
}

async function lock(tokenId) {
  console.log("Locking the NFT");
  await NFTLocker.lockNFT(seller, NFTAddress, tokenId, releaseTime);
  console.log("NFT locked");
}

async function setWinner() {
  console.log("Setting winner");
  await NFTLocker.setWinner(governor, winner);
  console.log("Winner set");
}

async function unlock(tokenId) {
  console.log("Unlocking NFT");
  console.log("Waiting...");
  await setTimeout(120000);
  await NFTLocker.unlockNFT(winner, NFTAddress, tokenId);
  console.log("NFT unlocked");
}

//main();

module.exports = { lock, approve };
