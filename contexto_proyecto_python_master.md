# Contexto del Proyecto — Python Master (GPS Rugby)

## Quién soy y cómo trabajo

- Estoy haciendo un **máster**, con módulos de entrega progresivos
- Soy **principiante en Python** — prefiero código simple, con comentarios `#` explicando cada línea
- Trabajo en **VS Code con Jupyter Notebook** (también usé Google Colab al inicio)
- Escribo los trabajos en **español**
- Quiero entender el **por qué** de cada cosa, no solo el código corregido
- Prefiero prosa natural en los textos académicos, sin transiciones forzadas

---

## El proyecto central

Análisis de datos GPS de un equipo de rugby, con el objetivo de extraer métricas de rendimiento físico por jugador y sesión.

**Nuevo proyecto en curso:** Web de rendimiento con **Streamlit** (archivo `.py` en VS Code), entrega el **25 de agosto**. Replica y expande un dashboard ya existente en Power BI.

---

## Datos

| Archivo | Descripción |
|---|---|
| `Datos_GPS_MASTER.xlsx` | Dataset principal con todas las sesiones |
| `Datos GPS Tarea 11.xlsx` | Dataset del Módulo 11 |

**Estructura del dato:** cada fila es un jugador en una sesión. Contiene:
- `Player Name`, `Position Name`, `Jersey`
- `Fecha`, `Activity Name`, `Day Name`, `Month Name`
- `MD` — tipo de día del microciclo: `MD`, `MD-2`, `MD-4`, `MD-5`, `MD+2`, `MD+3`
- `Rival` — usado como agrupador semanal
- `Minutos`, `Period Name`, `Period Tags`
- Métricas GPS: `Distancia Total`, `Total Player Load`, `HSR`, `Max Vel (% Max)`, `AI 18 Km/h`, aceleraciones, deceleraciones, contactos, etc.

**Columnas de posición agregadas:**
```python
# Posición simplificada agrupada
Pos_agrup = {'Prop': 'Pilar', 'Hooker': 'Hooker', ...}  # mapa a grupos

# Backs vs Forwards
Bk_Fw = {'Pilar': 'Fw', 'Hooker': 'Fw', ...}
```

**Filtros base aplicados:**
```python
df_sample = df[
    (df['Period Name'] == 'Session') &
    (df['Period Tags'] != 'Diferenciado') &
    (df['Minutos'] <= 100)
]
```

---

## DataFrames principales

| Variable | Qué es |
|---|---|
| `df_tot` | Dataset completo con jugadores reales + filas imputadas |
| `df_sample` / `df_sample_filtrado` | Subconjunto filtrado para análisis (jugadores con 6+ partidos) |
| `df_player` | Un registro por jugador (promedio de todas sus sesiones) |
| `df_faltantes` | Filas generadas para jugadores ausentes en sesiones |
| `df_md` | Filtrado solo a días de partido (`MD == 'MD'`) |

---

## Módulos completados

### Módulo 10 — Scoring de rendimiento (un partido)

**Métricas usadas:** Player Load, HSR, Sprint Distance, Aceleraciones, Deceleraciones, Contactos  
**Por qué esas:** baja intercorrelación, representan demandas neuromusculares distintas

**Proceso:**
```python
# 1. Normalización Min-Max (escala 0 a 1)
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
df_norm = scaler.fit_transform(df[metricas])

# 2. Multiplicar por peso de cada métrica
# Pesos asignados por impacto fisiológico en rugby (contacto tiene más peso)

# 3. Seleccionar solo columnas _p (ponderadas)
columnas_p = [col for col in df_norm.columns if col.endswith('_p')]

# 4. Sumar para puntuación final
df_pesos['Puntuacion_Final'] = df_pesos.sum(axis=1)
df_pesos = df_pesos.sort_values('Puntuacion_Final', ascending=False)
```

**Por qué Min-Max:** las métricas tienen escalas muy distintas (decimales vs cientos). Sin normalizar, las de mayor valor numérico dominarían el score injustamente.

**Visualización:** gráfico de barras apiladas (stacked bar) por jugador.

**Limitación documentada:** jugadores con menos minutos quedan penalizados (ej: Félix Paolucci con 60 min).

---

### Módulo 11 — Pipeline completo de análisis

#### 1. Generación de filas faltantes (`df_faltantes`)

**Lógica:** si un jugador estuvo en el partido (`MD`) de esa semana (`Rival`) pero no tiene registro en otro día, se le crea la fila.  
No se crean filas para el propio día de partido si falta.

```python
# Columnas fijas por jugador
cols_jugador = ['Jersey', 'Position Name']

# Columnas fijas por sesión
cols_sesion = ['Activity Name', 'Fecha', 'Month Name', 'Day Name', 'MD', 'Minutos', 'Rival']

# Métricas quedan en NaN para imputar después
df_faltantes = pd.concat([df_tot, nuevas_filas], ignore_index=True)
```

#### 2. Imputación personalizada de métricas

**Lógica (ratio individual/grupo):**
```python
# Para cada métrica y cada fila con NaN:
media_grupo = media histórica del grupo posicional (Pos_agrup) y tipo de día (MD)
media_jugador = media histórica individual del jugador para ese tipo de día
media_grupo_dia = media del grupo en esa fecha específica

# Valor imputado:
valor = media_grupo_dia * (media_jugador / media_grupo)
# Fallback si no hay dato de fecha: usar solo media_grupo
```

**Por qué:** imputa valores coherentes con el perfil individual del jugador, no solo el promedio del grupo.

```python
# Solo sobre filas reales (sin NaN) para calcular medias
df_reales = df_tot.dropna(subset=metricas)

# Rellenar NaN por grupo posicional y fecha
df_tot[col] = df_tot.groupby(["Pos_agrup", "Fecha"])[col].transform(
    lambda x: x.fillna(x.mean())
)
```

**Caso especial — Contactos:** valores < 5 se trataron como NaN y se imputaron con la media individual histórica del jugador (solo registros ≥ 5).

#### 3. Variable de fatiga (`fatiga`)

**Es una variable simulada/sintética** — no existe en el dataset original.

```python
# Métricas base normalizadas que componen la fatiga
fatiga = f(Minutos, Contacto x min, Esfuerzos Explosivos Rugby,
           Distancia Explosiva, Max Vel (% Max))

# Componente aleatorio (10%) para simular variabilidad individual
componente_random = np.random.uniform(0, 10, len(df_tot))
```

**Rangos por tipo de día:**
```python
md_fatiga_rango = {
    'MD': (70, 90),
    'MD-2': (50, 70),
    'MD-4': (40, 60),
    'MD-5': (30, 50),
    'MD+2': (10, 30),
    'MD+3': (20, 40)
}
```

**Limitación documentada:** la variable es sintética. Los jugadores con valores imputados por media recibirán fatiga diferente por el componente random, lo cual refleja variabilidad individual pero no datos reales.

#### 4. Modelo de fatiga — Random Forest

```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# Variables explicativas (excluir las que componen la fórmula de fatiga)
explicativas = ['Distancia Total', 'Total Player Load', 'HSR',
                'Max Deceleration', 'AI 18 Km/h', ...]
cat_cols = ['MD']  # se hace one-hot encoding

X = pd.get_dummies(df_tot[explicativas + cat_cols])
y = df_tot['fatiga']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = RandomForestRegressor()
model.fit(X_train, y_train)
```

**Métricas obtenidas:** R² ≈ 0.85, RMSE ≈ 0.22, MAE ≈ 0.16

**Lección clave:** `MD_MD+2` tenía 40% de importancia porque la variable `fatiga` fue construida con rangos por tipo de día — el modelo "aprendía de vuelta" esa información. Solución: reducir el componente por día a ruido aleatorio puro (10%), haciendo que `Distancia Total` (43%) sea la variable dominante, más coherente fisiológicamente.

**Importancia de features (tras corrección):**
1. Distancia Total (43%)
2. Contact Involvement
3. Deceleraciones
4. Aceleraciones

#### 5. Clustering de perfiles de jugadores

**Dataset:** `df_player` — un promedio por jugador, solo los con 6+ partidos (~55 jugadores)

**Problema resuelto:** jugadores con cambio de posición mid-season generaban duplicados. Solución: mapear a la posición más frecuente antes del `groupby`.

```python
# Posición más frecuente por jugador
pos_frecuente = df_sample_filtrado.groupby('Player Name')['Pos_agrup'].agg(
    lambda x: x.value_counts().index[0]
)

# Agregar por jugador
df_player = df_sample_filtrado.groupby('Player Name')[metricas].mean()
df_player['Pos_agrup'] = df_player.index.map(pos_frecuente)
```

**PCA antes de clustering:**
```python
from sklearn.decomposition import PCA

# Criterio Kaiser (eigenvalues > 1) o varianza acumulada >= 90%
pca = PCA()
pca.fit(df_scaled)
# Seleccionar n componentes según criterio elegido
```

**Método del codo para k óptimo:**
```python
inercias = []
for k in range(2, 8):
    km = KMeans(n_clusters=k)
    km.fit(df_pca)
    inercias.append(km.inertia_)

# Detectar codo automáticamente
diffs = np.diff(inercias)
k_opt = np.argmin(diffs) + (range_start + 1)
# +n porque np.argmin devuelve índice 0 pero el rango empieza en 2
```

**Resultados finales (k=3, jerárquico):**
- Silueta KMeans: 0.429 / Silueta Jerárquico: 0.423
- Se eligió jerárquico como método principal (clusters más compactos)

**3 perfiles identificados:**
| Cluster | Perfil | Características |
|---|---|---|
| 0 | Backs explosivos | HSR alto, aceleraciones altas, contactos bajos |
| 1 | Forwards de contacto | Contactos altos, HSR bajo |
| 2 | Forwards pesados / suplentes | Valores bajos en todo, menos tiempo de juego |

**Nota de dominio:** el Cluster de backs incluye principalmente wings y fullbacks, que en rugby tienen perfiles físicos muy distintos de los forwards.

---

## Nuevo proyecto — Web Streamlit

**Objetivo:** app web de rendimiento GPS en Python + Streamlit  
**Entrega máster:** 25 de agosto de 2026  
**Stack:** `app.py` directo en VS Code, sin Jupyter

```bash
# Para correr la app
streamlit run app.py
```

**Secciones — Bloque 1 (máster):**
- Informe de partido
- Informe de sesión
- % de velocidades máximas
- Distancia a distintos umbrales de velocidad
- Scoring de rendimiento por partido
- Perfiles de jugadores (clustering)

**Secciones — Bloque 2 (para el club, post-entrega):**
- Carga acumulada / ACWR / EWMA
- Datos antropométricos
- Comparativa jugador vs puesto / equipo
- Base de lesiones + predicción

**Referencia visual:** existe un dashboard en Power BI que muestra el resultado esperado.

---

## Errores frecuentes y cómo resolverlos

| Problema | Causa | Solución |
|---|---|---|
| `KeyError` en columna | El nombre no coincide exactamente | Verificar con `df.columns.tolist()` |
| Columna droped silenciosamente en `.mean()` | Dtype no numérico | Verificar con `df.dtypes` antes |
| `if value` falla con 0 | Python trata 0 como False | Usar `if value is not None` |
| `LossySetitemError` | Dtype incompatible al asignar | Agregar `.astype(float)` |
| `KeyError: 'MD+5'` | Valor inesperado en columna MD | Verificar con `df['MD'].unique()` |

---

## Librerías usadas

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import silhouette_score
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
import streamlit as st  # para el nuevo proyecto
```

**Instalación:**
```bash
pip install pandas openpyxl matplotlib seaborn scikit-learn streamlit scipy
```

---

## Preferencias de trabajo

- Código lo más simple posible, con comentarios `#` en cada línea importante
- Explicar el **por qué** antes de mostrar el código corregido
- Textos académicos en español, prosa natural (sin "se conecta" ni transiciones forzadas)
- Si hay varias opciones, presentar la más sencilla primero
- Siempre verificar nombres de columnas antes de asumir que existen
