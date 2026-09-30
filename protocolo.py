import json

def encode(msg: dict) -> bytes:
    return (json.dumps(msg) + "\n").encode("utf-8")

def decode(line: str) -> dict:
    return json.loads(line)

def tablero_a_dict(tablero):
    return {f"{k[0]},{k[1]}": v for k, v in tablero.items()}

def dict_a_tablero(d):
    return {tuple(int(x) for x in k.split(",")): v for k, v in d.items()}
