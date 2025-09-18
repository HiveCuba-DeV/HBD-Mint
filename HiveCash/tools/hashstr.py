from ..cryptof.hcdef import getScryptHash
from ..hiveManager.hiveconfig import active

def getUMsgHash(msg: str) -> str:
    msgx =  f"{msg}:{active}" 
    msh=getScryptHash(msgx)   
    return str(msh.__hash__().__abs__())

