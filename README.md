# Optimizador de portafolios financieros

Aplicación Streamlit para comparar carteras long-only mediante simulación Monte Carlo. Calcula rendimientos y covarianzas a partir de precios históricos o usa datos sintéticos de ejemplo.

## Funciones

- Acepta un CSV de precios con una columna por activo, o utiliza datos sintéticos.
- Simula pesos no negativos que suman 100%.
- Anualiza rendimiento, volatilidad y ratio de Sharpe.
- Identifica las carteras de mayor Sharpe simulado y mínima volatilidad.
- Muestra la nube riesgo-rendimiento y permite exportar los pesos seleccionados.

## Estructura

```text
.
├── backend.py       # Cálculo de carteras y métricas
├── frontend.py      # Interfaz Streamlit y visualizaciones
├── requirements.txt
└── README.md
```

## Formato del CSV

Cada columna numérica representa un activo y cada fila un periodo cronológico de precios. Se aceptan al menos dos activos y 11 filas. Una columna opcional `fecha` se usa para ordenar las observaciones.

```csv
fecha,Fondo A,Fondo B
2024-01-31,100,80
2024-02-29,102,79
2024-03-31,101,82
```

Usa precios ajustados y la frecuencia correcta al elegir periodos por año (12 mensual, 52 semanal o 252 diario).

## Instalación y ejecución

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run frontend.py
```

En macOS o Linux, activa el entorno con `source .venv/bin/activate`.

## Interpretación y límites

El ratio de Sharpe se calcula con la tasa libre de riesgo ingresada. La optimización es una búsqueda aleatoria con pesos long-only y las estimaciones dependen de los rendimientos históricos, del periodo de anualización y del número de carteras simuladas. Los resultados son educativos, no recomendaciones ni garantías de rendimiento.
