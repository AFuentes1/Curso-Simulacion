import random

def generar_numeros_rango0_1(cantidad = 1000000):
    return [random.random() for _ in range(cantidad)]

def generar_numeros_int(cantidad = 1000000, a = 1, b = 6):
    return [random.randint(a, b) for _ in range(cantidad)]

if __name__ == "__main__":
    
    n = 1000000

    with open("python_u01.txt", "w") as archivo:
        for i in generar_numeros_rango0_1(n):
            archivo.write(f"{i}\n")

    with open("python_u1_6.txt", "w") as archivo:
        for i in generar_numeros_int(n, 1, 6):
            archivo.write(f"{i}\n")