from beem.account import Account
from beem.amount import Amount
from beembase import operations
from beem.transactionbuilder import TransactionBuilder
from .hive import hive
from .hiveconfig import manager, active, fee, donate
import asyncio
from decimal import Decimal


async def averifytransactE(amount: int, memo: str) -> bool:
    eamount = f"{amount*1.e-3:.3f} HBD"
    try:
        manager_ac = Account(manager, blockchain_instance=hive)
        transac = manager_ac.get_account_history(
            index=-1, limit=1000, only_ops=['transfer'])
        for tr in transac:
            if tr == None:
                continue
            if tr.get('memo', '') == memo:
                amount_obj = Amount(tr['amount'], blockchain_instance=hive)
                stamount = f"{amount_obj.amount_decimal:.3f} {amount_obj.symbol}"

                if stamount == eamount:
                    return True
    except:
        return False
    return False


def aVerifyTransMemo(memo: str) -> int:
    try:
        manager_ac = Account(manager, blockchain_instance=hive)
        transac = manager_ac.get_account_history(
            index=-1, limit=1000, only_ops=['transfer'])
        for tr in transac:
            if tr == None:
                continue
            if tr.get('memo', '') == memo:
                amount_obj = Amount(tr['amount'], blockchain_instance=hive)
                if amount_obj.symbol == 'HBD':
                    return int(Decimal(str(amount_obj.amount)) * 1000)
    except:
        return 0
    return 0


def verifytransactE(amount: int, memo: str) -> bool:
    return asyncio.run(averifytransactE(amount, memo))


async def existHiveAcount(username: str):
    try:
        acc = Account(username, blockchain_instance=hive)
        return True
    except:
        return False


async def transferHBD(to: str, amount: int, memo: str):
    try:
        transfer_op = operations.Transfer(
            **{
                "to": to,
                "from": manager,
                "memo": memo,
                "amount": f"{amount*1.e-3*(1.0-fee):.3f} HBD"
            })
        tx = TransactionBuilder(blockchain_instance=hive)
        tx.appendOps(transfer_op)
        tx.appendWif(active)
        tx.sign()
        tx.broadcast()
        if amount*fee > 1:
            transfer_op2 = operations.Transfer(
                **{
                    "to": donate,
                    "from": manager,
                    "memo": "Extract fee",
                    "amount": f"{amount*1.e-3*fee:.3f} HBD"
                })
            tx2 = TransactionBuilder(blockchain_instance=hive)
            tx2.appendOps(transfer_op)
            tx2.appendWif(active)
            tx2.sign()
            tx2.broadcast()

        return True
    except:
        return False
