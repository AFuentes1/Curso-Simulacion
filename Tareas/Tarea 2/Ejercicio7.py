def ejercicio7(func):
    def wrapper(*args, **kwargs):
        secuencia, vistos, params = func(*args, **kwargs)

        x0, a, c, m = params

        print("=" * 50)
        print("Ejercicio 7 - Recorrido completo con el valor de m = 9")
        print("=" * 50)
        print(f"x(0) = {x0}")
        print(f"x(n+1) = ({a} * x(n) + {c}) mod {m}")
        print()
        print(f"Secuencia: {secuencia}")
        print(f"Cantidad de números: {len(secuencia)}")
        print()

        if len(secuencia) == m:
            print("Genera todos los números con el valor de m = 9")
        else:
            x = secuencia[-1]
            print("No genera recorrido completo")
            print(f"Se repite el valor {x} (ya había salido en la posición {vistos[x]})")

    return wrapper


@ejercicio7
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