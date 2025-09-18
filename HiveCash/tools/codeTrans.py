import base64


def hexTob64sp(hx: str):
    bt = bytes.fromhex(hx)
    if hx != bt.hex():
        raise ValueError("No hex input")
    b64url = base64.urlsafe_b64encode(bt).decode()
    return b64url.rstrip("=")


def b64spToHex(b64: str) -> str:
    padding = '=' * ((4 - (len(b64) % 4)) % 4)
    padded_b64 = b64 + padding
    # Decodificar Base64 URL-safe a bytes
    try:
        byte_data = base64.urlsafe_b64decode(padded_b64)
    except Exception as e:
        raise ValueError(f"Base64 inválido: {e}")
    return byte_data.hex()



