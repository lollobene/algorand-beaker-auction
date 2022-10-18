const algosdk = require("algosdk");
const { sandboxClient } = require("./clients");

const { encodeAddress, getApplicationAddress } = require("algosdk");

const encoder = new TextEncoder();

async function compileTealPrograms(approval, clear) {
  const approvalRes = await sandboxClient
    .compile(encoder.encode(approval))
    .do();
  // Convert the result of compilation from base64 to bytes
  const approvalProgram = new Uint8Array(
    Buffer.from(approvalRes["result"], "base64")
  );

  const clearRes = await sandboxClient.compile(encoder.encode(clear)).do();
  const clearProgram = new Uint8Array(
    Buffer.from(clearRes["result"], "base64")
  );

  return { approvalProgram, clearProgram };
}

function getAppAddress(appId) {
  return getApplicationAddress(appId);
}

module.exports = { compileTealPrograms, getAppAddress };
