const txnLoader = require("./src/algo/txnLoader");

async function main() {
  try {
    const txns = await txnLoader();
  } catch (error) {
    console.error(error);
  }
}

main();
