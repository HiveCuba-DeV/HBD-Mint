from getpass import getpass
import json
from cryptography.fernet import Fernet
import base64
import hashlib
import sys
import os


def generar_clave(password: str) -> bytes:
    clave = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(clave)


def main():
    if len(sys.argv) < 3:
        print("Error: You must specify an input and output json file names")
        print("Use: python encrypt.py inputfile.json outputkeystore.json")
        sys.exit(1)

    filex = sys.argv[1]
    fileo = sys.argv[2]
    try:
        with open(filex, 'r') as archivo:
            datax = json.load(archivo)

        pspass = getpass("Encryption password of your keystore file: ")

        clave = generar_clave(pspass)

        fernet = Fernet(clave)

        texto_cifrado = fernet.encrypt(str(datax).encode())

        keystore = {
            "cipher": texto_cifrado.decode()
        }

        with open(fileo, 'w') as archivo:
            json.dump(keystore, archivo, indent=4)

        os.remove(filex)

    except FileNotFoundError as e:
        print(f"Error: File not found: {e}")
    except PermissionError as e:
        print(f"Error: You don't have permission to read: {e}")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
