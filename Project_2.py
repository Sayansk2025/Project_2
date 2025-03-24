import pandas as pd
import streamlit as st
import os

# Функция для внесения данных
def input_data():
    st.header("Внесение данных")
    
    # Поле для названия мероприятия
    event_name = st.text_input("Название мероприятия")
    if not event_name:
        st.warning("Пожалуйста, введите название мероприятия.")
        return
    
    # Поле для уровня мероприятия
    event_level = st.selectbox("Уровень мероприятия", ["Областной", "Региональный", "Городской", "Школьный"])
    
    # Поле для выбора типа мероприятия
    event_type = st.radio("Тип мероприятия", ["Индивидуальный", "Групповой"])
    
    # Поле для выбора результата участия
    result_options = [
        "Победитель", "Призер (2 место)", "Призер (3 место)", "Участник",
        "Диплом 1 степени", "Диплом 2 степени", "Диплом 3 степени",
        "Лауреат", "Гран-при", "Дипломант", "Специальный приз"
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
        save_data(event_name, event_level, event_type, event_result, participants, classes)

# Функция для анализа данных
def analyze_data():
    st.header("Анализ данных")
    
    # Загрузка данных из файла
    try:
        df = pd.read_excel("events_data.xlsx")
    except FileNotFoundError:
        st.warning("Файл с данными не найден. Пожалуйста, сначала внесите данные.")
        return
    
    # Выбор анализа: по классу или по ученику
    analysis_type = st.radio("Выберите тип анализа", ["По классу", "По ученику"])
    
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
        
        # Список мероприятий для класса
        st.write("### Мероприятия:")
        st.write(class_data[["Название мероприятия", "Уровень мероприятия", "Тип мероприятия", "Результат участия", "Участник"]])
    
    else:
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
        
        # Список мероприятий для участника
        st.write("### Мероприятия:")
        st.write(participant_data[["Название мероприятия", "Уровень мероприятия", "Тип мероприятия", "Результат участия", "Класс"]])

# Функция для сохранения данных и обновления Excel-таблицы
def save_data(event_name, event_level, event_type, event_result, participants, classes):
    # Создаем DataFrame с данными
    data = {
        "Название мероприятия": [],
        "Уровень мероприятия": [],
        "Тип мероприятия": [],
        "Результат участия": [],
        "Участник": [],
        "Класс": []
    }
    
    # Заполняем данные для каждого участника
    for participant, cls in zip(participants, classes):
        data["Название мероприятия"].append(event_name)
        data["Уровень мероприятия"].append(event_level)
        data["Тип мероприятия"].append(event_type)
        data["Результат участия"].append(event_result)
        data["Участник"].append(participant)
        data["Класс"].append(cls)
    
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