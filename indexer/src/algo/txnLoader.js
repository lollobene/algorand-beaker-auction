// requires algosdk@1.6.1 or higher

const algosdk = require("algosdk");

const indexer_token = "";
const indexer_server = "http://localhost";
const indexer_port = 8980;

const indexerClient = new algosdk.Indexer(
  indexer_token,
  indexer_server,
  indexer_port
);

// /indexer/python/SearchTransactionsNote.js
async function loadTxns() {
  const enc = new TextEncoder();
  let note = enc.encode("START_AUCTION");
  let limit = 1;
  let s = Buffer.from(note).toString("base64");
  let transactionInfo = await indexerClient
    .searchForTransactions()
    .limit(limit)
    .notePrefix(s)
    .do();
  console.log(
    "Information for Transaction search: " +
      JSON.stringify(transactionInfo, undefined, 2)
  );
}

module.exports = loadTxns;
