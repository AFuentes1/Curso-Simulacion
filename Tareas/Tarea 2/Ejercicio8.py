#Ejercicio 8 
#Defina los parametros de a, c, x0 para un recorrido completo para un valor de m = 19
def ejercicio_8():
    # Parámetros para recorrido completo con m = 19
    x0 = 0
    a  = 20
    c  = 1
    m  = 19

    x = x0 # Valor inicial
    secuencia = [] # Lista para almacenar la secuencia generada
    vistos = {}  # Diccionario para rastrear los números ya vistos y su posición
    while x not in vistos: # Mientras no se haya visto el número
        vistos[x] = len(secuencia) # Guardar la posición donde aparece el número
        secuencia.append(x) # Agregar el número a la secuencia
        x = (a * x + c) % m # Calcular el siguiente número en la secuencia con la fórmula

    print("=" * 50)
    print("Ejercicio 8 - Recorrido completo con m = 19")
    print("=" * 50)
    print(f"x(0) = {x0}")
    print(f"x(n+1) = ({a} * x(n) + {c}) mod {m}\n")
    print(f"Secuencia generada: {secuencia}")
    print(f"Cantidad de números (distintos): {len(secuencia)}\n")

    if len(secuencia) == m:
        print("Si cumple: recorrido completo (0 a 18)")
    else:
        print("No cumple recorrido completo")
        print(f"Se repite el valor {x} (ya había salido en la posición {vistos[x]})")

ejercicio_8()