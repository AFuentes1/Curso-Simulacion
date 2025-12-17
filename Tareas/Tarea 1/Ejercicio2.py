import math
import random

def menu():
    while True:
        print("\n EJERCICIO 2 (3 monedas) ")
        print("a) Probabilidad matemática de obtener 2 coronas")
        print("b) Simulación: probabilidad de obtener 0 coronas")
        print("c) Simulación: probabilidad de obtener 1 corona")
        print("d) Simulación: probabilidad de obtener 2 coronas")
        print("e) Simulación: probabilidad de obtener 3 coronas")
        print("f) Tipo de distribución de probabilidad")
        print("0) Salir")

        op = input("Elija una opción: ").strip().lower()

        if op == "0":
            print("Saliendo...")
            break
        elif op == "a":
            Ejercicio_a()
        elif op == "b":
            Ejercicio_b()
            pausa()
        elif op == "c":
            Ejercicio_c()
            pausa()
        elif op == "d":
            Ejercicio_d()
            pausa()
        elif op == "e":
            Ejercicio_e()
            pausa()
        elif op == "f":
            Ejercicio_f()
            pausa()
        
        else:
            print("Opción inválida. Intente de nuevo.")

def pausa():
    input("Presione enter para continuar ")

#Obtener 2 coronas, con probabilidad matematica
def Ejercicio_a():
    p = 3 * (0.5 ** 3) #hay 3 formas 3 *(0.5 ^ 3)
    print(p) 
    pausa()

#Probabilidad de obtener 0 coronas
def Ejercicio_b():
    n = int(input("cantidad de simulaciones: "))
    conteo_0 = 0
    for _ in range (n):
        coronas = 0
        for _ in range(3):
            moneda = random.randint(0, 1) #devuelve un entero al azar
            coronas += moneda
        if coronas == 0: 
            conteo_0 += 1 
    p = conteo_0 / n 
    print ("probabilidad de 0 coronas es ", p)

#Probabilidad de obtener 1 corona
def Ejercicio_c():
    n = int(input("Cantidad de simulaciones "))
    conteo_1 = 0

    for _ in range(n): #Repite n veces (Tirar 3 monesdas)
        coronas = 0
        for _ in range(3): #Tira las 3 monedas y suma cuantas salieron 
            moneda = random.randint(0, 1)
            coronas += moneda 
        
        if coronas == 1: 
            conteo_1 += 1

    p = conteo_1 / n
    print ("Probabilidad de que salga 1 corona: ", p)


def Ejercicio_d():
    n = int(input("cantidad de simulaciones: "))
    conteo_2 = 0

    for _ in range (n):
        coronas = 0
        for _ in range(3):
            moneda = random.randint(0,1)
            coronas += moneda 
        if coronas == 2:  
            conteo_2 += 1
    p = conteo_2 / n
    print("Probilidad de 2 coronas es: ", p)


#Calcule la probabilidad de 3 coronas 
def Ejercicio_e():
    n = int(input("cantidad de simulaciones: "))
    conteo_3 = 0

    for _ in range (n):
        coronas = 0
        for _ in range(3):
            moneda = random.randint(0,1)
            coronas += moneda 
        if coronas == 3:  
            conteo_3 += 1
    p = conteo_3 / n
    print("Probilidad de 3 coronas es: ", p)

def Ejercicio_f():
    print("La clase de distribución de probabilidad usada es la binomial (n=3, p=0.5), esto debido a que")
    

if __name__ == "__main__":
    menu()