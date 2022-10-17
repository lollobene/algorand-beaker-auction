const Web3Utils = require("web3-utils");
const { NFT } = require("./web3");

async function mint(from, to) {
  try {
    const txReceipt = await NFT.methods.safeMint(to).send({ from: from });
    const hexNumber = txReceipt.events.Transfer.raw.topics.pop();
    const tokenId = Web3Utils.hexToNumber(hexNumber);
    return tokenId;
  } catch (error) {
    return error;
  }
}

async function approve(from, to, tokenId) {
  return await NFT.methods.approve(to, tokenId).send({ from: from });
}

module.exports = {
  mint,
  approve,
};
