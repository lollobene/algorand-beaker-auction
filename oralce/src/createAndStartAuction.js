const algosdk = require("algosdk");
const fs = require("fs");
const path = require("path");
const { loadAccountsMnemonic } = require("./account");
const { compileTealPrograms, getAppAddress } = require("./smartContract");
const {
  createApplicationDeployTxn,
  signTxn,
  sendSignedTxn,
  createApplicationCallTxn,
  createSignedPaymentTxn,
} = require("./transaction");
require("dotenv").config();

const ALGO = 1000000;
const MICRO_ALGO = 1000;

let appId;
let appAddress;

const { governor, bidder1, bidder2 } = loadAccountsMnemonic();

const sk =
  "CdZA2W4m0tMM/Scs5YPdCkbm1TwuQukdZLKdumJgtJPqiT/AHPssn1jADmk04t9IIElPwOkwGnXGQqrwmInmXw==";
governor.sk = new Uint8Array(Buffer.from(sk, "base64"));
governor.addr = "5KET7QA47MWJ6WGABZUTJYW7JAQEST6A5EYBU5OGIKVPBGEJ4ZP2NBGUTI";

async function createAuction() {
  try {
    console.log("Smart contract creation and deploy");

    const approval = readFile("approval.teal");
    const clear = readFile("clear.teal");

    const { approvalProgram, clearProgram } = await compileTealPrograms(
      approval,
      clear
    );

    const acTxn = await createApplicationDeployTxn(
      governor.addr,
      approvalProgram,
      clearProgram,
      [],
      2,
      4,
      0,
      0
    );

    const signedAcTxn = await signTxn(governor.sk, acTxn);
    const confirmation = await sendSignedTxn(signedAcTxn);
    appId = confirmation["application-index"];
    appAddress = getAppAddress(appId);

    return { appId, appAddress };
  } catch (error) {
    console.log(error);
  }
}

async function startAuction() {
  if (appId) {
    try {
      const pTxn = await createSignedPaymentTxn(
        governor.sk,
        governor.addr,
        appAddress,
        1 * ALGO,
        "START_AUCTION"
      );
      const args = [pTxn, 1 * ALGO, asaTxn];
      const acTxn = await createApplicationCallTxn(governor.addr, appId, args);
      const signedAcTxn = await signTxn(governor.sk, acTxn);
      const confirmation = await sendSignedTxn(signedAcTxn);
      console.log("Auction started at round ", confirmation["confirmed-round"]);
    } catch (error) {
      console.log(error);
    }
  } else {
    throw Error("Application not created yet!");
  }
}

function readFile(filename) {
  const filePath = path.join(__dirname, "..", "artifacts", filename);
  const file = fs.readFileSync(filePath);
  return file;
}

module.exports = { createAuction, startAuction };
