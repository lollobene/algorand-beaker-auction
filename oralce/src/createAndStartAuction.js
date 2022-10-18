const { isTransactionWithSigner } = require("algosdk");
const algosdk = require("algosdk");
const fs = require("fs");
const path = require("path");
const { loadAccountsFromMnemonic } = require("./account");
const {
  compileTealPrograms,
  getAppAddress,
  getContractABI,
  getMethodByName,
} = require("./smartContract");
const {
  createApplicationDeployTxn,
  signTxn,
  sendSignedTxn,
  createApplicationCallTxn,
  createSignedPaymentTxn,
  createAssetCreationTxn,
  createUnsignedPaymentTxn,
  createAtomicTransaction,
  executeAtomicTransaction,
} = require("./transaction");
const { createAsset } = require("./utils");
require("dotenv").config();

const ALGO = 1000000;
const MICRO_ALGO = 1000;

let appId;
let appAddress;

const { governor, bidder1, bidder2 } = loadAccountsFromMnemonic();

const sk =
  "CdZA2W4m0tMM/Scs5YPdCkbm1TwuQukdZLKdumJgtJPqiT/AHPssn1jADmk04t9IIElPwOkwGnXGQqrwmInmXw==";
governor.sk = new Uint8Array(Buffer.from(sk, "base64"));
governor.addr = "5KET7QA47MWJ6WGABZUTJYW7JAQEST6A5EYBU5OGIKVPBGEJ4ZP2NBGUTI";

const governorSigner = algosdk.makeBasicAccountTransactionSigner(governor);
const approval = readFile("approval.teal");
const clear = readFile("clear.teal");
const jsonContract = readFile("contract.json");
const auctionContract = getContractABI(jsonContract);

async function createAuction() {
  try {
    console.log("Smart contract creation and deploy");

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
      const res = await createAsset(governor.addr, governor.sk, "DummyAsset");
      console.log("Asset created: ", res["asset-index"]);
      const pTxn = await createUnsignedPaymentTxn(
        governor.addr,
        appAddress,
        ALGO,
        "START_AUCTION"
      );
      const methodCall = {
        appID: appId,
        method: getMethodByName(auctionContract, "setup"),
        sender: governor.addr,
        methodArgs: [
          { txn: pTxn, signer: governorSigner },
          ALGO,
          res["asset-index"],
          10,
          100,
        ],
        signer: governorSigner,
      };
      const atc = await createAtomicTransaction(
        undefined,
        undefined,
        methodCall,
        governorSigner
      );
      //const acTxn = await createApplicationCallTxn(governor.addr, appId, args);

      const atcRes = await executeAtomicTransaction(atc);
      console.log("Auction started at round ", atcRes["confirmedRound"]);
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
