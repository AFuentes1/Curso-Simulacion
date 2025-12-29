# =========================
# Ejercicio 9a y 9b – Mixto
# =========================
def ejercicio9(func):
    def wrapper(*args, **kwargs):
        secuencia, vistos, params = func(*args, **kwargs)
        x0, a, c, m = params

        print("=" * 50)

        if c == 0:
            print("Ejercicio 9b - Método congruencial multiplicativo")
            print(f"x(0) = {x0}")
            print(f"x(n+1) = ({a} * x(n)) mod {m}")
            print("En la secuencia generada se puede o bien hacer mod 10 para que el 10 se tome como 0")
            print("o bien restar 1 a cada valor para que el rango sea de 0 a 9")
        else:
            print("Ejercicio 9a - Método congruencial mixto")
            print(f"x(0) = {x0}")
            print(f"x(n+1) = ({a} * x(n) + {c}) mod {m}")

        print()
        print(f"Secuencia: {secuencia}")
        print(f"Cantidad de números: {len(secuencia)}")
        print()

        if len(vistos) == 10:
            print("Genera recorrido completo con m = {m}")
        else:
            x = secuencia[-1]
            print("No genera recorrido completo")
            print(f"Se repite el valor {x} (ya había salido en la posición {vistos[x]})")

    return wrapper

@ejercicio9
def recorrido_m_c_mixto(x0, a, c, m):
    x = x0
    secuencia = []
    vistos = {}

    while x not in vistos:
        vistos[x] = len(secuencia)
        secuencia.append(x)
        x = (a * x + c) % m
    return secuencia, vistos, (x0, a, c, m)


# =========================
# Ejercicio 9c – Aditivo
# =========================

def ejercicio9c(func):
    def wrapper(*args, **kwargs):
        secuencia, vistos, params = func(*args, **kwargs)
        x0, x1, m = params

        print("=" * 50)
        print("Ejercicio 9c - Método congruencial aditivo con m = 10")
        print(f"x(0) = {x0}")
        print(f"x(n+1) = ({x0} + {x1}) mod {m}")
        print()
        print("En la secuencia generada, hay que tener en cuenta que los recorridos son más largos al haber 2 semillas")
        print()
        print(f"Secuencia: {secuencia}")
        print(f"Cantidad de números: {len(secuencia)}")
        print()

        if len(vistos) == m:
            print("Genera todos los números con el valor de m = 10")
        else:
            x = secuencia[-1]
            print("No genera recorrido completo")
            print(f"Se repite el valor {x} (ya había salido en la posición {vistos[x]})")

    return wrapper


@ejercicio9c
def recorrido_m_c_aditivo(x0,x1,m):
    secuencia = [x0]
    vistos = {}
    xA = x0
    xB = x1

    vistos[x0] = 1


    for i in range(100):
        vistos[xB] = len(secuencia)   # guarda en qué posición apareció
        secuencia.append(xB)
        tmp = xB
        xB = (xA + xB) % m
        xA = tmp
        if len(vistos) == 10:
            break

    print(f"x(n+1) = ({x0} + {x1}) mod {m}")
    print(vistos)

    return secuencia, vistos, (x0, x1, m)

recorrido_m_c_mixto(
    x0=7,
    a=1,
    c=7,
    m=10
)

print()
print()

recorrido_m_c_mixto(
    x0=1,
    a=2,
    c=0,
    m=11
)

print()
print()

recorrido_m_c_aditivo(
    x0=1,
    x1=1,
    m=10
)