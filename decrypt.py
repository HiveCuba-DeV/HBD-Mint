from getpass import getpass
import json
from cryptography.fernet import Fernet
import base64
import hashlib
import sys


def generar_clave(password: str) -> bytes:
    clave = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(clave)


def main():
    if len(sys.argv) < 2:
        print("Error: You must specify an input json keystore file name")
        print("Use: python decrypt.py keystorefile.json")
        sys.exit(1)

    filex = sys.argv[1]
    password = getpass("#Encryption password of your keystore file: ")
    try:
        with open(filex, 'r') as archivo:
            keystore = json.load(archivo)

        clave = generar_clave(password)
        fernet = Fernet(clave)

    # Descifrar el texto
        texto_descifrado = fernet.decrypt(
            keystore["cipher"].encode()).decode().replace("'", '"')

        datax = json.loads(texto_descifrado)

        for k in datax:
            print(f"export {k}=\"{datax[k]}\" ")

    except FileNotFoundError as e:
        print(f"Error: File not found: {e}")
    except PermissionError as e:
        print(f"Error: You don't have permission to read: {e}")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
