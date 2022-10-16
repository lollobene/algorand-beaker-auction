const fs = require("fs");
const { web3, NFTLocker } = require("./web3");
const { sleep } = require("./utils");

const locked = {};

let lastBlock = readBlockNumber();

function readBlockNumber() {
  try {
    const buffer = fs.readFileSync("blocknumber.json");
    const data = JSON.parse(buffer);
    console.log("Starting block", data.lastBlock);
    return data.lastBlock;
  } catch (error) {
    console.error(error);
    return undefined;
  }
}

function writeBlockNumber() {
  try {
    fs.writeFileSync(
      "blocknumber.json",
      JSON.stringify({ lastBlock: lastBlock })
    );
    // file written successfully
  } catch (err) {
    console.error(err);
  }
}

async function processEvents(events) {
  let edit = false;
  let token;
  let tokenId;
  let winner;
  for (const event of events) {
    const data = event.returnValues;
    if (!data) continue;
    try {
      switch (event.event) {
        case "Winner":
          winner = data.winner;
          console.log("WINNER: ", winner);
          break;
        case "TokenLocked":
          token = data.token;
          tokenId = data.tokenId;
          console.log("LOCKED: ", tokenId, token);
          break;
        case "TokenUnlocked":
          token = data.token;
          tokenId = data.tokenId;
          console.log("UNLOCKED: ", tokenId, token);
          break;
      }
    } catch (e) {
      console.log(e);
    }
  }
}

async function fetchEvents(checkedBlock) {
  let log = 10;
  while (true) {
    try {
      lastBlock = Math.min(
        parseInt(checkedBlock) + 4000,
        await web3.eth.getBlockNumber()
      );
      await processEvents(
        await NFTLocker.getPastEvents("allEvents", {
          fromBlock: checkedBlock,
          toBlock: lastBlock,
        })
      );
      checkedBlock = lastBlock + 1;
    } catch (e) {
      console.log(e);
      await sleep(10000);
    }
    log--;
    if (log <= 0) {
      console.log(checkedBlock);
      log = 10;
    }
    await sleep(100);
  }
}

fetchEvents(lastBlock);

process.on("SIGINT", () => {
  console.log("Caught interrupt signal");
  writeBlockNumber();
  process.exit();
});

module.exports = {
  fetchEvents,
};
