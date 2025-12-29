from math import log10, ceil

def cuadrados_medios_4(x):
    x2 = x * x
    t = ceil((ceil(log10(x2)) - 4) / 2)
    x2 //= 10 ** t
    x2 %= 10 ** 4
    return x2

def pausa():
    input("Presiona enter para continuar...")

def menu():
    s = [3567345, 1234500012, 4567234902]
    print("Ejercicio 3 Generador de cuadrados medios")
    for i in range(len(s)):
        print(f"{i+1}) {chr(65+i)} Semilla: {s[i]}")
    print("0) Salir")

    op = int(input("Ingrese una opcion: ").strip())

    if op == 0:
        print("Saliendo...")
    elif op <= len(s) and op > 0:
        ejecutar(s[int(op)-1])
        pausa()
        menu()
    else:
        print("Opcion invalida")
        pausa()
        menu()

def ejecutar(x):
    cantidad = 50

    print("Semilla x(0): ", x)

    for n in range(1, cantidad + 1):
        x = cuadrados_medios_4(x)
        print("n = ", n, "Xn = ", f"{x:04d}")

menu()
