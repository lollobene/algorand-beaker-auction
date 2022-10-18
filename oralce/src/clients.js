const algosdk = require("algosdk");

// Connect your client
const sandboxToken =
  "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
const algodServer = "http://localhost";
const algodPort = 4001;
let sandboxClient = new algosdk.Algodv2(sandboxToken, algodServer, algodPort);

module.exports = { sandboxClient };
