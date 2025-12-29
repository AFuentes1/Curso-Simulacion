#Ejercicio 4 
def pause():
    input("Presiona Enter para continuar...")

def menu():
    print("Generador congruencial mixto")
    print("1. x(0) = 7")
    print("2. x(0) = 8")
    print("3. x(0) = 13")
    print("4. x(0) = 13")
    print("5. x(0) = 3")
    print("6. Salir")

    op = int(input("Selecciona una opción: "))

    if op == 1:
        congruecial_mixto("4a", 7, 5, 24, 32)
        pause()
    elif op == 2:
        congruecial_mixto("4b", 8, 9, 13, 32)
    elif op == 3:
        congruecial_mixto("4c", 13, 50, 17, 64)
        pause()
    elif op == 4:
        congruecial_mixto("4d", 15, 8, 16, 100)
        pause()
    elif op == 5:
        congruecial_mixto("4e", 3, 5, 21, 100)
        pause()
    elif op == 6:
        print("Saliendo...")
    else:
        print("Opción inválida")
        pause()
        menu()

def congruecial_mixto(nombre, x0, a, c, m):
    secuencia = []  # Lista para almacenar la secuencia generada
    vistos = {}  # Diccionario para rastrear los números ya vistos y su posición
    x = x0  # Valor inicial
    
    while x not in vistos:  # Mientras no se haya visto el número
        vistos[x] = len(secuencia)  # Guardar la posición donde aparece el número
        secuencia.append(x)  # Agregar el número a la secuencia
        x = (a * x + c) % m  # Calcular el siguiente número en la secuencia con la fórmula
    
    recorrido = len(secuencia)  # Cantidad de números distintos generados
    periodo_ciclo = recorrido - vistos[x]  # Calcular el período del ciclo
    cumple_periodo_completo = (periodo_ciclo == m) and (recorrido == m)  # Verificar si cumple con el período completo
    
    print("=" * 50)
    print(f"Ejercicio {nombre} - Generador Congruencial Mixto")
    print("=" * 50)
    print(f"x(0) = {x0}")
    print(f"x(n+1) = ({a} * x(n) + {c}) mod {m}\n")
    print(f"Secuencia generada: {secuencia}")
    print(f"Recorrido (distintos): {recorrido}")
    print(f"Período del ciclo: {periodo_ciclo}")
    print(f"Módulo (m): {m}\n")

    if cumple_periodo_completo:
        print("Si cumple con todo el período de m")
    else:
        print("No cumple con todo el período de m")
    pause()
    menu()





menu()