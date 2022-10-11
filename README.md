# Smart contract for auction

We will refer to the user who want to sell an object using the auction smart contract with the name "seller".
When the seller wants to sell something it must open an auction.
The users who are willing to buy that object are referred to as "bidders" or "participants" and must send a bid to the smart contract according to the smart contract rules.

## Features:
We present a smart contract which allows the blockchain users to create and customize an auction. 

### Bidding visibility:
The seller may:

1.  require the bids to be public and accessible to anyone as soon as they are sent to the smart contract;
2. require the bids to be committed to in a way that once the bidding process ends, the bidders open their commitment and the winner is revealed.



### Auction participants

1. the auction is accessible to anyone in the network: there is no control on the accounts that send bids to the smart contract.
2. only some accounts, selected by the seller, can take part to the auction. The seller **S** sends off-chain to each users **U** (who wants to allow to participate to the auction) the `authorisation data` which consists of: the signature with its secret key of the address `add_u` of the user and the identifier `id` of the auction: `( sk_s, add_u||id , sig(sk_s, add_u||id) )`. 
    
    The user authorised to participate can send a bid to the smart contract giving as input (at least) the amount of money willing to spend (either committed or not) together with the authorisation data received by the seller off-chain. The smart contract will accept its bid only if the signature of the user account concatenated to the auction id verifies using the public key of the seller.
 

### Number of bids

1. every account can make a single bid during the auction process;
2. every account can make a number of bids equal to the number of auction token in their possess.


## Bridge between Algorand and Ethereum

We want to implement a mechanism that allows a user to sell an asset which lives on the Ethereum blockchain opening an auction on the blockchain of Algorand. Every actor must own an address both in the Algorand and in the Ethereum blockchain. The change of property of the asset happens in the Ethereum blockchain and the payment is performed in Algo in the Algorand blockchain.

### Components
We need two smart contracts, one implemented on Algorand **SC<sub>A </sub>** and one on Ethereum **SC<sub>E</sub>**. We need an oracle **O**

**SC<sub>E</sub>** manages:

1. the request of opening of a new auction from an account to sell an asset it owns;
3. the change of property of the same asset on the Ethereum blockchain assigning the ownership of the asset to the winner of the auction.



**SC<sub>A</sub>** manages:

1. opens a new auction whenever a new opening is published on smart contract **SC<sub>E</sub>** thanks to the communication of **O**. 
3. declares the auction winner according to the auction rules and this information is red by **O** who share the information with the Ethereum network

**O** manages:

1. whenever an asset is bounded to **SC<sub>E</sub>**, it triggers the creation of a new auction via **SC<sub>A/<sub>**.
3. when the auction has a winner, it triggers the creation of a transaction to **SC<sub>E</sub>** that (later) will allow the winner to redeem the asset.


### Workflow
The workflow is the following:

- the seller **S** sends a transaction to the smart contract **SC<sub>E</sub>** offering it for sale;
- the smart contract registers the transaction: the sale is identified by the transaction id `tr_id` and the seller address `add_s`;
- the oracle **O** detects the opening of a new sale and send a transaction to **SC<sub>A</sub>** instructing the opening of a new auction associated to `tr_id`;
- all the auction participants can send their bids to the smart contract **SC<sub>A</sub>**: in the bidding process, each participant `p` will include an hidden secret `h_p(s_p)` which will be used to bind the accounts possessed by each participant on the Algorand and Ethereum blockchain;
- the smart contract **SC<sub>A</sub>** eventually closes the bidding phase and announces the winner;
- the oracle **O** detects the end of the auction phase and sends a transaction to **SC<sub>E</sub>** containing a reference to the hidden secret `h_w(s_w)` of the winner `w`.
- the winner `w` discloses its secret `s_w` (which is bounded to its Ethereum public key via the function `h_w` that it previously used) and becomes the owner of the asset.
- the seller uses the secret  `s_w` published by the winner `w` to redeem the transaction in Algo on the Algorand blockchain.

## Development Environment

### Install Sandbox

Install the [sandbox](https://github.com/algorand/sandbox) to start a local private node and start it with the `dev` configuration.

If you're in the sandbox directory run:

```bash
./sandbox up dev
```

### Clone repository

Next, clone this repository and cd to the root directory.

### Setup Virtual Environment

Create a virtual environment inside the project directory. 
#### This project requires Python 3.10.

```bash
python3 -m venv venv
```

Activate virtual environment.

```bash
source ./venv/bin/activate
```

requirements.txt file contains all of the required dependencies and packages. Install them in your virtual environment by running:

```bash
pip install -r requirements.txt
```

Check all dependencies and packages install in your virtual environment by running:

```bash
pip list
```

Run the client from auction directory
```bash
python auction.py
```
