const algosdk = require("algosdk");
require("dotenv").config();

const algodToken =
  "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
const algodServer = "http://localhost";
const algodPort = 4001;
let algodClient = new algosdk.Algodv2(algodToken, algodServer, algodPort);

let params = await algodClient.getTransactionParams();
params.fee = algosdk.ALGORAND_MIN_TX_FEE;
params.flatFee = true;

const receiver = "HZ57J3K46JIJXILONBBZOHX6BKPXEM2VVXNRFSUED6DKFD5ZD24PMJ3MVA";
const enc = new TextEncoder();
const note = enc.encode("Hello World");
let amount = 1000000;
let sender = myAccount.addr;

let txn = algosdk.makePaymentTxnWithSuggestedParamsFromObject({
  from: sender,
  to: receiver,
  amount: amount,
  note: note,
  suggestedParams: params,
});

let signedTxn = txn.signTxn(myAccount.sk);
let txId = txn.txID().toString();
console.log("Signed transaction with txID: %s", txId);

// Submit the transaction
await algodClient.sendRawTransaction(signedTxn).do();
