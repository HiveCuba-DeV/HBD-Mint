# HBD-Mint of HiveCash

## Project overview
This repository implements the HBD mint service for Hive following an eCash-like protocol adapted to Hive. The service exposes REST endpoints to mint tokens, check deposits, perform internal and external transfers, and provide signatures and the mint public key.

---

## Requirements
- Python >= 3.6
- Git
- Unix-like shell (bash) for provided scripts

---

## Quick start setup
1. Clone the repository:
```bash
git clone https://github.com/HiveCuba-DeV/HBD-Mint.git
cd HBD-Mint
```

2. Create a Python virtual environment inside the project folder:
```bash
python3 -m venv venv
```

3. Activate the virtual environment:
```bash
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requeriment.txt
```

---

## Prepare keystore file
1. Create a temporary JSON file named `temp.json` inside the project folder with this exact structure:
```json
{
    "MNEMONIC":"Valid 12 words bip39 mnemonic",
    "mintmanager":"ManagerHiveAccount",
    "mintdonate": "DonateHiveAccount",
    "minstactive": "ACTIVEWIF KEY OF MINT MANAGER",
    "HIVECASHDB": "db/HiveCash.db"
}
```

2. Encrypt `temp.json` to produce `fdata.kdb` and remove the plaintext file:
```bash
python encrypt.py temp.json fdata.kdb
```
- After this command `temp.json` is deleted and only the encrypted `fdata.kdb` remains.
- The encryption step protects sensitive keys and values behind a password.

3. To decrypt and export values into the shell in a Bash-compatible `export KEY=VALUE` format:
```bash
python decrypt.py fdata.kdb
```
- The decrypt script prints or outputs values in a format compatible with `eval $(python decrypt.py fdata.kdb)` so environment variables can be set for the running process.

---

## Run the mint service
1. Ensure `fdata.kdb` exists and contains the encrypted keystore.
2. Make `run.sh` executable:
```bash
chmod +x run.sh
```
3. Run the mint service:
```bash
./run.sh
```

4. Contents of `run.sh` used by the project:
```bash
#!/bin/bash

source ./venv/bin/activate

pip install -r requeriment.txt

eval $(python decript.py fdata.kdb)


hypercorn --bind 127.0.0.1:5000 HiveCash.hiveCash:app -w 1 >> logs/weblog.txt 2>&1 & 

export webpid=`echo $!`
echo "$webpid" > pids/web.pid
echo "Web  start at pid $webpid"
```
- The script activates the venv, installs requirements, sources environment variables from the decrypted keystore, launches the Hypercorn ASGI server bound to 127.0.0.1:5000, and writes the web PID to `pids/web.pid`.
- Logs are appended to `logs/weblog.txt`.

---

## Endpoints
All endpoints return JSON and use standard HTTP status codes for errors.

### POST /mint/tokens
- Purpose: request minting of HBD tokens.
- Request body example:
```json
{
  "secret_hash": "hexadecimal-string",
  "amount": 1000
}
```
- Successful response:
```json
{
  "signature": "signature-string",
  "deposit_uri": "deposit-uri-string",
  "memo": "optional-memo"
}
```
- Behavior: service converts `secret_hash` from hex and calls mint logic to produce a signature, deposit URI, and memo.

### GET /mint/check_deposit/<string:secret_hash>
- Purpose: verify that a deposit for the given secret hash is valid.
- Path parameter: `secret_hash` as hex string.
- Successful response:
```json
{
  "deposit_valid": true
}
```
- Error responses return a JSON message and HTTP 400 for invalid hex or other validation errors.

### POST /mint/internal_transfer
- Purpose: perform an internal transfer inside the mint system.
- Request body example:
```json
{
  "tx": "transaction-hex-or-struct",
  "payhash": "payment-hash-string"
}
```
- Successful response:
```json
{
  "status": "success",
  "message": "transfer message"
}
```
- On failure the response uses status "error" with an explanatory message.

### POST /mint/external_transfer
- Purpose: create an external Hive transfer (broadcasted to Hive network).
- Request body example:
```json
{
  "tx": "transaction-hex-or-struct"
}
```
- Successful response:
```json
{
  "status": "success",
  "message": "external transfer message"
}
```
- On failure the response uses status "error" with an explanatory message.

### GET /mint/public_key
- Purpose: retrieve the mint public key in hex format.
- Successful response:
```json
{
  "public_key_hex": "hex-encoded-public-key"
}
```

### GET /mint/get_sign/<string:secret_hash>
- Purpose: obtain the mint's signature and metadata for a given secret hash.
- Successful response:
```json
{
  "signature": "signature-string",
  "amount": 1000,
  "status": "status-string",
  "msg": "additional message"
}
```
- Error responses return a JSON message and HTTP 400 for invalid input.

---

## File and folder notes
- **requeriments.txt** is the dependency list used throughout scripts.
- **fdata.kdb** is the encrypted keystore produced by `encrypt.py`.
- **logs/weblog.txt** receives Hypercorn output.
- **pids/web.pid** stores the running web process id.
- **db/HiveCash.db** is the expected SQLite path referenced in keystore under `HIVECASHDB`.

---

## Security considerations
- Always remove plaintext `temp.json` immediately after encryption.
- Protect `fdata.kdb` and limit filesystem access to the service user.
- Use strong passwords for encryption and secure storage for the mnemonic and active WIF keys.

---

## Troubleshooting
- If the server fails to start, inspect `logs/weblog.txt` and `pids/web.pid`.
- Ensure the virtual environment is activated before running scripts and that Python is >= 3.6.
- Confirm the filenames used by scripts match those in the project (`requeriment.txt` vs `requeriments.txt`, `decript.py` vs `decrypt.py`) and adjust if necessary.

# OpenAPI–Style: HiveCash Mint API of HiveCuba Community

- [HiveCuba Community on HIVE](https://ecency.com/created/hive-10053)
- [HiveCuba Community on Telegram](https://t.me/comunidadcubanahive)
- [HiveCash PWA Web App Beta](https://cash.hivecuba.com)

---

## POST /mint/tokens

URL  
```
POST https://cash.hivecuba.com/mint/tokens
```

Request Body  
```json
{
  "secret_hash": "string",
  "amount": 0
}
```

Responses  
- 200 OK  
  ```json
  {
    "signature": "string",
    "deposit_uri": "string",
    "memo": "string"
  }
  ```
- 4XX / 5XX Error  
  ```text
  Error al generar tokens
  ```

---

## GET /mint/check_deposit/{secretHash}

URL  
```
GET https://cash.hivecuba.com/mint/check_deposit/{secretHash}
```

Path Parameter  
- `secretHash` (string): Hash secreto generado por el usuario.

Responses  
- 200 OK  
  ```json
  {
    "deposit_valid": true
  }
  ```
- 4XX / 5XX Error  
  ```json
  {
    "message": "Error al verificar depósito"
  }
  ```

---

## POST /mint/internal_transfer

URL  
```
POST https://cash.hivecuba.com/mint/internal_transfer
```

Request Body  
```json
{
  "tx": "string",
  "payhash": "string"
}
```

Responses  
- 200 OK  
  ```json
  {
    "status": "string",
    "message": "string"
  }
  ```
- 4XX / 5XX Error  
  ```json
  {
    "message": "Error en transferencia interna"
  }
  ```

---

## POST /mint/external_transfer

URL  
```
POST https://cash.hivecuba.com/mint/external_transfer
```

Request Body  
```json
{
  "tx": "string"
}
```

Responses  
- 200 OK  
  ```json
  {
    "status": "string",
    "message": "string"
  }
  ```
- 4XX / 5XX Error  
  ```json
  {
    "message": "Error en transferencia externa"
  }
  ```

---

## GET /mint/public_key

URL  
```
GET https://cash.hivecuba.com/mint/public_key
```

Responses  
- 200 OK  
  ```json
  {
    "public_key_hex": "string"
  }
  ```
- 4XX / 5XX Error  
  ```json
  {
    "message": "Error al obtener clave pública"
  }
  ```

---

## GET /mint/get_sign/{secretHash}

URL  
```
GET https://cash.hivecuba.com/mint/get_sign/{secretHash}
```

Path Parameter  
- `secretHash` (string): Hash secreto para el cual se solicita la firma.

Responses  
- 200 OK  
  ```json
  {
    "signature": "string",
    "amount": 0,
    "status": "string",
    "msg": "string"
  }
  ```
- 4XX / 5XX Error  
  ```json
  {
    "message": "Error al obtener firma"
  }
  ```

---


