import pandas as pd
import numpy as np

FORWARDS = ['Pilar izquierdo', 'Pilar derecho', 'Hooker', 'Segunda Linea', 'Ala', 'Octavo']
BACKS    = ['Medio Scrum', 'Apertura', 'Centro', 'Wing', 'Full Back']
MDS      = ['MD', 'MD-4', 'MD+3']

COLS_CONTACTO = [
    'Contact Involvement Total Count Avg',
    'Contacto x min',
    'Contact Involvement Average BiG Time',
    'Contact Involvement BiG Time Short Count',
    'Contact Involvement BiG Time Med Count',
    'Contact Involvement BiG Time Long Count',
]

# Columnas que se imputan por ratio (Contacto x min se calcula al final)
COLS_CONTACTO_IMPUTAR = [
    'Contact Involvement Total Count Avg',
    'Contact Involvement Average BiG Time',
    'Contact Involvement BiG Time Short Count',
    'Contact Involvement BiG Time Med Count',
    'Contact Involvement BiG Time Long Count',
]

UMBRAL_CONTACTO    = 5
UMBRAL_CONTACTO_01 = 2
UMBRAL_MINUTOS     = 30
UMBRAL_SIMILITUD   = 0.90


def simular_contactos(df: pd.DataFrame):
    df = df.copy()
    df['Position Name'] = df['Position Name'].str.replace(
        'Pilar izquiero', 'Pilar izquierdo', regex=False
    )
    df['_Bk_Fw'] = df['Position Name'].apply(
        lambda x: 'Back' if x in BACKS else ('Forward' if x in FORWARDS else 'Otro')
    )
    df['_pos_grupo'] = df['_Bk_Fw']

    # Máscaras de detección — basadas SIEMPRE en Contact Count Avg
    mask_fw = (
        (df['_Bk_Fw'] == 'Forward') &
        (df['MD'].isin(MDS)) &
        (df['Contact Involvement Total Count Avg'] < UMBRAL_CONTACTO) &
        (df['Minutos'] > UMBRAL_MINUTOS)
    )
    mask_bk_prea = (
        (df['_Bk_Fw'] == 'Back') &
        (df['Equipo'] == 'Pre A') &
        (df['MD'].isin(MDS)) &
        (df['Contact Involvement Total Count Avg'] < UMBRAL_CONTACTO) &
        (df['Minutos'] > UMBRAL_MINUTOS)
    )
    mask_bk_01 = (
        (df['_Bk_Fw'] == 'Back') &
        (df['Equipo'].isin(['Primera', 'Intermedia'])) &
        (df['MD'].isin(MDS)) &
        (df['Contact Involvement Total Count Avg'] <= UMBRAL_CONTACTO_01) &
        (df['Minutos'] > UMBRAL_MINUTOS)
    )

    # Backs 2-4 contactos con promedio histórico > 5
    df_reales_bk = df[
        (df['_Bk_Fw'] == 'Back') &
        (df['Contact Involvement Total Count Avg'] >= UMBRAL_CONTACTO)
    ]
    jug_hist_5 = set(
        df_reales_bk.groupby('Player Name')['Contact Involvement Total Count Avg']
        .mean().pipe(lambda s: s[s > UMBRAL_CONTACTO]).index
    )
    mask_bk_24 = (
        (df['_Bk_Fw'] == 'Back') &
        (df['Equipo'].isin(['Primera', 'Intermedia'])) &
        (df['MD'].isin(MDS)) &
        (df['Contact Involvement Total Count Avg'] > UMBRAL_CONTACTO_01) &
        (df['Contact Involvement Total Count Avg'] < UMBRAL_CONTACTO) &
        (df['Minutos'] > UMBRAL_MINUTOS) &
        (df['Player Name'].isin(jug_hist_5))
    )

    mask_ratio   = mask_fw | mask_bk_01 | mask_bk_24
    mask_prom_dia = mask_bk_prea
    mask_total   = mask_ratio | mask_prom_dia

    # Datos reales para calcular medias (excluir filas a simular)
    df_reales = df[~mask_total].copy()

    idx_corregidos = df[mask_total].index.tolist()

    # Aplicar imputación para cada columna de contacto
    for col in COLS_CONTACTO_IMPUTAR:
        df[col] = df[col].astype(float)

        media_hist_jug   = df_reales.groupby(['Player Name', 'MD'])[col].mean()
        media_hist_grupo = df_reales.groupby(['_pos_grupo', 'MD'])[col].mean()
        media_dia_grupo  = df_reales.groupby(['_pos_grupo', 'MD', 'Fecha'])[col].mean()
        mins_dia_grupo   = df_reales.groupby(['_pos_grupo', 'MD', 'Fecha'])['Minutos'].mean()

        def imputar(row, modo):
            pos     = row['_pos_grupo']
            md      = row['MD']
            fecha   = row['Fecha']
            jugador = row['Player Name']
            mins    = row['Minutos']

            med_dia   = media_dia_grupo.get((pos, md, fecha), None)
            mins_prom = mins_dia_grupo.get((pos, md, fecha), None)

            if med_dia is None:
                return row[col]

            if modo == 'promedio_dia':
                return med_dia

            # Modo ratio
            med_jug   = media_hist_jug.get((jugador, md), None)
            med_grupo = media_hist_grupo.get((pos, md), None)

            if med_jug is not None and med_grupo is not None and med_grupo > 0:
                valor_esperado = med_dia * (med_jug / med_grupo)
            else:
                valor_esperado = med_dia

            # Descuento por minutos
            if mins_prom is not None and mins_prom > 0:
                pct = mins / mins_prom
                if pct < UMBRAL_SIMILITUD:
                    return valor_esperado * pct

            return valor_esperado

        if mask_ratio.any():
            df.loc[mask_ratio, col] = df[mask_ratio].apply(
                lambda r: imputar(r, 'ratio'), axis=1
            ).astype(float)

        if mask_prom_dia.any():
            df.loc[mask_prom_dia, col] = df[mask_prom_dia].apply(
                lambda r: imputar(r, 'promedio_dia'), axis=1
            ).astype(float)

    # Contacto x min: calculado directo de las columnas ya imputadas
    df['Contacto x min'] = df['Contact Involvement Total Count Avg'] / df['Minutos']

    df = df.drop(columns=['_Bk_Fw', '_pos_grupo'])
    return df, idx_corregidos



if __name__ == '__main__':
    # ── Generar Excel ─────────────────────────────────────────────────────────────
    df_orig = pd.read_excel('/mnt/project/TOTALES_GPS.xlsx')
    df_filt = df_orig[
        (df_orig['Period Name'] == 'Session') &
        (df_orig['Period Tags'] != 'Diferenciado')
    ].copy()
    df_filt['Fecha'] = pd.to_datetime(df_filt['Fecha'])

    df_corregido, idx = simular_contactos(df_filt)

    # Tomar solo las filas simuladas con todas las columnas originales
    df_export = df_corregido.loc[idx].copy()

    # Restaurar formato de Fecha igual al original (date sin hora)
    df_export['Fecha'] = df_export['Fecha'].dt.date

    # Field Time: tomar del original (ya está bien, son strings "H:MM:SS")
    df_export['Field Time'] = df_filt.loc[idx, 'Field Time'].values

    df_export = df_export.sort_values(['Equipo', 'Fecha', 'Player Name']).reset_index(drop=True)
    df_export.to_excel('/home/claude/simulacion_contactos.xlsx', index=False)
    print(f'Exportado: {len(df_export)} filas, {len(df_export.columns)} columnas')
    print('\nVerificación columnas contacto (primeras 5 filas):')
    print(df_export[['Player Name','Fecha','MD'] + COLS_CONTACTO].head(5).to_string(index=False))