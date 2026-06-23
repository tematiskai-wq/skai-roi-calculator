import streamlit as st
import pandas as pd
import numpy as np

# Настройка страницы
st.set_page_config(page_title="SKAI Платформа: Калькулятор окупаемости (ROI)", layout="wide", page_icon="📊")

# ==========================================
# 1. ОБЪЯВЛЕНИЕ КОНТЕЙНЕРОВ ДЛЯ ВЕРХА СТРАНИЦЫ
# ==========================================
title_container = st.container()
metrics_container = st.container()
table_container = st.container()
chart_container = st.container()

# Визуальный разделитель перед настройками
st.markdown("<br><br><br><hr style='border:1px solid #1E88E5;'>", unsafe_allow_html=True)

# ==========================================
# 2. БАЗА ДАННЫХ И ПРЕСЕТЫ ПО ТИПАМ ТС
# ==========================================
presets = {
    "🚛 Магистральный тягач (Фура)": {
        "fleet_size": 50, "mileage": 120000, "consumption": 32.0, "maintenance": 60000,
        "accidents_year": 8, "accident_cost": 800000,
        "video_capex": 120000, "video_opex": 2000, "video_eff": 55,
        "base_capex": 15000, "base_opex": 400, "base_eff": 7,
        "safe_capex": 10000, "safe_opex": 500, "safe_eff_to": 15, "safe_eff_acc": 15,
        "fuel_capex": 25000, "fuel_opex": 600, "fuel_eff": 10,
        "service_capex": 0, "service_opex": 1000, "service_eff": 800
    },
    "🏗️ Самосвал / Тяжелая спецтехника": {
        "fleet_size": 30, "mileage": 45000, "consumption": 45.0, "maintenance": 90000,
        "accidents_year": 6, "accident_cost": 600000,
        "video_capex": 130000, "video_opex": 2000, "video_eff": 50,
        "base_capex": 15000, "base_opex": 400, "base_eff": 5,
        "safe_capex": 10000, "safe_opex": 500, "safe_eff_to": 20, "safe_eff_acc": 10,
        "fuel_capex": 30000, "fuel_opex": 600, "fuel_eff": 12,
        "service_capex": 0, "service_opex": 1000, "service_eff": 600
    },
    "📦 Легкий коммерческий транспорт (LCV / Газель)": {
        "fleet_size": 40, "mileage": 60000, "consumption": 13.0, "maintenance": 35000,
        "accidents_year": 7, "accident_cost": 300000,
        "video_capex": 110000, "video_opex": 1800, "video_eff": 60,
        "base_capex": 12000, "base_opex": 350, "base_eff": 8,
        "safe_capex": 8000, "safe_opex": 400, "safe_eff_to": 12, "safe_eff_acc": 20,
        "fuel_capex": 20000, "fuel_opex": 500, "fuel_eff": 8,
        "service_capex": 0, "service_opex": 900, "service_eff": 500
    }
}

# Вспомогательная функция для форматирования валюты по стандарту РФ
def fmt(val):
    return f"{val:,.0f}".replace(",", " ")

# ==========================================
# 3. ПАНЕЛЬ КОНФИГУРАЦИИ ПРОЕКТА
# ==========================================
st.header("⚙️ Панель конфигурации проекта")

# Базовые параметры: Тип ТС и Количество
col_preset, col_fleet = st.columns([2, 1])
with col_preset:
    selected_preset = st.selectbox("Шаблон под тип ТС:", list(presets.keys()))
    p = presets[selected_preset]
with col_fleet:
    fleet_size = st.number_input("Размер автопарка (шт.):", min_value=1, value=p["fleet_size"], step=5)

st.markdown("<br>", unsafe_allow_html=True)
st.subheader("📊 Текущие показатели парка (До внедрения)")

# Распределение операционной базы в 2 колонки
base_col1, base_col2 = st.columns(2)

with base_col1:
    st.markdown("**Пробег и техническое обслуживание**")
    in_c1, out_c1 = st.columns([3, 2])
    with in_c1:
        annual_mileage = st.number_input("Пробег 1 ТС в год (км)", min_value=1000, value=p["mileage"], step=5000)
    with out_c1:
        st.metric("Общий пробег парка / год", f"{fmt(annual_mileage * fleet_size)} км")
        
    in_c2, out_c2 = st.columns([3, 2])
    with in_c2:
        annual_maintenance_cost = st.number_input("Затраты на ТО 1 ТС в год (руб.)", min_value=0, value=p["maintenance"], step=5000)
    with out_c2:
        fleet_monthly_maintenance_before = (annual_maintenance_cost / 12) * fleet_size
        st.metric("Расходы на ТО парка / мес", f"{fmt(fleet_monthly_maintenance_before)} ₽")

with base_col2:
    st.markdown("**Потребление и стоимость ГСМ**")
    in_c3, out_c3 = st.columns([3, 2])
    with in_c3:
        fuel_consumption = st.number_input("Расход топлива (л/100 км)", min_value=1.0, value=p["consumption"], step=0.5)
        fuel_price = st.number_input("Цена топлива (руб./литр)", min_value=1.0, value=65.0, step=1.0)
    with out_c3:
        fleet_monthly_fuel_before = ((annual_mileage / 100 * fuel_consumption * fuel_price) / 12) * fleet_size
        st.metric("Затраты на ГСМ парка / мес", f"{fmt(fleet_monthly_fuel_before)} ₽")

# Перенос конструктора модулей ниже базовых показателей
st.markdown("<br>", unsafe_allow_html=True)
st.subheader("🧩 Конструктор модулей SKAI Платформы")
available_modules = [
    "Видеоаналитика", "Базовый Мониторинг", "Безопасное вождение", 
    "Контроль топлива", "Сервис аналитики и реагирования"
]
m_cols = st.columns(5)
selected_modules = []
for i, module_name in enumerate(available_modules):
    with m_cols[i]:
        default_checked = True if module_name in ["Видеоаналитика", "Базовый Мониторинг"] else False
        if st.checkbox(module_name, value=default_checked):
            selected_modules.append(module_name)

if not selected_modules:
    st.warning("⚠️ Выберите хотя бы один модуль SKAI Платформы для расчета.")
    st.stop()

st.markdown("---")

# Инициализация глобальных накопителей для расчетов
total_capex = 0
total_opex_monthly = 0
monthly_savings_dict = {}

# Формирование аналитической таблицы численных параметров
current_params_table = [
    ["Размер автопарка (масштабирует все затраты и эффекты)", f"{fleet_size}", "шт."],
    ["Базовый профиль ТС (определяет стартовые коэффициенты экономии)", selected_preset.replace("🚛 ", "").replace("🏗️ ", "").replace("📦 ", ""), "Тип"],
    ["Суммарный пробег всего автопарка за год", f"{fmt(annual_mileage * fleet_size)}", "км"],
    ["Базовые затраты автопарка на ГСМ в месяц", f"{fmt(fleet_monthly_fuel_before)}", "руб."],
    ["Базовые затраты автопарка на ТО и ремонт в месяц", f"{fmt(fleet_monthly_maintenance_before)}", "руб."]
]

# РАЗДЕЛЕНИЕ НА 2 КОЛОНКИ ДЛЯ ПОДРОБНЫХ НАСТРОЕК ВЫБРАННЫХ МОДУЛЕЙ
config_col1, config_col2 = st.columns(2)

with config_col1:
    # МОДУЛЬ: ВИДЕОАНАЛИТИКА
    if "Видеоаналитика" in selected_modules:
        with st.expander("👁️ Модуль: Видеоаналитика", expanded=True):
            in_col, out_col = st.columns([3, 2])
            with in_col:
                v_capex = st.number_input("Capex оборудования на 1 ТС", value=p["video_capex"], step=5000, key="v_cap")
            with out_col:
                st.metric("Итого Capex (Видео)", f"{fmt(v_capex * fleet_size)} ₽")
                
            in_col, out_col = st.columns([3, 2])
            with in_col:
                v_opex = st.number_input("Opex лицензии на 1 ТС / мес", value=p["video_opex"], step=100, key="v_op")
            with out_col:
                st.metric("Итого Opex (Видео) / мес", f"{fmt(v_opex * fleet_size)} ₽")
                
            in_col, out_col = st.columns([3, 2])
            with in_col:
                accidents_year = st.number_input("Количество ДТП в парке в год (шт)", min_value=0, value=p["accidents_year"], step=1)
                accident_cost = st.number_input("Средний ущерб от 1 ДТП (руб)", min_value=0, value=p["accident_cost"], step=50000)
            with out_col:
                fleet_monthly_accident_before = (accidents_year * accident_cost) / 12
                st.metric("Ущерб от ДТП парка / мес", f"{fmt(fleet_monthly_accident_before)} ₽")
                
            v_eff = st.slider("Снижение аварийности со SKAI (%)", min_value=0, max_value=100, value=p["video_eff"], step=5) / 100
            v_saving = fleet_monthly_accident_before * v_eff
            
            total_capex += v_capex * fleet_size
            total_opex_monthly += v_opex * fleet_size
            monthly_savings_dict["Видеоаналитика"] = v_saving
            
            current_params_table.extend([
                ["Исходное количество ДТП в год (база аварийности)", f"{accidents_year}", "шт."],
                ["Средний ущерб от одного ДТП", f"{fmt(accident_cost)}", "руб."],
                ["Эффективность предотвращения ДТП видеоаналитикой", f"{v_eff*100:.0f}", "%"]
            ])

    # МОДУЛЬ: БАЗОВЫЙ МОНИТОРИНГ
    if "Базовый Мониторинг" in selected_modules:
        with st.expander("📍 Модуль: Базовый Мониторинг", expanded=True):
            in_col, out_col = st.columns([3, 2])
            with in_col:
                b_capex = st.number_input("Capex трекера на 1 ТС", value=p["base_capex"], step=1000, key="b_cap")
            with out_col:
                st.metric("Итого Capex (Мониторинг)", f"{fmt(b_capex * fleet_size)} ₽")
                
            in_col, out_col = st.columns([3, 2])
            with in_col:
                b_opex = st.number_input("Opex ПО на 1 ТС / мес", value=p["base_opex"], step=50, key="b_op")
            with out_col:
                st.metric("Итого Opex (Мониторинг) / мес", f"{fmt(b_opex * fleet_size)} ₽")
                
            b_eff = st.slider("Сокращение левых рейсов / простоев (%)", min_value=0.0, max_value=25.0, value=float(p["base_eff"]), step=0.5) / 100
            b_saving = (fleet_monthly_fuel_before + fleet_monthly_maintenance_before) * b_eff
            
            total_capex += b_capex * fleet_size
            total_opex_monthly += b_opex * fleet_size
            monthly_savings_dict["Базовый Мониторинг"] = b_saving
            
            current_params_table.extend([
                ["Коэффициент сокращения нецелевого пробега (ГСМ+ТО)", f"{b_eff*100:.1f}", "%"]
            ])


with config_col2:
    # МОДУЛЬ: БЕЗОПАСНОЕ ВОЖДЕНИЕ
    if "Безопасное вождение" in selected_modules:
        with st.expander("🛡️ Модуль: Безопасное вождение", expanded=True):
            in_col, out_col = st.columns([3, 2])
            with in_col:
                sd_capex = st.number_input("Capex модуля безопасности на 1 ТС", value=p["safe_capex"], step=1000, key="sd_cap")
            with out_col:
                st.metric("Итого Capex (Безопасность)", f"{fmt(sd_capex * fleet_size)} ₽")
                
            in_col, out_col = st.columns([3, 2])
            with in_col:
                sd_opex = st.number_input("Opex подписки на 1 ТС / мес", value=p["safe_opex"], step=50, key="sd_op")
            with out_col:
                st.metric("Итого Opex (Безопасность) / мес", f"{fmt(sd_opex * fleet_size)} ₽")
                
            sd_eff_to = st.slider("Экономия на ТО от бережной езды (%)", min_value=0, max_value=40, value=p["safe_eff_to"], step=5) / 100
            sd_eff_acc = st.slider("Доп. снижение ДТП от скоринга (%)", min_value=0, max_value=40, value=p["safe_eff_acc"], step=5) / 100
            
            sd_saving_to = fleet_monthly_maintenance_before * sd_eff_to
            base_accident_for_sd = (fleet_monthly_accident_before - v_saving) if "Видеоаналитика" in selected_modules else (p["accidents_year"] * p["accident_cost"] / 12)
            sd_saving_acc = base_accident_for_sd * sd_eff_acc
            sd_saving = sd_saving_to + sd_saving_acc
            
            total_capex += sd_capex * fleet_size
            total_opex_monthly += sd_opex * fleet_size
            monthly_savings_dict["Безопасное вождение"] = sd_saving
            
            current_params_table.extend([
                ["Коэффициент снижения износа ТО за счет бережной езды", f"{sd_eff_to*100:.0f}", "%"],
                ["Дополнительный коэффициент снижения ДТП от скоринга", f"{sd_eff_acc*100:.0f}", "%"]
            ])

    # МОДУЛЬ: КОНТРОЛЬ ТОПЛИВА
    if "Контроль топлива" in selected_modules:
        with st.expander("⛽ Модуль: Контроль топлива", expanded=True):
            in_col, out_col = st.columns([3, 2])
            with in_col:
                f_capex = st.number_input("Capex ДУТ + тарировка на 1 ТС", value=p["fuel_capex"], step=2000, key="f_cap")
            with out_col:
                st.metric("Итого Capex (Топливо)", f"{fmt(f_capex * fleet_size)} ₽")
                
            in_col, out_col = st.columns([3, 2])
            with in_col:
                f_opex = st.number_input("Opex ML-модуля на 1 ТС / мес", value=p["fuel_opex"], step=50, key="f_op")
            with out_col:
                st.metric("Итого Opex (Топливо) / мес", f"{fmt(f_opex * fleet_size)} ₽")
                
            f_eff = st.slider("Прямая экономия ГСМ (сливы/карты) (%)", min_value=0.0, max_value=25.0, value=float(p["fuel_eff"]), step=0.5) / 100
            f_saving = fleet_monthly_fuel_before * f_eff
            
            total_capex += f_capex * fleet_size
            total_opex_monthly += f_opex * fleet_size
            monthly_savings_dict["Контроль топлива"] = f_saving
            
            current_params_table.extend([
                ["Коэффициент чистой экономии топлива от контроля махинаций", f"{f_eff*100:.1f}", "%"]
            ])

    # МОДУЛЬ: СЕРВИС АНАЛИТИКИ И РЕАГИРОВАНИЯ
    if "Сервис аналитики и реагирования" in selected_modules:
        with st.expander("🎧 Модуль: Ситуационный центр (Аутсорсинг)", expanded=True):
            in_col, out_col = st.columns([3, 2])
            with in_col:
                s_capex = st.number_input("Capex настройки интеграции", value=p["service_capex"], step=1000, key="s_cap")
            with out_col:
                st.metric("Итого Capex (Сервис)", f"{fmt(s_capex * fleet_size)} ₽")
                
            in_col, out_col = st.columns([3, 2])
            with in_col:
                s_opex = st.number_input("Opex диспетчеризации 1 ТС / мес", value=p["service_opex"], step=100, key="s_op")
            with out_col:
                st.metric("Итого Opex (Сервис) / мес", f"{fmt(s_opex * fleet_size)} ₽")
                
            in_col, out_col = st.columns([3, 2])
            with in_col:
                s_eff_val = st.number_input("Снижение скрытых потерь на 1 ТС / мес", value=p["service_eff"], step=100)
            with out_col:
                st.metric("Итого возвращенные потери парка / мес", f"{fmt(s_eff_val * fleet_size)} ₽")
                
            s_saving = s_eff_val * fleet_size
            total_capex += s_capex * fleet_size
            total_opex_monthly += s_opex * fleet_size
            monthly_savings_dict["Сервис аналитики и реагирования"] = s_saving
            
            current_params_table.extend([
                ["Экономия скрытых затрат (администрирование) на 1 автомобиль", f"{fmt(s_eff_val)}", "руб./мес."]
            ])

# ==========================================
# 4. МАТЕМАТИЧЕСКИЙ ПЕРЕСЧЕТ РЕЗУЛЬТАТОВ
# ==========================================
fleet_monthly_saving = sum(monthly_savings_dict.values())
net_monthly_benefit = fleet_monthly_saving - total_opex_monthly

if net_monthly_benefit > 0:
    payback_period = total_capex / net_monthly_benefit
else:
    payback_period = float('inf')

# ==========================================
# 5. ЗАПОЛНЕНИЕ ВЕРХНИХ КОНТЕЙНЕРОВ (РЕЗУЛЬТАТЫ)
# ==========================================
with title_container:
    st.title("📊 SKAI платформа: калькулятор окупаемости (ROI)")
    st.markdown(f"Выбранный профиль техники: **{selected_preset}** | Активных модулей платформы: **{len(selected_modules)}**")
    st.caption("Изменяйте параметры конфигурации — результаты сверху пересчитываются мгновенно.")
    st.markdown("---")

with metrics_container:
    st.subheader("💰 Экономический итог проекта")
    m1, m2, m3 = st.columns(3)
    m1.metric("Стартовые инвестиции (Capex)", f"{fmt(total_capex)} ₽")
    m2.metric("Чистая прибыль парка в месяц (после Opex)", f"{fmt(net_monthly_benefit)} ₽")
    
    if payback_period != float('inf'):
        m3.metric("Срок окупаемости платформы", f"{payback_period:.1f} мес.")
    else:
        m3.metric("Срок окупаемости платформы", "Проект не окупается")
    st.markdown("---")

with table_container:
    st.subheader("📋 Сводная таблица численных параметров расчета")
    df_params = pd.DataFrame(current_params_table, columns=["Параметр (и его влияние на математику модели)", "Текущее значение", "Ед. изм."])
    st.dataframe(df_params, use_container_width=True, hide_index=True)
    st.markdown("---")

with chart_container:
    st.subheader("📈 График кумулятивного эффекта и баланса проекта (36 месяцев)")
    
    months = np.arange(0, 37)
    chart_data_dict = {"Месяц": months}
    
    project_balance = []
    for m in months:
        if m == 0:
            project_balance.append(-total_capex)
        else:
            project_balance.append(project_balance[m-1] + net_monthly_benefit)
    chart_data_dict["Общий баланс проекта (с учетом затрат)"] = project_balance
    
    for module_name, monthly_save_val in monthly_savings_dict.items():
        chart_data_dict[f"Эффект: {module_name}"] = [monthly_save_val * m for m in months]
        
    df_chart = pd.DataFrame(chart_data_dict).set_index("Месяц")
    st.line_chart(df_chart)