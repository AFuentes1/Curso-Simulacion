import random

def pausa():
    input("Presione enter para continuar ")

def menu():
    while True: 

        print("Ejercicio 4: 2 cartas y ambas ases")
        print ("1) Probabilidad teórica")
        print("2) Ejecutar Simulacion")
        print("3) Salir")

        op = input("Opcion: ").strip() #.strip quita espacios en la entrada
        
        if op == "1": 
            Ejercicio_a()
            pausa()
        
        elif op == "2":
            Ejerciciob()
            pausa()
        elif op == "3":
            break
        else: 
            print("Opcion invalida ")
            pausa()


def Ejercicio_a():
    prob_teorica = (4/52) * (3/51)
    print("La probabilidad teorica es ", prob_teorica)


def Ejerciciob():
    n = int(input("Cuantas simulaciones desea ejecutar ").strip())
    exitos = 0 
    mazo = [1]*4 + [0]*48 #Representación del mazo 
    for _ in range(n):
        c1, c2 = random.sample(mazo, 2) #Sacar 2 cartas y que ambas sean ases
        if c1 == 1 and c2 == 1: 
            exitos += 1 
    p = exitos / n 
    print("La simulación es igual a ", p)
    

    
menu()