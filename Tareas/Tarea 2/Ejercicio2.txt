#Ejercicio 2 
#para 5 bits, método congruencial binario con recorrido completo 
#Semilla y operación que se realiza 
def Ejercicio2(semilla, pasos = 40):
    print("Semilla: ", semilla)
    print("Operacion: Xn+1 = (5*Xn + 1) % 32\n")

    m = 32
    a = 5
    c = 1

    x = semilla 
    vistos = []

    print("Semilla(X0): ", semilla)

    for n in range(pasos): #Repite el proceso 'pasos' veces (n = 0,1,2,3...)
        if x in vistos: #Verifica si el número salio antes
            print("Se repitio el valor", x) 
            break
    
        vistos.append(x) #Agrega el número a la lista de vistos
        print("n =", n, "Xn =", x, "bits =", format(x, '05b')) #Muestra el valor y su forma en 5 bits
        #formula congruencial 
        x = (a * x + c) % m #Calcula el siguiente número con la formula congruencial 
    
    print("Salieron estos valores distintos:", len(vistos)) #Cuantos valores diferentes aparecieron
    if len(vistos) == m: #Verifica si salieron 32 distintos
        print("Recorrido completo")
    else:
        print("No se completo el recorrido") #De lo contrario no recorrio todos los valores 
    
    return vistos #Valores generados 

Ejercicio2(semilla=1, pasos=40) 
