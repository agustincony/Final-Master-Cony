import pandas as pd

df = pd.read_excel(r"C:\Users\GPS\Desktop\MASTER\Trabajo final master\TOTALES GPS.xlsx")
df['Field Time'] = df['Field Time'].astype(str)
df.to_parquet(r"C:\Users\GPS\Desktop\MASTER\Trabajo final master\totales_gps.parquet", index=False)
print("Listo!")


# CADA VEZ QUE ACTUALICE EXCEL 
# python convertir_a_parquet.py