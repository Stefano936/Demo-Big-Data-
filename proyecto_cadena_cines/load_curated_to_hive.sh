#!/usr/bin/env bash
set -e

echo "[INFO] Creando base de datos si no existe..."
docker exec -it hive-server schematool -dbType derby -initSchema >/dev/null 2>&1 || true

echo "[INFO] Ejecutando comandos Hive..."

docker exec -it hive-server bash -c "
hive -e \"
CREATE DATABASE IF NOT EXISTS imdb_curated;

-- ===========================================
-- Tabla movies_curated
-- ===========================================
CREATE EXTERNAL TABLE IF NOT EXISTS imdb_curated.movies_curated (
    tconst STRING,
    primarytitle STRING,
    originaltitle STRING,
    isadult INT,
    startyear INT,
    runtimeminutes INT,
    averagerating DOUBLE,
    numvotes INT
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION 'hdfs://namenode:9000/datalake/curated/movies_curated';

-- ===========================================
-- Tabla generos
-- ===========================================
CREATE EXTERNAL TABLE IF NOT EXISTS imdb_curated.generos (
    tconst STRING,
    genero STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION 'hdfs://namenode:9000/datalake/curated/generos';

MSCK REPAIR TABLE imdb_curated.movies_curated;
MSCK REPAIR TABLE imdb_curated.generos;

\"
"

echo "[OK] Tablas Hive creadas y listas para Power BI."
