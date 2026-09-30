import socket
import sys
from AgenteIA.AgenteJugador import ElEstado
from AgenteTresEnRaya import AgenteTresEnRaya
from HumanoTresEnRaya import HumanoTresEnRaya
from protocolo import encode, decode, dict_a_tablero


class ClienteTresEnRaya:
    def __init__(self, host, puerto, modo="humano", tecnica="minimax", n=3):
        self.host = host
        self.puerto = puerto
        self.n = n
        self.modo = modo
        self.tecnica = tecnica
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.buffer = ""
        self.mi_jugador = None

        if modo == "humano":
            self.agente = HumanoTresEnRaya(n)
        else:
            self.agente = AgenteTresEnRaya(n)
            self.agente.tecnica = tecnica

    def _recv_msg(self):
        while "\n" not in self.buffer:
            data = self.sock.recv(4096)
            if not data:
                raise ConnectionError("Servidor cerró la conexión")
            self.buffer += data.decode("utf-8")
        line, self.buffer = self.buffer.split("\n", 1)
        return decode(line)

    def _send_msg(self, msg):
        self.sock.sendall(encode(msg))

    def _mostrar_tablero(self, tablero):
        for x in range(1, self.n + 1):
            fila = ""
            for y in range(1, self.n + 1):
                fila += tablero.get((x, y), ".") + " "
            print(fila)
        print()

    def _construir_estado(self, msg):
        return ElEstado(
            jugador=msg["jugador"],
            get_utilidad=msg.get("utilidad", 0),
            tablero=dict_a_tablero(msg["tablero"]),
            movidas=[tuple(m) for m in msg["movidas"]],
        )

    def _pedir_jugada_humano(self, movidas):
        while True:
            try:
                cad = input("Tu jugada (x,y): ")
                movida = eval(cad)
                if tuple(movida) in [tuple(m) for m in movidas]:
                    return list(movida)
                print("Movida inválida.")
            except Exception:
                print("Formato inválido. Usa (x,y).")

    def _decidir_jugada(self, estado):
        if self.modo == "humano":
            return self._pedir_jugada_humano(estado.movidas)
        self.agente.estado = estado
        self.agente.programa()
        accion = self.agente.get_acciones()
        return list(accion)

    def iniciar(self):
        self.sock.connect((self.host, self.puerto))
        print(f"[Cliente] Conectado a {self.host}:{self.puerto}")

        try:
            while True:
                msg = self._recv_msg()
                tipo = msg["tipo"]

                if tipo in ("turno", "espera", "estado"):
                    self.mi_jugador = self.mi_jugador or msg.get("jugador")
                    estado = self._construir_estado(msg)
                    print(f"\n--- Tablero (tú eres '{self.mi_jugador}') ---")
                    self._mostrar_tablero(estado.tablero)
                    print(f"Turno de: {estado.jugador}")

                    if tipo == "turno":
                        accion = self._decidir_jugada(estado)
                        print(f"Envías: {accion}")
                        self._send_msg({"tipo": "jugada", "accion": accion})

                elif tipo == "error":
                    print(f"[Error] {msg['motivo']}")

                elif tipo == "fin":
                    g = msg["ganador"]
                    if g == "empate":
                        print("\n¡Empate!")
                    elif g == self.mi_jugador:
                        print(f"\n¡Ganaste! (tú = {self.mi_jugador})")
                    else:
                        print(f"\nPerdiste. Ganó {g}")
                    break

        finally:
            self.sock.close()


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    puerto = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    modo = sys.argv[3] if len(sys.argv) > 3 else "minimax"
    tecnica = sys.argv[4] if len(sys.argv) > 4 else "minimax"
    ClienteTresEnRaya(host, puerto, modo, tecnica).iniciar()
