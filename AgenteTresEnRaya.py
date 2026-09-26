from AgenteIA.AgenteJugador import AgenteJugador
from AgenteIA.AgenteJugador import ElEstado


class AgenteTresEnRaya(AgenteJugador):

    def __init__(self, n=3, altura=3):
        AgenteJugador.__init__(self, altura=altura)
        self.n = n
        self.h = n
        self.v = n
        self.k = n
        self.tecnica = "fun_eval"
        # Precalculamos ventanas y pesos posicionales para máxima velocidad
        self.ventanas = self._generar_ventanas()
        self.mapa_posicional = self._generar_mapa_posicional()

    def jugadas(self, estado):
        # Move Ordering: Priorizar casillas centrales y cercanas al juego para podar más rápido
        centro = (self.n + 1) / 2.0
        return sorted(
            estado.movidas,
            key=lambda m: (
                -self.mapa_posicional.get(m, 0),
                abs(m[0] - centro) + abs(m[1] - centro)
            )
        )

    def getResultado(self, estado, m):
        if m not in estado.movidas:
            return ElEstado(jugador=('O' if estado.jugador == 'X' else 'X'),
                            get_utilidad=self.computa_utilidad(estado.tablero, m, estado.jugador),
                            tablero=estado.tablero, movidas=estado.movidas)
        tablero = estado.tablero.copy()
        tablero[m] = estado.jugador
        movidas = list(estado.movidas)
        movidas.remove(m)
        return ElEstado(jugador=('O' if estado.jugador == 'X' else 'X'),
                        get_utilidad=self.computa_utilidad(tablero, m, estado.jugador),
                        tablero=tablero, movidas=movidas)

    def get_utilidad(self, estado, jugador):
        return estado.get_utilidad if jugador == 'X' else -estado.get_utilidad

    def testTerminal(self, estado):
        return estado.get_utilidad != 0 or len(estado.movidas) == 0

    def mostrar(self, estado):
        tablero = estado.tablero
        print("    " + " ".join(f"{y:2}" for y in range(1, self.v + 1)))
        for x in range(1, self.h + 1):
            print(f"{x:2}  ", end="")
            for y in range(1, self.v + 1):
                val = tablero.get((x, y), '.')
                print(f" {val} ", end="")
            print()
        print()

    def computa_utilidad(self, tablero, m, jugador):
        if (self.en_raya(tablero, m, jugador, (0, 1)) or
                self.en_raya(tablero, m, jugador, (1, 0)) or
                self.en_raya(tablero, m, jugador, (1, -1)) or
                self.en_raya(tablero, m, jugador, (1, 1))):
            return +1 if jugador == 'X' else -1
        else:
            return 0

    def en_raya(self, tablero, m, jugador, delta_x_y):
        (delta_x, delta_y) = delta_x_y
        x, y = m
        n = 0
        while tablero.get((x, y)) == jugador:
            n += 1
            x, y = x + delta_x, y + delta_y
        x, y = m
        while tablero.get((x, y)) == jugador:
            n += 1
            x, y = x - delta_x, y - delta_y
        n -= 1
        return n >= self.k

    def _generar_ventanas(self):
        ventanas = []
        n, k = self.n, self.k

        # Filas horizontales
        for x in range(1, n + 1):
            for y in range(1, n - k + 2):
                ventanas.append(tuple((x, y + i) for i in range(k)))

        # Columnas verticales
        for y in range(1, n + 1):
            for x in range(1, n - k + 2):
                ventanas.append(tuple((x + i, y) for i in range(k)))

        # Diagonal principal (\)
        for x in range(1, n - k + 2):
            for y in range(1, n - k + 2):
                ventanas.append(tuple((x + i, y + i) for i in range(k)))

        # Diagonal secundaria (/)
        for x in range(1, n - k + 2):
            for y in range(k, n + 1):
                ventanas.append(tuple((x + i, y - i) for i in range(k)))

        return tuple(ventanas)

    def _generar_mapa_posicional(self):
        mapa = {}
        centro = (self.n + 1) / 2.0
        for x in range(1, self.n + 1):
            for y in range(1, self.n + 1):
                dist = max(abs(x - centro), abs(y - centro))
                if self.n == 5:
                    mapa[(x, y)] = 6 if dist == 0 else (3 if dist <= 1 else 1)
                elif self.n == 4:
                    mapa[(x, y)] = 4 if dist <= 0.5 else 1
                else:  # n == 3
                    mapa[(x, y)] = 4 if dist == 0 else 1
        return mapa

    def _contar_racha_maxima(self, fichas, simbolo):
        """Calcula la longitud máxima de fichas consecutivas dentro de la ventana."""
        max_racha = 0
        racha_actual = 0
        for f in fichas:
            if f == simbolo:
                racha_actual += 1
                if racha_actual > max_racha:
                    max_racha = racha_actual
            else:
                racha_actual = 0
        return max_racha

    def funcion_evaluacion(self, estado, jugador=None, profundidad=None):
        if jugador is None:
            jugador = estado.jugador
        oponente = 'O' if jugador == 'X' else 'X'

        if estado.get_utilidad != 0:
            return self.get_utilidad(estado, jugador) * 100000

        tablero = estado.tablero
        puntaje = 0
        k = self.k

        for ventana in self.ventanas:
            fichas = [tablero.get(pos) for pos in ventana]
            count_jugador = fichas.count(jugador)
            count_oponente = fichas.count(oponente)

            # Si ambos tienen fichas en la ventana, queda bloqueada
            if count_jugador > 0 and count_oponente > 0:
                continue

            # Ventana favorable al jugador (ataque)
            if count_jugador > 0 and count_oponente == 0:
                racha = self._contar_racha_maxima(fichas, jugador)
                if count_jugador == k:
                    puntaje += 100000
                elif count_jugador == k - 1:
                    # Racha contigua de k-1 es más amenazante
                    puntaje += 12000 if racha == k - 1 else 8000
                elif count_jugador == k - 2 and k >= 4:
                    puntaje += 700 if racha == k - 2 else 400
                elif count_jugador == k - 2 and k == 3:
                    puntaje += 60
                elif count_jugador == k - 3 and k == 5:
                    puntaje += 40
                elif count_jugador == 1:
                    puntaje += 2

            # Ventana favorable al oponente (defensa con mayor peso asimétrico)
            elif count_oponente > 0 and count_jugador == 0:
                racha = self._contar_racha_maxima(fichas, oponente)
                if count_oponente == k:
                    puntaje -= 100000
                elif count_oponente == k - 1:
                    # Penalización severa para forzar bloqueo inmediato
                    puntaje -= 18000 if racha == k - 1 else 13000
                elif count_oponente == k - 2 and k >= 4:
                    puntaje -= 1000 if racha == k - 2 else 600
                elif count_oponente == k - 2 and k == 3:
                    puntaje -= 90
                elif count_oponente == k - 3 and k == 5:
                    puntaje -= 60
                elif count_oponente == 1:
                    puntaje -= 3

        # Control posicional (centro) precalculado
        for pos, ficha in tablero.items():
            bonus = self.mapa_posicional.get(pos, 0)
            if ficha == jugador:
                puntaje += bonus
            elif ficha == oponente:
                puntaje -= bonus

        return puntaje
