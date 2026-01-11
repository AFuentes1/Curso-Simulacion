import os
from pathlib import Path

from src.Pruebas_Estadisticas.P_Corridas import prueba_corridas
from src.Pruebas_Estadisticas.P_Huecos_Digitos import prueba_huecos_digitos
from src.Pruebas_Estadisticas.P_Huecos_Numeros import prueba_huecos_numeros
from src.Pruebas_Estadisticas.P_Poker import prueba_poker
from src.Pruebas_Estadisticas.P_Promedio import prueba_promedio
from src.Pruebas_Estadisticas.P_Series import prueba_series
from src.Pruebas_Estadisticas.P_Varianza import prueba_varianza


if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent
    DATA_DIR = BASE_DIR / "Data"
    NORM_DIR = DATA_DIR / "_norm"   # aquí quedan los *_u01.txt (discretos reescalados)

    total_pruebas = 0
    pruebas_pasadas = 0

    resumen_tipo = {
        "continuous": {"total": 0, "pasan": 0},
        "discrete": {"total": 0, "pasan": 0}
    }

    # Pruebas que “requieren” trabajar en [0,1) en tu implementación
    PRUEBAS_U01 = [
        ("huecos_digitos", lambda p: prueba_huecos_digitos(p, alpha=0.05)),
        ("huecos_numeros", lambda p: prueba_huecos_numeros(p, a=0, b=1, u0=0.0, u1=0.5, alpha=0.05, kmax=5)),
        ("poker",          lambda p: prueba_poker(p, a=0, b=1, alpha=0.05, d=5)),
        ("series",         lambda p: prueba_series(p, a=0, b=1, k=10, alpha=0.05)),
    ]

    for filename in sorted(os.listdir(DATA_DIR)):
        if not filename.endswith(".txt"):
            continue

        data_path = DATA_DIR / filename
        stem = filename.replace(".txt", "")
        partes = stem.split("_")

        # Detectar tipo y rango teórico
        if len(partes) == 2:
            tipo = "continuous"
            a, b = 0, 1
        else:
            tipo = "discrete"
            a = int(partes[1].replace("u", ""))
            b = int(partes[2])

        print(f"\nProcesando: {filename} - {tipo} ({a},{b})")

        # 1) Promedio / Varianza / Corridas sobre la muestra ORIGINAL
        pruebas_base = [
            ("promedio", lambda p: prueba_promedio(p, kind=tipo, a=a, b=b, alpha=0.05)),
            ("varianza", lambda p: prueba_varianza(p, kind=tipo, a=a, b=b, alpha=0.05)),
            ("corridas", lambda p: prueba_corridas(p, alpha=0.05)),
        ]

        # 2) Las otras 4 pruebas:
        #    - continuous: usar el mismo archivo
        #    - discrete: usar el archivo normalizado *_u01.txt si existe
        if tipo == "continuous":
            extra_tests = PRUEBAS_U01
            extra_path = data_path
        else:
            extra_tests = PRUEBAS_U01
            extra_path = NORM_DIR / f"{stem}_u01.txt"
            if not extra_path.exists():
                print(f"  AVISO: falta {extra_path.name} en Data/_norm. (No puedo correr huecos/poker/series)")
                extra_tests = []  # no revienta; solo no corre esas 4

        # Ejecutar todas las pruebas (7 en total cuando aplica)
        for nombre, fn in (pruebas_base + [(n, (lambda p, f=f: f(p))) for n, f in extra_tests]):
            total_pruebas += 1
            resumen_tipo[tipo]["total"] += 1

            try:
                pasa, _ = fn(data_path if nombre in {"promedio", "varianza", "corridas"} else extra_path)
                if pasa:
                    pruebas_pasadas += 1
                    resumen_tipo[tipo]["pasan"] += 1
                print(f"  {nombre}: {'✓' if pasa else '✗'}")
            except Exception as e:
                print(f"  {nombre}: ERROR - {e}")

    print("\n" + "=" * 50)
    print("RESUMEN DE RESULTADOS")
    print("=" * 50)
    print(f"Total de pruebas ejecutadas: {total_pruebas}")
    print(f"Pruebas que pasaron: {pruebas_pasadas}")
    print(f"Pruebas que fallaron: {total_pruebas - pruebas_pasadas}")
    print(f"Tasa de éxito: {(pruebas_pasadas / total_pruebas) * 100:.2f}%")

    print("\nPor tipo de distribución:")
    for tipo, datos in resumen_tipo.items():
        if datos["total"] > 0:
            tasa = datos["pasan"] / datos["total"] * 100
            print(f"  {tipo}: {datos['pasan']}/{datos['total']} ({tasa:.2f}%)")