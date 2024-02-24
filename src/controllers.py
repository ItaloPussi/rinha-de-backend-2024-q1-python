from typing import Dict, List
from datetime import datetime
from .database import database_connection
from .errors import HttpNotFoundError, HttpUnprocessableEntityError

def make_transaction_controller(client_id: str, transaction: Dict[str, str | int]) -> List[int]:
    cur = database_connection.cursor()
    
    cur.execute("SELECT credit_line, balance from clients where id = %s", (client_id))
    client = cur.fetchone()
    if not client:
        raise HttpNotFoundError("User not found.")
    [credit_line, balance] = client

    forecast_balance = balance + transaction["value"] if transaction["type"] == "c" else balance - transaction["value"]

    if transaction["type"] == "d":
        will_limit_be_infringed = (balance - transaction["value"]) < -credit_line
        if will_limit_be_infringed:
            raise HttpUnprocessableEntityError("Not enough money.")

    cur.execute("UPDATE clients SET balance = balance + %s where id = %s and balance = %s", (transaction["value"] if transaction["type"] == "c" else -transaction["value"], client_id, balance))
    if cur.rowcount == 1:
        cur.execute("INSERT INTO transactions (client_id, amount, operation, summary) values (%s, %s, %s, %s)", (client_id, transaction["value"], transaction["type"], transaction["description"]))
        database_connection.commit()
    else:
        database_connection.commit()
        return make_transaction_controller(client_id, transaction)

    return credit_line, forecast_balance

def get_statement_controller(client_id: str) -> Dict[str, str]:
    cur = database_connection.cursor()

    cur.execute("SELECT credit_line, balance from clients where id = %s", (client_id))
    client = cur.fetchone()
    if not client:
        raise HttpNotFoundError("User not found.")
    [credit_line, balance] = client

    cur.execute("SELECT amount, operation, summary, created_at from transactions where client_id = %s ORDER BY created_at DESC LIMIT 10", (client_id))
    client_transactions = cur.fetchall()

    parsed_client_statement = {
        "saldo": {
            "total": balance,
            "data_extrato": datetime.utcnow().isoformat(),
            "limite": credit_line
        },
        "ultimas_transacoes": [
            {
                "valor": client_transaction[0],
                "tipo": client_transaction[1],
                "descricao": client_transaction[2],
                "realizada_em": client_transaction[3].isoformat()
            }
            for client_transaction in client_transactions
        ]
    }

    return parsed_client_statement
