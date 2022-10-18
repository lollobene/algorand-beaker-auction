const {
  createApplicationDeployTxn,
  signTxn,
  sendSignedTxn,
  createApplicationCallTxn,
  createSignedPaymentTxn,
  createAssetCreationTxn,
  createUnsignedPaymentTxn,
} = require("./transaction");

async function createAsset(addr, sk, name) {
  const asaTxn = await createAssetCreationTxn(addr, name, 1, 0);
  const asaTxnSigned = signTxn(sk, asaTxn);
  const res = await sendSignedTxn(asaTxnSigned);
  return res;
}

module.exports = { createAsset };
