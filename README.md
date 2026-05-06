# PokeFisi

Simulador de combates por turnos estilo Pokémon con agentes de Inteligencia Artificial. Permite jugar Humano vs IA o enfrentar dos IAs entre sí, tanto desde una interfaz gráfica como desde la terminal.

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

Abre una ventana con menú, selección de Pokémon y pantalla de combate interactiva.

### Modo consola (solo texto, sin entorno gráfico)

| Sistema | Comando |
|---|---|
| Windows | `python main.py --console` |
| Linux | `python3 main.py --console` |

Útil para jugar desde una terminal sin entorno de escritorio. Todo el juego se controla con el teclado.

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

| Sistema | Comando |
|---|---|
| Windows | `python -m pytest tests/ -v` |
| Linux | `python3 -m pytest tests/ -v` |

Verifica que la fórmula de daño, la tabla de tipos y el flujo de batalla funcionen correctamente.

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
