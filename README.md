# To be included in the discussion
1) Algorand guarantees instant finalization so the oracle can share the information straight away. Ethereum does not have this property.. Think about it..

2)
# G1
# E-auction Smart Contract (implemented in Beaker)
## Problem
We want to implement a decentralised auction service in order to avoid that the seller and the auction participants must trust a centralised auctioneer that can deviate from the auction rules.
A reasonable solution to this trust problem consists into implementing a smart contract which resides on a public blockchain platform. The blockchain, and in particular the smart contract, impersonates the trusted third party, the auctioneer, therefore choosing the right blockchain platform is a core problem in a solution design. In fact different blockchain platforms have different characteristics (such as block finality, cryptographic agility, security or the costs in terms of fees) and allow the implementation of different kind of smart contract for auctions. When the assets which are going to be sold using the auction process lives inside a blockchain (for example a token controlled by a smart contract in Algorand or Ethereum), the easiest solution to arrange the auction consists into using a smart contract which lives in the same blockchain. However, in some cases it would be more profitable for the seller and auction participants to perform an auction on a different blockchain with different characteristics making them interoperate accordingly with the users needs.

Below we present our solution to the following problems: 
1) implementing a smart contract in Beaker which manages auctions on the Algorand blockchain 
2) design the necessary infrastructure to sell assets which live on Ethereum using the same Algorand smart contract. 

## Solution 
Our solution consists into creating two smart contracts in Beaker that allow the users of the Algorand network to perform auctions: one smart contract implements the auction with public bids and the other with blinded bids via the use of commitments.

Moreover, in order to augment the interoperability between blockchains and to allow the users of multiple networks to minimize their operation costs, we implemented an architecture which puts into communication the Algorand and Ethereum blockchains. In particular we allow a user to sell an asset living on Ethereum using an auction that is performed on Algorand. Therefore, the seller of an Ethereum asset can incentivate the participation to the auction process by choosing where to make the auction happen: on Ethereum using one of the smart contract ad hoc, otherwise they can use the architecture we present in our project making it happen on the Algorand blockchain.

-- copia la descrizione da future works se ce la si fa... --

# Smart Contract Specifications
**Requirements, Use cases, Functions ...
**
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

# State of the Art
**Relevant Smart Contracts, Papers
Posts in the developer portal ...**
https://github.com/avolabs-io/nft-auction Ethereum flexible auction

E-commerce activities has become part of everyone daily life, as a consequence of the popularity of the Internet. One of the most used e-commerce activities are e-auctions, where the auction participants can send their bid to buy a product over the Internet [2]. Centralised e-auction systems require the auction participants and the seller of the asset to trust the auction manager [3]. The e-auction managers may be dishonest and circumvent the auction rules in order to favour or penalise some auction participants. A solution to this trust problem, (which is: requiring the participants to trust a possibly dishonest third party), consists into considering as "the trusted third party" blockchain platforms that support the creation of smart contracts, such as Ethereum or Algorand. In this way the trust do not resides on a centralised third party but on the network of a public blockchain.

In literature there exist multiple kind of auction: for example in [3] the authors classify the auction models in the following macro-cathegories according to how the bidding process takes place: notarized bidding, deposited bidding, committed bidding and confidential bidding. Basically, the **notarized bidding** is the most simple and insecure auction model and only requires the contract to record the participant bids on the blockchain. The **deposited bidding** requires the participants to send to the smart contract the amount of native cryptocurrency that one is willing to bid in a completely transparent fashion so that everyone can see in real time each other bids. The **committed bidding** auction aims to hide in a first moment the participants bidded amount and to let them reveal it only once the bidding time has expired. The smart contract verifies that the revealed amount corresponds with the committed one.


Taking transactions on blockchain may be quite expensive, moreover the costs may vary through the time according to the price of the native criptocurrencies of the blockchain platforms. Not only the price required to launch an auction can vary through time, but also it is different according to the platform that implements the auction smart contract:

# Technical Challenges
Beyond the state of the art

Implementare in Beaker che è uno strumento nuovo e poco documentato.


# Future Works
We will refer to the user who want to sell an object using the auction smart contract with the name "seller".
When the seller wants to sell something it must open an auction.
The users who are willing to buy that object are referred to as "bidders" or "participants" and must send a bid to the smart contract according to the smart contract rules.

## Features:
We present a smart contract which allows the blockchain users to create and customize an auction.
We already have created two smart contracts that allow the seller to:

1. require the bids to be public and accessible to anyone as soon as they are sent to the smart contract;
2. require the bids to be committed to in a way that once the bidding process ends, the bidders open their commitment and the winner is revealed.


As future works we include the following features:
### Auction participants

1) the auction is accessible to anyone in the network: there is no control on the accounts that send bids to the smart contract.
2) only some accounts, selected by the seller, can take part to the auction. The seller **S** sends off-chain to each users **U** (who wants to allow to participate to the auction) the `authorisation data` which consists of: the signature with its secret key of the address `add_u` of the user and the identifier `id` of the auction: `( sk_s, add_u||id , sig(sk_s, add_u||id) )`. 
    
The user authorised to participate can send a bid to the smart contract giving as input (at least) the amount of money willing to spend (either committed or not) together with the authorisation data received by the seller off-chain. The smart contract will accept its bid only if the signature of the user account concatenated to the auction id verifies using the public key of the seller.
 

### Number of bids

1. every account can make a single bid during the auction process;
2. every account can make a number of bids equal to the number of auction token in their possess. This mechanism is inspired by the sortition mechanism used in Algorand consensus protocol. The more token one user is in possess of, the higher is the number of commitments that it can send to the smart contract. When the 


### Management of ties
We have implemented a mechanism which manages the ties which is: among the people who mead the highest bid, in case of ties the one which wins the auction is the first who revealed the commitment (according to the opening transaction list included in the Algorand blocks). Even if this approach is coherent with the smart contract that accepts only public bids, this mechanism incentivise the participants to pay an higher fee to the network in order to have their opening transaction included in a block as soon as possible. 

To fix this problem one could use the the random beacon used in the Algorand consensus protocol and sign it using its own secret key. If every participant `p` signs  the same random value `r` computing `sig_p=sign(r,sk_p)` it is possible to randomly select the winner of the auction in case of ties choosing as winner the participant `w` such that `sig_w<sig_p` for each participant `p` who is involved in the tie. This 


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







## Bibliography
[1] Chen, Yi-Hui, Shih-Hsin Chen, and Iuon-Chang Lin. "Blockchain based smart contract for bidding system." 2018 IEEE International Conference on Applied System Invention (ICASI). IEEE, 2018.

[2] Omar, Ilhaam A., et al. "Implementing decentralized auctions using blockchain smart contracts." Technological Forecasting and Social Change 168 (2021): 120786.

[3] Mogavero, Francesco, et al. "The Blockchain Quadrilemma: When Also Computational Effectiveness Matters." 2021 IEEE Symposium on Computers and Communications (ISCC). IEEE, 2021.

## Useful Link

[L1] https://gitlab.com/quadrilemma/quadrilemma
