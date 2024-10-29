import streamlit as st
import pandas as pd 


file_path = 'historico.xlsx'
historico_df = pd.read_excel(file_path, sheet_name='Historico')

file_path_vpr = 'BASE DE DATOS VALOR PRESENTE RELOAD.xlsx'
siniestros = pd.read_excel(file_path_vpr, sheet_name='Pólizas y Eventos')

siniestros = siniestros[siniestros['Evento ID'].notna()]

occurrences_by_country = historico_df['ISO'].value_counts().reset_index()
occurrences_by_country.columns = ['Country', 'Occurrences']
occurrences_by_country = occurrences_by_country.merge(
    historico_df[['ISO', 'Region']].drop_duplicates(),
    left_on='Country', 
    right_on='ISO',
    how='left'
).drop(columns=['ISO']).rename(columns={'Region': 'Continent'})
occurrences_by_country = occurrences_by_country.merge(
    historico_df[['ISO', 'Country']].drop_duplicates(),
    left_on='Country',
    right_on='ISO',
    how='left'
).drop(columns=['ISO'])

total_occurrences = occurrences_by_country['Occurrences'].sum()
occurrences_by_country['Percentage'] = (occurrences_by_country['Occurrences'] / total_occurrences)

df_means = siniestros.groupby('Continente')[
    ['Suma Asegurada ajustada', 'Monto del siniestro valor presente','Precipitación (mm)']
].mean().reset_index()
global_mean_precipitacion = siniestros['Precipitación (mm)'].mean()
df_means['Factor precipitacion'] = (df_means['Precipitación (mm)'] / global_mean_precipitacion)


#######################################WEB APP#######################################

# Define the calculator function
def calculate_prima_comercial(frecuencia_inundacion,costo_medio_siniestros,factor_precipitacion,factor_suma_asegurada
                              ,gastos_percent=5,utilidad_percent=5):
    # Calculate Prima Pura
    prima_pura = (frecuencia_inundacion * costo_medio_siniestros * 
                  factor_precipitacion * factor_suma_asegurada)
    
    # Calculate Prima Comercial
    prima_comercial = prima_pura / (1 - (gastos_percent + utilidad_percent) / 100)
    
    return prima_pura, prima_comercial

# Title of the app
st.title("Calculadora de Prima Comercial y Prima Pura")

# User inputs
suma_asegurada=st.number_input("Suma Asegurada", min_value=0.0)
pais = st.selectbox("País", options=occurrences_by_country["Country_y"].unique())
gastos_percent=st.number_input("Gastos en Porcentaje", min_value=0.0)
utilidad_percent=st.number_input("Utilidad en Porcentaje", min_value=0.0)


contienente=occurrences_by_country[occurrences_by_country['Country_y']==pais]['Continent'].values[0]
frecuencia_inundacion=occurrences_by_country[occurrences_by_country['Country_y']==pais]['Percentage'].values[0] 

costo_medio_siniestros=df_means[df_means['Continente']==contienente]['Monto del siniestro valor presente'].values[0]
factor_precipitacion=df_means[df_means['Continente']==contienente]['Factor precipitacion'].values[0]

factor_suma_asegurada=suma_asegurada/df_means[df_means['Continente']==contienente]['Suma Asegurada ajustada'].values[0]



# Calculate and display results when the button is clicked
if st.button("Calcular Prima"):
    prima_pura, prima_comercial = calculate_prima_comercial(
        frecuencia_inundacion,costo_medio_siniestros,factor_precipitacion,factor_suma_asegurada
                              ,gastos_percent,utilidad_percent
    )
    st.write(f"**Prima Pura:** {prima_pura:,.2f}")
    st.write(f"**Prima Comercial:** {prima_comercial:,.2f}")
