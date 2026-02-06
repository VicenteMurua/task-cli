import sys


def main():
    # sys.argv[0] es siempre el nombre del archivo/comando
    # sys.argv[1:] son los argumentos que tú escribes
    args = sys.argv[1:]

    if len(args) == 0:
        print("Hola, estás usando el CLI de tareas (0 argumentos)")

    elif len(args) == 1:
        print(f"Se recibio el argumento: {args[0]}")

    else:
        print("Se recibieron varios argumentos, pero solo esperaba uno.")
        print(f"Los argumentos fueron: {args}")


if __name__ == "__main__":
    main()