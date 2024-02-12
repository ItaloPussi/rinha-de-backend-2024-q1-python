from flask import Flask, request, jsonify
from cerberus import Validator
from datetime import datetime
from time import sleep
import psycopg2

app = Flask(__name__)

try:
    conn = psycopg2.connect("dbname=crebito user=rinha password=R1nh@Cr3b1t0! host=db")
except Exception as e:
    sleep(1)
    conn = psycopg2.connect("dbname=crebito user=rinha password=R1nh@Cr3b1t0! host=db")

@app.route("/clientes/<client_id>/transacoes", methods=["POST"])
def make_transaction(client_id: str):
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

    is_valid_body_values = body_validator.validate(request.json)

    if(not is_valid_body_values):
        return jsonify({"message": "Body values not valid"}), 422

    transaction_value = request.json['valor']
    transaction_type = request.json['tipo']
    transaction_description = request.json['descricao']

    cur = conn.cursor()
    
    cur.execute("SELECT limite, saldo from clientes where id = %s", (client_id))
    client_values = cur.fetchone()

    if not client_values:
        return jsonify({"message": "The client was not founded."}), 404
    
    resulting_amount = (client_values[1] - transaction_value) if transaction_type == "d" else (client_values[1] + transaction_value)

    if(transaction_type == "d"):
        will_limit_be_infringed = (client_values[1] - transaction_value) < -client_values[0]
        if will_limit_be_infringed:
            return jsonify({"message": "Not enough money."}), 422
    
    cur.execute("INSERT INTO transacoes (cliente_id, valor, tipo, descricao) values (%s, %s, %s, %s)", (client_id, transaction_value, transaction_type, transaction_description))
    cur.execute("UPDATE clientes SET saldo = saldo + %s where id = %s", (transaction_value if transaction_type == "c" else -transaction_value, client_id))
    conn.commit()
    return jsonify({"limite": client_values[0], "saldo": resulting_amount})


@app.route("/clientes/<client_id>/extrato")
def get_statement(client_id: str):
    cur = conn.cursor()
    
    cur.execute("SELECT limite, saldo from clientes where id = %s", (client_id))
    client_values = cur.fetchone()

    if not client_values:
        return jsonify({"message": "The client was not founded."}), 404
    
    cur.execute("SELECT valor, tipo, descricao, realizada_em from transacoes where cliente_id = %s ORDER BY realizada_em DESC LIMIT 10", (client_id))
    client_transactions = cur.fetchall()
    
    result = {
    "saldo": {
        "total": client_values[1],
        "data_extrato": datetime.utcnow().isoformat(),
        "limite": client_values[0]
    },
    "ultimas_transacoes": [
        {
            "valor": transacao[0],
            "tipo": transacao[1],
            "descricao": transacao[2],
            "realizada_em": transacao[3].isoformat()
        }
        for transacao in client_transactions
    ]

    }

    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
