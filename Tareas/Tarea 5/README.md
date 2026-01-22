# Tarea 5 — Simulación de red de colas (restaurante de comida rápida)

## 1) Objetivo
Modelar el restaurante como **una red de colas abierta (tipo Jackson)** y, con **simulación de eventos discretos**, decidir cuántos servidores \(c_i\) asignar a cada estación (con **12 colaboradores en total**) para:
- **Minimizar** el **tiempo promedio** en el sistema \(\bar W\)
- **Minimizar** la **varianza** \(Var(W)\)
- Mantener **utilización por estación** \( \rho_i < 0.8 \) (estabilidad) :contentReference[oaicite:0]{index=0}

La simulación se ejecuta por un turno de **\(T = 8\) horas**, con **muchas réplicas** para estimar promedios/varianzas. :contentReference[oaicite:1]{index=1}

---

## 2) Especificación del sistema (enunciado)
### Estaciones
\(\{ \text{cajas, refrescos, freidora, postres, pollo} \}\) :contentReference[oaicite:2]{index=2}

### Llegadas
- Llegadas externas: **Poisson** con tasa \(\lambda = 3\) (ajustable en la simulación). :contentReference[oaicite:3]{index=3}

### Disciplina de colas
- **FCFS** y **capacidad infinita**. :contentReference[oaicite:4]{index=4}

### Tiempos de servicio (minutos)
- **Cajas:** exponencial con media **2.5** min :contentReference[oaicite:5]{index=5}  
- **Refrescos:** exponencial con media **0.75** min :contentReference[oaicite:6]{index=6}  
- **Freidora:** normal discreta con media **3** min :contentReference[oaicite:7]{index=7}  
- **Postres:** binomial (según enunciado) :contentReference[oaicite:8]{index=8}  
- **Pollo:** geométrica con \(p=0.1\) :contentReference[oaicite:9]{index=9}  

### Workflow / enrutamiento probabilístico
Todos pasan por **cajas** (\(p=1\)) y luego visitan etapas de forma independiente con:  
- \(p_{\text{refrescos}}=0.9\), \(p_{\text{freidora}}=0.7\), \(p_{\text{postres}}=0.25\), \(p_{\text{pollo}}=0.3\) :contentReference[oaicite:10]{index=10}  
Ejemplo válido: cajas → refrescos → freidora (sin pollo ni postres). :contentReference[oaicite:11]{index=11}

### Cantidad de órdenes por cliente
Cada cliente tiene un número de órdenes \(K\) que sigue **Binomial** con \(n=5\), \(p=2/5\). :contentReference[oaicite:12]{index=12}

---

## 3) Modelo y métricas usadas
### Tiempo total en el sistema
El enunciado define que el **tiempo total de espera** de un cliente es la suma de **cola + servicio** en las estaciones visitadas. :contentReference[oaicite:13]{index=13}  
Métrica principal: \(\bar W\) y \(Var(W)\). :contentReference[oaicite:14]{index=14}

### Utilización por estación
Para cada estación \(i\):
\[
\rho_i = \frac{\lambda_i}{c_i \mu_i}
\]
donde \(\lambda_i\) es la tasa efectiva a la estación \(i\). :contentReference[oaicite:15]{index=15}  
Restricción deseada: \(\rho_i < 0.8\). :contentReference[oaicite:16]{index=16}

---

## 4) Estrategia de optimización
Se enumeraron todas las asignaciones enteras positivas de 12 servidores en 5 estaciones:
- **Configuraciones válidas:** **330** (todas las particiones de 12 en 5 positivos).

Para cada configuración se estimó:
- \(\bar W\), \(Var(W)\)
- IC 95% de \(\bar W\) (cuando aplica)
- Conteo de violaciones `viol` = número de estaciones con \(\rho_i \ge 0.8\)

---

## 5) Resultados (resumen)
De la corrida de evaluación sobre las 330 configuraciones:

### Óptimo 1 — Minimiza \(\bar W\)
- **MIN_W:** `cfg=(6, 3, 1, 1, 1)`  *(orden: cajas, ref, frei, pos, pol)*  
- \(\bar W = 112.3511\)  
- IC95% \([111.8644,\;112.8378]\)

### Óptimo 2 — Minimiza \(Var(W)\)
- **MIN_VAR:** `cfg=(3, 2, 5, 1, 1)`  
- \(Var(W)= 8605.9414\)  
- \(\bar W = 161.3158\)

> Nota: el enunciado menciona que \(\lambda_i\) debe ajustarse por probabilidades del workflow. :contentReference[oaicite:17]{index=17}  
> Por eso también se reporta una comparación de tasas efectivas por estación.

---

## 6) Chequeo de tasas efectivas: \(\hat\lambda_i\) vs \(\lambda \cdot p_i \cdot E[K]\)
Se exportó una mini-tabla por configuración (MIN_W y MIN_VAR) comparando:
- \(\hat\lambda_i\): estimada desde la simulación
- \(\lambda \cdot p_i \cdot E[K]\): valor teórico esperado (según probabilidades y órdenes)

Archivos:
- `lambda_hat_vs_teorico_MIN_W.csv`
- `lambda_hat_vs_teorico_MIN_VAR.csv`

> Importante: para que el **ratio** sea interpretable, \(\hat\lambda_i\) y \(\lambda \cdot p_i \cdot E[K]\) deben estar en **las mismas unidades** (por hora o por minuto).

---

## 7) Archivos generados
- `resultados_todas_configuraciones.csv`  
  Contiene, por configuración: \(c_i\), \(W\_sim\), \(Var(W)\), IC, \(W\_analitico\) (si aplica), clientes completados y violaciones.
- `lambda_hat_vs_teorico_MIN_W.csv`
- `lambda_hat_vs_teorico_MIN_VAR.csv`

---

## 8) Cómo ejecutar (rápido)
1. Asegurar Python 3.x
2. Ejecutar el script principal de la tarea (el que genera los CSV y el resumen por consola).
3. Revisar los CSV exportados en la carpeta del proyecto.

---

## 9) Conclusiones
- Se evaluaron **330** distribuciones posibles de 12 servidores.
- Se obtuvieron dos configuraciones recomendadas:
  - Una que **minimiza \(\bar W\)** (MIN_W)
  - Otra que **minimiza \(Var(W)\)** (MIN_VAR)
- Se incluyó un chequeo de consistencia de **tasas efectivas** por estación, alineado con el enunciado. :contentReference[oaicite:18]{index=18}
