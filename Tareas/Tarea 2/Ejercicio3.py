#Ejercicio 3 Tarea 2 

def pausa():
    input("Presiona enter para continuar...")

def menu():
    print("Ejercicio 3 Generador de cuadrados medios")
    print("1) Ejercicio A (3567345)")
    print("2) Ejercicio B (1234500012)")
    print("3) Ejercicio C (4567234902)")
    print("0) Salir")

    op = input("Ingrese una opcion: ").strip()
    if op == "1":
        ejercicio_a(x0=3567345)
        pausa()
    elif op == "2":
        ejercicio_b()
        pausa()
    elif op == "3":
        ejercicio_c()
        pausa()
    elif op == "0":
        print("Saliendo...")
    else:
        print("Opcion invalida")
        pausa()
        menu()

def ejercicio_a():
    x = 3567345  #semilla
    k = 4
    cantidad = 50 #cantidad de numeros a generar
    numeros = [] #lista para almacenar los numeros generados
    
    print("\n" + "="*60) #Imprimimos una línea de separación
    print("MÉTODO DE LOS CUADRADOS MEDIOS")
    print("="*60)
    print(f"Semilla x(0) = {x0}") 
    print(f"k = {k} dígitos")
    print(f"Cantidad: {cantidad} números")
    print("="*60 + "\n")
    
    for n in range(1, cantidad + 1): #Ciclo, genera "cantidad" números (1 hasta cantidad)
        cuadrado = x * x             #calcula el cuadrado de x
        str_cuadrado = str(cuadrado).zfill(2 * k) #convierte a string y rellena con ceros hasta 2k dígitos
        
        inicio = (len(str_cuadrado) - k) // 2 #calcula donde empieza el bloque del centro 
        medio = str_cuadrado[inicio:inicio + k] #extrea los k digitos del centro
        
        x = int(medio) #convierte "medio" a entero y se usa como nuevo x
        numeros.append(medio) #Guarda el número generado en la lista 
        
        print(f"x({n:2d}) = ({medio})^2 = {str(cuadrado).ljust(14)} -> {medio}") #Imprime el resultado del paso
    
    print("\n" + "="*60) 
    print("NÚMEROS GENERADOS:") 
    print("="*60)
    for i in range(0, len(numeros), 10):   #Imprime 10 números por línea
        print(" | ".join(numeros[i:i+10])) #Une los números con " | "
    print("="*60 + "\n")
    
    return numeros #Se devuelve la lista con todos los numeros generados 

def ejercicio_b():
    x = 1234500012
    k = 4
    cantidad = 50
    numeros = [] #lista para almacenar los numeros generados

    print("Semilla x(0): ", x)

    for n in range(1, cantidad + 1): #Genera cantidad de números
        cuadrado = str(x * x) #calcula el cuadrado de x y lo convierte a string

        #relleno con ceros para que no quede muy corto 
        if len(cuadrado) < 2 * k:
            cuadrado = cuadrado.zfill(2 * k)

            inicio = (len(cuadrado) - k) // 2 #calcula donde empieza el bloque del centro 
            medio = cuadrado[inicio:inicio + k] #extrea los k digitos del centro 

            numeros.append(medio) #Guarda el número generado en la lista
            print("n = ", n, "Xn = ", medio) #Imprime el resultado del paso
            x = int(medio) #nuevo x

        return numeros #Se devuelve la lista con todos los numeros generados
    
def ejercicio_c():
    x = 4567234902
    k = 4 
    cantidad = 50
    numeros = [] #lista para almacenar los numeros generados

    print("Semilla x(0): ", x)

    for n in range(1, cantidad + 1): #Genera cantidad de números
        cuadrado = str(x * x)

        if len(cuadrado) < 2 * k:
            cuadrado = cuadrado.zfill(2 * k) #se rellena con ceros para que no quede muy corto 

        inicio = (len(cuadrado) - k) // 2 #calcula donde empieza el bloque del centro
        medio = cuadrado[inicio:inicio + k] #extrea los k digitos del centro

        numeros.append(medio) #Guarda el número generado en la lista
        print("n = ", n, "Xn = ", medio) #Imprime el resultado del paso
        x = int(medio) #nuevo x

    return numeros #Se devuelve la lista con todos los numeros generados


            








menu()