# -*- coding: utf-8 -*-
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, split, explode
from pyspark.sql.types import IntegerType, FloatType

# ================================
# CONFIGURACIÓN
# ================================

HDFS_BASE = "hdfs://namenode:9000/datalake"
LANDING = HDFS_BASE + "/landing"
RAW = HDFS_BASE + "/raw"
CURATED = HDFS_BASE + "/curated"

IMDB_FILES = ["title.basics.tsv", "title.ratings.tsv"]

spark = (
    SparkSession.builder
    .appName("IMDb Pipeline HDFS + Spark (Py2 Compatible)")
    .getOrCreate()
)

# ================================
# 1) INGESTA → LANDING
# ================================

def copiar_a_landing():

    for fname in IMDB_FILES:
        local_path = fname
        hdfs_path = LANDING + "/" + fname

        if not os.path.exists(local_path):
            print("[WARN] No existe " + local_path)
            continue

        df = (
            spark.read
            .option("sep", "\t")
            .option("header", True)
            .csv(local_path)
        )

        df.write.mode("overwrite").option("sep", "\t").csv(hdfs_path)

        print("[OK] Copiado TSV a LANDING: " + fname)

# ================================
# 2) LANDING → RAW (TSV → CSV)
# ================================

def procesar_a_raw():

    basics_path = LANDING + "/title.basics.tsv"
    ratings_path = LANDING + "/title.ratings.tsv"

    print("[INFO] Leyendo TSV desde landing...")

    basics = spark.read.option("sep", "\t").csv(basics_path, header=True)
    ratings = spark.read.option("sep", "\t").csv(ratings_path, header=True)

    # normalizar columnas
    basics = basics.toDF(*[c.lower() for c in basics.columns])
    ratings = ratings.toDF(*[c.lower() for c in ratings.columns])

    basics.write.mode("overwrite").csv(RAW + "/basics_raw", header=True)
    ratings.write.mode("overwrite").csv(RAW + "/ratings_raw", header=True)

    print("[OK] RAW generado (TSV → CSV).")

# ================================
# 3) RAW → CURATED
# ================================

def construir_curated():

    basics_raw = spark.read.csv(RAW + "/basics_raw", header=True)
    ratings_raw = spark.read.csv(RAW + "/ratings_raw", header=True)

    # filtrar películas
    movies = basics_raw.filter(col("titletype") == "movie")

    movies = (
        movies
        .withColumn("startyear", col("startyear").cast(IntegerType()))
        .withColumn("runtimeminutes", col("runtimeminutes").cast(IntegerType()))
    )

    ratings = (
        ratings_raw
        .withColumn("averagerating", col("averagerating").cast(FloatType()))
        .withColumn("numvotes", col("numvotes").cast(IntegerType()))
    )

    # join
    merged = (
        movies.join(
            ratings.select("tconst", "averagerating", "numvotes"),
            on="tconst",
            how="inner"
        )
        .dropna(subset=["startyear", "runtimeminutes", "averagerating", "numvotes"])
    )

    # tabla de géneros
    generos = (
        merged
        .select("tconst", split(col("genres"), ",").alias("genre_list"))
        .withColumn("genero", explode(col("genre_list")))
        .select("tconst", "genero")
        .drop_duplicates()
    )

    generos.write.mode("overwrite").csv(CURATED + "/generos", header=False)

    curated = merged.drop("genres","titletype","endyear","genres")
    curated.write.mode("overwrite").csv(CURATED + "/movies_curated", header=False)

    print("[OK] CURATED generado en HDFS.")

# ================================
# MAIN
# ================================

def main():
    copiar_a_landing()
    procesar_a_raw()
    construir_curated()
    print("[DONE] Pipeline Spark + HDFS completado (Python 2.7 compatible).")

if __name__ == "__main__":
    main()
