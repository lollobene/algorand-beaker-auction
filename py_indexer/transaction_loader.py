import json
import base64
# requires Python SDK version 1.3 or higher
from algosdk.v2client import indexer

note_prefix = 'showing prefix'.encode()
flag = True

def is_supported_transaction(transaction):
  return True

while flag :
  # instantiate indexer client
  myindexer = indexer.IndexerClient(indexer_token="", indexer_address="http://localhost:8980")

  response = myindexer.search_transactions(note_prefix=note_prefix)
  transactions = response["transactions"]
  
  numtx = len(transactions)
  if (numtx > 0):
    # Pretty Printing JSON string
    # print(json.dumps(transactions, indent=2, sort_keys=True))
    valid_txns = filter(is_supported_transaction, transactions)
    
