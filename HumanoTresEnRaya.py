from AgenteTresEnRaya import AgenteTresEnRaya


class HumanoTresEnRaya(AgenteTresEnRaya):
    def __init__(self, n=3):
        AgenteTresEnRaya.__init__(self, n=n)

    def programa(self):
        print("Jugadas permitidas: {}".format(self.jugadas(self.estado)))
        print("")
        cad_movida = input('jugada (ej: 1,1 o (1, 1)): ').strip()
        try:
            if not cad_movida.startswith('('):
                cad_movida = f"({cad_movida})"
            movida = eval(cad_movida)
        except Exception:
            movida = None
        self.set_acciones(movida)
