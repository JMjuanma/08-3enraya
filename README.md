# 08-3enraya: Agente IA con Poda Alfa-Beta y Heurística Adaptable ($3\times 3$ a $5\times 5$)

Implementación de un Agente Inteligente para el juego de Tres en Raya (y $N$ en Raya) capaz de jugar en tableros de $3\times 3$, $4\times 4$ y $5\times 5$ utilizando búsqueda con **Poda Alfa-Beta** optimizada, ordenamiento de movimientos (*Move Ordering*) y una **función de evaluación heurística exponencial y asimétrica**.

---

## Características Principales

1. **Tableros Dinámicos ($3\times 3$, $4\times 4$, $5\times 5$):**
   - Configurable para cualquier dimensión $N\times N$ donde la condición de victoria es alinear $N$ fichas.
2. **Poda Alfa-Beta con Profundidad Configurable:**
   - Profundidad por defecto: **`altura = 3`**.
   - Tiempo de respuesta menor a $20\text{ ms}$ en tableros de $5\times 5$.
3. **Move Ordering (Ordenamiento de Jugadas):**
   - Explora primero las casillas con mayor influencia estratégica y cercanía al centro, maximizando las podas tempranas en el árbol de búsqueda.
4. **Función Evaluadora Heurística:**
   - **Ventanas Viables:** Evalúa solo líneas no bloqueadas de tamaño $k$.
   - **Pesos Exponenciales:** Escala de puntos para rachas contiguas vs no contiguas.
   - **Asimetría Defensiva:** Mayor penalización a las amenazas del rival para priorizar bloqueos críticos.
   - **Control Posicional:** Bonificación por ocupación de casillas centrales.

---

## Estructura del Proyecto

* [`main.py`](main.py): Punto de entrada para jugar partidas locales (Humano vs IA).
* [`AgenteTresEnRaya.py`](AgenteTresEnRaya.py): Agente inteligente con la función evaluadora, heurística y ventanas.
* [`Tablero.py`](Tablero.py): Entorno de simulación del tablero $N\times N$.
* [`HumanoTresEnRaya.py`](HumanoTresEnRaya.py): Interfaz para jugadas del usuario.
* [`benchmark.py`](benchmark.py): Batería de pruebas automatizadas (100 partidas vs Aleatorio, Greedy y comparativa de profundidades).
* [`ServidorTresEnRaya.py`](ServidorTresEnRaya.py) y [`ClienteTresEnRaya.py`](ClienteTresEnRaya.py): Modo de juego distribuido cliente/servidor por sockets.

---

## Ejecución

### 1. Partida Local (Humano vs IA)
```bash
python3 main.py
```
*(Puedes cambiar `N` y `ALTURA` editando `main.py`).*

### 2. Ejecutar Pruebas Automatizadas y Benchmarks
```bash
python3 benchmark.py
```

### 3. Modo Cliente / Servidor
```bash
# Terminal 1: Servidor
python3 ServidorTresEnRaya.py

# Terminal 2: Cliente
python3 ClienteTresEnRaya.py
```

---

## Resultados del Benchmark

* **Vs. Agente Aleatorio ($3\times 3$, 100 partidas):** 96% Victorias, 4% Empates, **0% Derrotas** ($1.25\text{ ms}$/jugada).
* **Vs. Agente Goloso / Greedy ($3\times 3$, 50 partidas):** 100% Empates, **0% Derrotas** (juego óptimo).
* **Vs. Agente Aleatorio ($5\times 5$, 50 partidas):** 80% Victorias, 20% Empates, **0% Derrotas** ($20.25\text{ ms}$/jugada).
