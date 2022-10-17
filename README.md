# G1
# E-auction Smart Contract in Algorand (implemented in Beaker) which communicates with Ethereum  
## Problem
We want to implement a decentralised auction service in order to avoid that the seller and the auction participants must trust a centralised auctioneer that can deviate from the auction rules.
A reasonable solution to this trust problem consists into implementing a smart contract which resides on a public blockchain platform. The blockchain, and in particular the smart contract, impersonates the trusted third party, the auctioneer, therefore choosing the right blockchain platform is a core problem in a solution design. In fact different blockchain platforms have different characteristics (such as block finality, cryptographic agility, security or the costs in terms of fees) and allow the implementation of different kind of smart contract for auctions. When the assets which are going to be sold using the auction process lives inside a blockchain (for example a token controlled by a smart contract in Algorand or Ethereum), the easiest solution to arrange the auction consists into using a smart contract which lives in the same blockchain. However, in some cases it would be more profitable for the seller and auction participants to perform an auction on a different blockchain with different characteristics making them interoperate accordingly with the users needs.

Below we present our solution to the following problems: 
1) implementing a smart contract in Beaker which manages auctions on the Algorand blockchain;
2) design the necessary infrastructure to sell assets which live on Ethereum using the same Algorand smart contract. 

## Solution 
Our solution consists into creating two smart contracts in Beaker that allow the users of the Algorand network to perform auctions: one smart contract implements the auction with public bids and the other with committed bids.

Moreover, in order to augment the interoperability between blockchains and to allow the users of multiple networks to minimize their operation costs, we designed an architecture which puts into communication the Algorand and Ethereum blockchains. In particular, we allow a user to sell an asset living on Ethereum using an auction that is performed on Algorand. Therefore, the seller of an Ethereum asset can incentivate the participation to the auction process by choosing where to make the auction happen: on Ethereum using one of the smart contract ad hoc (for example provided by Auctionity [L2]), otherwise they can use the architecture we present in our project making it happen on the Algorand blockchain.
In order to create the bridge between the Algorand and Ethereum blockchain we have implemented the following programs:

1) a smart contract implemented in Solidity **SC<sub>E</sub>** which lives in Ethereum and manages:

    1. the request of opening of a new auction from an account to sell an asset it owns;
    2. the change of property of the same asset on the Ethereum blockchain assigning the ownership of the asset to the winner of the auction.


2) a smart contract implemented in Beaker **SC<sub>A</sub>** which lives in Algorand and manages:

    1. the execution of the auction whenever a new asset is published and locked in the smart contract **SC<sub>E</sub>** thanks to the communication of **O**. 
    2. the declaration the auction winner according to the auction rules.


We designed an oracle **O** which manages the following:

1) whenever an asset is locked into *SC<sub>E</sub>, **O** triggers the creation of a new auction via **SC<sub>A</sub>**.
2) when the auction has a winner, it triggers the creation of a transaction to *SC<sub>E</sub>* that will allow the winner to redeem the asset.
 
**The oracle is still in the development for future release.**

# Smart Contract Specifications
**Requirements, Use cases, Functions ...
**

## Use cases
We present two smart contracts implemented in Beaker which allow the creation of a 
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

E-commerce activities has become part of everyone daily life, as a consequence of the popularity of the Internet. One of the most used e-commerce activities are e-auctions, where the auction participants can send their bid to buy a product over the Internet [2]. Centralised e-auction systems require the auction participants and the seller of the asset to trust the auction manager [3]. The e-auction managers may be dishonest and circumvent the auction rules in order to favour or penalise some auction participants. A solution to this trust problem, (which is: requiring the participants to trust a possibly dishonest third party), consists into considering as "the trusted third party" blockchain platforms that support the creation of smart contracts, such as Ethereum or Algorand. In this way the trust do not resides on a centralised third party but on the network of a public blockchain.

In literature there exist multiple kind of auction: for example in [3] the authors classify the auction models in the following macro-cathegories according to how the bidding process takes place: notarized bidding, deposited bidding, committed bidding and confidential bidding. Basically, the **notarized bidding** is the most simple and insecure auction model and only requires the contract to record the participant bids on the blockchain. The **deposited bidding** requires the participants to send to the smart contract the amount of native cryptocurrency that one is willing to bid in a completely transparent fashion so that everyone can see in real time each other bids. The **committed bidding** auction aims to hide in a first moment the participants bidded amount and to let them reveal it only once the bidding time has expired. The smart contract verifies that the revealed amount corresponds with the committed one and assigns the ownership of the asset to the participant who committed to and opened the highest bid. Finally **confidential bidding** allows the participants to encrypt their bids using the public key of the auctioneer so that at the end of the auction the bids of the loosing participants remain confidential.



Not every blockchain platform can support the implementation of the auction models described above: the reason behind it resides in the capabilities of the scripting language adopted by the blockchain platforms. For example Bitcoin with Bitcoin Script only allows the notarized bidding, Algorand, with Teal, allows the notarized bidding, the deposited bidding and the committed bidding, whereas in Ethereum it is possible to implement all of them [3]. However, due to the differences in the consensus protocol, transaction throughput, and costs in terms of fees, it might be more convenient to perform an aucton on a given platform rather than another. For example Ethereum allows the implementation of more privacy preserving smart contracts thank to the supported cryptographic functions but it is extremely more expensive than Algorand (see the table below to compare the prices of runs of smart contract implemented in [L1]). Also the block finality which in Algorand is immediate, in Ethereum may take tens of seconds. 


![table Megavero](https://user-images.githubusercontent.com/76473749/196223807-cad28190-6cca-49d4-8be9-e428ef89aee8.PNG)

For these reson, in some cases, if one have to sell an asset living in Ethereum it might be useful to have the possibility to open an auction on another platform, for instance, Algorand.  

# Technical Challenges
Developing in Beaker was very difficult given the little documentation available and few existing examples [L4],[L5],[L6],[L7],L[8],L[9],L[10]. In addition, the SDK for Javascript is still very cumbersome, this in fact precluded the possibility of making the oracle capable of communicating simultaneously with the Ethereum and Algorand blockchains.


# Future Works
## A more secure Bridge between Algorand and Ethereum

We want to implement a mechanism that allows a user to sell an asset which lives on the Ethereum blockchain opening an auction on the blockchain of Algorand. Every actor must own an address both in the Algorand and in the Ethereum blockchain. The change of property of the asset happens in the Ethereum blockchain and the payment is performed in Algo in the Algorand blockchain.

The workflow adopted in our project up to now is not very secure since the oracle is in full control of the exchange of communication between the two smart contracts. In order to reduce the power we give to the oracle, we could implement an atomic swap between the two blockchain. As you will see below, the oracle still moves information from a blockchain to the other, however, if the oracle stops working at a certain point, the asset will be returned to the seller and the payment in Algos will not be performed.

We recall that the entities involved are the two smart contracts, one implemented on Algorand **SC<sub>A </sub>** and one on Ethereum **SC<sub>E</sub>**,  and the oracle **O** described in section **Solution**. 

The workflow is the following:

- the seller **S** sends a transaction to the smart contract **SC<sub>E</sub>** offering it for sale;
- the smart contract registers the transaction: the sale is identified by the transaction id `tr_id` and the seller address `add_s`;
- the oracle **O** detects the opening of a new sale and send a transaction to **SC<sub>A</sub>** instructing the opening of a new auction associated to `tr_id`;
- all the auction participants can send their bids to the smart contract **SC<sub>A</sub>**: in the bidding process, each participant `p` will include an hidden secret `h_p(s_p)` which will be used to bind the accounts possessed by each participant on the Algorand and Ethereum blockchain;
- the smart contract **SC<sub>A</sub>** eventually closes the bidding phase and announces the winner;
- the oracle **O** detects the end of the auction phase and sends a transaction to **SC<sub>E</sub>** containing a reference to the hidden secret `h_w(s_w)` of the winner `w`.
- the winner `w` discloses its secret `s_w` (which is bounded to its Ethereum public key via the function `h_w` that it previously used) and becomes the owner of the asset.
- the seller uses the secret  `s_w` published by the winner `w` to redeem the transaction in Algo on the Algorand blockchain.

To hide the secret one can compute the hash of the concatenation of the secret and the user's account on Ethereum. In this way, when the winner of the auction is declared, it can disclose the secret binding it to the Ethereum account. Once the secret is revealed, the funds stored on the Algorand smart contract are moved to the seller. 


![workflow](https://user-images.githubusercontent.com/76473749/196230984-5004d471-b300-43af-9aa9-69f5aebb0072.PNG)



## Other future works
As future works it would be interesting to implement auction smart contracts that allow the seller to choose an auction model choosing among the following features: 

### Auction participants

1) the auction is accessible to anyone in the network: there is no control on the accounts that send bids to the smart contract.
2) only some accounts, selected by the seller, can take part to the auction. The seller **S** sends off-chain to each users **U** (who wants to allow to participate to the auction) the `authorisation data` which consists of: the signature with its secret key of the address `add_u` of the user and the identifier `id` of the auction: `( sk_s, add_u||id , sig(sk_s, add_u||id) )`. 
    
The user authorised to participate can send a bid to the smart contract giving as input (at least) the amount of money willing to spend (either committed or not) together with the authorisation data received by the seller off-chain. The smart contract will accept its bid only if the signature of the user account concatenated to the auction id verifies using the public key of the seller.
 

### Number of bids

1. every account can make a single bid during the auction process;
2. every account can make a number of bids equal to the number of auction token in their possess. This mechanism is inspired by the sortition mechanism used in Algorand consensus protocol. The more token one user is in possess of, the higher is the number of commitments that it can send to the smart contract. When the 


### Management of ties
We have implemented a mechanism which manages the ties which is: among the people who mead the highest bid, in case of ties the one which wins the auction is the first who revealed the commitment (according to the opening transaction list included in the Algorand blocks). Even if this approach is coherent with the smart contract that accepts only public bids, this mechanism incentivise the participants to pay an higher fee to the network in order to have their opening transaction included in a block as soon as possible. 

To fix this problem one could use the the random beacon [L3] used in the Algorand consensus protocol [4] and sign it using its own secret key. If every participant `p` signs  the same random value `r` computing `sig_p=sign(r,sk_p)` it is possible to randomly select the winner of the auction in case of ties choosing as winner the participant `w` such that `sig_w < sig_p` for each participant `p` who is involved in the tie. This 






## Bibliography
[1] Chen, Yi-Hui, Shih-Hsin Chen, and Iuon-Chang Lin. "Blockchain based smart contract for bidding system." 2018 IEEE International Conference on Applied System Invention (ICASI). IEEE, 2018.

[2] Omar, Ilhaam A., et al. "Implementing decentralized auctions using blockchain smart contracts." Technological Forecasting and Social Change 168 (2021): 120786.

[3] Mogavero, Francesco, et al. "The Blockchain Quadrilemma: When Also Computational Effectiveness Matters." 2021 IEEE Symposium on Computers and Communications (ISCC). IEEE, 2021.

[4] Chen, Jing, and Silvio Micali. "Algorand: A secure and efficient distributed ledger." Theoretical Computer Science 777 (2019): 155-183.

## Useful Links

[L1] https://gitlab.com/quadrilemma/quadrilemma

[L2] https://www.auctionity.com/

[L3] https://developer.algorand.org/articles/randomness-on-algorand/

[L4] https://algorand-devrel.github.io/beaker/html/index.html

[L5] https://py-algorand-sdk.readthedocs.io/en/latest/

[L6] https://github.com/algorand/py-algorand-sdk

[L7] https://github.com/algorand-devrel/beaker/tree/master/examples

[L8] https://github.com/algorand-school/handson-contract

[L9] https://github.com/algorand-devrel/beaker-starter-kit

[L10] https://github.com/algorand-devrel/beaker-auction









