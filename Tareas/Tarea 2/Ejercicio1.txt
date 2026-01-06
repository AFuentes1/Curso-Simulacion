#Ejercicio 1 
#Utilice el metodo congruencial binario pero en lugar de realizar un xor con las posiciones 0 y 1
#de derecha a izquierda, realice un xon con las posiciones 0 y 2, utilice las siguinetes semillas: 
#y muestre si realiza todo el recorrido o no 
def pausa():
    input("Presiona Enter para continuar ")

def menu():
    print("Ejercicio 1 - Xor (0 y 2)")
    print("1) Ejercicio A")
    print("2) Ejercicio B")
    print("0) Salir")

    op = input("Ingrese una opcion: ").strip()

    if op == "1":
        ejercicio_a()
        pausa()
    elif op == "2":
        ejercicio_b()
        pausa()
    elif op == "0":
        print("Saliendo...")
    else:
        print("Opcion invalida")
        pausa()
        menu()

#x(0) = 110
def ejercicio_a():
    semilla_bin = "110"
    bits = 3
    x = int(semilla_bin, 2) #de binario a entero

    vistos = set() #conjunto para almacenar los numeros vistos

    def paso(x):
        #obtener bits 0 y 2
        bit0 = (x >> 0) & 1
        bit2 = (x >> 2) & 1
        #realizar xor
        nuevo_bit = bit0 ^ bit2 #Xor entre bit0 y bit2
        #desplazar a la derecha y agregar el nuevo bit a la izquierda
        x_nuevo = (x >> 1) | (nuevo_bit << (bits - 1)) #insertar como MSB
        return x_nuevo
    
    n = 0 
    while True: 
        if x == 0:
            print("Parálisis: llegó a 000")
            break 
        if x in vistos: 
            print("Ciclo detectado después de", n, "iteraciones.")
            break
        vistos.add(x)

        b0 = (x >> 0) & 1
        b2 = (x >> 2) & 1
        xr = b0 ^ b2
        x_next = paso(x)

        print(f"x({n}) = {format(x, f'0{bits}b')} = {x}")
        x = x_next
        n += 1

#x(0) = 1111
def ejercicio_b():
    semilla_bin = "1111"
    bits = 4
    x = int(semilla_bin, 2) #de binario a entero

    vistos = set() #conjunto para almacenar los numeros vistos

    def paso(x):
        #obtener bits 0 y 2
        bit0 = (x >> 0) & 1 
        bit2 = (x >> 2) & 1
        #realizar xor
        nuevo_bit = bit0 ^ bit2 #Xor entre bit0 y bit2
        #desplazar a la derecha y agregar el nuevo bit a la izquierda
        x_nuevo = (nuevo_bit << (bits - 1)) | (x >> 1) #insertar como MSB (bit más a la izquierda)
        return x_nuevo
    
    n = 0
    while x not in vistos and x != 0:
        vistos.add(x)
        print(f"x({n}) = {format(x,'04b')} = {x}")
        x = paso(x)
        n += 1

    if x == 0:
        print("Parálisis: llegó a 0000.")
    else:
        print(f"Ciclo: se repite {format(x,'04b')}.")
        print(f"No hizo todo el recorrido: {len(vistos)} de 15 estados.")

menu()
    





