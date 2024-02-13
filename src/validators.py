from cerberus import Validator
from flask import Request
from .errors import HttpUnprocessableEntityError

def make_transaction_body_validator(request: Request) -> None:
    body_validator = Validator({
        "valor": {
            "type": "integer",
            "min": 1,
            "required": True,
        },
        "tipo": {
            "type": "string",
            "allowed": ["c", "d"],
            "required": True
        },
        "descricao": {
            "type": "string",
            "minlength": 1,
            "maxlength": 10,
            "required": True
        },
    })

    response = body_validator.validate(request.json)
    if response is False:
        raise HttpUnprocessableEntityError("Invalid value(s) provided")
