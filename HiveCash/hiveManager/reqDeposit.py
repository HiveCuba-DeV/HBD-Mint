from ..tools.hashstr import getUMsgHash
from .hiveuri import encodeOp, hiveuri
from .hiveconfig import manager


def regDeposit(intext: str, amount: int):
    memo = getUMsgHash(intext)
    #print(f"G->Hash:{intext}, memo:{memo}")
    transfer_op = ["transfer", {
        "to": manager,
        "amount": f"{amount*1.e-3:.3f} HBD",
        "memo": memo
    }]
    tx = encodeOp(transfer_op)
    return hiveuri(tx), memo
