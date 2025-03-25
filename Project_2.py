import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt

# Функция для внесения данных
def input_data():
    st.header("Внесение данных")
    
    # Поле для названия мероприятия
    event_name = st.text_input("Название мероприятия")
    if not event_name:
        st.warning("Пожалуйста, введите название мероприятия.")
        return
    
    # Поле для даты мероприятия
    event_date = st.date_input("Дата мероприятия")
    
    # Поле для уровня мероприятия
    event_level = st.selectbox("Уровень мероприятия", ["Областной", "Региональный", "Городской", "Школьный"])
    
    # Поле для выбора типа мероприятия
    event_type = st.radio("Тип мероприятия", ["Индивидуальный", "Групповой"])
    
    # Поле для выбора результата участия
    result_options = [
        "Победитель", "Призер (2 место)", "Призер (3 место)", "Участник",
        "Диплом 1 степени", "Диплом 2 степени", "Диплом 3 степени",
        "Лауреат", "Гран-при", "Дипломант", "Специальный приз",
        "Без места", "Активный участник"
    ]
    event_result = st.selectbox("Результат участия", result_options)
    
    participants = []
    classes = []
    
    # Внесение участников в зависимости от типа мероприятия
    if event_type == "Индивидуальный":
        participants_input = st.text_area("Введите имена участников (каждое имя с новой строки)")
        participants = [name.strip() for name in participants_input.split("\n") if name.strip()]
        
        # Поле для ввода класса для индивидуального мероприятия
        class_input = st.text_input("Введите класс участника (например, 10А)")
        if class_input:
            classes = [class_input] * len(participants)
        else:
            st.warning("Пожалуйста, введите класс участника.")
            return
    else:
        # Множественный выбор классов для группового мероприятия
        class_options = [f"{i}{j}" for i in range(1, 12) for j in ['А', 'Б', 'В']]
        selected_classes = st.multiselect("Выберите классы", class_options)
        
        if not selected_classes:
            st.warning("Пожалуйста, выберите хотя бы один класс.")
            return
        
        for cls in selected_classes:
            # Поле для ввода количества учеников в каждом классе
            count = st.number_input(f"Количество учеников в классе {cls}", min_value=1, max_value=50, value=1, key=f"count_{cls}")
            
            # Текстовые поля для ввода имен учеников
            st.write(f"Введите имена учеников для класса {cls}:")
            for i in range(1, count + 1):
                student_name = st.text_input(f"Ученик {i} из {cls}", key=f"student_{cls}_{i}")
                if student_name:  # Если имя введено, добавляем его в список участников
                    participants.append(student_name)
                    classes.append(cls)
    
    if not participants:
        st.warning("Пожалуйста, введите хотя бы одного участника.")
        return
    
    # Кнопка для сохранения данных и создания таблицы
    if st.button("Сохранить данные"):
        save_data(event_date, event_name, event_level, event_type, event_result, participants, classes)

# Функция для анализа данных
def analyze_data():
    st.header("Анализ данных")
    
    # Загрузка данных из файла
    try:
        df = pd.read_excel("events_data.xlsx")
    except FileNotFoundError:
        st.warning("Файл с данными не найден. Пожалуйста, сначала внесите данные.")
        return
    
    # Выбор анализа: по классу, по ученику или по школе
    analysis_type = st.radio("Выберите тип анализа", ["По классу", "По ученику", "По школе"])
    
    if analysis_type == "По классу":
        # Анализ по классу
        class_options = df["Класс"].dropna().unique()
        selected_class = st.selectbox("Выберите класс", class_options)
        
        # Фильтрация данных по выбранному классу
        class_data = df[df["Класс"] == selected_class]
        
        # Группировка по результату участия
        result_counts = class_data["Результат участия"].value_counts().reset_index()
        result_counts.columns = ["Результат", "Количество"]
        
        st.write(f"### Результаты для класса {selected_class}")
        st.write(result_counts)
        
        # Визуализация: круговая диаграмма для распределения результатов
        fig, ax = plt.subplots()
        ax.pie(result_counts["Количество"], labels=result_counts["Результат"], autopct="%1.1f%%", startangle=90)
        ax.set_title(f"Распределение результатов для класса {selected_class}")
        st.pyplot(fig)
        
        # Список мероприятий для класса
        st.write("### Мероприятия:")
        st.write(class_data[["Дата", "Название мероприятия", "Уровень мероприятия", "Тип мероприятия", "Результат участия", "Участник"]])
    
    elif analysis_type == "По ученику":
        # Анализ по ученику
        participants = df["Участник"].unique()
        selected_participant = st.selectbox("Выберите участника", participants)
        
        # Фильтрация данных по выбранному участнику
        participant_data = df[df["Участник"] == selected_participant]
        
        # Группировка по результату участия
        result_counts = participant_data["Результат участия"].value_counts().reset_index()
        result_counts.columns = ["Результат", "Количество"]
        
        st.write(f"### Результаты для участника {selected_participant}")
        st.write(result_counts)
        
        # Визуализация: столбчатая диаграмма для распределения результатов
        fig, ax = plt.subplots()
        ax.bar(result_counts["Результат"], result_counts["Количество"], color="skyblue")
        ax.set_title(f"Результаты участника {selected_participant}")
        ax.set_xlabel("Результат")
        ax.set_ylabel("Количество")
        st.pyplot(fig)
        
        # Список мероприятий для участника
        st.write("### Мероприятия:")
        st.write(participant_data[["Дата", "Название мероприятия", "Уровень мероприятия", "Тип мероприятия", "Результат участия", "Класс"]])
    
    elif analysis_type == "По школе":
        # Анализ по школе
        st.subheader("Общий рейтинг школы")
        
        # 1. Количество мероприятий по уровням
        level_counts = df["Уровень мероприятия"].value_counts().reset_index()
        level_counts.columns = ["Уровень", "Количество"]
        
        st.write("### Количество мероприятий по уровням")
        st.write(level_counts)
        
        # Визуализация: столбчатая диаграмма
        fig, ax = plt.subplots()
        ax.bar(level_counts["Уровень"], level_counts["Количество"], color="lightgreen")
        ax.set_title("Количество мероприятий по уровням")
        ax.set_xlabel("Уровень мероприятия")
        ax.set_ylabel("Количество")
        st.pyplot(fig)
        
        # 2. Распределение результатов по школе
        result_counts = df["Результат участия"].value_counts().reset_index()
        result_counts.columns = ["Результат", "Количество"]
        
        st.write("### Распределение результатов по школе")
        st.write(result_counts)
        
        # Визуализация: круговая диаграмма
        fig, ax = plt.subplots()
        ax.pie(result_counts["Количество"], labels=result_counts["Результат"], autopct="%1.1f%%", startangle=90)
        ax.set_title("Распределение результатов по школе")
        st.pyplot(fig)
        
        # 3. Лидеры среди классов по количеству мероприятий
        class_counts = df.groupby("Класс").size().reset_index(name="Количество мероприятий")
        class_counts = class_counts.sort_values(by="Количество мероприятий", ascending=False)
        
        st.write("### Лидеры среди классов по количеству мероприятий")
        st.write(class_counts)
        
        # Визуализация: линейная диаграмма
        fig, ax = plt.subplots()
        ax.plot(class_counts["Класс"], class_counts["Количество мероприятий"], marker="o", color="orange")
        ax.set_title("Лидеры среди классов по количеству мероприятий")
        ax.set_xlabel("Класс")
        ax.set_ylabel("Количество мероприятий")
        st.pyplot(fig)

# Функция для сохранения данных и обновления Excel-таблицы
def save_data(event_date, event_name, event_level, event_type, event_result, participants, classes):
    # Создаем DataFrame с данными
    data = {
        "Дата": [event_date] * len(participants),
        "Название мероприятия": [event_name] * len(participants),
        "Уровень мероприятия": [event_level] * len(participants),
        "Тип мероприятия": [event_type] * len(participants),
        "Результат участия": [event_result] * len(participants),
        "Участник": participants,
        "Класс": classes
    }
    
    df = pd.DataFrame(data)
    
    # Проверяем, существует ли файл
    if os.path.exists("events_data.xlsx"):
        # Если файл существует, загружаем его и добавляем новые данные
        existing_data = pd.read_excel("events_data.xlsx")
        updated_data = pd.concat([existing_data, df], ignore_index=True)
    else:
        # Если файла нет, создаем новый
        updated_data = df
    
    # Сохраняем обновленные данные в файл
    updated_data.to_excel("events_data.xlsx", index=False)
    
    st.success("Данные успешно сохранены!")
    st.write(df)  # Показываем таблицу в приложении

# Основная функция приложения
def main():
    st.title("Приложение для управления мероприятиями")
    
    # Выбор действия
    action = st.sidebar.radio("Выберите действие", ["Внести данные", "Анализировать данные"])
    
    if action == "Внести данные":
        input_data()
    else:
        analyze_data()

if __name__ == "__main__":
    main()
