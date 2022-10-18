const algosdk = require("algosdk");
const { sandboxClient } = require("./clients");

async function createUnsignedPaymentTxn(from, to, amount, note = "") {
  // Construct the transaction
  let params = await sandboxClient.getTransactionParams().do();
  // comment out the next two lines to use suggested fee
  params.fee = algosdk.ALGORAND_MIN_TX_FEE;
  params.flatFee = true;

  const enc = new TextEncoder();
  const encNote = enc.encode(note);

  let txn = algosdk.makePaymentTxnWithSuggestedParams(
    from,
    to,
    amount,
    undefined,
    encNote,
    params
  );
  /*
  {
    from: from,
    to: to,
    amount: amount,
    note: encNote,
    suggestedParams: params,
  }*/
  return txn;
}

async function createSignedPaymentTxn(sk, from, to, amount, note = "") {
  // Sign the transaction
  txn = await createUnsignedPaymentTxn(from, to, amount, note);
  let signedTxn = txn.signTxn(sk);
  let txId = txn.txID().toString();
  //console.log("Signed transaction with txID: %s", txId);
  return signedTxn;
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

async function createAssetCreationTxn(from, name, amount, decimals) {
  const sp = await sandboxClient.getTransactionParams().do();

  const txn = algosdk.makeAssetCreateTxnWithSuggestedParamsFromObject({
    from: from,
    assetName: name,
    total: amount,
    decimals: decimals,
    manager: from, // The manager address should be your address (should be your address)
    freeze: from, // The address that may issue freeze/unfreeze transactions  (shouuld be your address)
    clawback: from, // The address that may clawback an asset  (should be your address)
    reserve: from, // The account that should be treated as `Reserve` for computing number of tokens in circulation (should be your address)
    unitName: "", // The unit name of the asset (can stay empty)
    assetURL: "", // The url of asset (can leave blank for this task, for an NFT this might be an IPFS uri)
    defaultFrozen: false, // Whether or not to have the asset frozen on xfer (can leave false)
    suggestedParams: sp,
  });
  return txn;
}

async function createAtomicTransaction(
  unsignedPaymentTransaction,
  assetTransferTransaction,
  methodCall,
  signer
) {
  const sp = await sandboxClient.getTransactionParams().do();
  const atc = new algosdk.AtomicTransactionComposer();
  if (unsignedPaymentTransaction) {
    const pTxnWs = {
      txn: unsignedPaymentTransaction,
      signer: signer,
    };
    atc.addTransaction(pTxnWs);
  }
  if (assetTransferTransaction) {
    const atTxnWs = {
      txn: assetTransferTransaction,
      signer: signer,
    };
    atc.addTransaction(atTxnWs);
  }
  if (methodCall) {
    methodCall.suggestedParams = sp;
    atc.addMethodCall(methodCall);
  }
  return atc;
}

async function executeAtomicTransaction(atc) {
  const res = await atc.execute(sandboxClient, 2);
  return res;
}

function signTxn(sk, txn) {
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
  createUnsignedPaymentTxn,
  createApplicationDeployTxn,
  createApplicationCallTxn,
  createAssetCreationTxn,
  createAtomicTransaction,
  sendSignedTxn,
  signTxn,
  getTxnNote,
  executeAtomicTransaction,
};
