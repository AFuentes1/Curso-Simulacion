#Ejercicio 5
def pause():
    input("Presiona Enter para continuar...")

e5 = [(5, 7, 0, 2**6), (11, 9, 0, 2**7), (221, 3, 0, 10**3), (203, 17, 0, 10**5), (211, 19, 0, 10**8)]

def menu():
    print("Generador congruencial mixto")
    for i in range (1, 6):
        print(f"{i}. x(0) = {e5[i-1][0]}")
    print("6. Salir")

    op = int(input("Selecciona una opción: ")) - 1

    if op < 6:
        congruecial_mixto(
            nombre = "5" + chr(97 + op),
            a = e5[op][1],
            x0 = e5[op][0],
            c = 0,
            m = e5[op-1][3])
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
    print(f"Recorrido: {recorrido}")
    print(f"Período del ciclo: {periodo_ciclo}")
    print(f"Módulo (m): {m}\n")

    if cumple_periodo_completo:
        print("Si cumple con todo el período de m")
    else:
        print("No cumple con todo el período de m")
    pause()
    menu()

menu()