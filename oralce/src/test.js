const { createAuction, startAuction } = require("./createAndStartAuction");

async function main() {
  const { appId, appAddress } = await createAuction();
  console.log(appId, appAddress);

  await startAuction();
}

main();
