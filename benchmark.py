"""
benchmark.py - Pruebas automatizadas y comparación de rendimiento para AgenteTresEnRaya.

Incluye:
1. Pruebas masivas (50-100 partidas) contra agentes basales (Aleatorio y Goloso/Greedy).
2. Comparativa de rendimiento entre profundidades (d=1, d=2, d=3, d=4).
3. Métricas de tiempos por jugada y tasa de victoria/empate/derrota.
"""

import time
import random
from collections import Counter
from AgenteTresEnRaya import AgenteTresEnRaya, ElEstado


class AgenteAleatorio(AgenteTresEnRaya):
    """Agente que elige movimientos completamente al azar."""
    def __init__(self, n=3):
        super().__init__(n=n)
        self.nombre = "Aleatorio"

    def elegir_movida(self, estado):
        return random.choice(estado.movidas) if estado.movidas else None


class AgenteGoloso(AgenteTresEnRaya):
    """Agente Greedy / Profundidad 1:
    - Si puede ganar en el turno, lo hace.
    - Si el rival puede ganar en el siguiente, bloquea.
    - Si no, toma la mejor casilla según la función heurística inmediata.
    """
    def __init__(self, n=3):
        super().__init__(n=n, altura=1)
        self.nombre = "Goloso (Greedy)"

    def elegir_movida(self, estado):
        jugador = estado.jugador
        oponente = 'O' if jugador == 'X' else 'X'

        # 1. ¿Puedo ganar en este turno?
        for m in estado.movidas:
            res = self.getResultado(estado, m)
            if self.testTerminal(res) and self.get_utilidad(res, jugador) > 0:
                return m

        # 2. ¿El oponente ganaría en el siguiente turno si juega ahí? (bloquear)
        for m in estado.movidas:
            # Simular tiro del oponente
            tablero_sim = estado.tablero.copy()
            tablero_sim[m] = oponente
            if self.computa_utilidad(tablero_sim, m, oponente) != 0:
                return m

        # 3. Elegir la jugada con mejor puntaje heurístico inmediato
        mejor_puntaje = -float('inf')
        mejor_mov = estado.movidas[0]
        for m in estado.movidas:
            res = self.getResultado(estado, m)
            score = self.funcion_evaluacion(res, jugador=jugador)
            if score > mejor_puntaje:
                mejor_puntaje = score
                mejor_mov = m
        return mejor_mov


def simular_partida(agente_x, agente_o, n=3):
    """Simula una partida completa entre dos agentes en un tablero nxn."""
    movidas_iniciales = [(x, y) for x in range(1, n + 1) for y in range(1, n + 1)]
    estado = ElEstado(jugador='X', get_utilidad=0, tablero={}, movidas=movidas_iniciales)

    ref_agente = AgenteTresEnRaya(n=n)
    tiempos_x = []
    tiempos_o = []

    while True:
        if ref_agente.testTerminal(estado):
            break

        turno_actual = estado.jugador
        if turno_actual == 'X':
            agente = agente_x
            t_lista = tiempos_x
        else:
            agente = agente_o
            t_lista = tiempos_o

        t0 = time.perf_counter()
        if hasattr(agente, 'elegir_movida'):
            mov = agente.elegir_movida(estado)
        else:
            mov = agente.podaAlphaBeta_eval(estado, altura=agente.altura)
        t1 = time.perf_counter()
        t_lista.append(t1 - t0)

        if mov is None or mov not in estado.movidas:
            # Movimiento inválido (derrota automática)
            utilidad_ganador = -1 if turno_actual == 'X' else 1
            estado = ElEstado(jugador=('O' if turno_actual == 'X' else 'X'),
                              get_utilidad=utilidad_ganador,
                              tablero=estado.tablero, movidas=[])
            break

        estado = ref_agente.getResultado(estado, mov)

    ganador = "Empate"
    if estado.get_utilidad > 0:
        ganador = "X"
    elif estado.get_utilidad < 0:
        ganador = "O"

    return {
        "ganador": ganador,
        "tiempos_x": tiempos_x,
        "tiempos_o": tiempos_o,
        "turnos_totales": len(tiempos_x) + len(tiempos_o)
    }


def ejecutar_torneo(nombre_test, agente_principal, agente_rival, total_partidas=100, n=3):
    """Ejecuta un torneo de N partidas alternando el jugador que inicia (X vs O)."""
    print(f"\n========================================================")
    print(f" TORNEO: {nombre_test} (Tablero {n}x{n}, Total partidas: {total_partidas})")
    print(f"========================================================")

    victorias_principal = 0
    derrotas_principal = 0
    empates = 0
    tiempos_principal = []

    mitad = total_partidas // 2

    # Fase 1: Agente principal juega como 'X' (inicia)
    for _ in range(mitad):
        res = simular_partida(agente_principal, agente_rival, n=n)
        tiempos_principal.extend(res["tiempos_x"])
        if res["ganador"] == "X":
            victorias_principal += 1
        elif res["ganador"] == "O":
            derrotas_principal += 1
        else:
            empates += 1

    # Fase 2: Agente principal juega como 'O' (segundo)
    for _ in range(total_partidas - mitad):
        res = simular_partida(agente_rival, agente_principal, n=n)
        tiempos_principal.extend(res["tiempos_o"])
        if res["ganador"] == "O":
            victorias_principal += 1
        elif res["ganador"] == "X":
            derrotas_principal += 1
        else:
            empates += 1

    t_prom = (sum(tiempos_principal) / len(tiempos_principal)) * 1000 if tiempos_principal else 0

    print(f"  Resultados para Agente Principal:")
    print(f"  - Victorias : {victorias_principal:3d} ({victorias_principal / total_partidas * 100:.1f}%)")
    print(f"  - Empates   : {empates:3d} ({empates / total_partidas * 100:.1f}%)")
    print(f"  - Derrotas  : {derrotas_principal:3d} ({derrotas_principal / total_partidas * 100:.1f}%)")
    print(f"  - Tiempo prom/jugada: {t_prom:.2f} ms")
    return victorias_principal, empates, derrotas_principal, t_prom


def comparar_profundidades(profundidades=(1, 2, 3, 4), partidas_por_duelo=20, n=3):
    """Realiza un torneo cruzado entre diferentes profundidades."""
    print(f"\n========================================================")
    print(f" COMPARATIVA DE PROFUNDIDADES (Tablero {n}x{n})")
    print(f" Duelo por pares: {partidas_por_duelo} partidas (10 como X, 10 como O)")
    print(f"========================================================")

    # 1. Medir tiempo de respuesta y jugadas
    print(f"\n--- Enfrentamientos Cruzados ---")
    tabla_enfrentamientos = []
    
    for i, d1 in enumerate(profundidades):
        for d2 in profundidades[i + 1:]:
            a1 = AgenteTresEnRaya(n=n, altura=d1)
            a2 = AgenteTresEnRaya(n=n, altura=d2)

            v_d1 = 0
            v_d2 = 0
            emp = 0

            # 10 partidas d1 como X
            for _ in range(partidas_por_duelo // 2):
                r = simular_partida(a1, a2, n=n)
                if r["ganador"] == "X":
                    v_d1 += 1
                elif r["ganador"] == "O":
                    v_d2 += 1
                else:
                    emp += 1

            # 10 partidas d2 como X
            for _ in range(partidas_por_duelo // 2):
                r = simular_partida(a2, a1, n=n)
                if r["ganador"] == "X":
                    v_d2 += 1
                elif r["ganador"] == "O":
                    v_d1 += 1
                else:
                    emp += 1

            print(f"Profundidad {d1} vs Profundidad {d2}: P{d1} ganó {v_d1:2d} | P{d2} ganó {v_d2:2d} | Empates {emp:2d}")


def medir_tiempos_por_profundidad(n=3, profundidades=(1, 2, 3, 4)):
    """Mide los tiempos medios de cómputo en tablero inicial y medio juego."""
    print(f"\n--- Métricas de Tiempo de Cómputo por Profundidad en {n}x{n} ---")
    print(f"{'Profundidad':<12} | {'Tiempo Mov 1 (ms)':<20} | {'Tiempo Mov 2 (ms)':<20}")
    print("-" * 60)

    for d in profundidades:
        agente = AgenteTresEnRaya(n=n, altura=d)
        movidas = [(x, y) for x in range(1, n + 1) for y in range(1, n + 1)]
        e1 = ElEstado(jugador='X', get_utilidad=0, tablero={}, movidas=movidas)

        # Medición movimiento inicial
        t0 = time.perf_counter()
        agente.podaAlphaBeta_eval(e1, altura=d)
        t_m1 = (time.perf_counter() - t0) * 1000

        # Medición movimiento intermedio
        centro = ((n + 1) // 2, (n + 1) // 2)
        tab_intermedio = {centro: 'X'}
        mov_intermedio = [m for m in movidas if m != centro]
        e2 = ElEstado(jugador='O', get_utilidad=0, tablero=tab_intermedio, movidas=mov_intermedio)
        
        t0 = time.perf_counter()
        agente.podaAlphaBeta_eval(e2, altura=d)
        t_m2 = (time.perf_counter() - t0) * 1000

        print(f"d = {d:<9} | {t_m1:17.2f} ms | {t_m2:17.2f} ms")


if __name__ == "__main__":
    # 1. Torneo 100 partidas vs Agente Aleatorio en 3x3 y 5x5
    ia_d3_3x3 = AgenteTresEnRaya(n=3, altura=3)
    aleatorio_3x3 = AgenteAleatorio(n=3)
    ejecutar_torneo("IA (Profundidad 3) vs Agente Aleatorio", ia_d3_3x3, aleatorio_3x3, total_partidas=100, n=3)

    # 2. Torneo 50 partidas vs Agente Goloso (Greedy) en 3x3
    goloso_3x3 = AgenteGoloso(n=3)
    ejecutar_torneo("IA (Profundidad 3) vs Agente Goloso (Greedy)", ia_d3_3x3, goloso_3x3, total_partidas=50, n=3)

    # 3. Torneo 50 partidas vs Agente Aleatorio en 5x5
    ia_d3_5x5 = AgenteTresEnRaya(n=5, altura=3)
    aleatorio_5x5 = AgenteAleatorio(n=5)
    ejecutar_torneo("IA (Profundidad 3) vs Agente Aleatorio", ia_d3_5x5, aleatorio_5x5, total_partidas=50, n=5)

    # 4. Comparativa de Profundidades (d=1, 2, 3, 4) en 3x3
    comparar_profundidades(profundidades=(1, 2, 3, 4), partidas_por_duelo=20, n=3)

    # 5. Métricas de tiempos de cómputo en 3x3 y 5x5
    medir_tiempos_por_profundidad(n=3, profundidades=(1, 2, 3, 4))
    medir_tiempos_por_profundidad(n=5, profundidades=(1, 2, 3))
