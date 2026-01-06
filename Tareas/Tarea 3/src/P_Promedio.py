import numpy as np
from scipy.stats import norm

def params_uniform(kind, a, b):
    if kind == "continuous":          
        mu = (a + b) / 2   #Media de U(a, b)
        sigma2 = ((b - a) ** 2) / 12 #Varianza de U(a, b)
        return mu, sigma2 #Retorna la media y varianza
    else:                            
        m = int(b - a + 1) #Número de valores posibles 
        mu = (a + b) / 2  #Media de la uniforme discreta (a+b)/2
        sigma2 = (m**2 - 1) / 12 #Varianza de la uniforme discreta (m^2 - 1)/12 para m valores
        return mu, sigma2 #Retorna la media y varianza

def prueba_promedio(path, kind="continuous", a=0, b=1, alpha=0.05):
    x = np.loadtxt(path)
    n = x.size

    mu, sigma2 = params_uniform(kind, a, b)
    xbar = x.mean()

    zcrit = norm.ppf(1 - alpha/2)
    half = zcrit * np.sqrt(sigma2 / n)
    low, high = mu - half, mu + half

    pasa = (low <= xbar <= high)

    return pasa, {
        "n": int(n),
        "xbar": float(xbar),
        "mu": float(mu),
        "sigma2": float(sigma2),
        "alpha": float(alpha),
        "intervalo": [float(low), float(high)]
    }

if __name__ == "__main__":
    pasa, info = prueba_promedio("data/python_u01.txt", kind="continuous", a=0, b=1, alpha=0.05)
    print("PASA:", pasa)
    print(info)
