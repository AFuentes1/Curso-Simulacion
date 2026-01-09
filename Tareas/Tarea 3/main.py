import os
from pathlib import Path

from src.Pruebas_Estadisticas.P_Corridas import prueba_corridas
from src.Pruebas_Estadisticas.P_Huecos_Numeros import prueba_huecos_numeros
from src.Pruebas_Estadisticas.P_Poker import prueba_poker
from src.Pruebas_Estadisticas.P_Promedio import prueba_promedio
from src.Pruebas_Estadisticas.P_Series import prueba_series
from src.Pruebas_Estadisticas.P_Varianza import prueba_varianza


if __name__ == "__main__":

    BASE_DIR = Path(__file__).resolve().parent
    DATA_DIR = BASE_DIR / "Data"

    total_pruebas = 0
    pruebas_pasadas = 0

    resumen_tipo = {
        "continuous": {"total": 0, "pasan": 0},
        "discrete": {"total": 0, "pasan": 0}
    }

    # ==============================
    # Configuración de pruebas
    # ==============================
    pruebas_config = {
        "continuous": {
            "parametros": (0, 1),
            "pruebas": [
                ("corridas", lambda p, a, b: prueba_corridas(p, alpha=0.05)),
                ("huecos_numeros", lambda p, a, b: prueba_huecos_numeros(
                    p, a=a, b=b, u0=0.0, u1=0.5, alpha=0.05, kmax=5
                )),
                ("poker", lambda p, a, b: prueba_poker(p, a=a, b=b, alpha=0.05, d=5)),
                ("promedio", lambda p, a, b: prueba_promedio(
                    p, kind="continuous", a=a, b=b, alpha=0.05
                )),
                ("series", lambda p, a, b: prueba_series(p, a=a, b=b, k=10, alpha=0.05)),
                ("varianza", lambda p, a, b: prueba_varianza(
                    p, kind="continuous", a=a, b=b, alpha=0.05
                ))
            ]
        },
        "discrete": {
            "pruebas": [
                ("corridas", lambda p, a, b: prueba_corridas(p, alpha=0.05)),
                ("promedio", lambda p, a, b: prueba_promedio(
                    p, kind="discrete", a=a, b=b, alpha=0.05
                )),
                ("varianza", lambda p, a, b: prueba_varianza(
                    p, kind="discrete", a=a, b=b, alpha=0.05
                ))
            ]
        }
    }

    # ==============================
    # Procesar archivos
    # ==============================
    for filename in sorted(os.listdir(DATA_DIR)):
        if not filename.endswith(".txt"):
            continue

        data_path = DATA_DIR / filename
        partes = filename.replace(".txt", "").split("_")

        if len(partes) == 2:
            tipo = "continuous"
            a, b = pruebas_config["continuous"]["parametros"]
        else:
            tipo = "discrete"
            a = int(partes[1].replace("u", ""))
            b = int(partes[2])

        print(f"\nProcesando: {filename} - {tipo} ({a},{b})")

        for nombre, funcion in pruebas_config[tipo]["pruebas"]:
            total_pruebas += 1
            resumen_tipo[tipo]["total"] += 1

            try:
                pasa, _ = funcion(data_path, a, b)
                if pasa:
                    pruebas_pasadas += 1
                    resumen_tipo[tipo]["pasan"] += 1
                print(f"  {nombre}: {'✓' if pasa else '✗'}")

            except Exception as e:
                print(f"  {nombre}: ERROR - {e}")

    # ==============================
    # Resumen final
    # ==============================
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
