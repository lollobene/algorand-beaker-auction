const { fetchTxns } = require("./src/algo/txnLoader");

async function main() {
  try {
    const tx = fetchTxns();
  } catch (error) {
    console.error(error);
  }
}

main();
