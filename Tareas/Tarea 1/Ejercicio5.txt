#Ejercicio 5
#Se tiene un mazo de cartas convencional
#a) cual es la probabilidad que al sacar una carta se obtenga una espada o un trebol 
#b) Construya un programa de simulación que genere estos resultados 
import random
def pausa():
    input("Presione Enter para continuar")

def menu():
    while True:
        print("Espada o Trebol")
        print("1) Calcular la probabilidad teorica")
        print("2) Ejecutar simulación")
        print("3) Salir")

        op = input("Opcion: ").strip()
        if op == "1":
            Ejercicio_a()
            pausa()
        elif op == "2":
            Ejercicio_b()
        elif op == "3":
            break
        else:
            print("Opcion no valida, intente de nuevo.")

def Ejercicio_a():
    p = (13 + 13) / 52 # 13 espadas y 13 treboles en un mazo de 52 cartas
    print("La probabilidad teorica de sacar una espada o un trebol es:", p)

def Ejercicio_b():
    n = int(input("Ingrese el numero de simulaciones a realizar: "))
    exitos = 0

    mazo = [1]*26 + [0]*26  #Se crea una lista con 52 elementos 
    #1 representa espada o trebol, 0 representa los demas palos


    for _ in range(n):
        carta = random.choice(mazo) #Se saca una carta al azar
        if carta == 1:
            exitos += 1
    
    p = exitos / n 
    print("Simulada = ", p)

menu()


