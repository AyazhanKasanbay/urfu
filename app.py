import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
from sklearn.linear_model import LinearRegression
import requests
from bs4 import BeautifulSoup
import time

def parse_data(selectedCities, selectedBrands, selectedModels):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    cars = []


    for i in range(10):
        try:
            for nameCity in selectedCities:
                for carBrand in selectedBrands:
                    for carModel in selectedModels[carBrand]:
                        if nameCity == 'Екатеринбург':
                            response = requests.get(f"https://ekaterinburg.drom.ru/{carBrand.lower()}/{carModel.lower()}/page{i}/?maxyear=2019&ph=1&unsold=1", headers=headers)
                        elif nameCity == 'Москва':
                            response = requests.get(f"https://moscow.drom.ru/{carBrand.lower()}/{carModel.lower()}/page{i}/?maxyear=2019&ph=1&unsold=1", headers=headers)
                        elif nameCity == 'Санкт-Петербург':
                            response = requests.get(f"https://spb.drom.ru/{carBrand.lower()}/{carModel.lower()}/page{i}/?maxyear=2019&ph=1&unsold=1", headers=headers)
                        else:
                            response = requests.get(f"https://auto.drom.ru/{carBrand.lower()}/{carModel.lower()}/page{i}/?maxyear=2019&ph=1&unsold=1", headers=headers)

                        response.raise_for_status()  # проверка успешности запроса
                        soup = BeautifulSoup(response.content, "html.parser")
                        tags = soup.find_all("div", {"data-ftid": "bulls-list_bull"})

                        if not tags:
                            print(f"No tags found on page {i}")
                            continue

                        for tag in tags:
                            try:
                                title_tag = tag.find("a", {"data-ftid": "bull_title"})
                                name_year = title_tag.text.strip() if title_tag else ""
                                name, year = name_year.split(',') if ',' in name_year else (name_year, "")

                                price_tag = tag.find("span", {"data-ftid": "bull_price"})
                                price = price_tag.text.replace('\xa0', '').replace('₽', '').strip() if price_tag else ""

                                city_tag = tag.find("span", {"data-ftid": "bull_location"})
                                city = city_tag.text.strip() if city_tag else ""

                                if price and name and city:  # Проверка, что данные не пустые
                                    cars.append({"car": name.strip(), "year": year.strip(), "price": float(price.replace(' ', '')),
                                                 "city": city.strip()})

                            except Exception as e:
                                print(f"Error processing tag: {e}")

            # Задержки между запросами для избежания блокировки со стороны сервера
            time.sleep(0.1)

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")

    return pd.DataFrame(cars)

def main(selectedCities, selectedBrands, selectedModels, yearRange):
    df = parse_data(selectedCities, selectedBrands, selectedModels)
    df_filtered = df[(df['year'].astype(int).between(yearRange[0], yearRange[1]))]

    if df_filtered.empty:
        st.write("Нет данных для выбранных критериев.")
        return

    # Линейная регрессия
    X = df_filtered[['year']].astype(int)
    y = df_filtered['price']

    model = LinearRegression()
    model.fit(X, y)

    # Предсказание
    df_filtered['predicted_price'] = model.predict(X)

    # Построение графика
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df_filtered, x='year', y='price', label='Фактические цены')
    sns.lineplot(data=df_filtered, x='year', y='predicted_price', color='red', label='Предсказанные цены')
    plt.xlabel('Год')
    plt.ylabel('Цена')
    plt.title(f'Линейная регрессия цен по годам для выбранных автомобилей в выбранных городах')
    plt.legend()
    st.pyplot(plt)
    
    # Вывод коэффициентов модели
    st.write(f"Перехват: {model.intercept_}")
    st.write(f"Коэффициент: {model.coef_[0]}")

# Streamlit UI
st.title('Анализ цен на автомобили')
st.write('### Линейная регрессия цен на автомобили по годам')

# Выбор городов
cities = st.multiselect('Выберите города', ['Екатеринбург', 'Москва', 'Санкт-Петербург'])

# Словарь марок и моделей автомобилей
model_dict = {
    'Chevrolet': ['Cruze', 'Aveo', 'Spark', 'Captiva', 'Lacetti'],
    'Toyota': ['Corolla', 'Camry', 'RAV4', 'Prius', 'Highlander'],
    'Nissan': ['Almera', 'Teana', 'Qashqai', 'X-Trail', 'Juke'],
    'Ford': ['Focus', 'Fiesta', 'Mondeo', 'Kuga', 'EcoSport'],
    'Honda': ['Civic', 'Accord', 'CR-V', 'Fit', 'HR-V']
}

# Выбор марок автомобилей
selected_brands = st.multiselect('Выберите марки автомобилей', list(model_dict.keys()))

# Фильтрация моделей по выбранным маркам
selected_models = {brand: st.multiselect(f'Выберите модели для {brand}', model_dict[brand]) for brand in selected_brands}

# Выбор диапазона лет
years = st.slider('Года', 2008, 2019, (2008, 2019))

if st.button('Выполнить'):
    main(cities, selected_brands, selected_models, years)

if st.button('Очистить'):
    st.cache_data.clear()
    # Очистка всех введенных данных
    cities.clear()
    selected_brands.clear()
    selected_models.clear()
    years = (2008, 2019)
    st.experimental_rerun()
