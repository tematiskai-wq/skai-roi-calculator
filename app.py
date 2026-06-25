import streamlit as st
import pandas as pd
import numpy as np

# Настройка страницы
st.set_page_config(page_title="SKAI Платформа: Калькулятор окупаемости (ROI)", layout="wide", page_icon="📊")

# ==========================================
# 1. БАЗА ДАННЫХ И ПРЕСЕТЫ ПО ТИПАМ ТС
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

def fmt(val):
    return f"{val:,.0f}".replace(",", " ")

# ==========================================
# 2. СЕКЦИЯ САЙДБАРА (КОНФИГУРАЦИЯ СМЕШАННОГО ПАРКА)
# ==========================================
st.sidebar.header("⚙️ Параметры и конфигурация")

st.sidebar.subheader("🚚 Состав автопарка (укажите шт.)")
fleet_quantities = {}
# По умолчанию выставляем стартовый состав для демонстрации
default_qtys = {
    "🚛 Магистральный тягач (Фура)": 30,
    "🏗️ Самосвал / Тяжелая спецтехника": 10,
    "📦 Легкий коммерческий транспорт (LCV / Газель)": 15
}

for preset_name in presets.keys():
    qty = st.sidebar.number_input(f"{preset_name}:", min_value=0, value=default_qtys[preset_name], step=5)
    if qty > 0:
        fleet_quantities[preset_name] = qty

total_fleet_size = sum(fleet_quantities.values())

if total_fleet_size == 0:
    st.sidebar.warning("⚠️ Укажите количество хотя бы для одного типа ТС.")
    st.stop()

# Динамический расчет базовых показателей парка до внедрения
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Показатели до внедрения")

total_fuel_before = 0
total_maint_before = 0
weighted_accidents_year = 0
weighted_accident_cost = 0

# Собираем пропорциональные данные по ГСМ, ТО и ДТП исходя из структуры парка
for name, qty in fleet_quantities.items():
    p = presets[name]
    # Топливо
    total_fuel_before += ((p["mileage"] / 100 * p["consumption"] * 65.0) / 12) * qty
    # ТО
    total_maint_before += (p["maintenance"] / 12) * qty
    # ДТП (масштабируем аварийность относительно базового размера парка в пресете)
    ratio = qty / p["fleet_size"]
    weighted_accidents_year += p["accidents_year"] * ratio
    weighted_accident_cost += p["accident_cost"] * (qty / total_fleet_size)

# Показываем агрегированную базу в сайдбаре для контроля
st.sidebar.caption(f"Всего ТС в парке: {total_fleet_size} шт.")
st.sidebar.caption(f"Базовые ГСМ парка: {fmt(total_fuel_before)} ₽/мес.")
st.sidebar.caption(f"Базовое ТО парка: {fmt(total_maint_before)} ₽/мес.")

# Конструктор технологических модулей
st.sidebar.markdown("---")
st.sidebar.subheader("🧩 Модули SKAI Платформы")

available_modules = [
    "Видеоаналитика", "Базовый Мониторинг", "Безопасное вождение", 
    "Контроль топлива", "Сервис аналитики и реагирования"
]

selected_modules = []
for module_name in available_modules:
    default_checked = True if module_name in ["Видеоаналитика", "Базовый Мониторинг"] else False
    if st.sidebar.checkbox(module_name, value=default_checked):
        selected_modules.append(module_name)

if not selected_modules:
    st.sidebar.warning("⚠️ Выберите хотя бы один модуль для расчета.")
    st.stop()

# Вычисление средневзвешенных дефолтов для тонких настроек модулей
def get_weighted_value(field):
    total = 0
    for name, qty in fleet_quantities.items():
        total += presets[name][field] * qty
    return total / total_fleet_size

# Накопители для экономики проекта
total_capex = 0
total_opex_monthly = 0
monthly_savings_dict = {}

st.sidebar.markdown("---")
st.sidebar.subheader("🔧 Тонкие настройки модулей")

# Все блоки по умолчанию открыты (expanded=True)

# МОДУЛЬ: ВИДЕОАНАЛИТИКА
if "Видеоаналитика" in selected_modules:
    with st.sidebar.expander("👁️ Модуль: Видеоаналитика", expanded=True):
        v_capex_def = get_weighted_value("video_capex")
        v_opex_def = get_weighted_value("video_opex")
        v_eff_def = get_weighted_value("video_eff")
        
        v_capex = st.number_input("Capex оборудования на 1 ТС", value=int(v_capex_def), step=5000, key="v_cap")
        v_opex = st.number_input("Opex лицензии на 1 ТС / мес", value=int(v_opex_def), step=100, key="v_op")
        accidents_year = st.number_input("Количество ДТП в парке в год", min_value=0.0, value=float(weighted_accidents_year), step=0.5)
        accident_cost = st.number_input("Средний ущерб от 1 ДТП (руб)", min_value=0, value=int(weighted_accident_cost), step=50000)
        v_eff = st.slider("Снижение аварийности со SKAI (%)", min_value=0, max_value=100, value=int(v_eff_def), step=5) / 100
        
        fleet_monthly_accident_before = (accidents_year * accident_cost) / 12
        v_saving = fleet_monthly_accident_before * v_eff
        
        total_capex += v_capex * total_fleet_size
        total_opex_monthly += v_opex * total_fleet_size
        monthly_savings_dict["Видеоаналитика"] = v_saving

# МОДУЛЬ: БАЗОВЫЙ МОНИТОРИНГ
if "Базовый Мониторинг" in selected_modules:
    with st.sidebar.expander("📍 Модуль: Базовый Мониторинг", expanded=True):
        b_capex_def = get_weighted_value("base_capex")
        b_opex_def = get_weighted_value("base_opex")
        b_eff_def = get_weighted_value("base_eff")
        
        b_capex = st.number_input("Capex трекера на 1 ТС", value=int(b_capex_def), step=1000, key="b_cap")
        b_opex = st.number_input("Opex ПО на 1 ТС / мес", value=int(b_opex_def), step=50, key="b_op")
        b_eff = st.slider("Сокращение левых рейсов / простоев (%)", min_value=0.0, max_value=25.0, value=float(b_eff_def), step=0.5) / 100
        
        b_saving = (total_fuel_before + total_maint_before) * b_eff
        
        total_capex += b_capex * total_fleet_size
        total_opex_monthly += b_opex * total_fleet_size
        monthly_savings_dict["Базовый Мониторинг"] = b_saving

# МОДУЛЬ: БЕЗОПАСНОЕ ВОЖДЕНИЕ
if "Безопасное вождение" in selected_modules:
    with st.sidebar.expander("🛡️ Модуль: Безопасное вождение", expanded=True):
        sd_capex_def = get_weighted_value("safe_capex")
        sd_opex_def = get_weighted_value("safe_opex")
        sd_eff_to_def = get_weighted_value("safe_eff_to")
        sd_eff_acc_def = get_weighted_value("safe_eff_acc")
        
        sd_capex = st.number_input("Capex модуля на 1 ТС", value=int(sd_capex_def), step=1000, key="sd_cap")
        sd_opex = st.number_input("Opex подписки на 1 ТС / мес", value=int(sd_opex_def), step=50, key="sd_op")
        sd_eff_to = st.slider("Экономия на ТО от бережной езды (%)", min_value=0, max_value=40, value=int(sd_eff_to_def), step=5) / 100
        sd_eff_acc = st.slider("Доп. снижение ДТП от скоринга (%)", min_value=0, max_value=40, value=int(sd_eff_acc_def), step=5) / 100
        
        sd_saving_to = total_maint_before * sd_eff_to
        base_accident_for_sd = (fleet_monthly_accident_before - v_saving) if "Видеоаналитика" in selected_modules else (weighted_accidents_year * weighted_accident_cost / 12)
        sd_saving_acc = base_accident_for_sd * sd_eff_acc
        sd_saving = sd_saving_to + sd_saving_acc
        
        total_capex += sd_capex * total_fleet_size
        total_opex_monthly += sd_opex * total_fleet_size
        monthly_savings_dict["Безопасное вождение"] = sd_saving

# МОДУЛЬ: КОНТРОЛЬ ТОПЛИВА
if "Контроль топлива" in selected_modules:
    with st.sidebar.expander("⛽ Модуль: Контроль топлива", expanded=True):
        f_capex_def = get_weighted_value("fuel_capex")
        f_opex_def = get_weighted_value("fuel_opex")
        f_eff_def = get_weighted_value("fuel_eff")
        
        f_capex = st.number_input("Capex ДУТ + тарировка на 1 ТС", value=int(f_capex_def), step=2000, key="f_cap")
        f_opex = st.number_input("Opex ML-модуля на 1 ТС / мес", value=int(f_opex_def), step=50, key="f_op")
        f_eff = st.slider("Прямая экономия ГСМ (сливы/карты) (%)", min_value=0.0, max_value=25.0, value=float(f_eff_def), step=0.5) / 100
        
        f_saving = total_fuel_before * f_eff
        
        total_capex += f_capex * total_fleet_size
        total_opex_monthly += f_opex * total_fleet_size
        monthly_savings_dict["Контроль топлива"] = f_saving

# МОДУЛЬ: СЕРВИС АНАЛИТИКИ И РЕАГИРОВАНИЯ
if "Сервис аналитики и реагирования" in selected_modules:
    with st.sidebar.expander("🎧 Модуль: Ситуационный центр", expanded=True):
        s_capex_def = get_weighted_value("service_capex")
        s_opex_def = get_weighted_value("service_opex")
        s_eff_def = get_weighted_value("service_eff")
        
        s_capex = st.number_input("Capex настройки интеграции", value=int(s_capex_def), step=1000, key="s_cap")
        s_opex = st.number_input("Opex диспетчеризации 1 ТС / мес", value=int(s_opex_def), step=100, key="s_op")
        s_eff_val = st.number_input("Снижение скрытых потерь на 1 ТС / мес", value=int(s_eff_def), step=100)
        
        s_saving = s_eff_val * total_fleet_size
        total_capex += s_capex * total_fleet_size
        total_opex_monthly += s_opex * total_fleet_size
        monthly_savings_dict["Сервис аналитики и реагирования"] = s_saving


# ==========================================
# 3. ОСНОВНАЯ ЧАСТЬ СТРАНИЦЫ (РЕЗУЛЬТАТЫ)
# ==========================================
fleet_monthly_saving = sum(monthly_savings_dict.values())
net_monthly_benefit = fleet_monthly_saving - total_opex_monthly

if net_monthly_benefit > 0:
    payback_period = total_capex / net_monthly_benefit
else:
    payback_period = float('inf')

st.title("📊 SKAI Платформа: Калькулятор ROI для смешанных автопарков")

# Краткое описание структуры выбранного парка
fleet_structure_str = " + ".join([f"**{qty}** {name.split(' (')[0]}" for name, qty in fleet_quantities.items()])
st.markdown(f"Текущая структура проекта: {fleet_structure_str} | Всего: **{total_fleet_size} ТС**")
st.markdown("---")

# Метрики верхнего уровня
st.subheader("💰 Финансово-экономические показатели проекта")
m1, m2, m3 = st.columns(3)
m1.metric("Стартовые инвестиции (Capex)", f"{fmt(total_capex)} ₽")
m2.metric("Чистая прибыль парка / мес (после Opex)", f"{fmt(net_monthly_benefit)} ₽")

if payback_period != float('inf'):
    m3.metric("Срок окупаемости системы", f"{payback_period:.1f} мес.")
else:
    m3.metric("Срок окупаемости системы", "Проект не окупается")
st.markdown("---")

# Накопительный график (Примыкающие столбцы без наложения)
st.subheader("📈 Структура накопительного эффекта во времени (36 месяцев)")

months = np.arange(1, 37)
chart_data_dict = {}
for module_name, monthly_save_val in monthly_savings_dict.items():
    chart_data_dict[module_name] = [monthly_save_val * m for m in months]

df_chart = pd.DataFrame(chart_data_dict, index=months)
df_chart.index.name = "Месяц"

# Использование st.bar_chart гарантирует строгое примыкание слоев без прозрачности и наложений
st.bar_chart(df_chart)

st.markdown(f"""
> **💡 Анализ структуры ценности:**
> * **Примыкание слоев:** Столбцы наглядно показывают структуру кумулятивного дохода. Каждый цвет — это изолированный финансовый вклад конкретного продукта, слои примыкают друг к другу строго вертикально.
> * **Масштаб эффекта:** К 12-му месяцу платформа сберегает для автопарка в **{total_fleet_size} ТС** в общей сложности **{fmt(fleet_monthly_saving * 12)} ₽**, а к 36-му месяцу сумма чистого эффекта достигает **{fmt(fleet_monthly_saving * 36)} ₽**.
""")
st.markdown("---")

# Сводная таблица параметров
st.subheader("📋 Детализированные параметры расчета")
current_params_table = [
    ["Общий размер смешанного автопарка", f"{total_fleet_size}", "шт."],
    ["Суммарные базовые затраты на топливо до внедрения", f"{fmt(total_fuel_before)}", "руб./мес."],
    ["Суммарные базовые затраты на ремонт и ТО до внедрения", f"{fmt(total_maint_before)}", "руб./мес."],
    ["Расчетная совокупная аварийность парка до внедрения", f"{weighted_accidents_year:.1f}", "ДТП/год"],
    ["Средневзвешенный ущерб от одного инцидента", f"{fmt(weighted_accident_cost)}", "руб."]
]
df_params = pd.DataFrame(current_params_table, columns=["Параметр расчета", "Текущее значение", "Ед. изм."])
st.dataframe(df_params, use_container_width=True, hide_index=True)