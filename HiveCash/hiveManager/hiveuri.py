import base64
import json

b64u_lookup = {'/': '_', '_': '/', '+': '-', '-': '+', '=': '.', '.': '='}
def btoa(x: str): return base64.b64decode(x).decode('utf-8')
def atob(x: str) -> str: return base64.b64encode(bytes(x, 'utf-8')).decode('utf-8')

def genb64U(x: str) -> str:
    lt = list(atob(x))
    tro = []
    for el in lt:
        em = b64u_lookup.get(el, el)
        tro.append(em)
    return "".join(tro)

def recb64U(x: str) -> str:
    lt = list(x)
    tro = []
    for el in lt:
        em = b64u_lookup.get(el, el)
        tro.append(em)
    er = "".join(tro)
    return btoa(er)

def encodeOp(tx):
    jst = json.dumps(tx)
    return genb64U(jst)

def hiveuri(conten,action:str='op',options:list[str]=[]):
    ap=''
    if options:
        ap='?'+"&".join(options)
    return f"hive://sign/{action}/{conten}{ap}"