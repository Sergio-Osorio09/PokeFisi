import sys


def main():
    args = sys.argv[1:]

    if "--console" in args:
        from console.console_menu import start_console
        start_console()

    elif "--gui" in args:
        from gui.game_manager import GameManager
        game = GameManager()
        game.run()

    else:
        print("Uso:")
        print("  python3 main.py --gui       Iniciar con interfaz grafica")
        print("  python3 main.py --console   Iniciar en modo consola")


if __name__ == "__main__":
    main()
