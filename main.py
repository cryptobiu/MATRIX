from Matrix import MatrixMenu
import sys


def main():
    menu = MatrixMenu()
    if len(sys.argv) == 2:
        menu.run(sys.argv[1])
    else:
        menu.run()


if __name__ == '__main__':
    main()
