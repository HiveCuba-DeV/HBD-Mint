from ..tools.ctime import getNow
from .dbconfig import db

hdbmint_columnsnames = ("mintid", "minthash", "amount", "status", "date")


async def isMinted(secret_hash: str):
    try:
        if await db.query_data('hdbmint', {"minthash": secret_hash}):
            return True
        return False
    except:
        return False


async def newToken(secret_hash: str, amount: int):
    try:         
        if await db.insert_data('hdbmint', {"minthash": secret_hash,
                                            "amount": amount,
                                            'date': getNow()}):
            return True
        return False
    except:
        return False


async def getToken(secret_hash: str):
    try:
        return await db.query_data('hdbmint', {"minthash": secret_hash})
    except:
        return []


async def updateToken(secret_hash: str, data: dict):
    try:
        if await db.update_data('hdbmint', data, {"minthash": secret_hash}):
            return True
        return False
    except:
        return False
