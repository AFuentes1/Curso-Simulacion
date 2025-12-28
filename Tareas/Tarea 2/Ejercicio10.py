#Ejercicio 10
import random
def pause():
    input("Presiona Enter para continuar...")

def menu():
    print("Generador aleatorio un digito")
    print("1) Moneda legal (0,1)")
    print("2) Simulación con tres eventos")
    print("3) Simulación de lanzamiento de dado")
    print("4) Asignaciones con generador [0-99]")
    print("5) Salir")

    op = int(input("Selecciona una opción: "))

    if op == 1:
        Ejercicio_a()
        pause()
        menu()
    
    elif op == 2:
        Ejercicio_b()
        pause()
        menu()
    elif op == 3:
        Ejercicio_c()
        pause()
        menu()
    elif op == 4:
        ejercicio_10d()
        pause()
        menu()
    elif op == 5:
        print("Saliendo...")
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


def Ejercicio_b():
    print("=" * 60)
    print("Ejercicio 10b - Simulación con tres eventos")
    print("=" * 60)
    print("Generador: dígitos del 0 al 9 (uniforme)")
    print("Probabilidades: P(a)=0.10, P(b)=0.40, P(c)=0.50")
    print()
 
    digito = random.randint(0, 9) #genera un digito aleatorio entre 0 y 9

    if digito == 0: #si el digito salio 0 (1 caso de 10)
        resultado = "a" #asigna al evento a (quedo 10%)
    elif digito >= 1 and digito <= 4: #si salio 1,2,3 o 4| (4 casos de 10)
        resultado = "b" #asigna al evento b (quedo 40%)
    else: 
        resultado = "c" #si salio 5,6,7,8 o 9 (5 casos de 10) asigna al evento c (quedo 50%)

    print(f"Dígito generado: {digito}")
    print(f"Resultado: {resultado}")
    print()
    print("Explicación:")
    print("  - Dígito 0 → evento a (1 caso = 10%)")
    print("  - Dígitos 1, 2, 3, 4 → evento b (4 casos = 40%)")
    print("  - Dígitos 5, 6, 7, 8, 9 → evento c (5 casos = 50%)")

def Ejercicio_c():

    print("=" * 60)
    print("Ejercicio 10c - Simulación de lanzamiento de dado")
    print("=" * 60)
    print("Generador: dígitos del 0 al 9 (uniforme)")
    print("Objetivo: Generar valores de 1 a 6 con igual probabilidad")
    print()

    digito = random.randint(0, 9) #saca un digito aleatorio entre 0 y 9

    while digito > 5:  #si el numero salio 6,7,8 o 9 (fuera del rango) entra al ciclo para repetir
        print(f"Dígito {digito} descartado (fuera de rango)") #muestra que el digito fue descartado
        digito = random.randint(0, 9) #genera otro digito aleatorio entre 0 y 9
    resultado = digito + 1 #Si el digito es 0-5, le suma 1 para obtener un resultado entre del dado

    print(f"Dígito generado: {digito}")
    print(f"Resultado del dado: {resultado}")
    print()
    print("Explicación:")
    print("  - Dígitos 0, 1, 2, 3, 4, 5 → se convierten en 1, 2, 3, 4, 5, 6")
    print("  - Dígitos 6-9 → se descartan y se genera otro")

def ejercicio_10d():
    print("=" * 60)
    print("Ejercicio 10d - Asignaciones con generador [0-99]")
    print("=" * 60)
    print()

    print("a) Moneda legal:") 
    numero_a = random.randint(0, 99) #Genera un numero aleatorio entre 0 y 99
    if numero_a <= 49: #si el numero es entre 0 y 49
        resultado_a = "Corona" #asigna Corona
    else:
        resultado_a = "Escudo" #si es entre 50 y 99 asigna Escudo
    print(f"   Número: {numero_a} → {resultado_a}")
    print("   Regla: 0-49 = Corona (50%), 50-99 = Escudo (50%)")
    print()

    print("b) Tres eventos (a, b, c):")
    numero_b = random.randint(0, 99) #Genera un numero aleatorio entre 0 y 99
    if numero_b <= 9: #si el numero es entre 0 y 9 asigan a 
        resultado_b = "a" 
    elif numero_b <= 49: #si el numero es entre 10 y 49 asigna b
        resultado_b = "b"
    else:
        resultado_b = "c" #si es entre 50 y 99 asigna c
    print(f"   Número: {numero_b} → evento {resultado_b}")
    print("   Regla: 0-9=a (10%), 10-49=b (40%), 50-99=c (50%)")
    print()

    print("c) Dado (1-6):")
    numero_c = random.randint(0, 99) #Genera un numero aleatorio entre 0 y 99
    resultado_c = (numero_c % 6) + 1 #Aplica la regla del dado
    print(f"   Número: {numero_c} → dado = {resultado_c}") 
    print("   Regla: (número mod 6) + 1")
    print("   Alternativa: descartar si número > 5 y tomar número + 1")



menu()