' EJERCICIO 3: Binomial n=3, p=0.5

COPY 3 nMonedas
COPY 0.5 p
COPY 10000 Nsim

' Probabilidades teóricas
BINOMIALPROB nMonedas p 0 p0
BINOMIALPROB nMonedas p 1 p1
BINOMIALPROB nMonedas p 2 p2
BINOMIALPROB nMonedas p 3 p3
PRINT p0 p1 p2 p3

' Simulación para histograma (valores 0..3)
CLEAR resultados

REPEAT Nsim
  COPY 0 exitos

  REPEAT nMonedas
    UNIFORM 1 0 1 r
    IF r <= p
      LET exitos = exitos + 1
    END
  END

  SCORE exitos resultados
END

HISTOGRAM percent binsize 1 "Porcentaje" "Éxitos (0-3)" resultados