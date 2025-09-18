from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from pydantic import BaseModel
from werkzeug.exceptions import HTTPException
import os


from HiveCash.cryptof.ecashmint import EcashMint
from HiveCash.hiveManager.hiveconfig import active

app = Flask(__name__, static_url_path='')

CORS(app)


# Configuración inicial
mint_instance = EcashMint(active)

# Modelos Pydantic


class MintRequest(BaseModel):
    secret_hash: str
    amount: int


class TransferRequest(BaseModel):
    tx: str


class TransferRequestI(TransferRequest):
    payhash: str


# Manejo de errores


@app.errorhandler(ValueError)
async def handle_value_error(e):
    return jsonify({"message": str(e)}), 400

# Endpoints


@app.route('/mint/tokens', methods=['POST'])
async def mint_tokens():
    try:
        data = request.get_json()
        mint_request = MintRequest(**data)
        secret_hash_bytes = bytes.fromhex(mint_request.secret_hash)
        signature, uri, memo = await mint_instance.mint_tokens(
            secret_hash_bytes, mint_request.amount)

        return jsonify({
            "signature": signature,
            "deposit_uri": uri,
            "memo": memo
        })
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
# OK


@app.route('/mint/check_deposit/<string:secret_hash>', methods=['GET'])
async def check_deposit(secret_hash: str):
    try:
        if secret_hash != bytes.fromhex(secret_hash).hex():
            raise ValueError("Formato hexadecimal inválido")
        result = await mint_instance.mint_check_deposit(bytes.fromhex(secret_hash))
        return jsonify({"deposit_valid": result})
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
# OK


@app.route('/mint/internal_transfer', methods=['POST'])
async def internal_transfer():
    try:
        data = request.get_json()
        transfer_request = TransferRequestI(**data)
        success, message = await mint_instance.mint_internal_transfer(
            transfer_request.tx, transfer_request.payhash)
        if not success:
            raise ValueError(message)
        return jsonify({"status": "success", "message": message})
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)})
# OK


@app.route('/mint/external_transfer', methods=['POST'])
async def external_transfer():
    try:
        data = request.get_json()
        transfer_request = TransferRequest(**data)
        success, message = await mint_instance.mint_external_transfer(
            transfer_request.tx)
        if not success:
            raise ValueError(message)
        return jsonify({"status": "success", "message": message})
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)})
# OK


@app.route('/mint/public_key', methods=['GET'])
async def get_public_key():
    return jsonify({"public_key_hex": mint_instance.mint_get_public_key_hex()})
# OK


@app.route('/mint/get_sign/<string:secret_hash>', methods=['GET'])
async def get_sign(secret_hash: str):
    try:
        sig, amount, status, msg = await mint_instance.mint_get_sign(
            bytes.fromhex(secret_hash))
        return jsonify({"signature": sig, "amount": amount, "status": status, "msg": msg})
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
# OK

if __name__ == '__main__':
    app.run()
# OK
