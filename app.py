import streamlit as st
import pandas as pd
import numpy as np

# Настройка страницы
st.set_page_config(page_title="SKAI Платформа: Калькулятор окупаемости (ROI)", layout="wide", page_icon="📊")

# ==========================================
# 1. БАЗА ДАННЫХ И ДЕФОЛТНЫЕ НАСТРОЙКИ ТС
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
# 2. СЕКЦИЯ САЙДБАРА: КОНФИГУРАЦИЯ ТИПОВ ТС
# ==========================================
st.sidebar.header("⚙️ Параметры и конфигурация")
st.sidebar.subheader("🚚 Состав и параметры ТС")

fleet_quantities = {}
custom_fleet_params = {}

# Стартовые значения количества машин для демонстрации
default_qtys = {
    "🚛 Магистральный тягач (Фура)": 30,
    "🏗️ Самосвал / Тяжелая спецтехника": 10,
    "📦 Легкий коммерческий транспорт (LCV / Газель)": 15
}

fuel_price = st.sidebar.number_input("Цена топлива (руб./литр)", min_value=1.0, value=65.0, step=1.0)
st.sidebar.markdown("---")

# Цикл создания настроек для каждого типа ТС
for name, p_default in presets.items():
    qty = st.sidebar.number_input(f"{name} (кол-во, шт):", min_value=0, value=default_qtys[name], step=5)
    
    if qty > 0:
        fleet_quantities[name] = qty
        # Рассчитываем пропорциональный дефолт по ДТП под текущее кол-во машин
        default_accidents = p_default["accidents_year"] * (qty / p_default["fleet_size"])
        
        # Компактный подблок настроек для конкретного типа техники
        with st.sidebar.expander(f"🛠️ Настройки: {name.split(' ')[1]}", expanded=False):
            mileage = st.number_input("Пробег 1 ТС в год (км)", min_value=1000, value=p_default["mileage"], step=5000, key=f"mil_{name}")
            consumption = st.number_input("Расход (л/100 км)", min_value=1.0, value=p_default["consumption"], step=0.5, key=f"cons_{name}")
            maintenance = st.number_input("ТО 1 ТС в год (руб.)", min_value=0, value=p_default["maintenance"], step=5000, key=f"maint_{name}")
            accidents = st.number_input("ДТП этой группы в год (шт)", min_value=0.0, value=float(default_accidents), step=0.5, key=f"acc_{name}")
            acc_cost = st.number_input("Ущерб от 1 ДТП (руб.)", min_value=0, value=p_default["accident_cost"], step=50000, key=f"acost_{name}")
        
        # Сохраняем кастомные параметры группы
        custom_fleet_params[name] = {
            "qty": qty,
            "mileage": mileage,
            "consumption": consumption,
            "maintenance": maintenance,
            "accidents_year": accidents,
            "accident_cost": acc_cost,
            # Копируем экономику тарифов модулей СКАЙ для этого типа ТС
            **{k: v for k, v in p_default.items() if "capex" in k or "opex" in k or "eff" in k}
        }
        st.sidebar.markdown("---")

total_fleet_size = sum(fleet_quantities.values())

if total_fleet_size == 0:
    st.sidebar.warning("⚠️ Укажите количество хотя бы для одного типа ТС.")
    st.stop()

# Агрегация динамического базиса на основе кастомных параметров
total_fuel_before = 0
total_maint_before = 0
weighted_accidents_year = 0
total_accident_damage_before = 0

for name, cp in custom_fleet_params.items():
    q = cp["qty"]
    total_fuel_before += ((cp["mileage"] / 100 * cp["consumption"] * fuel_price) / 12) * q
    total_maint_before += (cp["maintenance"] / 12) * q
    weighted_accidents_year += cp["accidents_year"]
    total_accident_damage_before += cp["accidents_year"] * cp["accident_cost"]

weighted_accident_cost = (total_accident_damage_before / weighted_accidents_year) if weighted_accidents_year > 0 else 0

# ==========================================
# 3. СЕКЦИЯ САЙДБАРА: ВЫБОР И НАСТРОЙКА МОДУЛЕЙ
# ==========================================
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

# Функция расчета средневзвешенной стоимости тарифов внедрения
def get_weighted_value(field):
    total = 0
    for name, cp in custom_fleet_params.items():
        total += cp[field] * cp["qty"]
    return total / total_fleet_size

total_capex = 0
total_opex_monthly = 0
monthly_savings_dict = {}

st.sidebar.markdown("---")
st.sidebar.subheader("🔧 Тонкие настройки модулей")

# ВСЕ БЛОКИ НАСТРОЕК МОДУЛЕЙ ПО УМОЛЧАНИЮ ОТКРЫТЫ (expanded=True)

# МОДУЛЬ: ВИДЕОАНАЛИТИКА
if "Видеоаналитика" in selected_modules:
    with st.sidebar.expander("👁️ Модуль: Видеоаналитика", expanded=True):
        v_capex_def = get_weighted_value("video_capex")
        v_opex_def = get_weighted_value("video_opex")
        v_eff_def = get_weighted_value("video_eff")
        
        v_capex = st.number_input("Capex оборудования на 1 ТС", value=int(v_capex_def), step=5000, key="v_cap")
        v_opex = st.number_input("Opex лицензии на 1 ТС / мес", value=int(v_opex_def), step=100, key="v_op")
        accidents_input = st.number_input("Общее кол-во ДТП в год (база)", min_value=0.0, value=float(weighted_accidents_year), step=0.5)
        accident_cost_input = st.number_input("Средний ущерб от 1 ДТП (руб)", min_value=0, value=int(weighted_accident_cost), step=50000)
        v_eff = st.slider("Снижение аварийности со SKAI (%)", min_value=0, max_value=100, value=int(v_eff_def), step=5) / 100
        
        fleet_monthly_accident_before = (accidents_input * accident_cost_input) / 12
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
        
        # Если видеоаналитика включена, защитное вождение снижает остаточную аварийность
        base_accident_for_sd = (fleet_monthly_accident_before - v_saving) if "Видеоаналитика" in selected_modules else (total_accident_damage_before / 12)
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
# 4. ОСНОВНАЯ ЧАСТЬ СТРАНИЦЫ (РЕЗУЛЬТАТЫ)
# ==========================================
fleet_monthly_saving = sum(monthly_savings_dict.values())
net_monthly_benefit = fleet_monthly_saving - total_opex_monthly

if net_monthly_benefit > 0:
    payback_period = total_capex / net_monthly_benefit
else:
    payback_period = float('inf')

st.title("📊 SKAI Платформа: Калькулятор ROI под кастомный автопарк")

# Отображение текущего состава парка
fleet_structure_str = " + ".join([f"**{qty}** {name.split(' (')[0]}" for name, qty in fleet_quantities.items()])
st.markdown(f"Структура парка: {fleet_structure_str} | Всего: **{total_fleet_size} ТС**")
st.markdown("---")

# Финансовые метрики
st.subheader("💰 Финансово-экономические показатели проекта")
m1, m2, m3 = st.columns(3)
m1.metric("Стартовые инвестиции (Capex)", f"{fmt(total_capex)} ₽")
m2.metric("Чистая прибыль парка / мес (после Opex)", f"{fmt(net_monthly_benefit)} ₽")

if payback_period != float('inf'):
    m3.metric("Срок окупаемости системы", f"{payback_period:.1f} мес.")
else:
    m3.metric("Срок окупаемости системы", "Проект не окупается")
st.markdown("---")

# Накопительный график (Примыкающие столбцы)
st.subheader("📈 Структура накопительного эффекта во времени (36 месяцев)")

months = np.arange(1, 37)
chart_data_dict = {}
for module_name, monthly_save_val in monthly_savings_dict.items():
    chart_data_dict[module_name] = [monthly_save_val * m for m in months]

df_chart = pd.DataFrame(chart_data_dict, index=months)
df_chart.index.name = "Месяц"

st.bar_chart(df_chart)

st.markdown(f"""
> **💡 Анализ структуры ценности:**
> * **Индивидуальный расчет:** Экономический эффект рассчитан на основе персональных параметров (пробега, расхода, ТО) для каждого выбранного вами типа техники.
> * **Масштаб эффекта:** К 12-му месяцу платформа сберегает для вашего уникального автопарка в **{total_fleet_size} ТС** в общей сложности **{fmt(fleet_monthly_saving * 12)} ₽**, а к 36-му месяцу сумма чистого эффекта достигает **{fmt(fleet_monthly_saving * 36)} ₽**.
""")
st.markdown("---")

# Таблица детализации базовых параметров
st.subheader("📋 Сводные исходные показатели (агрегированные на базе кастомных ТС)")
current_params_table = [
    ["Общий размер настроенного автопарка", f"{total_fleet_size}", "шт."],
    ["Рассчитанные затраты на топливо всей группы до внедрения", f"{fmt(total_fuel_before)}", "руб./мес."],
    ["Рассчитанные затраты на ремонт и ТО всей группы до внедрения", f"{fmt(total_maint_before)}", "руб./мес."],
    ["Совокупная стартовая аварийность парка (сумма по типам)", f"{weighted_accidents_year:.1f}", "ДТП/год"],
    ["Средневзвешенный ущерб от одного инцидента", f"{fmt(weighted_accident_cost)}", "руб."]
]
df_params = pd.DataFrame(current_params_table, columns=["Параметр расчета", "Значение", "Ед. изм."])
st.dataframe(df_params, use_container_width=True, hide_index=True)