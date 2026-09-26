#################################################################
# Nombre      : Entorno                                         #
# Version     : 0.05.03.2017                                    #
# Autor       : Victor Estevez                                  #
# Descripcion : Clase Agentes con Adversarios                   #
##################################################################


from AgenteIA.Agente import Agente
from collections import namedtuple
import time


ElEstado = namedtuple('ElEstado', 'jugador, get_utilidad, tablero, movidas')


class AgenteJugador(Agente):

    def __init__(self, altura=3):
        Agente.__init__(self)
        self.estado = None
        self.juego = None
        self.utilidad = None
        self.tecnica = "fun_eval"
        self.altura = altura

    def jugadas(self, estado):
        raise Exception("Error: No se implemento")

    def get_utilidad(self, estado, jugador):
        raise Exception("Error: No se implemento")

    def testTerminal(self, estado):
        return not self.jugadas(estado)

    def getResultado(self, estado, m):
        raise Exception("Error: No se implemento")

    def minimax(self, estado):

        def valorMax(e):
            if self.testTerminal(e):
                return self.get_utilidad(e, self.estado.jugador)
            v = -100
            for a in self.jugadas(e):
                v = max(v, valorMin(self.getResultado(e, a)))
            return v

        def valorMin(e):
            if self.testTerminal(e):
                return self.get_utilidad(e, self.estado.jugador)
            v = 100
            for a in self.jugadas(e):
                v = min(v, valorMax(self.getResultado(e, a)))
            return v

        return max(self.jugadas(estado), key=lambda a: valorMin(self.getResultado(estado, a)))

    def podaAlphaBeta(self, estado):
        jugador = estado.jugador

        def max_value(e, alpha, betita):
            if self.testTerminal(e):
                return self.get_utilidad(e, jugador)
            vm = -float('inf')
            for j in self.jugadas(e):
                vm = max(vm, min_value(self.getResultado(e, j), alpha, betita))
                if vm >= betita:
                    return vm
                alpha = max(alpha, vm)
            return vm

        def min_value(e, alpha, betita):
            if self.testTerminal(e):
                return self.get_utilidad(e, jugador)
            vm = float('inf')
            for j in self.jugadas(e):
                vm = min(vm, max_value(self.getResultado(e, j), alpha, betita))
                if vm <= alpha:
                    return vm
                betita = min(betita, vm)
            return vm

        mejor_score = -float('inf')
        alpha = -float('inf')
        beta = float('inf')
        mejor_accion = None
        for a in self.jugadas(estado):
            v = min_value(self.getResultado(estado, a), alpha, beta)
            if v > mejor_score:
                mejor_score = v
                mejor_accion = a
            alpha = max(alpha, mejor_score)
        return mejor_accion

    def funcion_evaluacion(self, estado, jugador=None, profundidad=None):
        raise Exception("no se implemento")

    def podaAlphaBeta_eval(self, estado, altura=None):
        limite_altura = self.altura if altura is None else altura
        jugador_raiz = estado.jugador

        def max_value(e, alpha, betita, prof):
            if self.testTerminal(e):
                return self.get_utilidad(e, jugador_raiz) * 100000
            if prof >= limite_altura:
                return self.funcion_evaluacion(e, jugador=jugador_raiz, profundidad=prof)

            vm = -float('inf')
            for j in self.jugadas(e):
                vm = max(vm, min_value(self.getResultado(e, j), alpha, betita, prof + 1))
                if vm >= betita:
                    return vm
                alpha = max(alpha, vm)
            return vm

        def min_value(e, alpha, betita, prof):
            if self.testTerminal(e):
                return self.get_utilidad(e, jugador_raiz) * 100000
            if prof >= limite_altura:
                return self.funcion_evaluacion(e, jugador=jugador_raiz, profundidad=prof)

            vm = float('inf')
            for j in self.jugadas(e):
                vm = min(vm, max_value(self.getResultado(e, j), alpha, betita, prof + 1))
                if vm <= alpha:
                    return vm
                betita = min(betita, vm)
            return vm

        mejor_score = -float('inf')
        alpha = -float('inf')
        beta = float('inf')
        mejor_accion = None

        for accion in self.jugadas(estado):
            v = min_value(self.getResultado(estado, accion), alpha, beta, 1)
            if v > mejor_score:
                mejor_score = v
                mejor_accion = accion
            alpha = max(alpha, mejor_score)

        return mejor_accion

    def expectimax(self, estado, profundidad, es_turno_jugador):
        if self.testTerminal(estado) or profundidad == self.max_profundidad:
            return self.funcion_evaluacion(estado)

        if es_turno_jugador:
            max_valor = -float('inf')
            for movida in self.jugadas(estado):
                nuevo_estado = self.getResultado(estado, movida)
                valor = self.expectimax(nuevo_estado, profundidad + 1, False)
                max_valor = max(max_valor, valor)
            return max_valor
        else:
            suma_valores = 0
            jugadas = self.jugadas(estado)
            probabilidad = 1 / len(jugadas)  # Supone que cada movimiento es igualmente probable

            for movida in jugadas:
                nuevo_estado = self.getResultado(estado, movida)
                valor = self.expectimax(nuevo_estado, profundidad + 1, True)
                suma_valores += valor * probabilidad

            return suma_valores

    def expectiminimax(self, estado, profundidad, es_turno_jugador):
        if self.testTerminal(estado) or profundidad == self.max_profundidad:
            return self.funcion_evaluacion(estado)

        if es_turno_jugador:  # Nodo de Maximización (turno del jugador)
            max_valor = -float('inf')
            for movida in self.jugadas(estado):
                nuevo_estado = self.getResultado(estado, movida)
                valor = self.expectiminimax(nuevo_estado, profundidad + 1, False)
                max_valor = max(max_valor, valor)
            return max_valor

        else:  # Nodo de Minimización o Expectación (turno del oponente o azar)
            if self.es_nodo_minimizacion(estado):
                min_valor = float('inf')
                for movida in self.jugadas(estado):
                    nuevo_estado = self.getResultado(estado, movida)
                    valor = self.expectiminimax(nuevo_estado, profundidad + 1, True)
                    min_valor = min(min_valor, valor)
                return min_valor
            else:
                suma_valores = 0
                jugadas = self.jugadas(estado)
                probabilidad = 1 / len(jugadas)  # Supone que cada movimiento es igualmente probable

                for movida in jugadas:
                    nuevo_estado = self.getResultado(estado, movida)
                    valor = self.expectiminimax(nuevo_estado, profundidad + 1, True)
                    suma_valores += valor * probabilidad

                return suma_valores

    def mide_tiempo(funcion):
        def funcion_medida(*args, **kwards):
            inicio = time.time()
            c = funcion(*args, **kwards)
            print("Tiempo de ejecucion: ", time.time() - inicio)
            return c

        return funcion_medida

    @mide_tiempo
    def programa(self):
        if self.tecnica == "minimax":
            self.set_acciones(self.minimax(self.estado))
        elif self.tecnica == "podaalfabeta":
            self.set_acciones(self.podaAlphaBeta(self.estado))
        elif self.tecnica == "fun_eval":
            self.set_acciones(self.podaAlphaBeta_eval(self.estado, self.altura))
