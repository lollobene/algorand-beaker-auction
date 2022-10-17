// requires algosdk@1.6.1 or higher

const algosdk = require("algosdk");
const { sleep } = require("../../../ethereum/scripts/utils");

const indexer_token = "";
const indexer_server = "http://localhost";
const indexer_port = 8980;

const indexerClient = new algosdk.Indexer(
  indexer_token,
  indexer_server,
  indexer_port
);

// /indexer/python/SearchTransactionsNote.js
async function loadTxns(note = "END_AUCTION", appID = 0) {
  const enc = new TextEncoder();
  let enc_note = enc.encode(note);
  let limit = 1;
  let s = Buffer.from(enc_note).toString("base64");
  let transactionInfo = await indexerClient
    .searchForTransactions()
    .limit(limit)
    .applicationID(appIP)
    .notePrefix(s)
    .do();
  tx = transactionInfo.transactions[0];
  return tx;
}

async function fetchTxns(appID) {
  let tx = undefined;
  while (!tx) {
    try {
      tx = await loadTxns("END_AUCTION", appID);
      if (tx) console.log("Tx found", JSON.stringify(tx, undefined, 2));
      await sleep(1000);
    } catch (e) {}
  }
  return tx;
}

module.exports = { fetchTxns };
