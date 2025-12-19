import random 

def pausa():
    input("Presione Enter para continuar")

def Ejercicio3(): 
    n = int(input("Ingrese el numero de simulacion es a realizar: "))
    exitos = 0 

    mazo = []
    for i in range(1, 14): #cartas del 1 al 13
        mazo += [i] * 4 #4 palos por cada valor, corazones, diamantes, treboles, espadas
    
    for i in range(n):
        mano = random.sample(mazo, 5) #se reparten 5 cartas al azar sin reemplazo
        s = sum(mano) 

        if 17 <= s <= 21:
            exitos += 1

    p = exitos / n
    print("La probabilidad simulada de obtener una mano con suma entre 17 y 21 es:", p)
    pausa()
  

Ejercicio3()