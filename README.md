# PokeFisi

Simulador de combates por turnos estilo Pokémon con agentes de Inteligencia Artificial. Permite jugar Humano vs IA o enfrentar dos IAs entre sí, tanto desde una interfaz gráfica como desde la terminal. Incluye seis estrategias de IA —desde elección aleatoria hasta minimax con poda alfa-beta optimizado por un algoritmo genético— y un panel que muestra en tiempo real el razonamiento de cada agente.

---

## Requisitos del sistema

- Python 3.10 o superior
- Windows 10/11 o Linux (Debian/Ubuntu y derivados)
- Conexión a internet solo para la instalación de dependencias

---

## Instalación rápida en Windows

> Esta es la forma más sencilla de poner el juego en marcha en Windows. No requiere entorno virtual.

### 1. Instalar Python

Descarga Python desde [https://www.python.org/downloads/](https://www.python.org/downloads/) e instálalo marcando la opción **"Add Python to PATH"** durante la instalación.

> **Importante:** en Windows el comando es `python`, no `python3`. Si escribes `python3` el sistema abrirá la Microsoft Store en lugar de ejecutar Python.

### 2. Clonar el repositorio

Abre **PowerShell** o **CMD** y ejecuta:

```cmd
git clone https://github.com/Sergio-Osorio09/PokeFisi.git
cd PokeFisi
```

### 3. Instalar las dependencias

```cmd
pip install -r requirements.txt
```

Esto instala `pygame`, `numpy` y `pytest`. El proceso tarda aproximadamente un minuto.

### 4. Ejecutar el juego

```cmd
python main.py --gui
```

---

## Instalación en Windows con entorno virtual (opcional)

Un entorno virtual aísla las dependencias del proyecto del resto del sistema. Es opcional, pero recomendado si tienes varios proyectos Python.

### 1. Crear el entorno virtual

```cmd
python -m venv venv
```

### 2. Activar el entorno virtual

**Opción A — CMD (recomendado, sin problemas de permisos):**

```cmd
venv\Scripts\activate.bat
```

**Opción B — PowerShell:**

```powershell
venv\Scripts\Activate.ps1
```

> Si PowerShell muestra el error `"la ejecución de scripts está deshabilitada"`, ejecuta este comando primero y luego vuelve a activar:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

Sabrás que el entorno está activo porque el prompt mostrará `(venv)` al inicio:

```
(venv) C:\Users\usuario\PokeFisi>
```

### 3. Instalar las dependencias

```cmd
pip install -r requirements.txt
```

### 4. Ejecutar el juego

```cmd
python main.py --gui
```

> Recuerda activar el entorno virtual cada vez que abras una nueva terminal antes de ejecutar el juego.

---

## Instalación en Linux (Debian/Ubuntu)

### 1. Instalar dependencias del sistema

pygame requiere las bibliotecas SDL2. Ejecuta esto **una sola vez**:

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv libsdl2-dev libsdl2-image-dev libsdl2-ttf-dev
```

### 2. Clonar el repositorio

```bash
git clone https://github.com/Sergio-Osorio09/PokeFisi.git
cd PokeFisi
```

### 3. Crear y activar el entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 5. Ejecutar el juego

```bash
python3 main.py --gui
```

---

## Ejecutar el juego

### Modo interfaz gráfica (recomendado)

| Sistema | Comando |
|---|---|
| Windows | `python main.py --gui` |
| Linux | `python3 main.py --gui` |

Abre una ventana con menú, selección de Pokémon, entrenamiento de IA y pantalla de combate interactiva.

### Modo consola (solo texto, sin entorno gráfico)

| Sistema | Comando |
|---|---|
| Windows | `python main.py --console` |
| Linux | `python3 main.py --console` |

Útil para jugar desde una terminal sin entorno de escritorio. Todo el juego se controla con el teclado.

---

## Cómo jugar

### Modo GUI

1. En el **menú principal** tienes cuatro botones: `NUEVA BATALLA`, `ENTRENAR IA GENETICA`, `ELIMINAR IAS ENTRENADAS` (borra pesos guardados con confirmación) y `SALIR`.
2. En `NUEVA BATALLA`, elige el modo: `HUMANO vs IA` o `IA vs IA`.
3. Selecciona el agente de IA con los botones `<` y `>`. La pantalla muestra la descripción del agente y, según el tipo, sus **pesos** o una **tabla de capacidades** (profundidad, fitness, etc.) para comparar fácilmente entre opciones. Los agentes entrenados aparecen aquí automáticamente con su win-rate.
4. Elige el tamaño del equipo (`3 vs 3` o `4 vs 4`) y pulsa `CONTINUAR`.
5. En la pantalla de selección elige tu equipo haciendo clic en las tarjetas de Pokémon. Usa la **rueda del ratón** o la **barra lateral** para desplazarte y ver los 30 Pokémon.
6. Una vez completado tu equipo, elige el equipo rival y pulsa `INICIAR BATALLA`.
7. Durante el combate pulsa los botones de movimiento para atacar o `CAMBIAR POKEMON` para cambiar al siguiente. A la derecha, el **panel cerebro** muestra en tiempo real qué está evaluando cada IA (ver más abajo).

### Modo Consola

El juego guía con menús numerados. Escribe el número de la opción y pulsa `Enter`. Para elegir Pokémon ingresa los IDs separados por espacios (por ejemplo: `1 5 12`).

```
╔══════════════════════════════════════════╗
║            POKEFISI  - Consola           ║
╠══════════════════════════════════════════╣
║  1. Humano vs IA                         ║
║  2. IA vs IA                             ║
║  3. Entrenar Heuristica Avanzada         ║
║  4. Entrenar Heuristica Mejorada         ║
║  5. Entrenar IA Genetica                 ║
║  6. Eliminar pesos entrenados            ║
║  7. Salir                                ║
╚══════════════════════════════════════════╝
```

Al seleccionar una IA, la consola muestra la descripción de cada agente disponible, incluyendo los entrenados que hayas generado.

---

## Agentes de IA disponibles

| Agente | Descripción |
|---|---|
| **Agente Aleatorio** | Elige movimientos y cambios completamente al azar. Línea base de comparación. |
| **Heurística Básica** | Evalúa cada acción a un solo nivel y elige la que maximiza `HP_propio − HP_rival` del Pokémon activo. |
| **Heurística Avanzada** | Evalúa **4 diferenciales** ponderados (todos en `[-1, 1]`): supervivencia, HP promedio, ventaja de tipo y velocidad. Pesos por defecto `[0.40, 0.35, 0.15, 0.10]`; un estado simétrico vale 0. |
| **Heurística Mejorada** | Evalúa **6 componentes**: supervivencia, HP ponderado, amenaza de KO, peligro de ser noqueado, cobertura de tipos del equipo y velocidad. |
| **Minimax `d=2` / `d=3`** | Búsqueda adversaria con **poda alfa-beta**. Anticipa la respuesta del rival hasta `d` turnos usando la evaluación de 4 diferenciales en las hojas. Mayor profundidad = más previsión y más coste. |
| **Expectimax `d=2`** | Variante de búsqueda que en vez de asumir el peor caso **modela al rival** con una política (por defecto la Heurística Básica) y desciende por la jugada que el rival realmente haría. Captura mejor la simultaneidad y evita el pesimismo del minimax. |
| **Genético** | El **mismo Minimax**, pero con los pesos de su evaluación **optimizados por un algoritmo genético**. Aparece como `Genetico g=… p=… d=…` tras entrenarlo. |
| **HeuristicaAvanzada-N / H.Mejorada-N** | Versiones de las heurísticas con pesos ajustados automáticamente (N batallas) mediante *hill-climbing*. Aparecen en el selector solo si previamente las entrenaste. |

---

## Visualización del razonamiento (panel cerebro)

Durante un combate con IA, la columna derecha muestra **qué está pensando** cada agente en el turno actual:

- **Aleatorio:** barras iguales (`1/N`) que dejan claro que elige al azar.
- **Heurísticas:** cada acción evaluada con su puntuación y el daño estimado.
- **Minimax:** el valor minimax de cada acción más estadísticas de búsqueda (**nodos explorados, podas alfa-beta, profundidad, tiempo**) y la **variante principal** (mi mejor acción → mejor réplica del rival).
- **Genético:** lo mismo que el Minimax, más los **4 pesos aprendidos** comparados con los de fábrica.

---

## Entrenar una IA

### Desde la consola

Ejecuta `python main.py --console` (Windows) o `python3 main.py --console` (Linux) y elige:

- **Opción 3 — Entrenar Heurística Avanzada:** ajusta sus 4 pesos por *stochastic hill-climbing* contra una mezcla de rivales. Guarda `data/weights_N.json` y crea el agente `HeuristicaAvanzada-N`.
- **Opción 4 — Entrenar Heurística Mejorada:** igual, para los 6 componentes de la Mejorada (`data/weights_improved_N.json`).
- **Opción 5 — Entrenar IA Genética:** evoluciona con un **algoritmo genético** los pesos de la evaluación que usa el **Minimax**. Pide población, generaciones, batallas por evaluación y profundidad; guarda `data/genetic_gG_pP_dD.json`.

### Desde la GUI

El botón **ENTRENAR IA GENETICA** del menú principal lanza el mismo entrenamiento genético sobre minimax con una **barra de progreso** y una **gráfica de fitness por generación**, sin congelar la interfaz, y permite **cancelar** en cualquier momento. Al terminar, el nuevo agente queda disponible en el selector sin reiniciar.

> El algoritmo genético se explica en detalle en [`docs/algoritmo_genetico.md`](docs/algoritmo_genetico.md).

---

## Estructura del proyecto

```
PokeFisi/
├── main.py               # Punto de entrada — detecta --gui o --console
├── config.py             # Constantes globales (resolución, FPS, factor K=0.25)
├── requirements.txt      # Dependencias pip
├── data/
│   ├── pokemon.json      # 30 Pokémon con stats y movimientos
│   ├── moves.json        # Movimientos con tipo, poder y precisión
│   ├── weights_*.json    # Pesos entrenados de las heurísticas (al entrenar)
│   └── genetic_*.json    # Pesos evolucionados del genético sobre minimax
├── engine/               # Motor de combate (lógica pura, sin GUI)
│   ├── pokemon.py · move.py · damage.py · loader.py
│   ├── state.py          # Estado de batalla (con copy() ligero para simular)
│   └── battle.py         # Flujo de turnos (con tope MAX_TURNS=200)
├── ai/
│   ├── base_agent.py     # Contrato abstracto de todos los agentes
│   ├── random_agent.py        # Agente Aleatorio
│   ├── heuristic_basic.py     # Heurística Básica
│   ├── heuristic_advanced.py  # Heurística Avanzada (4 diferenciales)
│   ├── heuristic_improved.py  # Heurística Mejorada (6 componentes)
│   ├── heuristic_trained.py   # Carga pesos de heurísticas entrenadas
│   ├── minimax_agent.py       # Minimax con poda alfa-beta
│   ├── expectimax_agent.py    # Expectimax: minimax que modela al rival
│   ├── genetic_agent.py       # Genético = Minimax con pesos evolucionados
│   ├── genetic_trainer.py     # Algoritmo genético sobre minimax
│   ├── trainer.py        # Entrenamiento hill-climbing de las heurísticas
│   └── registry.py       # Registro central de agentes disponibles
├── console/              # Modo consola (texto puro)
├── gui/                  # Interfaz gráfica con pygame
│   ├── screens/          # Menú, selección, combate, resultados, entrenamiento, eliminación
│   └── components/       # Botón, barra HP, tarjeta Pokémon, log de batalla
├── docs/
│   ├── algoritmo_genetico.md  # Explicación del algoritmo genético
│   └── informe/          # Informe académico (LaTeX, formato ACL)
├── assets/               # Sprites y fuentes
└── tests/                # Tests unitarios del motor de combate
```

---

## Ejecutar los tests

| Sistema | Comando |
|---|---|
| Windows | `python -m pytest tests/ -v` |
| Linux | `python3 -m pytest tests/ -v` |

Verifica que la fórmula de daño, la tabla de tipos y el flujo de batalla funcionen correctamente.

---

## Informe académico

En [`docs/informe/`](docs/informe/) está el informe del proyecto en LaTeX (formato ACL), con la metodología, los experimentos (torneo entre agentes, efecto de la profundidad y la poda alfa-beta, elitismo del genético) y sus resultados. Las figuras se reproducen con `python docs/informe/run_experiments.py` (requiere `matplotlib`, instalable con `pip install matplotlib`).

---

## Desactivar el entorno virtual

Cuando termines de usar el proyecto (solo si usas entorno virtual), en ambos sistemas:

```bash
deactivate
```

---

## Solución de problemas comunes

**`ModuleNotFoundError: No module named 'pygame'`**
Las dependencias no están instaladas en el entorno activo. Ejecuta `pip install -r requirements.txt` y vuelve a intentarlo. Si usas entorno virtual, asegúrate de activarlo primero.

**`python3` abre la Microsoft Store en Windows**
En Windows el comando correcto es `python` (sin el 3). Usa `python main.py --gui` en lugar de `python3 main.py --gui`.

**PowerShell muestra error de permisos al activar el entorno virtual**
Ejecuta `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` y vuelve a intentarlo. Alternativamente, usa CMD en lugar de PowerShell y activa con `venv\Scripts\activate.bat`.

**`pygame.error: No available video device`**
Estás en un sistema sin entorno gráfico. Usa el modo consola: `python main.py --console` (Windows) o `python3 main.py --console` (Linux).

**`pygame` falla al instalarse con pip en Linux**
Instala las dependencias SDL2 del sistema primero: `sudo apt install -y libsdl2-dev libsdl2-image-dev libsdl2-ttf-dev` y luego vuelve a ejecutar `pip install -r requirements.txt`.
