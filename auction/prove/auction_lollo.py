from typing import Final
from beaker import *
from pyteal import *

MIN_FEE = Int(1000)                                     # minimum fee on Algorand is currently 1000 microAlgos

class Auction(Application):

    governor: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type = TealType.bytes,
        key = Bytes("g"),
        default = Global.creator_address(),
        descr = "The current governor of this contract, allowed to do admin type actions"
    )

    highest_bidder: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type = TealType.bytes,
        default=Bytes("")
    )

    start_auction_note: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type= TealType.bytes,
        default = Bytes("START_AUCTION")
    )

    end_auction_note: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type= TealType.bytes,
        default = Bytes("END_AUCTION")
    )

    highest_bid: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type = TealType.uint64,
        default= Int(0)
    )

    auction_end: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type = TealType.uint64,
        default= Int(0)
    )

    @create
    def create(self):
        return self.initialize_application_state()

    @external(authorize = Authorize.only(governor))
    def set_governor(self, new_governor: abi.Account):
        """sets the governor of the contract, may only be called by the current governor"""
        return self.governor.set(new_governor.address())

    @internal(TealType.none)
    def pay_bidder(self, receiver: Expr, amount: Expr):
        return Seq(
            InnerTxnBuilder.Begin(),                            
            InnerTxnBuilder.SetFields(
                {
                    TxnField.type_enum: TxnType.Payment,
                    TxnField.receiver: receiver,
                    TxnField.amount: amount,
                    TxnField.fee: Int(0),
                }
            ),
            InnerTxnBuilder.Submit()
        )

    @internal(TealType.none)
    def pay_owner(self, receiver: Expr, amount: Expr):
        return Seq(
            InnerTxnBuilder.Begin(),                            
            InnerTxnBuilder.SetFields(
                {
                    TxnField.type_enum: TxnType.Payment,
                    TxnField.receiver: receiver,
                    TxnField.amount: amount,
                    TxnField.fee: MIN_FEE,
                    TxnField.close_remainder_to: Global.creator_address(),
                }
            ),
            InnerTxnBuilder.Submit()
        )

    @external(authorize = Authorize.only(governor))
    def start_auction(self, payment: abi.PaymentTransaction, starting_price: abi.Uint64, duration: abi.Uint64):
        payment = payment.get()
        start_auction_note = self.start_auction_note.get()

        return Seq(
            Assert(payment.receiver() == Global.current_application_address()),
            Assert(payment.amount() == Int(1000000)),
            Assert(Txn.note() == start_auction_note),
            self.auction_end.set(Global.latest_timestamp() + duration.get()),
            self.highest_bid.set(starting_price.get()),
            self.highest_bidder.set(Bytes(""))
        )

    @external
    def bid(self, payment: abi.PaymentTransaction, previous_bidder: abi.Account):
        payment = payment.get()
        auction_end = self.auction_end.get()
        highest_bidder = self.highest_bidder.get()
        highest_bid = self.highest_bid.get()

        return Seq(
            Assert(Global.latest_timestamp() < auction_end),
            # Verify payment transaction
            Assert(payment.amount() > highest_bid),
            Assert(Txn.sender() == payment.sender()),
            # Return money to previous bidder
            #If(highest_bidder != Bytes(""), Seq(self.pay(highest_bidder, highest_bid))),
            If(highest_bidder != Bytes(""), Seq(Assert(highest_bidder == previous_bidder.address()), self.pay_bidder(highest_bidder, highest_bid))),
            # Set global state
            self.highest_bid.set(payment.amount()),
            self.highest_bidder.set(payment.sender())
        )

    #OUR CURRENT IMPLEMENTATION
    @external
    def end_auction(self):
        auction_end = self.auction_end.get()
        highest_bid = self.highest_bid.get()
        owner = self.governor.get()
        end_auction_note = self.end_auction_note.get()

        return Seq(
            Assert(Global.latest_timestamp() > auction_end),
            Assert(Txn.note() == end_auction_note),
            self.pay_owner(owner, highest_bid)
        )

#    @close_out
#    def close_out(self):
#        return Approve()

#    @delete
#    def delete(self, app_addr: abi.Account):
#        auction_end = self.auction_end.get()
#        app_balance = client.account_info(app_addr)["amount"]
#        
#        return Seq(
#            Assert(Global.latest_timestamp() > auction_end),
#            Assert(Int(app_balance) == Int(0)),
##            Assert(payment.amount() == Int(1000000))
#            Approve()
#        )



if __name__ == "__main__":
    Auction().dump("artifacts")

#    if os.path.exists("approval.teal"):
#        os.remove("approval.teal")

#    if os.path.exists("approval.teal"):
#        os.remove("clear.teal")

#    if os.path.exists("abi.json"):
#        os.remove("abi.json")

#    if os.path.exists("app_spec.json"):
#        os.remove("app_spec.json")

#    with open("approval.teal", "w") as f:
#        f.write(app.approval_program)

#    with open("clear.teal", "w") as f:
#        f.write(app.clear_program)

#    with open("abi.json", "w") as f:
#        f.write(json.dumps(app.contract.dictify(), indent=4))

#    with open("app_spec.json", "w") as f:
#        f.write(json.dumps(app.application_spec(), indent=4))
