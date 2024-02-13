from flask import Blueprint, request, jsonify
from .controllers import make_transaction_controller, get_statement_controller
from .validators import make_transaction_body_validator
from .errors import HttpUnprocessableEntityError, HttpNotFoundError

client_operations_blueprint = Blueprint('client_operations', __name__)
@client_operations_blueprint.route("/clientes/<client_id>/transacoes", methods=["POST"])
def make_transaction(client_id: str):
    try:
        make_transaction_body_validator(request)
    except HttpUnprocessableEntityError as error:
        return jsonify({"message": error.message}), error.status_code

    try:
        [credit_line, current_balance] = make_transaction_controller(
            client_id,
            {
                "value": request.json['valor'],
                "type": request.json['tipo'],
                "description": request.json['descricao']

            }
        )

        return jsonify({"limite": credit_line, "saldo": current_balance})
    except (HttpUnprocessableEntityError, HttpNotFoundError) as error:
        return jsonify({"message": error.message}), error.status_code


@client_operations_blueprint.route("/clientes/<client_id>/extrato")
def get_statement(client_id: str):
    try:
        parsed_client_statement = get_statement_controller(client_id)
        return jsonify(parsed_client_statement)
    except HttpNotFoundError as error:
        return jsonify({"message": error.message}), error.status_code
