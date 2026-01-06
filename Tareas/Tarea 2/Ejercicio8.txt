#Ejercicio 8 
#Defina los parametros de a, c, x0 para un recorrido completo para un valor de m = 19
def ejercicio8(func):
    def wrapper(*args, **kwargs):
        secuencia, vistos, params = func(*args, **kwargs)

        x0, a, c, m = params

        print("=" * 50)
        print("Ejercicio 8 - Recorrido completo con m =", m)
        print("=" * 50)
        print(f"x(0) = {x0}")
        print(f"x(n+1) = ({a} * x(n) + {c}) mod {m}\n")
        print(f"Secuencia generada: {secuencia}")
        print(f"Cantidad de números (distintos): {len(secuencia)}\n")

        if len(secuencia) == m:
            print(f"Si cumple: recorrido completo (0 a {m - 1})")
        else:
            x = secuencia[-1]
            print("No cumple recorrido completo")
            print(f"Se repite el valor {x} (ya había salido en la posición {vistos[x]})")

    return wrapper


@ejercicio8
def recorrido_m_c_mixto(x0,a,c,m):
    x = x0
    secuencia = []
    vistos = {}

    while x not in vistos:
        vistos[x] = len(secuencia)
        secuencia.append(x)
        x = (a * x + c) % m

    return secuencia, vistos, (x0, a, c, m)


recorrido_m_c_mixto()
