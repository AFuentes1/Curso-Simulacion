#Ejercicio 6
#Utilice el metodo congreuncial mixto y encuentre los parametros adecuados de x(0), b, c y m 
#para generar un recorrido completo de numeros entre 0 y 14

def pause():
    input("Presiona Enter para continuar...")

def ejercicio6():
    x0 = 0
    a = 1
    c = 2
    m = 15

    x = x0 
    secuencia = []
    vistos = {}
    
    while x not in vistos:
        vistos[x] = len(secuencia)   # guarda en qué posición apareció
        secuencia.append(x)
        x = (a * x + c) % m
    
    print("=" * 50)
    print("Ejercicio 6 - Recorrido completo de 0 a 14")
    print("=" * 50)
    print(f"x(0) = {x0}")
    print(f"x(n+1) = ({a} * x(n) + {c}) mod {m}")
    print()
    print(f"Secuencia: {secuencia}")
    print(f"Cantidad de números: {len(secuencia)}")
    print()

    if len(secuencia) == m:
        print("Genera todos los números de 0 a 14")
    else:
        print("No genera recorrido completo")
        print(f"Se repite el valor {x} (ya había salido en la posición {vistos[x]})")

    pause()

ejercicio6()
   

