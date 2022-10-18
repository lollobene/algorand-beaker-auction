const algosdk = require("algosdk");
const { sandboxClient } = require("./clients");

async function createUnsignedPaymentTxn(from, to, amount, note = "") {
  try {
    // Construct the transaction
    let params = await sandboxClient.getTransactionParams().do();
    // comment out the next two lines to use suggested fee
    params.fee = algosdk.ALGORAND_MIN_TX_FEE;
    params.flatFee = true;

    const enc = new TextEncoder();
    const encNote = enc.encode(note);

    let txn = algosdk.makePaymentTxnWithSuggestedParamsFromObject({
      from: from,
      to: to,
      amount: amount,
      note: encNote,
      suggestedParams: params,
    });
    return txn;
  } catch (err) {
    console.log(err);
  }
}

async function createSignedPaymentTxn(sk, from, to, amount, note = "") {
  try {
    // Sign the transaction
    txn = await createUnsignedPaymentTxn(from, to, amount, note);
    let signedTxn = txn.signTxn(sk);
    let txId = txn.txID().toString();
    //console.log("Signed transaction with txID: %s", txId);
    return signedTxn;
  } catch (error) {
    console.log(error);
  }
}

async function createApplicationDeployTxn(
  from,
  approvalProgram,
  clearProgram,
  args,
  globalBytes,
  globalInts,
  localBytes,
  localInts
) {
  const sp = await sandboxClient.getTransactionParams().do();

  const txn = algosdk.makeApplicationCreateTxnFromObject({
    from: from,
    approvalProgram: approvalProgram,
    clearProgram: clearProgram,
    numGlobalByteSlices: globalBytes,
    numGlobalInts: globalInts,
    numLocalByteSlices: localBytes,
    numLocalInts: localInts,
    appArgs: args,
    suggestedParams: sp,
  });
  return txn;
}

async function createApplicationCallTxn(from, appId, args) {
  const sp = await sandboxClient.getTransactionParams().do();
  const ac_txn = algosdk.makeApplicationCallTxnFromObject({
    from: from,
    appIndex: appId,
    appArgs: args,
    suggestedParams: sp,
  });
  return ac_txn;
}

async function signTxn(sk, txn) {
  const signed = txn.signTxn(sk);
  return signed;
}

async function sendSignedTxn(signedTxn) {
  try {
    // Submit the transaction
    const { txId } = await sandboxClient.sendRawTransaction(signedTxn).do();
    // Wait for confirmation
    let confirmedTxn = await algosdk.waitForConfirmation(
      sandboxClient,
      txId,
      2
    );
    return confirmedTxn;
  } catch (error) {
    console.log(error);
  }
}

function getTxnNote(confirmedTxn) {
  let string = new TextDecoder().decode(confirmedTxn.txn.txn.note);
  return string;
}

module.exports = {
  createSignedPaymentTxn,
  createApplicationDeployTxn,
  createApplicationCallTxn,
  sendSignedTxn,
  signTxn,
  getTxnNote,
};
