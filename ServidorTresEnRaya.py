import socket
import sys
import threading
from AgenteIA.AgenteJugador import ElEstado
from ClienteTresEnRaya import ClienteTresEnRaya
from protocolo import encode, decode, tablero_a_dict, dict_a_tablero


class ServidorTresEnRaya:
    def __init__(self, host="0.0.0.0", puerto=5000, n=3):
        self.host = host
        self.puerto = puerto
        self.n = n
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def _estado_inicial(self):
        movidas = [(x, y) for x in range(1, self.n + 1)
                   for y in range(1, self.n + 1)]
        return ElEstado(jugador='X', get_utilidad=0,
                        tablero={}, movidas=movidas)

    def _en_raya(self, tablero, m, jugador, delta):
        dx, dy = delta
        x, y = m
        c = 0
        while tablero.get((x, y)) == jugador:
            c += 1
            x, y = x + dx, y + dy
        x, y = m
        while tablero.get((x, y)) == jugador:
            c += 1
            x, y = x - dx, y - dy
        c -= 1
        return c >= self.n

    def _utilidad(self, tablero, m, jugador):
        for d in [(0, 1), (1, 0), (1, 1), (1, -1)]:
            if self._en_raya(tablero, m, jugador, d):
                return 1 if jugador == 'X' else -1
        return 0

    def _enviar(self, conn, msg):
        conn.sendall(encode(msg))

    def _recibir(self, conn, buffer_holder):
        while "\n" not in buffer_holder[0]:
            data = conn.recv(4096)
            if not data:
                raise ConnectionError("Cliente desconectado")
            buffer_holder[0] += data.decode("utf-8")
        line, buffer_holder[0] = buffer_holder[0].split("\n", 1)
        return decode(line)

    def _jugar_con(self, conn_x, conn_o):
        estado = self._estado_inicial()
        self._enviar(conn_x, {"tipo": "turno", "jugador": "X",
                              "tablero": tablero_a_dict(estado.tablero),
                              "movidas": estado.movidas})
        self._enviar(conn_o, {"tipo": "espera", "jugador": "O",
                              "tablero": tablero_a_dict(estado.tablero),
                              "movidas": estado.movidas})

        conexiones = {'X': conn_x, 'O': conn_o}
        buffers = {'X': [""] , 'O': [""]}
        ganador = None

        while True:
            actual = estado.jugador
            rival = 'O' if actual == 'X' else 'X'
            msg = self._recibir(conexiones[actual], buffers[actual])

            if msg["tipo"] != "jugada":
                continue
            m = tuple(msg["accion"])
            if m not in estado.movidas:
                self._enviar(conexiones[actual],
                             {"tipo": "error", "motivo": "movida inválida"})
                continue

            nuevo_tablero = estado.tablero.copy()
            nuevo_tablero[m] = actual
            nuevas_movidas = list(estado.movidas)
            nuevas_movidas.remove(m)
            util = self._utilidad(nuevo_tablero, m, actual)

            estado = ElEstado(
                jugador=rival,
                get_utilidad=util,
                tablero=nuevo_tablero,
                movidas=nuevas_movidas,
            )

            for j, conn in conexiones.items():
                self._enviar(conn, {
                    "tipo": "estado",
                    "tablero": tablero_a_dict(estado.tablero),
                    "movidas": estado.movidas,
                    "jugador": estado.jugador,
                    "utilidad": estado.get_utilidad,
                })

            if util != 0:
                ganador = actual
                break
            if not nuevas_movidas:
                ganador = "empate"
                break

        for j, conn in conexiones.items():
            self._enviar(conn, {"tipo": "fin", "ganador": ganador})

    def iniciar(self):
        self.sock.bind((self.host, self.puerto))
        self.sock.listen(2)
        print(f"[Servidor] Esperando en {self.host}:{self.puerto} ...")
        conn_x, addr_x = self.sock.accept()
        print(f"[Servidor] Conectado X desde {addr_x}")
        conn_o, addr_o = self.sock.accept()
        print(f"[Servidor] Conectado O desde {addr_o}")

        try:
            self._jugar_con(conn_x, conn_o)
        finally:
            conn_x.close()
            conn_o.close()
            self.sock.close()
        print("[Servidor] Partida finalizada.")

if __name__ == "__main__":
    servidor = ServidorTresEnRaya(host="0.0.0.0", puerto=5000, n=3)
    servidor.iniciar()
