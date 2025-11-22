# Demo Big Data - Cadena de Cines

Pipeline ETL para procesar datos de películas de IMDb en un Data Lake con arquitectura de capas (Landing → Raw → Curated).

## 📋 Requisitos

- Python 3.8 o superior
- pandas
- pathlib (incluido en Python)

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/Stefano936/Demo-Big-Data-.git
cd Demo-Big-Data-/proyecto_cadena_cines
```

### 2. Instalar dependencias

```bash
pip install pandas
```

## 📁 Estructura de directorios

El pipeline requiere la siguiente estructura de carpetas:

```
proyecto_cadena_cines/
├── pipeline.py                 # Script principal
├── data_original/              # 📥 Archivos fuente (REQUIERE AGREGAR)
│   ├── title.basics.tsv       # Datos básicos de títulos IMDb
│   └── title.ratings.tsv      # Ratings e información de votos
├── datalake/
│   ├── landing/               # ⚠️ Capa de ingesta (se genera automáticamente)
│   ├── raw/                   # ⚠️ Capa de procesamiento (se genera automáticamente)
│   └── curated/               # ⚠️ Capa de datos finales (se genera automáticamente)
└── analytics/                 # ⚠️ KPIs y reportes (se genera automáticamente)
```

**NOTA:** Las carpetas marcadas con ⚠️ se crean automáticamente al ejecutar el pipeline.

## 📥 Descargar archivos de IMDb

Los archivos TSV no están en el repositorio por su tamaño. Debes descargarlos manualmente de IMDb:

### Opción 1: Descarga manual

1. Visita: https://datasets.imdbws.com/
2. Descarga los siguientes archivos:
   - `title.basics.tsv.gz`
   - `title.ratings.tsv.gz`
3. Descomprimelos y renómbralos quitando la extensión `.gz`
4. Copia ambos archivos a la carpeta `data_original/`

### Opción 2: Script de descarga (si tienes wget o curl)

```powershell
# En Windows PowerShell, desde la carpeta proyecto_cadena_cines:
$url_basics = "https://datasets.imdbws.com/title.basics.tsv.gz"
$url_ratings = "https://datasets.imdbws.com/title.ratings.tsv.gz"

# Crear carpeta si no existe
New-Item -ItemType Directory -Path "data_original" -Force

# Descargar
Invoke-WebRequest -Uri $url_basics -OutFile "data_original/title.basics.tsv.gz"
Invoke-WebRequest -Uri $url_ratings -OutFile "data_original/title.ratings.tsv.gz"

# Descomprimir (necesita 7-Zip o similar instalado)
```

## ▶️ Ejecutar el pipeline

Una vez que hayas agregado los archivos TSV en `data_original/`:

```bash
cd proyecto_cadena_cines
python pipeline.py
```

## 📊 ¿Qué hace el pipeline?

El pipeline ejecuta 4 etapas automáticamente:

### 1️⃣ **Ingesta (Landing)**
- Copia `title.basics.tsv` y `title.ratings.tsv` desde `data_original/` a `datalake/landing/`

### 2️⃣ **Procesamiento (Raw)**
- Lee archivos TSV
- Normaliza nombres de columnas a minúsculas
- Guarda como CSV en `datalake/raw/`
  - `basics_raw.csv`
  - `ratings_raw.csv`

### 3️⃣ **Integración (Curated)**
- Filtra solo películas (excluye series, documentales, etc.)
- Une datos de básicos + ratings
- Elimina filas con valores faltantes críticos
- Genera columna `genre_principal`
- Guarda en `datalake/curated/movies_curated.csv`

### 4️⃣ **Analytics (KPIs)**
Genera 3 reportes en `analytics/`:
- `ratings_por_genero.csv` → Rating promedio por género
- `popularidad_por_anio.csv` → Votos promedio por año de estreno
- `distribucion_duracion.csv` → Estadísticas de duración de películas

## 📤 Salida esperada

Después de ejecutar el pipeline, verás algo como:

```
[OK] Estructura de carpetas creada/verificada.
[OK] Copiado a landing: title.basics.tsv
[OK] Copiado a landing: title.ratings.tsv
[INFO] Cargando title.basics.tsv...
[INFO] Cargando title.ratings.tsv...
[OK] Archivos procesados a RAW.
[OK] Dataset curated generado: datalake/curated/movies_curated.csv
[INFO] Filas en curated: 500000 (aproximadamente)
[OK] KPI rating promedio por género generado.
[OK] KPI popularidad por año generado.
[OK] Métricas de distribución de duración generadas.
[DONE] Pipeline completo ejecutado.
```

## 🔍 Solución de problemas

### ❌ Error: "No se encontró data_original/title.basics.tsv"
**Solución:** Verifica que los archivos TSV estén en la carpeta `data_original/` correctamente nombrados.

### ❌ Error: "No existe movies_curated.csv"
**Solución:** Asegúrate de que el pipeline se ejecutó correctamente sin errores en etapas anteriores.

### ❌ Error de memoria con archivos muy grandes
**Solución:** El archivo `title.basics.tsv` (~1 GB) requiere al menos 4 GB de RAM disponible.

## 📝 Archivos del proyecto

| Archivo | Descripción |
|---------|-------------|
| `pipeline.py` | Script principal del ETL |
| `README.md` | Este archivo |
| `.gitignore` | Configuración para excluir archivos grandes |

## 🔗 Referencias

- IMDb Datasets: https://datasets.imdbws.com/
- Documentación de pandas: https://pandas.pydata.org/

## 📧 Notas

- Los archivos `.tsv` originales NO están en el repositorio (excedían límite de GitHub)
- Se requiere descargarlos manualmente desde IMDb
- El pipeline está optimizado para arquitectura de Data Lake moderna
