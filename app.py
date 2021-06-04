#!/usr/bin/env python
# coding: utf-8

# In[1]:


import altair as alt
import pandas as pd
import streamlit as st

alt.data_transformers.disable_max_rows()


def get_vaccine_data():
    # Conjunto completo de datos
    covid_data = pd.read_csv(
        "https://raw.githubusercontent.com/govex/COVID-19/master/data_tables/vaccine_data/global_data/time_series_covid19_vaccine_global.csv"
    )
    # Agrupamos por región y fecha
    grouped_data = covid_data.groupby(["Country_Region", "Date"]).sum()
    # Convertimos índices en columnas
    vaccine_data = grouped_data.reset_index()
    # Cambiamos el tipo de datoos a fecha
    vaccine_data["Date"] = vaccine_data["Date"].astype("datetime64[ns]")
    return vaccine_data


def expand_with_population(vaccine_data: pd.DataFrame):
    # Obtenemos la población mundial por paises para poder obtener porcentajes
    population = pd.read_csv("data/population_by_country_2020.csv")
    # Hacemos un left join entre los datos de porcentaje de vacunación y población
    vaccine_data["Country_Region"].replace({"US": "United States"}, inplace=True)
    vaccine_data = vaccine_data[vaccine_data["Country_Region"] != "US (Aggregate)"]
    expanded_data = vaccine_data.join(
        population[["Country (or dependency)", "Population (2020)"]].set_index(
            "Country (or dependency)"
        ),
        on="Country_Region",
    )
    return expanded_data


def generate_plot(data: pd.DataFrame, country_list: list):

    # Obtenemos los porcentajes
    data["Doses_admin_pct"] = data["Doses_admin"] / data["Population (2020)"]
    data["People_partially_vaccinated_pct"] = (
        data["People_partially_vaccinated"] / data["Population (2020)"]
    )
    data["People_fully_vaccinated_pct"] = (
        data["People_fully_vaccinated"] / data["Population (2020)"]
    )
    data.head(1)
    data = data.loc[data["Country_Region"].isin(country_list)]
    # Crear gráfica Altair (for the win)

    chart = (
        alt.Chart(data)
        .mark_line()
        .encode(
            x="Date:T",
            color="Country_Region",
            strokeDash="Country_Region",
            tooltip=[
                "Country_Region",
                "Date",
                "People_fully_vaccinated_pct",
                "People_partially_vaccinated",
                "Doses_admin_pct",
                "Doses_admin",
                "Population (2020)",
            ],
        )
    ).properties(width=500)
    return (
        chart.encode(y="People_fully_vaccinated_pct:Q").interactive()
        & chart.encode(y="People_partially_vaccinated_pct:Q").interactive()
    )


st.title("Covid-19 Full vaccination percentage tracker")


data = expand_with_population(get_vaccine_data())
full_country_list = sorted(list(set(data["Country_Region"])))
country_list = st.multiselect(
    "Countries",
    options=full_country_list,
    default=["Poland", "Mexico", "United States"],
)

st.altair_chart(generate_plot(data, country_list), use_container_width=True)

# %%
