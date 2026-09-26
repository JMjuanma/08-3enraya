from AgenteIA.Entorno import Entorno
from AgenteIA.AgenteJugador import ElEstado


class Tablero(Entorno):

    def __init__(self, n=3):
        Entorno.__init__(self)
        self.n = n
        movidas = [(x, y) for x in range(1, n + 1) for y in range(1, n + 1)]
        self.juegoActual = ElEstado(jugador='X', get_utilidad=0, tablero={}, movidas=movidas)

    def get_percepciones(self, agente):
        agente.estado = self.juegoActual
        if agente.estado.movidas:
            agente.programa()
        if agente.testTerminal(agente.getResultado(self.juegoActual, agente.get_acciones())):
            for a in self.get_agentes():
                a.inhabilitar()

    def ejecutar(self, agente):
        self.juegoActual = agente.getResultado(self.juegoActual, agente.get_acciones())
        agente.mostrar(self.juegoActual)
        resul = self.juegoActual.get_utilidad
        if resul != 0:
            if resul > 0:
                print("Victoria para X")
            else:
                print("Victoria para O")
            agente.vive = False
