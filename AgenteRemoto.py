# AgenteRemoto.py
import socket
import json
from AgenteIA.AgenteJugador import AgenteJugador, ElEstado
from protocolo import encode, decode, dict_a_tablero


class AgenteRemoto(AgenteJugador):
    """
    Agente que delega la decisión a un 'agente_local' (humano o IA)
    pero envía/recibe el estado por socket con el servidor.
    """
    def __init__(self, sock, agente_local, n=3):
        AgenteJugador.__init__(self)
        self.sock = sock
        self.agente_local = agente_local
        self.h = self.v = self.k = n
        self.buffer = ""

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

    def jugadas(self, estado):
        return estado.movidas

    def getResultado(self, estado, m):
        # El cliente NO aplica la jugada, solo la envía. El servidor la valida.
        return estado

    def testTerminal(self, estado):
        return False  # el servidor manda el fin

    def mostrar(self, estado):
        tablero = estado.tablero
        for x in range(1, self.h + 1):
            fila = ""
            for y in range(1, self.v + 1):
                fila += tablero.get((x, y), ".") + " "
            print(fila)
        print()