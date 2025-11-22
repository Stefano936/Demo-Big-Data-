# 📥 GUÍA: Cómo agregar los archivos necesarios

## Archivos que necesitas descargar

El pipeline necesita **2 archivos TSV** del dataset de IMDb que NO están en el repositorio (por su tamaño).

### Paso 1: Descargar los archivos

1. Ve a: https://datasets.imdbws.com/
2. Busca y descarga estos dos archivos:
   - **title.basics.tsv.gz** (~500 MB comprimido, ~1 GB descomprimido)
   - **title.ratings.tsv.gz** (~50 MB comprimido, ~350 MB descomprimido)

### Paso 2: Descomprimir los archivos

Si descargaste con extensión `.gz`:
- **En Windows:** Usa 7-Zip o WinRAR para descomprimir
- **En Linux/Mac:** `gunzip title.basics.tsv.gz`

Resultado: deberías tener dos archivos sin extensión:
- `title.basics.tsv`
- `title.ratings.tsv`

### Paso 3: Colocar en la carpeta correcta

Copia ambos archivos a esta ruta:

```
Demo-Big-Data-/
└── proyecto_cadena_cines/
    └── data_original/          ← AQUÍ van los archivos
        ├── title.basics.tsv
        └── title.ratings.tsv
```

**Estructura completa esperada:**

```
proyecto_cadena_cines/
├── pipeline.py
├── README.md
├── data_original/
│   ├── title.basics.tsv       ✅ AGREGAR AQUÍ
│   ├── title.crew.tsv          (opcional)
│   └── title.ratings.tsv       ✅ AGREGAR AQUÍ
├── datalake/
│   ├── landing/
│   ├── raw/
│   └── curated/
└── analytics/
```

### Paso 4: Verificar

Antes de ejecutar el pipeline, verifica:
- [ ] `data_original/title.basics.tsv` existe y pesa ~1 GB
- [ ] `data_original/title.ratings.tsv` existe y pesa ~350 MB
- [ ] Estás en la carpeta `proyecto_cadena_cines/`
- [ ] Python 3.8+ está instalado: `python --version`
- [ ] Pandas está instalado: `pip install pandas`

### Paso 5: Ejecutar

```bash
python pipeline.py
```

## ⚠️ Importante

- **Tamaño total:** Necesitarás ~1.5 GB de espacio en disco
- **RAM recomendada:** Mínimo 4 GB para procesar sin problemas
- **Tiempo de ejecución:** Depende de tu equipo (entre 5-15 minutos aprox.)

## Alternativa: Script de descarga automática

Si tienes `Python` y `requests`, ejecuta esto en PowerShell desde `proyecto_cadena_cines`:

```powershell
python -c "
import urllib.request
import gzip
import os

urls = {
    'title.basics.tsv': 'https://datasets.imdbws.com/title.basics.tsv.gz',
    'title.ratings.tsv': 'https://datasets.imdbws.com/title.ratings.tsv.gz'
}

os.makedirs('data_original', exist_ok=True)

for filename, url in urls.items():
    print(f'Descargando {filename}...')
    gz_path = f'data_original/{filename}.gz'
    
    urllib.request.urlretrieve(url, gz_path)
    
    print(f'Descomprimiendo {filename}...')
    with gzip.open(gz_path, 'rb') as f_in:
        with open(f'data_original/{filename}', 'wb') as f_out:
            f_out.writelines(f_in)
    
    os.remove(gz_path)
    print(f'✓ {filename} listo')

print('¡Descarga completada!')
"
```

## 🤔 ¿Preguntas?

Consulta el `README.md` principal para más información sobre el pipeline.
