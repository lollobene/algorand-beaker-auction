import json
import base64
# requires Python SDK version 1.3 or higher
from algosdk.v2client import indexer

note_prefix = 'showing prefix'.encode()

# instantiate indexer client
myindexer = indexer.IndexerClient(indexer_token="", indexer_address="http://localhost:8980")

# /indexer/python/search_transactions_min_amount.py
response = myindexer.search_transactions(limit=10)

transactions = response["transactions"]
numtx = len(transactions)

if (numtx > 0):
  # Pretty Printing JSON string
  print(json.dumps(transactions, indent=2, sort_keys=True))