# G1
# E-auction Smart Contract in Algorand (implemented in Beaker) which communicates with Ethereum  
## Problem
We want to implement a decentralised auction service in order to avoid that the seller and the auction participants must trust a centralised auctioneer that can deviate from the auction rules.
A reasonable solution to this trust problem consists into implementing a smart contract which resides on a public blockchain platform. The blockchain, and in particular the smart contract, impersonates the trusted third party, the auctioneer, therefore choosing the right blockchain platform is a core problem in a solution design. In fact different blockchain platforms have different characteristics (such as block finality, cryptographic agility, security or the costs in terms of fees) and allow the implementation of different kind of smart contract for auctions. When the asset which is put up for auction lives inside a blockchain (for example a token controlled by a smart contract in Algorand or Ethereum), the easiest solution to arrange the auction consists into using a smart contract which lives in the same blockchain. However, in some cases, it would be more profitable for the seller and auction participants to perform an auction on a different blockchain with different characteristics making them interoperate accordingly with the users needs.

Below we present our solution to the following problems: 
1) **implementing** a smart contract in Beaker which manages auctions on the Algorand blockchain;
2) **design** the necessary infrastructure to sell assets which live on Ethereum using the same Algorand smart contract. 

## Solution 
Our solution consists into creating two smart contracts in Beaker that allow the users of the Algorand network to perform auctions: one smart contract implements the auction with public bids (also referred to as deposited bidding auction) and the other with committed bids.

In order to augment the interoperability between blockchains and to allow the users of multiple networks to minimize their operation costs, we designed an architecture which puts into communication the Algorand and Ethereum blockchains. In particular, we allow a user to sell an asset living on Ethereum using an auction that is performed on Algorand. Therefore, the seller of an Ethereum asset can incentivate the participation to the auction process by choosing where to make the auction happen: on Ethereum using one of the  ad hoc smart contracts (for example provided by Auctionity [L2]), otherwise they can use the architecture we present in our project making it happen on the Algorand blockchain.
In order to create the bridge between the Algorand and Ethereum blockchain we have implemented the following programs:

1) a smart contract implemented in Solidity **SC<sub>E</sub>** which lives in Ethereum and manages:

    1. the request of opening of a new auction from an account to sell an asset it owns;
    2. the change of property of the same asset on the Ethereum blockchain assigning the ownership of the asset to the winner of the auction.


2) a smart contract implemented in Beaker **SC<sub>A</sub>** which lives in Algorand and manages:

    1. the execution of the auction whenever a new asset is published and locked in the smart contract **SC<sub>E</sub>**. 
    2. the declaration the auction winner according to the auction rules.


We designed an oracle **O** which allows the communication between **SC<sub>E</sub>** and **SC<sub>A</sub>** and manages the following steps:

1) whenever an asset is locked into *SC<sub>E</sub>, **O** triggers the creation of a new auction via **SC<sub>A</sub>**.
2) when the auction has a winner, it triggers the creation of a transaction to *SC<sub>E</sub>* that will allow the winner to redeem the asset.
 
**The oracle is still in under development in JavaScript for future release.**

# Smart Contract Specifications

Asset Auction program

This program, developed using the Beaker framework, is intended to setup a standar auction involving two users. Each of them can see the bids of the other competitor, hence he/she can submit a new bid to start winning the auction. The prize is a NFT created by the seller, who in this case coincides with the owner of the contract (he/she developed it).

asset_auction_main.py steps:

- create the accounts derived by sandbox or mnemomics;
- set the parameters: - offset starting auction
		      - auction duration
		      - client transaction suggested parameters (setting the fee as the minimum fee allowed)
- invoke the client;
- deploy the smart contract;
- create the asset;
- start the auction: - the owner of the asset (= owner of the contract) send a signed transaction for enabling the smart contract having enough funds to do inner payments;
		     - the starting price has been set up to 1 Algo
- transfer the asset to the smart contract by using the`AssetTransferTxn` class
- start bidding: - two bids per user, trying to compete each other
		 - bid amount explicitly set for simple and immediate testing purposes
		 - previous bidder explicitly set for simple and immediate testing purposes
- end auction: - checking the winning address (in this case, explicitly set for simple and immediate testing purposes)
	       - opt-in the asset for the winning address
	       - transfer the asset to the winning address

During each different step, some print statements (stored in`util.py` file) have been added for control/test purposes. These are:
-`print_created_asset(...)`: print the asset data
- print current app state by invoking the method`get_application_state`
- print current app address info by invoking the method`get_application_account_info`
-`print_asset_holding(...)` to check who is holding the asset (this function called also after opting-in the asset to check if the asset_id is among the account fields)
-`print_balances(...)` to check the balances of all the addresses (app and accounts) step by step


asset_auction.py contract functions:

- declaration of parameters: - 2 global bytes parameters (`owner` and`highest_bidder`), setting default values
			     - 4 global int parameters (`highest_bid`,`nft_id`,`auction_start`,`auction_end`), setting default values
- declaration of administrative actions by using the function`set_owner` with the`authorize = Authorize.only(owner)` label enabled
- function`create` to initialize the application state
- function`setup` to start the auction: - added assert control statements on the time and the payment sent by the owner to fund the contract
					 - setting the global parameters to the correct values
- function`bid` to start the bid phase: - added assert control statements on the time and the payment amount/sender
					 - setting the parameters according to the bid values received
					 - paying back the previous bidder if the current bid > previous bid (by using an inner transaction)
- function`end_auction` to close the auction logic: - added assert control statements on the time
						     -`do_aclose` function to send the asset to the receiver (`asset_close_to` field set to`receiver`)
						     -`pay_owner` to give back the owner all the tokens stored on the contract (initial funds - fees for the inner transactions + bid amount).`close_remainder_to` set to`Global.creator_address()`
- function`do_opt_in` to opting-in the asset for the smart contract. Inside it, the function`do_axfer` is triggered for transferring the asset to the smart contract

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

E-commerce activities has become part of everyone daily life, as a consequence of the popularity of the Internet. One of the most used e-commerce activities are e-auctions, where the auction participants can send their bid to buy a product over the Internet [2]. 

Centralised e-auction systems require the auction participants and the seller of the asset to trust the auction manager [3]. The e-auction managers may be dishonest and circumvent the auction rules in order to favour or penalise some auction participants. A solution to this trust problem, (which is: requiring the participants to trust a possibly dishonest third party), consists into considering as "the trusted third party" blockchain platforms that support the creation of smart contracts, such as Ethereum or Algorand. In this way the trust do not resides on a centralised third party but on the network of a public blockchain.

In literature there exist multiple kind of auction: for example in [3] the authors classify the auction models in the following macro-cathegories according to how the bidding process takes place: notarized bidding, deposited bidding, committed bidding and confidential bidding. Basically, the **notarized bidding** is the most simple and insecure auction model and only requires the contract to record the participant bids on the blockchain. The **deposited bidding** requires the participants to send to the smart contract the amount of native cryptocurrency that one is willing to bid in a completely transparent fashion so that everyone can see in real time each other bids. The **committed bidding** auction aims to hide in a first moment the participants bidded amount and to let them reveal it only once the bidding time has expired. The smart contract verifies that the revealed amount corresponds with the committed one and assigns the ownership of the asset to the participant who committed to and opened the highest bid. Finally **confidential bidding** allows the participants to encrypt their bids using the public key of the auctioneer so that at the end of the auction the bids of the loosing participants remain confidential. 

Not every blockchain platform can support the implementation of the auction models described above: the reason behind it resides in the capabilities of the scripting language adopted by the blockchain platforms which may not allow the implementation of some security requirements [1]. For example Bitcoin, with Bitcoin Script, only allows the notarized bidding, Algorand, with Teal, allows the notarized bidding, the deposited bidding and the committed bidding, whereas in Ethereum it is possible to implement all of them [3]. However, due to the differences in the consensus protocol, transaction throughput, and costs in terms of fees, it might be more convenient to perform an aucton on a given platform rather than another. For example, Ethereum allows the implementation of more privacy preserving smart contracts thank to the supported cryptographic functions but it is extremely more expensive in terms of fees than Algorand. In the table below (taken from [3]) one can compare the estimations of the transaction fees considering 80 bytes as token metadata and 10 bidders submitting 1 bid each on different blockchain platforms and with different auction models. The implementations of the smart contracts used to collect the data come from [L1] and the prices in Euro refers to the period February 2020 - January 2021.  


![table Megavero](https://user-images.githubusercontent.com/76473749/196223807-cad28190-6cca-49d4-8be9-e428ef89aee8.PNG)

Another aspect that is relevant when one have to choose the platform to rely on is block finality: in Algorand, which is a based on a BFT consensus protocol, it is immediate, in Ethereum may take tens of seconds. 

For these reson, in some cases, if one have to sell an asset living in Ethereum it might be useful to have the possibility to open an auction on another platform, for instance, on Algorand allowing the participants who trust both the Algorand and Ethereum blockchain to use the most profitable solution. For example if confidentiality is important, than Ethereum will be the right choice, if the price of the asset do not justify the price in terms of fee that the participants should pay working on Ethereum, then Algorand will be the right choice. 

# Technical Challenges and Security considerations on the Bridge 
Developing in Beaker was very difficult given the little documentation [L4],[L7],L[9],L[10] available and few existing examples [L5],[L6],[L10]. In addition, the SDK for Javascript is still very cumbersome, this in fact precluded the possibility of making the oracle capable of communicating simultaneously with the Ethereum and Algorand blockchains.

Another challenge has been designing a protocol (described in the future work section) which creates a bridge between Algorand and Ethereum. The bridge is made possible by the introduction of an Oracle which moves information from the "outside world" to the two blockchains. Note that Algorand is part of the Ethereum's outside world and viceversa. However, since the oracle is the weakest component of our protocol we have tried to remove as much power as possible from its hands. In particular, our commitment has been put in designing the protocol in such a way that an Oracle fault would not allow payment without the asset being sold, or that the sale of the asset would take place without payment being made in Algo.
# Future Works
## A more secure Bridge between Algorand and Ethereum

We want to implement a mechanism that allows a user to sell an asset which lives on the Ethereum blockchain opening an auction on the blockchain of Algorand. Every actor must own an address both in the Algorand and in the Ethereum blockchain. The change of property of the asset happens in the Ethereum blockchain and the payment is performed in Algo in the Algorand blockchain.

The workflow adopted in our project up to now is not very secure since the oracle is in full control of the exchange of communication between the two smart contracts. In order to reduce the power we give to the oracle, we could implement an **atomic swap** between the two blockchain. As you will see below, the oracle still moves information from a blockchain to the other, however, if the oracle stops working at a certain point, the asset will be returned to the seller and the payment in Algos will not be performed.

We recall that the entities involved are the two smart contracts, one implemented on Algorand **SC<sub>A </sub>** and one on Ethereum **SC<sub>E</sub>**,  and the oracle **O** described in section **Solution**. 

The **workflow** is the following:
The protocol which allows the seller of an asset on Ethereum to sell it using an auction on ethereum works as follows:
1) the oracle **O** start listening the two smart contract on Ethereum and Algorand.
2) the seller **S** sends a transaction to the smart contract **SC<sub>E</sub>** offering it for sale: the sale is identified by the transaction id `tr_id` and the seller address `add_s`;
2.1)**SC<sub>E</sub>** will return the asset to the seller if after time `T>>t_a` a buyer has not redeemed it (where `t_a` is the auction duration time); 
3) **O** listens the `asset lock` event coming from **SC<sub>E</sub>**;
5) **O** sends a script to open a new auction associated to `tr_id` on Algorand using **SC<sub>A</sub>**;(a)
6) anyone in the Algorand network can send a transaction to start the auction created by the Oracle; 
7)  all the auction participants can send their bids to the smart contract **SC<sub>A</sub>**: in the bidding process, each participant `p` will include an hidden secret binded to the Ethereum account `h_p(s_p||account_(p,E))`. This will be used to bind the accounts possessed by each participant on the Algorand and Ethereum blockchain (to perform the atomic swap) and to avoid that, when the winner sends a transaction revealing the secret (see step 11) someone steals it and sends a transaction advertising the same secret. It must be binded to account_(p,E);
9) the deposited bidding auction ends and the smart contract **SC<sub>A</sub>** specifies the winner, but the payment is blocked untill the seller sends a transaction proving knowledge of the secret `s_w` hidden behind `h_w(s_w||account_(w,E))` which is the secret of the auction winner;
10) **O** detects the end of the auction phase and sends a transaction to **SC<sub>E</sub>** containing a reference to the hidden secret `h_w(s_w||account_(w,E))` of the winner `w`. (b)
11) the winner `w` discloses its secret `s_w` using its account account_(w,E) and becomes the owner of the asset.
12) the auction winner, who controls the Ethereum account recorded by **O** in **SC<sub>E</sub>** can redeem the locked token
13) once the asset has changed owner, the seller uses the secret `s_w` published by the winner `w` to redeem the transaction in Algo on the Algorand blockchain sending a transaction to **SC<sub>A</sub>**.



To hide the secret one can compute the hash of the concatenation of the secret and the user's account on Ethereum. In this way, when the winner of the auction is declared, it can disclose the secret binding it to the Ethereum account. Once the secret is revealed, the funds stored on the Algorand smart contract are moved to the seller. 

(a) note that if the oracle do not create the auction the asset will return to the seller
(b) note that if the oracle do not move the information from Algorand to Ethereum, then the asset will be returned to the seller and the payment will return to the winner of the auction.

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









