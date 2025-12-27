#Ejercicio 10
import random
def pause():
    input("Presiona Enter para continuar...")

def menu():
    print("Generador aleatorio un digito")
    print("1) Moneda legal (0,1)")

    op = int(input("Selecciona una opción: "))

    if op == 1:
        Ejercicio_a()
        pause()
        menu()
    else:
        print("Opción inválida")
        pause()
        menu()
    
def Ejercicio_a():
    print("=" * 50)
    print("Ejercicio 10 a) - Generador aleatorio un digito")
    print("=" * 50)
    print("Generador: digitos del 0 y 9 uniformemente")
    print("Regal: 0-4 = Corona, 5-9 = Escudo")
    print()

    digito = random.randint(0, 9) #Genera un numero entero aleatorio entre 0 y 9 y lo guarda en digito

    if digito <= 4: #Verifica si el digito salio 0,1,2,3 o 4  
        resultado = "Corona" #si se cumple, asgina que el resultado es Corona
    else: #Entonces fue 5-9
        resultado = "Escudo" #asigna que el resultado es Escudo

    print(f"Digito generado: {digito}")
    print(f"Resultado: {resultado}")
    print()
    print("Explicación: ")
    print("  - Dígitos 0, 1, 2, 3, 4 → Corona (5 casos = 50%)")
    print("  - Dígitos 5, 6, 7, 8, 9 → Escudo (5 casos = 50%)")

menu()