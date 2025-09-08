import streamlit as st
import pandas as pd

@st.cache_data
def cargar_datos():
    df = pd.read_csv('composicion_macro_100g.csv', delimiter=';', decimal=',')
    df.columns = [col.strip() for col in df.columns]
    return df

df_alimentos = cargar_datos()

def harris_benedict(sexo, peso, altura, edad):
    if sexo == 'hombre':
        return 88.362 + (13.397 * peso) + (4.799 * altura) - (5.677 * edad)
    else:
        return 447.593 + (9.247 * peso) + (3.098 * altura) - (4.330 * edad)

activity_multipliers = {
    "Alto": 1.6,
    "Medio": 1.55,
    "Bajo": 1.5
}

macro_per_kg = {
    "Alto": {"proteina": 1.4, "grasas": 0.7},
    "Medio": {"proteina": 1.7, "grasas": 1.1},
    "Bajo": {"proteina": 2.0, "grasas": 1.5}
}

meal_distribution = {
    "Desayuno": {"proteina": 0.10, "grasas": 0.10, "carbos": 0.27},
    "Comida": {"proteina": 0.39, "grasas": 0.40, "carbos": 0.26},
    "Merienda": {"proteina": 0.08, "grasas": 0.06, "carbos": 0.17},
    "Cena": {"proteina": 0.43, "grasas": 0.44, "carbos": 0.30}
}

def calcular_macros(peso, kcal_totales, nivel, ajuste_porcentual):
    proteina_g = macro_per_kg[nivel]["proteina"] * peso
    grasas_g = macro_per_kg[nivel]["grasas"] * peso

    kcal_proteinas = proteina_g * 4
    kcal_grasas = grasas_g * 9

    kcal_carbos = kcal_totales - kcal_proteinas - kcal_grasas
    carbos_g = kcal_carbos / 4 if kcal_carbos > 0 else 0

    factor_ajuste = 1 + (ajuste_porcentual / 100)
    proteina_g = round(proteina_g * factor_ajuste, 1)
    grasas_g = round(grasas_g * factor_ajuste, 1)
    carbos_g = round(carbos_g * factor_ajuste, 1)

    return proteina_g, grasas_g, carbos_g

def macros_por_comida(proteina_g, grasas_g, carbos_g, comida):
    dist = meal_distribution[comida]
    prot = round(proteina_g * dist["proteina"], 1)
    gras = round(grasas_g * dist["grasas"], 1)
    carb = round(carbos_g * dist["carbos"], 1)
    return prot, gras, carb

st.title("Calculadora de kcal y macros con recetas")

sexo = st.selectbox("Sexo", ["hombre", "mujer"])
peso = st.number_input("Peso (kg)", value=65.0, min_value=30.0, max_value=200.0, step=0.1)
altura = st.number_input("Altura (cm)", value=178.0, min_value=100.0, max_value=250.0, step=0.1)
edad = st.number_input("Edad (años)", value=30, min_value=10, max_value=120)
nivel_actividad = st.selectbox("Nivel de actividad", list(activity_multipliers.keys()))
multiplicador_custom = st.text_input("Multiplicador personalizado (opcional)")
kcal_extra = st.number_input("Calorías extras manuales", value=0)
ajuste_porcentual = st.slider("Ajuste porcentual total (%)", -25, 25, 0)
comida = st.selectbox("Comida del día", list(meal_distribution.keys()))

if st.button("Calcular"):
    tmb = harris_benedict(sexo, peso, altura, edad)

    if multiplicador_custom.strip() != "":
        try:
            multiplicador = float(multiplicador_custom)
        except:
            st.error("Multiplicador personalizado inválido")
            st.stop()
    else:
        multiplicador = activity_multipliers[nivel_actividad]

    kcal_totales = tmb * multiplicador + kcal_extra
    kcal_totales *= (1 + ajuste_porcentual / 100)

    proteinas, grasas, carbos = calcular_macros(peso, kcal_totales, nivel_actividad, 0)
    prot_comida, grasas_comida, carbos_comida = macros_por_comida(proteinas, grasas, carbos, comida)

    st.subheader("Resultados:")
    st.write(f"Consumo calórico basal: {tmb:.1f} kcal/día")
    st.write(f"Multiplicador usado: {multiplicador:.2f}")
    st.write(f"Calorías totales ajustadas: {kcal_totales:.1f}")
    st.write("Macros para el día (g):")
    st.write(f"Proteínas: {proteinas:.1f} g")
    st.write(f"Grasas: {grasas:.1f} g")
    st.write(f"Carbohidratos: {carbos:.1f} g")

    st.write(f"Macros para la comida {comida} (g):")
    st.write(f"Proteínas: {prot_comida} g")
    st.write(f"Grasas: {grasas_comida} g")
    st.write(f"Carbohidratos: {carbos_comida} g")

    tabla_macro = []
    for comida_tipo in ['Desayuno', 'Comida', 'Merienda', 'Cena']:
        p, g, c = macros_por_comida(proteinas, grasas, carbos, comida_tipo)
        kcal = round(p * 4 + g * 9 + c * 4, 1)
        tabla_macro.append({"Comida": comida_tipo, "Proteínas (g)": p, "Grasas (g)": g, "Carbohidratos (g)": c, "Kcal": kcal})

    st.table(tabla_macro)

    st.subheader("Base de datos de alimentos")
    st.dataframe(df_alimentos)
