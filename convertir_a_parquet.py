import pandas as pd

df = pd.read_excel(r"C:\Users\GPS\Desktop\MASTER\Trabajo final master\TOTALES GPS.xlsx")

# Columnas que deben ser texto
df['Field Time'] = df['Field Time'].astype(str)

# Todas las demás columnas problemáticas las forzamos a numérico
columnas_numericas = [
    'Start Time',
    'End Time',
    '0-6km/h Velocity Band 1 Total Duration',
    '6-12km/h Velocity Band 2 Total Duration',
    '12-15km/h Velocity Band 3 Total Duration',
    '15-18km/h Velocity Band 4 Total Duration',
    '18-21km/h Velocity Band 5 Total Duration',
    '21-25km/h Velocity Band 6 Total Duration',
    '+25 Km/h Velocity Band 7 Total Duration',
]

for col in columnas_numericas:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df.to_parquet(r"C:\Users\GPS\Desktop\MASTER\Trabajo final master\totales_gps.parquet", index=False)
print("Listo!")


# CADA VEZ QUE ACTUALICE EXCEL 
#1. Convertir a Parquet

#python convertir_a_parquet.py

#Tiene que decir Listo!

#2. Subir a GitHub

#git add totales_gps.parquet
#git commit -m "Actualizar datos GPS"
#git push

#3. Actualizar la web

#Entrá a https://share.streamlit.io/ → tu app → tres puntitos ⋮ → Reboot app

#Listo. En 1-2 minutos la app tiene los datos nuevos.
