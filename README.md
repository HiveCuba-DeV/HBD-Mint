# HBD-Mint
# OpenAPI–Style: HiveCash Mint API

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


