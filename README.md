# PokeFisi

Simulador de combates por turnos estilo Pokémon con agentes de Inteligencia Artificial. Permite jugar Humano vs IA o enfrentar dos IAs entre sí, tanto desde una interfaz gráfica como desde la terminal.

---

## Requisitos del sistema

- Python 3.10 o superior
- Sistema operativo Linux (probado en Debian/Ubuntu)
- Conexión a internet solo para la instalación de dependencias

---

## Instalación paso a paso

### 1. Clonar el repositorio

```bash
git clone https://github.com/Sergio-Osorio09/PokeFisi.git
cd PokeFisi
```

### 2. Instalar dependencias del sistema para pygame

pygame necesita las bibliotecas SDL2 instaladas en el sistema. Ejecuta esto **una sola vez**:

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv libsdl2-dev libsdl2-image-dev libsdl2-ttf-dev
```

> Si ya tienes `python3-pip` y `python3-venv` instalados puedes omitir el `apt update` y solo instalar las dependencias SDL2.

### 3. Crear el entorno virtual

Un entorno virtual aísla las dependencias del proyecto del resto del sistema. Créalo dentro de la carpeta del proyecto:

```bash
python3 -m venv venv
```

Esto genera una carpeta llamada `venv/` con una instalación de Python independiente.

### 4. Activar el entorno virtual

Cada vez que abras una nueva terminal debes activar el entorno antes de usar el proyecto:

```bash
source venv/bin/activate
```

Sabrás que está activo porque el prompt de la terminal mostrará `(venv)` al inicio:

```
(venv) usuario@maquina:~/PokeFisi$
```

### 5. Instalar las dependencias de Python

Con el entorno virtual activo, instala las librerías necesarias:

```bash
pip install -r requirements.txt
```

Esto instala `pygame` y `pytest`. El proceso tarda aproximadamente un minuto dependiendo de la conexión.

---

## Ejecutar el juego

Asegúrate de tener el entorno virtual activo (`source venv/bin/activate`) antes de ejecutar cualquiera de estos comandos.

### Modo interfaz gráfica (recomendado)

```bash
python3 main.py --gui
```

Abre una ventana con menú, selección de Pokémon y pantalla de combate interactiva.

### Modo consola (solo texto, sin entorno gráfico)

```bash
python3 main.py --console
```

Útil para jugar desde una terminal SSH o en sistemas sin entorno de escritorio. Todo el juego se controla con el teclado.

### Ver los modos disponibles

```bash
python3 main.py
```

Muestra el mensaje de ayuda con los argumentos aceptados.

---

## Cómo jugar

### Modo GUI

1. En el **menú principal** selecciona `NUEVA BATALLA`.
2. Elige el modo de juego: `HUMANO vs IA` o `IA vs IA`.
3. Si elegiste `HUMANO vs IA`, selecciona con qué IA quieres enfrentarte (Agente Aleatorio o Heurística Básica).
4. Elige el tamaño del equipo (`3 vs 3` o `4 vs 4`) y pulsa `CONTINUAR`.
5. En la pantalla de selección elige tu equipo haciendo clic en las tarjetas de Pokémon. Usa la **rueda del ratón** o la **barra lateral** para desplazarte y ver los 30 Pokémon.
6. Una vez completado tu equipo, elige el equipo rival y pulsa `INICIAR BATALLA`.
7. Durante el combate pulsa los botones de movimiento para atacar o `CAMBIAR POKEMON` para cambiar al siguiente.

### Modo Consola

El juego guía con menús numerados. Escribe el número de la opción y pulsa `Enter`. Para elegir Pokémon ingresa los IDs separados por espacios (por ejemplo: `1 5 12`).

---

## Agentes de IA disponibles

| Agente | Descripción |
|---|---|
| **Agente Aleatorio** | Elige movimientos y cambios completamente al azar. Sirve como línea base de comparación. |
| **Heurística Básica** | Evalúa cada acción posible y elige la que maximiza su HP propio mientras reduce el del oponente. |

---

## Estructura del proyecto

```
PokeFisi/
├── main.py          # Punto de entrada — detecta --gui o --console
├── config.py        # Constantes globales (resolución, FPS, factor K)
├── requirements.txt # Dependencias pip
├── data/
│   ├── pokemon.json # 30 Pokémon con stats y movimientos
│   └── moves.json   # 72 movimientos con tipo, poder y precisión
├── engine/          # Motor de combate (lógica pura, sin GUI)
├── ai/              # Agentes de inteligencia artificial
├── console/         # Modo consola (texto puro)
├── gui/             # Interfaz gráfica con pygame
│   ├── screens/     # Pantallas: menú, selección, combate, resultados
│   └── components/  # Botón, barra HP, tarjeta Pokémon, log de batalla
├── assets/          # Carpetas para sprites y fuentes (vacías por defecto)
└── tests/           # Tests unitarios del motor de combate
```

---

## Ejecutar los tests

Con el entorno virtual activo:

```bash
python3 -m pytest tests/ -v
```

Verifica que la fórmula de daño, la tabla de tipos y el flujo de batalla funcionen correctamente.

---

## Desactivar el entorno virtual

Cuando termines de usar el proyecto:

```bash
deactivate
```

---

## Solución de problemas comunes

**`ModuleNotFoundError: No module named 'pygame'`**
El entorno virtual no está activo. Ejecuta `source venv/bin/activate` y vuelve a intentarlo.

**`pygame.error: No available video device`**
Estás en un sistema sin entorno gráfico. Usa el modo consola: `python3 main.py --console`.

**`pygame` falla al instalarse con pip**
Instala las dependencias SDL2 del sistema con el comando del paso 2 y vuelve a ejecutar `pip install -r requirements.txt`.
