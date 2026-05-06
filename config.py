WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
FPS = 60
K = 0.5
TEAM_SIZE = 3

# Colors
WHITE    = (255, 255, 255)
BLACK    = (0,   0,   0)
GRAY     = (180, 180, 180)
DARK     = (40,  40,  40)
RED      = (220, 50,  50)
GREEN    = (60,  200, 80)
YELLOW   = (240, 200, 40)
BLUE     = (50,  120, 220)
ORANGE   = (230, 120, 40)
PURPLE   = (130, 60,  200)
BG_COLOR = (20,  20,  40)

# Type colors for rendering
TYPE_COLORS = {
    "Fire":     (240, 90,  40),
    "Water":    (60,  130, 230),
    "Grass":    (70,  190, 70),
    "Electric": (250, 210, 30),
    "Psychic":  (220, 70,  150),
    "Ghost":    (100, 80,  170),
    "Fighting": (190, 80,  40),
    "Dragon":   (80,  60,  220),
    "Ice":      (150, 220, 240),
    "Ground":   (200, 170, 80),
    "Rock":     (170, 150, 80),
    "Flying":   (150, 180, 240),
    "Bug":      (150, 190, 40),
    "Normal":   (170, 170, 140),
    "Poison":   (160, 80,  160),
    "Fairy":    (240, 150, 200),
    "Dark":     (80,  60,  50),
    "Steel":    (170, 170, 200),
}

# AI agent names
AI_NAMES = {
    1: "Agente Aleatorio",
    2: "Heurística Básica",
}

# Battle delays (ms) for IA vs IA mode in GUI
AI_TURN_DELAY = 1500
