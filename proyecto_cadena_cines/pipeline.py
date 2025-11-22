import os
from pathlib import Path

import pandas as pd


# =========================
# CONFIGURACIÓN DE PATHS
# =========================

BASE_DIR = Path(__file__).resolve().parent

DATA_ORIGINAL_DIR = BASE_DIR / "data_original"
DATALAKE_DIR = BASE_DIR / "datalake"

LANDING_DIR = DATALAKE_DIR / "landing"
RAW_DIR = DATALAKE_DIR / "raw"
CURATED_DIR = DATALAKE_DIR / "curated"

ANALYTICS_DIR = BASE_DIR / "analytics"


def crear_estructura_directorios():
    """Crea la estructura de carpetas del Data Lake si no existe."""
    for d in [LANDING_DIR, RAW_DIR, CURATED_DIR, ANALYTICS_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    print("[OK] Estructura de carpetas creada/verificada.")


# =========================
# 1) INGESTA -> LANDING
# =========================

def copiar_a_landing():
    """
    'Ingesta' simple: copia los archivos originales de IMDb
    desde data_original/ hacia datalake/landing/.
    """
    archivos = ["title.basics.tsv", "title.ratings.tsv"]  # podés agregar más si querés

    for nombre in archivos:
        origen = DATA_ORIGINAL_DIR / nombre
        destino = LANDING_DIR / nombre

        if not origen.exists():
            print(f"[WARN] No se encontró {origen}. Saltando.")
            continue

        # Copia simple leyendo y escribiendo (para evitar usar shutil si querés mantenerlo básico)
        with open(origen, "rb") as f_src, open(destino, "wb") as f_dst:
            f_dst.write(f_src.read())

        print(f"[OK] Copiado a landing: {nombre}")


# =========================
# 2) LANDING -> RAW
# =========================

def procesar_a_raw():
    """
    Lee los archivos de landing, hace limpieza mínima y los guarda en raw.
    """
    basics_path = LANDING_DIR / "title.basics.tsv"
    ratings_path = LANDING_DIR / "title.ratings.tsv"

    if not basics_path.exists() or not ratings_path.exists():
        print("[ERROR] Faltan archivos en landing. Ejecutar primero copiar_a_landing().")
        return

    print("[INFO] Cargando title.basics.tsv...")
    basics = pd.read_csv(basics_path, sep="\t", low_memory=False)

    print("[INFO] Cargando title.ratings.tsv...")
    ratings = pd.read_csv(ratings_path, sep="\t", low_memory=False)

    # Limpieza mínima: estandarizar nombres a minúsculas
    basics.columns = [c.lower() for c in basics.columns]
    ratings.columns = [c.lower() for c in ratings.columns]

    # Guardar en RAW como CSV
    basics.to_csv(RAW_DIR / "basics_raw.csv", index=False)
    ratings.to_csv(RAW_DIR / "ratings_raw.csv", index=False)

    print("[OK] Archivos procesados a RAW.")


# =========================
# 3) RAW -> CURATED
# =========================

def construir_curated():
    """
    Construye el dataset integrado 'movies_curated.csv' a partir de RAW.
    - Filtra solo películas
    - Une basics + ratings
    - Limpia nulos críticos
    - Convierte tipos
    """
    basics_raw_path = RAW_DIR / "basics_raw.csv"
    ratings_raw_path = RAW_DIR / "ratings_raw.csv"

    if not basics_raw_path.exists() or not ratings_raw_path.exists():
        print("[ERROR] Faltan archivos RAW. Ejecutar primero procesar_a_raw().")
        return

    basics = pd.read_csv(basics_raw_path)
    ratings = pd.read_csv(ratings_raw_path)

    # Filtrar solo películas
    movies = basics[basics["titletype"] == "movie"].copy()

    # Conversión de tipos
    movies["startyear"] = pd.to_numeric(movies["startyear"], errors="coerce")
    movies["runtimeminutes"] = pd.to_numeric(movies["runtimeminutes"], errors="coerce")

    ratings["averageRating"] = pd.to_numeric(ratings["averagerating"], errors="coerce")
    ratings["numVotes"] = pd.to_numeric(ratings["numvotes"], errors="coerce")

    # Unir basics + ratings
    merged = movies.merge(
        ratings[["tconst", "averageRating", "numVotes"]],
        on="tconst",
        how="inner"
    )

    # Eliminar nulos críticos
    merged = merged.dropna(
        subset=["startyear", "runtimeminutes", "averageRating", "numVotes"]
    )

    # Normalizar géneros (tomar el primero como género principal)
    merged["genre_principal"] = merged["genres"].str.split(",").str[0]

    # Guardar como curated
    curated_path = CURATED_DIR / "movies_curated.csv"
    merged.to_csv(curated_path, index=False)

    print(f"[OK] Dataset curated generado: {curated_path}")
    print(f"[INFO] Filas en curated: {len(merged)}")


# =========================
# 4) GENERAR KPIs / ANALYTICS
# =========================

def generar_kpis():
    """
    A partir de movies_curated.csv genera algunos indicadores
    y los guarda como CSV en /analytics.
    """
    curated_path = CURATED_DIR / "movies_curated.csv"
    if not curated_path.exists():
        print("[ERROR] No existe movies_curated.csv. Ejecutar construir_curated().")
        return

    df = pd.read_csv(curated_path)

    # KPI 1: Rating promedio por género principal
    ratings_por_genero = (
        df.groupby("genre_principal")["averageRating"]
        .mean()
        .sort_values(ascending=False)
    )
    ratings_por_genero.to_csv(ANALYTICS_DIR / "ratings_por_genero.csv")
    print("[OK] KPI rating promedio por género generado.")

    # KPI 2: Popularidad (número de votos) promedio por año de estreno
    popularidad_por_anio = (
        df.groupby("startyear")["numVotes"]
        .mean()
        .sort_values(ascending=False)
    )
    popularidad_por_anio.to_csv(ANALYTICS_DIR / "popularidad_por_anio.csv")
    print("[OK] KPI popularidad por año generado.")

    # KPI 3: Distribución de duración (para histograma rápido)
    distribucion_duracion = df["runtimeminutes"].describe()
    distribucion_duracion.to_csv(ANALYTICS_DIR / "distribucion_duracion.csv")
    print("[OK] Métricas de distribución de duración generadas.")


# =========================
# MAIN
# =========================

def main():
    crear_estructura_directorios()
    copiar_a_landing()
    procesar_a_raw()
    construir_curated()
    generar_kpis()
    print("[DONE] Pipeline completo ejecutado.")


if __name__ == "__main__":
    main()
import os
from pathlib import Path

import pandas as pd


# =========================
# CONFIGURACIÓN DE PATHS
# =========================

BASE_DIR = Path(__file__).resolve().parent

DATA_ORIGINAL_DIR = BASE_DIR / "data_original"
DATALAKE_DIR = BASE_DIR / "datalake"

LANDING_DIR = DATALAKE_DIR / "landing"
RAW_DIR = DATALAKE_DIR / "raw"
CURATED_DIR = DATALAKE_DIR / "curated"

ANALYTICS_DIR = BASE_DIR / "analytics"


def crear_estructura_directorios():
    """Crea la estructura de carpetas del Data Lake si no existe."""
    for d in [LANDING_DIR, RAW_DIR, CURATED_DIR, ANALYTICS_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    print("[OK] Estructura de carpetas creada/verificada.")


# =========================
# 1) INGESTA -> LANDING
# =========================

def copiar_a_landing():
    """
    'Ingesta' simple: copia los archivos originales de IMDb
    desde data_original/ hacia datalake/landing/.
    """
    archivos = ["title.basics.tsv", "title.ratings.tsv"]  # podés agregar más si querés

    for nombre in archivos:
        origen = DATA_ORIGINAL_DIR / nombre
        destino = LANDING_DIR / nombre

        if not origen.exists():
            print(f"[WARN] No se encontró {origen}. Saltando.")
            continue

        # Copia simple leyendo y escribiendo (para evitar usar shutil si querés mantenerlo básico)
        with open(origen, "rb") as f_src, open(destino, "wb") as f_dst:
            f_dst.write(f_src.read())

        print(f"[OK] Copiado a landing: {nombre}")


# =========================
# 2) LANDING -> RAW
# =========================

def procesar_a_raw():
    """
    Lee los archivos de landing, hace limpieza mínima y los guarda en raw.
    """
    basics_path = LANDING_DIR / "title.basics.tsv"
    ratings_path = LANDING_DIR / "title.ratings.tsv"

    if not basics_path.exists() or not ratings_path.exists():
        print("[ERROR] Faltan archivos en landing. Ejecutar primero copiar_a_landing().")
        return

    print("[INFO] Cargando title.basics.tsv...")
    basics = pd.read_csv(basics_path, sep="\t", low_memory=False)

    print("[INFO] Cargando title.ratings.tsv...")
    ratings = pd.read_csv(ratings_path, sep="\t", low_memory=False)

    # Limpieza mínima: estandarizar nombres a minúsculas
    basics.columns = [c.lower() for c in basics.columns]
    ratings.columns = [c.lower() for c in ratings.columns]

    # Guardar en RAW como CSV
    basics.to_csv(RAW_DIR / "basics_raw.csv", index=False)
    ratings.to_csv(RAW_DIR / "ratings_raw.csv", index=False)

    print("[OK] Archivos procesados a RAW.")


# =========================
# 3) RAW -> CURATED
# =========================

def construir_curated():
    """
    Construye el dataset integrado 'movies_curated.csv' a partir de RAW.
    - Filtra solo películas
    - Une basics + ratings
    - Limpia nulos críticos
    - Convierte tipos
    """
    basics_raw_path = RAW_DIR / "basics_raw.csv"
    ratings_raw_path = RAW_DIR / "ratings_raw.csv"

    if not basics_raw_path.exists() or not ratings_raw_path.exists():
        print("[ERROR] Faltan archivos RAW. Ejecutar primero procesar_a_raw().")
        return

    basics = pd.read_csv(basics_raw_path)
    ratings = pd.read_csv(ratings_raw_path)

    # Filtrar solo películas
    movies = basics[basics["titletype"] == "movie"].copy()

    # Conversión de tipos
    movies["startyear"] = pd.to_numeric(movies["startyear"], errors="coerce")
    movies["runtimeminutes"] = pd.to_numeric(movies["runtimeminutes"], errors="coerce")

    ratings["averageRating"] = pd.to_numeric(ratings["averagerating"], errors="coerce")
    ratings["numVotes"] = pd.to_numeric(ratings["numvotes"], errors="coerce")

    # Unir basics + ratings
    merged = movies.merge(
        ratings[["tconst", "averageRating", "numVotes"]],
        on="tconst",
        how="inner"
    )

    # Eliminar nulos críticos
    merged = merged.dropna(
        subset=["startyear", "runtimeminutes", "averageRating", "numVotes"]
    )

    # Normalizar géneros (tomar el primero como género principal)
    merged["genre_principal"] = merged["genres"].str.split(",").str[0]

    # Guardar como curated
    curated_path = CURATED_DIR / "movies_curated.csv"
    merged.to_csv(curated_path, index=False)

    print(f"[OK] Dataset curated generado: {curated_path}")
    print(f"[INFO] Filas en curated: {len(merged)}")


# =========================
# 4) GENERAR KPIs / ANALYTICS
# =========================

def generar_kpis():
    """
    A partir de movies_curated.csv genera algunos indicadores
    y los guarda como CSV en /analytics.
    """
    curated_path = CURATED_DIR / "movies_curated.csv"
    if not curated_path.exists():
        print("[ERROR] No existe movies_curated.csv. Ejecutar construir_curated().")
        return

    df = pd.read_csv(curated_path)

    # KPI 1: Rating promedio por género principal
    ratings_por_genero = (
        df.groupby("genre_principal")["averageRating"]
        .mean()
        .sort_values(ascending=False)
    )
    ratings_por_genero.to_csv(ANALYTICS_DIR / "ratings_por_genero.csv")
    print("[OK] KPI rating promedio por género generado.")

    # KPI 2: Popularidad (número de votos) promedio por año de estreno
    popularidad_por_anio = (
        df.groupby("startyear")["numVotes"]
        .mean()
        .sort_values(ascending=False)
    )
    popularidad_por_anio.to_csv(ANALYTICS_DIR / "popularidad_por_anio.csv")
    print("[OK] KPI popularidad por año generado.")

    # KPI 3: Distribución de duración (para histograma rápido)
    distribucion_duracion = df["runtimeminutes"].describe()
    distribucion_duracion.to_csv(ANALYTICS_DIR / "distribucion_duracion.csv")
    print("[OK] Métricas de distribución de duración generadas.")


# =========================
# MAIN
# =========================

def main():
    crear_estructura_directorios()
    copiar_a_landing()
    procesar_a_raw()
    construir_curated()
    generar_kpis()
    print("[DONE] Pipeline completo ejecutado.")


if __name__ == "__main__":
    main()
