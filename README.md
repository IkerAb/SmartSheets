# SmartSheets — Sales Forecasting API

API REST production-ready para análisis, forecasting y detección de anomalías en datos de ventas.
Sube un CSV o Excel y obtén KPIs, predicciones con intervalos de confianza y simulaciones de escenarios.

## Stack

- **FastAPI** + Python 3.11
- **statsmodels** (ETS forecasting, fallback naive)
- **pandas / numpy** — ETL y análisis
- **PostgreSQL** — persistencia canonical
- **Docker + docker-compose** — deploy en un comando

## Inicio rápido

### Con Docker (recomendado)

```bash
git clone https://github.com/Txmpeer/SmartSheets.git
cd SmartSheets
git checkout workspace
cd project
cp .env.example .env   # opcional, valores por defecto funcionan
docker compose up --build
```

API disponible en `http://localhost:8000`
Documentación: `http://localhost:8000/docs`

### Local (sin Docker)

```bash
cd project
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# requiere PostgreSQL corriendo localmente
uvicorn app.main:app --reload
```

## Formato del archivo

El CSV/Excel debe tener estas columnas (case-insensitive):

| Columna   | Tipo     | Ejemplo      |
|-----------|----------|--------------|
| `fecha`   | fecha    | `2023-01-15` |
| `producto`| texto    | `Laptop Pro` |
| `ventas`  | numérico | `4500.00`    |

## Ejemplos curl

### 1. Subir archivo
```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@data/sample/sales_sample.csv"
# → {"dataset_id": "abc-123", "row_count": 1825, ...}
```

### 2. Insights
```bash
curl "http://localhost:8000/api/v1/insights?dataset_id=abc-123"
```

### 3. Forecast 60 días
```bash
curl "http://localhost:8000/api/v1/forecast?dataset_id=abc-123&horizon=60"
```

### 4. Forecast por producto
```bash
curl "http://localhost:8000/api/v1/forecast?dataset_id=abc-123&product=Laptop+Pro&horizon=30"
```

### 5. Forecast mensual
```bash
curl "http://localhost:8000/api/v1/forecast?dataset_id=abc-123&horizon=6&aggregation=month"
```

### 6. Detectar anomalías
```bash
curl "http://localhost:8000/api/v1/insights?dataset_id=abc-123&anomaly_method=iqr"
```

### 7. Simular precio +20%, volumen -15%
```bash
curl -X POST http://localhost:8000/api/v1/simulate \
  -H "Content-Type: application/json" \
  -d '{"dataset_id":"abc-123","price_modifier":1.20,"volume_modifier":0.85,"horizon":30}'
```

### 8. Health check
```bash
curl http://localhost:8000/api/v1/health
```

## Tests

```bash
cd project
pytest tests/ -v --tb=short
```

## Estructura

```
project/
├── app/
│   ├── core/          # config, logging, database
│   ├── routes/        # HTTP endpoints
│   ├── services/      # lógica de negocio
│   ├── models/        # schemas Pydantic + DTOs
│   ├── repositories/  # acceso a PostgreSQL
│   └── utils/         # validators, file handler
├── tests/
├── data/sample/
├── docs/adr/
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```
