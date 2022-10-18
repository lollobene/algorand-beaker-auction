const algosdk = require("algosdk");
require("dotenv").config();

function createAccount() {
  try {
    const account = algosdk.generateAccount();
    console.log("Account Address = " + account.addr);
    let account_mnemonic = algosdk.secretKeyToMnemonic(account.sk);
    console.log("Account Mnemonic = " + account_mnemonic);
    console.log("Account created. Save off Mnemonic and address");
    console.log("Add funds to account using the TestNet Dispenser: ");
    console.log("https://dispenser.testnet.aws.algodev.network/ ");
    return account;
  } catch (err) {
    console.log(err);
  }
}

function loadAccountsMnemonic() {
  const governorMnemonic = process.env.GOVERNOR_MNEMONIC_PHRASE;
  const bidder1Mnemonic = process.env.BIDDER1_MNEMONIC_PHRASE;
  const bidder2Mnemonic = process.env.BIDDER2_MNEMONIC_PHRASE;

  const governor = algosdk.mnemonicToSecretKey(governorMnemonic);
  const bidder1 = algosdk.mnemonicToSecretKey(bidder1Mnemonic);
  const bidder2 = algosdk.mnemonicToSecretKey(bidder2Mnemonic);

  return { governor, bidder1, bidder2 };
}

async function getAccountBalance(address, client) {
  let accountInfo = await client.accountInformation(address).do();
  console.log("Account balance: %d microAlgos", accountInfo.amount);
  return accountInfo.amount;
}

module.exports = { createAccount, loadAccountsMnemonic, getAccountBalance };
