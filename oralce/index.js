const { lock, approve } = require("../ethereum/scripts/index");
const { loadEvents } = require("../ethereum/scripts/events");
const { fetchTxns } = require("../indexer/src/algo/txnLoader");

let tokenId = 2;

async function main() {
  // ORACOLO:parte script ascolto su ethereum
  loadEvents();

  // UTENTE AUTOMATIZZATO: parte script che blocca NFT sul locker contract di ethereum
  await approve(tokenId);
  await lock(tokenId);

  // ORACOLO:lo script in ascolta legge evento di lock da ethereum blockchain

  // ORACOLO: fa parire script creazione asta e inizio asta su algorand

  // ORACOLO:parte script ascolto su algorand
  //fetchTxns(appId);

  // AUTENTI AUTOMATIZZATI: parte script asta automatizzata

  // finisce asta

  // ORACOLO: lo script in ascolto legge tx di fine asta da algorand blockchain

  // ORACOLO: parte script che setta winner sul locker contract di ethereum

  // AUTENTE AUTOMATIZZATO: parte script che ritra NFT
}

main();
