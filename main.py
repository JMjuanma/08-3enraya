from AgenteTresEnRaya import AgenteTresEnRaya
from Tablero import Tablero
from HumanoTresEnRaya import HumanoTresEnRaya

if __name__ == "__main__":
    # Configuración del juego:
    # N puede ser de 3 hasta 5 (3x3, 4x4, 5x5)
    # ALTURA define el límite de profundidad en el árbol de búsqueda (por defecto 3)
    N = 3
    ALTURA = 3

    print(f"=== TRES EN RAYA ({N}x{N}) - Profundidad de búsqueda: {ALTURA} ===")

    jugador_humano = HumanoTresEnRaya(n=N)
    
    agente_ia = AgenteTresEnRaya(n=N, altura=ALTURA)
    agente_ia.tecnica = "fun_eval"  # Usa poda Alfa-Beta con la nueva función de evaluación

    tablero = Tablero(n=N)
    tablero.insertar(jugador_humano)
    tablero.insertar(agente_ia)

    tablero.run()
