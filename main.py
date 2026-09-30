from AgenteTresEnRaya import AgenteTresEnRaya
from Tablero import Tablero
from HumanoTresEnRaya import HumanoTresEnRaya

if __name__ == "__main__":
    N = 3
    ALTURA = 3

    print(f"=== TRES EN RAYA ({N}x{N}) - Profundidad de búsqueda: {ALTURA} ===")

    jugador_humano = HumanoTresEnRaya(n=N)
    
    agente_ia = AgenteTresEnRaya(n=N, altura=ALTURA)
    agente_ia.tecnica = "fun_eval"

    tablero = Tablero(n=N)
    tablero.insertar(jugador_humano)
    tablero.insertar(agente_ia)

    tablero.run()
