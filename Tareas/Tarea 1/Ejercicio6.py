#Ejercicio 6
#Se reparten 5 cartas 
#Dentro de esas 5 cartas, se encuentra un par de ases 
import random
from math import comb

def pausa():
    input("Presione Enter para continuar")

def menu():
    while True:
        print("Par de Ases en 5 cartas")
        print("1) Calcular la probabilidad teorica")
        print("2) Ejecutar simulación")
        print("3) Salir")

        op = input("Opcion: ").strip()
        if op == "1":
            ejercicio_a()
            pausa()
        elif op == "2":
            ejercicio_b()
            pausa()
        elif op == "3":
            break
        else:
            print("Opcion no valida, intente de nuevo.")

def ejercicio_a():
    #Calcular la probabilidad teorica 
    p = (comb(4,2) * comb(48,3)) / comb(52,5)
    print("La probabilidad teorica de obtener un par de ases en 5 cartas es:", p)

def ejercicio_b():
    n = int(input("Ingrese el numero de simulaciones a realizar: "))
    exitos = 0

    for _ in range(n):
        mazo = ['A']*4 + ['N']*48  # Se crea el mazo con 4 ases y 48 no ases
        mano = random.sample(mazo, 5)  #Reparte 5 cartas al azar sin reemplazo
        if sum(mano) == 2: #Cuenta si hay exactamente 2 ases
            exitos += 1

    p = exitos / n 
    print("La simulación es ", p)


