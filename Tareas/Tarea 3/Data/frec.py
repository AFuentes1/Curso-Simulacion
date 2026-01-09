import os
from collections import Counter
import matplotlib.pyplot as plt

def leer_numeros(ruta):
    datos = []
    with open(ruta, "r") as f:
        for linea in f:
            linea = linea.strip()
            if not linea:
                continue
            for x in linea.split():
                datos.append(float(x))
    return datos

def es_discreta(datos):
    return all(x.is_integer() for x in datos)

def graficar_frecuencias(nombre_archivo, datos):
    plt.figure()

    if es_discreta(datos):
        conteo = Counter(datos)
        valores = sorted(conteo.keys())
        frecuencias = [conteo[v] for v in valores]
        plt.bar(valores, frecuencias)
        plt.xlabel("Valor")
        plt.ylabel("Frecuencia")
    else:
        plt.hist(datos, bins=50)
        plt.xlabel("Intervalo")
        plt.ylabel("Frecuencia")

    plt.title(nombre_archivo)
    plt.tight_layout()
    plt.show()

def main():
    archivos = [f for f in os.listdir(".") if f.endswith(".txt")]

    for archivo in archivos:
        datos = leer_numeros(archivo)
        graficar_frecuencias(archivo, datos)

if __name__ == "__main__":
    main()
