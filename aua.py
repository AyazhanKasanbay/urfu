import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Пример данных
data = {
    'Месяц': ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'],
    'Температура': [-5, -3, 2, 10, 15, 20, 25, 24, 18, 10, 3, -2]
}
df = pd.DataFrame(data)

# Выбор диапазона месяцев
months = st.multiselect('Выберите месяцы', df['Месяц'])

if months:
    filtered_data = df[df['Месяц'].isin(months)]
else:
    filtered_data = df

# Построение графика
fig, ax = plt.subplots()
ax.plot(filtered_data['Месяц'], filtered_data['Температура'], marker='o')
ax.set_xlabel('Месяц')
ax.set_ylabel('Температура (°C)')
ax.set_title('Температура по месяцам')

# Отображение графика в Streamlit
st.pyplot(fig)