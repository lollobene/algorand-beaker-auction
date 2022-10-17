const Web3 = require("web3");
const HDWalletProvider = require("@truffle/hdwallet-provider");
require("dotenv").config();

const NFTLockerABI = require("../build/contracts/NFTLocker.json").abi;

const NFTABI = require("../build/contracts/DummyNFT.json").abi;

const NFTLockerAddress = process.env.LOCKER_ADDRESS;
const NFTAddress = process.env.NFT_ADDRESS;
const mnemonic = process.env.MNEMONIC;

const provider = new HDWalletProvider(mnemonic, process.env.RPC);
const addresses = provider.getAddresses();

const web3 = new Web3(provider);

const NFTLocker = new web3.eth.Contract(NFTLockerABI, NFTLockerAddress);

const NFT = new web3.eth.Contract(NFTABI, NFTAddress);

module.exports = {
  web3,
  NFTLocker,
  NFT,
  addresses,
  NFTAddress,
  NFTLockerAddress,
};
