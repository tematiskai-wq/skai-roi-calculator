import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Настройка страницы в строгом B2B стиле
st.set_page_config(page_title="Платформа SKAI: Калькулятор TCO и ROI", layout="wide")

# Фирменный SVG логотип SKAI
SKAI_LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 570 190" width="100%" height="100%">
<rect width="570" height="190" rx="28" fill="#166EFF"/>
<g transform="translate(53.15, 41.65)" fill="#FFFFFF">
<path d="M5.97,6.91H0.02v-6.9h6.96v6.9H5.97L5.97,6.91z M54.66,68.26h-5.95v-6.9h6.96v6.9H54.66L54.66,68.26z M30.32,68.26h-5.95
v-6.9h6.96v6.9H30.32L30.32,68.26z M5.97,68.26H0.02v-6.9h6.96v6.9H5.97L5.97,68.26z M30.31,47.81h-5.95v-6.9h6.96v6.9H30.31
L30.31,47.81z M5.97,47.81H0.02v-6.9h6.96v6.9H5.97L5.97,47.81z M54.66,47.81h-5.95v-6.9h6.96v6.9H54.66L54.66,47.81z M78.99,47.81
h-5.95v-6.9H80v6.9H78.99L78.99,47.81z M30.31,27.35h-5.95v-6.9h6.96v6.9H30.31L30.31,27.35z M5.97,27.36H0.02v-6.9h6.96v6.9H5.97
L5.97,27.36z M54.65,27.36H48.7v-6.9h6.96v6.9H54.65L54.65,27.36z M78.99,27.36h-5.95v-6.9H80v6.9H78.99L78.99,27.36z M30.31,6.9
h-5.95V0h6.96v6.9H30.31L30.31,6.9z M54.65,6.91H48.7v-6.9h6.96v6.9H54.65L54.65,6.91z M78.99,6.91h-5.95v-6.9H80v6.9H78.99
L78.99,6.91z M103.33,6.91h-5.95v-6.9h6.96v6.9H103.33L103.33,6.91z M103.33,27.36h-5.95v-6.9h6.96v6.9H103.33L103.33,27.36z"/>
<path d="M154.12,70.15c0.08,0.58,0.22,1.18,0.4,1.77c1.45,4.8,5.92,8,11.34,9.85c5.79,1.98,12.57,2.42,18.1,1.64
c1.44-0.2,2.83-0.5,4.08-0.88c2.25-0.67,4.59-1.63,6.5-2.97c1.73-1.22,3.12-2.77,3.71-4.73c1.64-5.38-1.13-8.69-5.27-10.79
c-4.94-2.5-11.77-3.56-16.59-4.23c-11.61-1.64-20.08-4.5-25.6-8.73c-5.94-4.54-8.54-10.52-8.03-18.05
c0.51-7.47,4.15-13.45,10.34-17.54c5.89-3.89,14.11-6,24.08-5.95c9.85,0.05,17.84,2.63,23.53,7.02c6.1,4.7,9.58,11.41,9.97,19.28
l0.14,2.93h-15.09v-2.8c0-4.01-1.88-6.86-4.64-8.8c-3.92-2.76-9.57-3.86-14.52-3.86c-6.11,0-11.03,1.07-14.41,3.03
c-2.98,1.72-4.73,4.17-4.95,7.17l-0.01,0.32c-0.1,1.94-0.47,9.06,21.5,11.89c15.04,1.9,23.88,5.83,28.95,10.57
c5.43,5.07,6.65,10.94,6.49,16.4c-0.19,6.12-3.85,13.14-11.4,18.08c-5.82,3.81-14,6.42-24.68,6.42c-9.03,0-19.55-1.97-27.38-7.12
c-6.38-4.2-10.98-10.44-11.65-19.32l-0.23-3.01h15L154.12,70.15L154.12,70.15z M0,85.76c45.1,17.53,69.53-5.53,93.13-27.8
c3.73-3.52,7.44-7.03,11.21-10.38v19.02l-1.63,1.54C76.49,92.88,49.37,118.47,0,100.9V85.76L0,85.76z M460.89,96.58h-11.46V10.11
h14.27v86.46H460.89L460.89,96.58z M396.87,64.19l-15.35-33.7l-15.35,33.7H396.87L396.87,64.19z M337.33,92.59L376,10.12h10.62
c13.55,28.8,27.05,57.63,40.55,86.45h-15.35l-8.96-19.69h-43.18l-8.86,19.69h-15.37L337.33,92.59L337.33,92.59z M266.45,58.48
l-14.09,14.74v23.45h-14.38V10.12h14.38v43.77l41.8-43.77h18.89l-36.8,38.28l40.13,48.17h-18.3L266.45,58.48L266.45,58.48z"/>
</g>
</svg>"""

# ==========================================
# 1. БАЗА ДАННЫХ ПРЕСЕТОВ (БАЗОВЫЕ ЗНАЧЕНИЯ В РУБЛЯХ)
# ==========================================
presets = {
    "Магистральный тягач (Фура)": {
        "fleet_size": 50, "mileage": 120000, "consumption": 32.0, "maintenance": 60000,
        "accidents_year": 8, "accident_cost": 1550000, "insurance_cost": 95000,
        "video_capex": 120000, "video_opex": 2000, "video_eff": 80,
        "base_capex": 15000, "base_opex": 400, "base_eff_fuel": 6.0, "base_eff_to": 5.0, "base_eff_fines": 40,
        "safe_capex": 10000, "safe_opex": 500, "safe_eff_fuel": 10.0, "safe_eff_to": 15, "safe_eff_acc": 75,
        "fuel_capex": 25000, "fuel_opex": 600, "fuel_eff": 10
    },
    "Самосвал / Тяжелая спецтехника": {
        "fleet_size": 30, "mileage": 45000, "consumption": 45.0, "maintenance": 90000,
        "accidents_year": 6, "accident_cost": 1200000, "insurance_cost": 85000,
        "video_capex": 130000, "video_opex": 2000, "video_eff": 80,
        "base_capex": 15000, "base_opex": 400, "base_eff_fuel": 9.0, "base_eff_to": 6.0, "base_eff_fines": 30,
        "safe_capex": 10000, "safe_opex": 500, "safe_eff_fuel": 10.0, "safe_eff_to": 20, "safe_eff_acc": 75,
        "fuel_capex": 30000, "fuel_opex": 600, "fuel_eff": 12
    },
    "Легкий коммерческий транспорт / Корпоративные авто": {
        "fleet_size": 40, "mileage": 60000, "consumption": 13.0, "maintenance": 35000,
        "accidents_year": 7, "accident_cost": 650000, "insurance_cost": 45000,
        "video_capex": 110000, "video_opex": 1800, "video_eff": 80,
        "base_capex": 12000, "base_opex": 350, "base_eff_fuel": 13.0, "base_eff_to": 8.0, "base_eff_fines": 60,
        "safe_capex": 8000, "safe_opex": 400, "safe_eff_fuel": 10.0, "safe_eff_to": 12, "safe_eff_acc": 75,
        "fuel_capex": 20000, "fuel_opex": 500, "fuel_eff": 8
    }
}

monetary_keys = [
    "fuel_price", "emp_salary", "downtime_loss_per_day", "disp_salary", 
    "fine_avg_cost", "s_cap", "s_op", "b_cap", "b_op", "v_cap", "v_op", 
    "sd_cap", "sd_op", "f_cap", "f_op"
]
for name in presets.keys():
    monetary_keys.extend([f"maint_{name}", f"acost_{name}", f"ins_{name}"])

# ==========================================
# 2. ИНИЦИАЛИЗАЦИЯ И КОНВЕРТАЦИЯ СОСТОЯНИЯ (SESSION STATE)
# ==========================================
st.session_state.setdefault("initialized", True)
st.session_state.setdefault("prev_currency", "₽ (RUB)")
st.session_state.setdefault("fuel_price", 65.0)
st.session_state.setdefault("emp_salary", 100000)
st.session_state.setdefault("downtime_loss_per_day", 10000)
st.session_state.setdefault("disp_salary", 80000)
st.session_state.setdefault("fine_avg_cost", 500)
st.session_state.setdefault("s_cap", 40000)
st.session_state.setdefault("s_op", 900)

for name, p_default in presets.items():
    st.session_state.setdefault(f"maint_{name}", p_default["maintenance"])
    st.session_state.setdefault(f"acost_{name}", p_default["accident_cost"])
    st.session_state.setdefault(f"ins_{name}", p_default["insurance_cost"])

st.session_state.setdefault("b_cap", 15000)
st.session_state.setdefault("b_op", 400)
st.session_state.setdefault("v_cap", 120000)
st.session_state.setdefault("v_op", 2000)
st.session_state.setdefault("sd_cap", 10000)
st.session_state.setdefault("sd_op", 500)
st.session_state.setdefault("f_cap", 25000)
st.session_state.setdefault("f_op", 600)

def fmt(val):
    return f"{val:,.0f}".replace(",", " ")

# ==========================================
# 3. СЕКЦИЯ САЙДБАРА: ПАРАМЕТРЫ И СТРУКТУРА ПАРКА
# ==========================================
# Закрепленный вверху сайдбара логотип
st.sidebar.markdown(
    f"""
    <style>
        /* Фиксация первого блока (логотипа) вверху сайдбара */
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:first-child {{
            position: sticky;
            top: 0;
            z-index: 9999;
            background: var(--secondary-background-color, #f0f2f6);
            padding-top: 0.8rem;
            padding-bottom: 0.8rem;
            margin-bottom: 0.5rem;
            border-bottom: 1px solid rgba(0, 0, 0, 0.08);
        }}
    </style>
    <div style="width: 140px; margin: 0 auto 0 0;">
        {SKAI_LOGO_SVG}
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.header("Параметры и конфигурация")

currency_choice = st.sidebar.radio("Валюта расчетов:", ["₽ (RUB)", "₸ (KZT)"], horizontal=True)
is_kzt = "KZT" in currency_choice
curr_symbol = "₸" if is_kzt else "₽"

if currency_choice != st.session_state["prev_currency"]:
    factor = 6.13 if is_kzt else (1 / 6.13)
    for k in monetary_keys:
        if k in st.session_state:
            if k == "fuel_price":
                st.session_state[k] = round(st.session_state[k] * factor, 1)
            else:
                st.session_state[k] = round(st.session_state[k] * factor)
    st.session_state["prev_currency"] = currency_choice

st.session_state["fuel_price"] = st.sidebar.number_input(f"Цена топлива ({curr_symbol}/литр)", min_value=1.0, value=float(st.session_state["fuel_price"]), step=1.0)
fuel_price = st.session_state["fuel_price"]

st.sidebar.markdown("---")
st.sidebar.subheader("Состав и параметры ТС")

fleet_quantities = {}
custom_fleet_params = {}

default_qtys = {
    "Магистральный тягач (Фура)": 30,
    "Самосвал / Тяжелая спецтехника": 10,
    "Легкий коммерческий транспорт / Корпоративные авто": 15
}

for name, p_default in presets.items():
    qty = st.sidebar.number_input(f"{name} (шт):", min_value=0, value=default_qtys[name], step=5, key=f"qty_input_{name}")
    
    if qty > 0:
        fleet_quantities[name] = qty
        clean_name = name.split(" (")[0]
        
        # Динамический пересчет частоты ДТП при изменении количества машин в группе
        prev_qty_key = f"prev_qty_{name}"
        acc_key = f"acc_{name}"
        
        if prev_qty_key not in st.session_state:
            st.session_state[prev_qty_key] = qty
            st.session_state[acc_key] = float(round(p_default["accidents_year"] * (qty / p_default["fleet_size"]), 1))
        elif st.session_state[prev_qty_key] != qty:
            st.session_state[acc_key] = float(round(p_default["accidents_year"] * (qty / p_default["fleet_size"]), 1))
            st.session_state[prev_qty_key] = qty
        
        with st.sidebar.expander(f"Настройки: {clean_name}", expanded=False):
            mileage = st.number_input("Пробег 1 ТС в год (км)", min_value=1000, value=p_default["mileage"], step=5000, key=f"mil_{name}")
            consumption = st.number_input("Расход (л/100 км)", min_value=1.0, value=p_default["consumption"], step=0.5, key=f"cons_{name}")
            
            st.session_state[f"maint_{name}"] = st.number_input(f"ТО + расходники 1 ТС/год ({curr_symbol})", min_value=0, value=int(st.session_state[f"maint_{name}"]), step=5000)
            accidents = st.number_input("ДТП этой группы в год (шт)", min_value=0.0, step=0.5, key=acc_key)
            st.session_state[f"acost_{name}"] = st.number_input(f"Ущерб/франшиза 1 ДТП ({curr_symbol})", min_value=0, value=int(st.session_state[f"acost_{name}"]), step=50000)
            st.session_state[f"ins_{name}"] = st.number_input(f"КАСКО и ОСАГО на 1 ТС в год ({curr_symbol})", min_value=0, value=int(st.session_state[f"ins_{name}"]), step=5000)
        
        custom_fleet_params[name] = {
            "qty": qty, "mileage": mileage, "consumption": consumption, 
            "maintenance": st.session_state[f"maint_{name}"],
            "accidents_year": accidents, "accident_cost": st.session_state[f"acost_{name}"],
            "insurance_cost": st.session_state[f"ins_{name}"],
            **{k: v for k, v in p_default.items() if "eff" in k}
        }

total_fleet_size = sum(fleet_quantities.values())
if total_fleet_size == 0:
    st.sidebar.warning("Укажите количество хотя бы для одного типа ТС.")
    st.stop()

# ==========================================
# 4. СЕКЦИЯ САЙДБАРА: УПРАВЛЕНИЕ TCO, ПЕРСОНАЛОМ И СТРАХОВАНИЕМ
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader("Управление TCO и персоналом")

with st.sidebar.expander("Потери бэк-офиса и простои персонала", expanded=False):
    st.session_state["emp_salary"] = st.number_input(f"Затраты на 1 водителя в месяц (ФОТ, {curr_symbol})", value=int(st.session_state["emp_salary"]), step=5000)
    
    st.session_state["downtime_loss_per_day"] = st.number_input(
        f"Потери от 1 дня простоя 1 ТС ({curr_symbol}/день)", 
        value=int(st.session_state["downtime_loss_per_day"]), 
        step=1000
    )
    st.caption("Расшифровка: упущенная чистая прибыль (маржа) от сорванного рейса или затраты на аренду подменного автомобиля за одни сутки.")

    st.markdown("**Диспетчеризация и администрирование**")
    st.session_state["disp_salary"] = st.number_input(f"ФОТ 1 диспетчера парка в месяц ({curr_symbol})", value=int(st.session_state["disp_salary"]), step=5000)
    calculated_disp_qty = max(1.0, round(total_fleet_size / 25, 1))
    disp_qty = st.number_input("Текущее кол-во диспетчеров в штате (база)", value=float(calculated_disp_qty), step=0.5)
    
    manager_hourly_rate = round(st.session_state["disp_salary"] / 168)
    st.caption(f"Себестоимость часа работы бэк-офиса: {manager_hourly_rate} {curr_symbol}/час (рассчитано автоматически: ФОТ / 168 ч).")
    
    st.markdown("**Издержки при инцидентах**")
    downtime_days = st.number_input("Средний простой ТС после ДТП (дней)", value=14, step=1)
    time_manager_accident = 8
    
    st.markdown("**Штрафы автопарка**")
    fines_per_car_year = st.number_input("Кол-во штрафов на 1 ТС в год (база)", value=12, step=2)
    st.session_state["fine_avg_cost"] = st.number_input(f"Средняя стоимость 1 штрафа ({curr_symbol})", value=int(st.session_state["fine_avg_cost"]), step=100)
    time_manager_fine = 0.5

with st.sidebar.expander("Страхование автопарка (КАСКО и ОСАГО)", expanded=False):
    st.caption("Скидка при пролонгации активируется при оснащении комплексами Видеоаналитики SKAI")
    insurance_discount = st.slider("Прогноз скидки на КАСКО/ОСАГО при снижении ДТП (%)", 0, 40, 20, step=5) / 100

working_days_month = 21.7
employee_daily_cost = st.session_state["emp_salary"] / working_days_month
downtime_daily_loss = st.session_state["downtime_loss_per_day"]

def get_total_accident_cost(direct_cost):
    downtime_loss = downtime_days * (employee_daily_cost + downtime_daily_loss)
    management_loss = time_manager_accident * manager_hourly_rate
    return direct_cost + downtime_loss + management_loss

fine_loss_per_car_month = (fines_per_car_year * (st.session_state["fine_avg_cost"] + (time_manager_fine * manager_hourly_rate))) / 12
total_disp_fot_before = disp_qty * st.session_state["disp_salary"]

# Базовый расчет расходов ДО внедрения системы
total_fuel_before, total_maint_before, total_accidents_year = 0, 0, 0
total_direct_accident_damage_before, total_tco_accident_damage_before = 0, 0
total_insurance_before, total_mileage_year = 0, 0

for name, cp in custom_fleet_params.items():
    q = cp["qty"]
    total_fuel_before += ((cp["mileage"] / 100 * cp["consumption"] * fuel_price) / 12) * q
    total_maint_before += (cp["maintenance"] / 12) * q
    total_accidents_year += cp["accidents_year"]
    total_direct_accident_damage_before += cp["accidents_year"] * cp["accident_cost"]
    total_tco_accident_damage_before += cp["accidents_year"] * get_total_accident_cost(cp["accident_cost"])
    total_insurance_before += (cp["insurance_cost"] / 12) * q
    total_mileage_year += cp["mileage"] * q

total_fines_loss_before = fine_loss_per_car_month * total_fleet_size

# ==========================================
# 5. СЕКЦИЯ САЙДБАРА: НАСТРОЙКИ МОДУЛЕЙ SKAI
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader("Модули платформы SKAI")
available_modules = ["Видеоаналитика", "Базовый Мониторинг", "Безопасное вождение", "Контроль топлива", "Сервис аналитики и реагирования"]
selected_modules = [m for m in available_modules if st.sidebar.checkbox(m, value=(m in ["Видеоаналитика", "Базовый Мониторинг"]))]

if not selected_modules:
    st.sidebar.warning("Выберите хотя бы один модуль.")
    st.stop()

modules_raw = {}
savings_by_cat = {"fuel": 0, "maint": 0, "acc_direct": 0, "acc_tco": 0, "fines": 0, "disp": 0, "insurance": 0}

# --- БАЗОВЫЙ МОНИТОРИНГ ---
if "Базовый Мониторинг" in selected_modules:
    with st.sidebar.expander("Модуль: Базовый Мониторинг", expanded=True):
        has_gps_status = st.radio(
            "Оснащенность автопарка GPS:",
            ["GPS-оборудование отсутствует", "GPS уже установлен на ТС"],
            key="has_gps_status"
        )
        is_gps_installed = (has_gps_status == "GPS уже установлен на ТС")
        
        if is_gps_installed:
            default_b_capex = int(2500 * (6.13 if is_kzt else 1.0))
            capex_label = f"Затраты на аудит и перевод 1 ТС на SKAI ({curr_symbol})"
        else:
            default_b_capex = int(15000 * (6.13 if is_kzt else 1.0))
            capex_label = f"Затраты на трекер + монтаж на 1 ТС ({curr_symbol})"

        avg_fleet_fuel_eff = sum(cp["qty"] * cp["base_eff_fuel"] for cp in custom_fleet_params.values()) / total_fleet_size
        default_b_fuel = round(avg_fleet_fuel_eff * (0.5 if is_gps_installed else 1.0), 1)
        default_b_to = 3.0 if is_gps_installed else 5.0
        default_b_fines = 20 if is_gps_installed else 40

        b_capex_input = st.number_input(capex_label, min_value=0, value=default_b_capex, step=500, key=f"b_cap_{is_gps_installed}")
        b_opex_input = st.number_input(f"АП на 1 ТС/мес ({curr_symbol})", value=int(st.session_state["b_op"]), step=50, key="b_op_input")
        
        eff_fuel = st.slider("Сокращение нецелевого пробега и расхода ГСМ (%)", 0.0, 20.0, float(default_b_fuel), step=0.5, key=f"eff_fuel_{is_gps_installed}") / 100
        eff_to = st.slider("Сокращение износа и ТО от исключения перепробегов (%)", 0.0, 15.0, float(default_b_to), step=0.5, key=f"eff_to_{is_gps_installed}") / 100
        eff_fines = st.slider("Сокращение штрафов (%)", 0, 100, int(default_b_fines), step=5, key=f"eff_fines_{is_gps_installed}") / 100

        b_dir_savings = (total_fuel_before * eff_fuel) + (total_maint_before * eff_to)
        b_tco_savings = total_fines_loss_before * eff_fines
        
        modules_raw["Базовый Мониторинг"] = {
            "capex": b_capex_input * total_fleet_size, 
            "opex": b_opex_input * total_fleet_size, 
            "direct_base": b_dir_savings, 
            "tco_base": b_tco_savings,
            "acc_weight": 0.0
        }
        savings_by_cat["fuel"] += total_fuel_before * eff_fuel
        savings_by_cat["maint"] += total_maint_before * eff_to
        savings_by_cat["fines"] += total_fines_loss_before * eff_fines

# --- СЕРВИС АНАЛИТИКИ И РЕАГИРОВАНИЯ ---
if "Сервис аналитики и реагирования" in selected_modules:
    with st.sidebar.expander("Сервис аналитики и реагирования", expanded=False):
        st.session_state["s_cap"] = st.number_input(f"Единовременные затраты ({curr_symbol})", value=int(st.session_state["s_cap"]), step=10000)
        st.session_state["s_op"] = st.number_input(f"АП на 1 ТС/мес ({curr_symbol})", value=int(st.session_state["s_op"]), step=100)
        s_eff_disp = st.slider("Сокращение затрат на ФОТ диспетчеров (%)", 0, 100, 60, step=5) / 100
        
        modules_raw["Сервис аналитики и реагирования"] = {
            "capex": st.session_state["s_cap"], 
            "opex": st.session_state["s_op"] * total_fleet_size, 
            "direct_base": 0, 
            "tco_base": total_disp_fot_before * s_eff_disp,
            "acc_weight": 0.0
        }
        savings_by_cat["disp"] += total_disp_fot_before * s_eff_disp

# --- ВИДЕОАНАЛИТИКА ---
if "Видеоаналитика" in selected_modules:
    with st.sidebar.expander("Модуль: Видеоаналитика", expanded=True):
        st.session_state["v_cap"] = st.number_input(f"Оборудование на 1 ТС ({curr_symbol})", value=int(st.session_state["v_cap"]), step=5000)
        st.session_state["v_op"] = st.number_input(f"АП на 1 ТС/мес ({curr_symbol})", value=int(st.session_state["v_op"]), step=100)
        
        v_eff_acc = st.slider("Снижение аварийности со SKAI (%)", 0, 100, 80, step=5) / 100
        
        modules_raw["Видеоаналитика"] = {
            "capex": st.session_state["v_cap"] * total_fleet_size, 
            "opex": st.session_state["v_op"] * total_fleet_size, 
            "direct_base": 0, 
            "tco_base": 0,
            "acc_weight": v_eff_acc
        }

# --- БЕЗОПАСНОЕ ВОЖДЕНИЕ ---
if "Безопасное вождение" in selected_modules:
    with st.sidebar.expander("Модуль: Безопасное вождение", expanded=False):
        st.session_state["sd_cap"] = st.number_input(f"Стоимость модуля на 1 ТС ({curr_symbol})", value=int(st.session_state["sd_cap"]), step=1000)
        st.session_state["sd_op"] = st.number_input(f"АП на 1 ТС/мес ({curr_symbol})", value=int(st.session_state["sd_op"]), step=50)
        
        sd_eff_acc = st.slider("Снижение аварийности от скоринга (%)", 0, 100, 75, step=5) / 100
        sd_eff_fuel = st.slider("Снижение расхода топлива от стиля езды (%)", 0.0, 25.0, 10.0, step=0.5) / 100
        sd_eff_to = st.slider("Экономия на ТО от бережной езды (%)", 0, 40, 15, step=5) / 100
        
        sd_fuel_saving = total_fuel_before * sd_eff_fuel
        sd_maint_saving = total_maint_before * sd_eff_to
        
        modules_raw["Безопасное вождение"] = {
            "capex": st.session_state["sd_cap"] * total_fleet_size, 
            "opex": st.session_state["sd_op"] * total_fleet_size, 
            "direct_base": sd_fuel_saving + sd_maint_saving, 
            "tco_base": 0,
            "acc_weight": sd_eff_acc
        }
        savings_by_cat["fuel"] += sd_fuel_saving
        savings_by_cat["maint"] += sd_maint_saving

# --- КОНТРОЛЬ ТОПЛИВА ---
if "Контроль топлива" in selected_modules:
    with st.sidebar.expander("Модуль: Контроль топлива", expanded=False):
        st.session_state["f_cap"] = st.number_input(f"Стоимость ДУТ на 1 ТС ({curr_symbol})", value=int(st.session_state["f_cap"]), step=2000)
        st.session_state["f_op"] = st.number_input(f"АП на 1 ТС/мес ({curr_symbol})", value=int(st.session_state["f_op"]), step=50)
        f_eff = st.slider("Прямая экономия ГСМ (сливы/карты) (%)", 0.0, 25.0, 10.0, step=0.5) / 100
        
        modules_raw["Контроль топлива"] = {
            "capex": st.session_state["f_cap"] * total_fleet_size, 
            "opex": st.session_state["f_op"] * total_fleet_size, 
            "direct_base": total_fuel_before * f_eff, 
            "tco_base": 0,
            "acc_weight": 0.0
        }
        savings_by_cat["fuel"] += total_fuel_before * f_eff

# ==========================================
# СИНЕРГЕТИЧЕСКИЙ РАСЧЕТ АВАРИЙНОСТИ И СТРАХОВАНИЯ
# ==========================================
acc_eff_va = modules_raw.get("Видеоаналитика", {}).get("acc_weight", 0.0)
acc_eff_sd = modules_raw.get("Безопасное вождение", {}).get("acc_weight", 0.0)

combined_no_accident_prob = (1.0 - acc_eff_va) * (1.0 - acc_eff_sd)
total_combined_acc_eff = 1.0 - combined_no_accident_prob

total_direct_acc_saving = (total_direct_accident_damage_before / 12) * total_combined_acc_eff
total_tco_acc_saving = ((total_tco_accident_damage_before - total_direct_accident_damage_before) / 12) * total_combined_acc_eff

savings_by_cat["acc_direct"] = total_direct_acc_saving
savings_by_cat["acc_tco"] = total_tco_acc_saving

# Скидка по КАСКО и ОСАГО предоставляется ИСКЛЮЧИТЕЛЬНО при наличии Видеоаналитики
has_va = ("Видеоаналитика" in selected_modules)
total_ins_saving = (total_insurance_before * insurance_discount) if has_va else 0.0
savings_by_cat["insurance"] = total_ins_saving

sum_acc_weights = sum(m["acc_weight"] for m in modules_raw.values())
modules_payload = {}

for m_name, m_data in modules_raw.items():
    if sum_acc_weights > 0 and m_data["acc_weight"] > 0:
        weight_ratio = m_data["acc_weight"] / sum_acc_weights
        m_dir_acc = total_direct_acc_saving * weight_ratio
        m_tco_acc = total_tco_acc_saving * weight_ratio
    else:
        m_dir_acc, m_tco_acc = 0.0, 0.0
        
    m_ins = total_ins_saving if m_name == "Видеоаналитика" else 0.0
        
    modules_payload[m_name] = {
        "capex": m_data["capex"],
        "opex": m_data["opex"],
        "direct": m_data["direct_base"] + m_dir_acc + m_ins,
        "tco": m_data["tco_base"] + m_tco_acc
    }

# ==========================================
# 6. РЕНДЕРИНГ ИНТЕРФЕЙСА И РАСЧЕТ МЕТРИК
# ==========================================
st.title("Платформа SKAI: Калькулятор TCO и ROI")

bar_colors = ["#2563EB", "#0EA5E9", "#64748B", "#F59E0B"]

# 1. Тонкая сегментированная шкала распределения
distribution_bar_html = "<div style='display: flex; height: 6px; width: 100%; border-radius: 3px; overflow: hidden; background-color: #E2E8F0; margin: 12px 0 16px 0;'>"
for idx, (name, cp) in enumerate(custom_fleet_params.items()):
    qty = cp["qty"]
    share = (qty / total_fleet_size * 100) if total_fleet_size > 0 else 0
    color = bar_colors[idx % len(bar_colors)]
    if share > 0:
        distribution_bar_html += f"<div style='width: {share}%; background-color: {color};' title='{name}: {share:.1f}%'></div>"
distribution_bar_html += "</div>"

risk_profiles = {
    "Магистральный тягач (Фура)": "Трассовые ДТП (сон/дистанция), непроизводительный ХХ на стоянках",
    "Самосвал / Тяжелая спецтехника": "Холостой ход на погрузке, маневрирование в ограниченном пространстве",
    "Легкий коммерческий транспорт / Корпоративные авто": "Плотный городской трафик, превышение скорости, отвлечение на телефон"
}

# 2. Карточки автопарка
cards_html = f"""<div style="display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 24px;">
<div style="flex: 1 1 180px; background-color: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 8px; padding: 14px 18px;">
<div style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #475569; margin-bottom: 4px;">Общий объем парка</div>
<div style="font-size: 28px; font-weight: 700; color: #0F172A; line-height: 1.1;">{total_fleet_size} <span style="font-size: 14px; font-weight: 500; color: #64748B;">ТС</span></div>
<div style="font-size: 12px; color: #64748B; margin-top: 6px;">100% расчетной базы</div>
</div>"""

for idx, (name, cp) in enumerate(custom_fleet_params.items()):
    clean_name = name.split(" (")[0]
    qty = cp["qty"]
    share = (qty / total_fleet_size * 100) if total_fleet_size > 0 else 0
    color = bar_colors[idx % len(bar_colors)]
    group_mileage = cp["mileage"] * qty
    profile_text = risk_profiles.get(name, "Операционные риски эксплуатации")
    
    cards_html += f"""<div style="flex: 1 1 230px; background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px 18px; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">
<div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
<div style="width: 8px; height: 8px; border-radius: 50%; background-color: {color};"></div>
<div style="font-size: 12px; font-weight: 600; color: #334155; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{clean_name}">{clean_name}</div>
</div>
<div style="font-size: 28px; font-weight: 700; color: #0F172A; line-height: 1.1;">{qty} <span style="font-size: 14px; font-weight: 500; color: #64748B;">ТС</span> <span style="font-size: 13px; font-weight: 600; color: {color};">({share:.1f}%)</span></div>
<div style="font-size: 12px; color: #64748B; margin-top: 4px;">Пробег группы: {fmt(group_mileage)} км/год</div>
<div style="font-size: 11px; color: #94A3B8; margin-top: 6px; line-height: 1.3;">Фокус: {profile_text}</div>
</div>"""

cards_html += "</div>"
st.markdown(distribution_bar_html + cards_html, unsafe_allow_html=True)

# ==========================================
# ДИНАМИЧЕСКИЙ АНАЛИЗ ПОТЕРЬ (ПРЯМЫЕ + СКРЫТЫЕ)
# ==========================================
annual_direct_accidents = total_direct_accident_damage_before
annual_iceberg_hidden = annual_direct_accidents * 3.0
annual_fuel_total = total_fuel_before * 12
annual_waste_fuel = annual_fuel_total * 0.12
annual_downtime_days = total_accidents_year * downtime_days
annual_downtime_cost = annual_downtime_days * (downtime_daily_loss + employee_daily_cost)

st.markdown(
    f"""
    <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #2563EB; border-radius: 6px; padding: 14px 18px; margin-bottom: 24px;">
        <div style="font-size: 13px; font-weight: 700; color: #1E293B; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px;">
            Оценка зоны потенциальных потерь парка до внедрения платформы SKAI
        </div>
        <div style="display: flex; gap: 16px; flex-wrap: wrap;">
            <div style="flex: 1 1 210px; background-color: #FFFFFF; border: 1px solid #FEE2E2; border-radius: 6px; padding: 10px 14px;">
                <div style="font-size: 12px; font-weight: 600; color: #991B1B;">Прямой ущерб от ДТП</div>
                <div style="font-size: 20px; font-weight: 700; color: #DC2626; margin: 2px 0;">~{fmt(annual_direct_accidents)} {curr_symbol}/год</div>
                <div style="font-size: 11px; color: #64748B;">Счета СТО, ремонт и франшизы при {total_accidents_year:.1f} ДТП</div>
            </div>
            <div style="flex: 1 1 210px; background-color: #FFFFFF; border: 1px solid #FFE4E6; border-radius: 6px; padding: 10px 14px;">
                <div style="font-size: 12px; font-weight: 600; color: #9F1239;">Скрытые потери от ДТП (1:3)</div>
                <div style="font-size: 20px; font-weight: 700; color: #E11D48; margin: 2px 0;">~{fmt(annual_iceberg_hidden)} {curr_symbol}/год</div>
                <div style="font-size: 11px; color: #64748B;">Срыв контрактов, субподряд, разбор инцидентов</div>
            </div>
            <div style="flex: 1 1 210px; background-color: #FFFFFF; border: 1px solid #FEF3C7; border-radius: 6px; padding: 10px 14px;">
                <div style="font-size: 12px; font-weight: 600; color: #92400E;">Балласт по ГСМ (ХХ и съезды)</div>
                <div style="font-size: 20px; font-weight: 700; color: #D97706; margin: 2px 0;">~{fmt(annual_waste_fuel)} {curr_symbol}/год</div>
                <div style="font-size: 11px; color: #64748B;">10–14% топлива сжигается впустую на стоянках и приписках</div>
            </div>
            <div style="flex: 1 1 210px; background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 6px; padding: 10px 14px;">
                <div style="font-size: 12px; font-weight: 600; color: #334155;">Потери от простоя техники</div>
                <div style="font-size: 20px; font-weight: 700; color: #475569; margin: 2px 0;">~{fmt(annual_downtime_cost)} {curr_symbol}/год</div>
                <div style="font-size: 11px; color: #64748B;">Суммарно {int(annual_downtime_days)} дней ожидания и кузовного ремонта</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("---")

calc_mode = st.radio("Аналитическая модель расчета:", ["Прямой экономический эффект (Классический)", "Полный TCO расчет (С учетом скрытых потерь и оптимизации ФОТ)"], horizontal=True)
is_tco = "Полный TCO" in calc_mode
mode_title = "полного TCO расчета" if is_tco else "прямого эффекта"

total_capex = sum(m["capex"] for m in modules_payload.values())
total_opex_monthly = sum(m["opex"] for m in modules_payload.values())

total_monthly_saving = sum(m["direct"] + (m["tco"] if is_tco else 0) for m in modules_payload.values())
net_monthly_benefit = total_monthly_saving - total_opex_monthly
payback_period = total_capex / net_monthly_benefit if net_monthly_benefit > 0 else float('inf')

st.subheader("Экономические показатели проекта")
m1, m2, m3 = st.columns(3)
m1.metric("Капитальные вложения (Стартовые инвестиции)", f"{fmt(total_capex)} {curr_symbol}")
m2.metric("Чистая экономия в месяц", f"{fmt(net_monthly_benefit)} {curr_symbol}")
m3.metric("Срок окупаемости инвестиций", f"{payback_period:.1f} мес." if payback_period != float('inf') else "Проект не окупается")

# ==========================================
# РАСЧЕТ СТОИМОСТИ РИСКА ДТП НА 100 КМ ПРОБЕГА
# ==========================================
st.markdown("---")
st.subheader("Анализ стоимости риска аварийности на 100 км пробега")

monthly_mileage_fleet = total_mileage_year / 12 if total_mileage_year > 0 else 1.0
base_accident_damage_mode = total_tco_accident_damage_before / 12 if is_tco else total_direct_accident_damage_before / 12
saved_accident_damage_mode = (savings_by_cat["acc_direct"] + savings_by_cat["acc_tco"]) if is_tco else savings_by_cat["acc_direct"]

risk_per_100km_before = (base_accident_damage_mode / monthly_mileage_fleet) * 100
risk_per_100km_after = ((base_accident_damage_mode - saved_accident_damage_mode) / monthly_mileage_fleet) * 100
risk_saving_per_100km = risk_per_100km_before - risk_per_100km_after

rc1, rc2, rc3 = st.columns(3)
rc1.metric(
    "Стоимость риска ДТП до внедрения", 
    f"{risk_per_100km_before:.1f} {curr_symbol} / 100 км"
)

rc2.metric(
    "Стоимость риска ДТП со SKAI", 
    f"{risk_per_100km_after:.1f} {curr_symbol} / 100 км", 
    delta=f"-{total_combined_acc_eff*100:.0f}% к риску", 
    delta_color="inverse"
)

with rc3:
    st.markdown(
        f"""
        <div>
            <div style="font-size: 14px; opacity: 0.85; margin-bottom: 4px;">Чистая экономия на 100 км пути</div>
            <div style="font-size: 32px; font-weight: 700; color: #09ab3b; line-height: 1.2;">
                +{risk_saving_per_100km:.1f} {curr_symbol} / 100 км
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

# ==========================================
# ТАБЛИЦА ДЕТАЛИЗАЦИИ РАСХОДОВ
# ==========================================
tco_table_data = [
    ["Затраты на ГСМ (Топливо)", fmt(total_fuel_before), fmt(savings_by_cat["fuel"]), "Прямой эффект"],
    ["Затраты на ТО и расходники", fmt(total_maint_before), fmt(savings_by_cat["maint"]), "Прямой эффект"],
    ["Прямой ущерб от аварий / франшизы", fmt(total_direct_accident_damage_before / 12), fmt(savings_by_cat["acc_direct"]), "Прямой эффект"],
    ["Затраты на страхование (КАСКО и ОСАГО)", fmt(total_insurance_before), fmt(savings_by_cat["insurance"]), "Прямой эффект"],
    ["Потери от простоя персонала и ТС при ДТП", fmt((total_tco_accident_damage_before - total_direct_accident_damage_before) / 12), fmt(savings_by_cat["acc_tco"] if is_tco else 0), "Косвенный (TCO)"],
    ["Расходы на собственный штат диспетчеров (ФОТ)", fmt(total_disp_fot_before), fmt(savings_by_cat["disp"] if is_tco else 0), "Косвенный (TCO)"],
    ["Администрирование и оплата штрафов бэк-офисом", fmt(total_fines_loss_before), fmt(savings_by_cat["fines"] if is_tco else 0), "Косвенный (TCO)"]
]

df_tco = pd.DataFrame(tco_table_data, columns=["Фактор / Статья расходов", f"Базовые затраты до внедрения ({curr_symbol}/мес)", f"Прогноз экономии от SKAI ({curr_symbol}/мес)", "Тип фактора"])
st.dataframe(df_tco, use_container_width=True, hide_index=True)

st.markdown("---")

# ==========================================
# ГРАФИКИ ОКУПАЕМОСТИ И ЧИСТОГО ЭФФЕКТА ПО ПРОДУКТАМ
# ==========================================
st.subheader(f"Динамика окупаемости и чистый эффект по продуктам ({mode_title})")

months = np.arange(0, 37)
chart_rows = []
total_savings_by_module = {}

for m in months:
    for module_name, metrics in modules_payload.items():
        if m == 0:
            accumulated_net_effect = -metrics["capex"]
        else:
            m_saving = metrics["direct"] + (metrics["tco"] if is_tco else 0)
            accumulated_net_effect = (m_saving - metrics["opex"]) * m - metrics["capex"]
        
        chart_rows.append({
            "Месяц": m,
            "Продукт": module_name,
            "Чистый финансовый эффект": accumulated_net_effect
        })
        
        if m == 36:
            total_savings_by_module[module_name] = max(0.0, accumulated_net_effect)

df_chart = pd.DataFrame(chart_rows)

chart_col1, chart_col2 = st.columns([2, 1])
with chart_col1:
    fig_line = px.line(
        df_chart, 
        x="Месяц", 
        y="Чистый финансовый эффект", 
        color="Продукт", 
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig_line.add_hline(y=0, line_dash="dash", line_color="#FF4B4B", annotation_text="Точка окупаемости", annotation_position="bottom right")
    fig_line.update_layout(
        margin=dict(l=10, r=10, t=10, b=10), 
        xaxis_title="Месяц", 
        yaxis_title=f"Чистый финансовый эффект ({curr_symbol})", 
        hovermode="x unified"
    )
    st.plotly_chart(fig_line, use_container_width=True)
    
with chart_col2:
    if sum(total_savings_by_module.values()) > 0:
        df_pie = pd.DataFrame([{"Продукт": k, "Чистая ценность (36 мес)": v} for k, v in total_savings_by_module.items()])
        fig_pie = px.pie(
            df_pie, 
            values="Чистая ценность (36 мес)", 
            names="Продукт", 
            hole=0.4, 
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_pie.update_layout(margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("К 36-му месяцу продукты еще не вышли в чистую прибыль для отображения долей на диаграмме.")

# ==========================================
# 7. ПОДРОБНЫЙ ГРАФИК ОКУПАЕМОСТИ ПО МЕСЯЦАМ
# ==========================================
st.markdown("---")
st.subheader("Подробный график окупаемости проекта (моделирование по месяцам)")
st.markdown("Таблица отражает накопленные затраты (капитальные и операционные) в сопоставлении с валовой накопленной экономией и чистым финансовым эффектом.")

col_month = "Месяц"
col_costs = f"Затраты накопленные ({curr_symbol})"
col_savings = f"Экономия ({curr_symbol})"
col_effect = f"Эффект ({curr_symbol})"

payback_rows = []
for m in months:
    cum_costs = total_capex + (total_opex_monthly * m)
    cum_savings = total_monthly_saving * m
    net_effect = cum_savings - cum_costs
    
    payback_rows.append({
        col_month: int(m),
        col_costs: cum_costs,
        col_savings: cum_savings,
        col_effect: net_effect
    })

df_payback = pd.DataFrame(payback_rows)

styled_payback = df_payback.style.format({
    col_month: lambda x: f"{int(x)}",
    col_costs: lambda x: f"{int(x):,}".replace(",", " "),
    col_savings: lambda x: f"{int(x):,}".replace(",", " "),
    col_effect: lambda x: f"{int(x):,}".replace(",", " ")
}).bar(
    subset=[col_effect],
    align='mid',
    vmin=-df_payback[col_effect].abs().max(),
    vmax=df_payback[col_effect].abs().max(),
    color=['#FF4B4B', '#00CC96']
).hide(axis='index')

custom_css = """
<style>
    .table-container {
        overflow-x: auto;
        margin: 15px 0;
    }
    .styled-table {
        border-collapse: collapse;
        font-family: sans-serif;
        font-size: 14px;
    }
    .styled-table th {
        background-color: #f0f2f6;
        color: #31333F;
        text-align: left;
        padding: 10px 14px;
        border: 1px solid #dddddd;
        font-weight: 600;
    }
    .styled-table td {
        padding: 8px 14px;
        border: 1px solid #dddddd;
        text-align: left;
    }
    .styled-table tr:nth-child(even) {
        background-color: #f9f9f9;
    }
</style>
"""

html_table = styled_payback.to_html(classes="styled-table")
st.markdown(f"{custom_css}<div class='table-container'>{html_table}</div>", unsafe_allow_html=True)

# ==========================================
# 8. МЕТОДОЛОГИЯ И МАТЕМАТИЧЕСКИЙ АППАРАТ РАСЧЕТА
# ==========================================
st.markdown("---")
with st.expander("Методология и математический аппарат расчетов", expanded=False):
    st.markdown(r"""
    ### 1. Расчет базовых ежемесячных затрат автопарка (до внедрения SKAI)
    
    * **Затраты на ГСМ (Топливо):** Вычисляются на основе годового пробега, нормативного расхода на 100 км и текущей стоимости топлива:  
        $$З_{ГСМ} = \sum \left( \frac{\text{Пробег}_{ТС} \times \text{Расход}_{ТС} \times \text{Цена топлива}}{100 \times 12} \right) \times \text{Кол-во ТС}$$
    
    * **Затраты на ТО и расходники:** $$З_{ТО} = \sum \left( \frac{\text{Стоимость ТО в год}}{12} \right) \times \text{Кол-во ТС}$$
    
    * **Прямой ущерб от ДТП:** Учитывает только прямые физические повреждения или затраты на страховую франшизу:  
        $$У_{прямой} = \sum \left( \frac{\text{Кол-во ДТП в год} \times \text{Стоимость 1 ДТП}}{12} \right)$$
        
    * **Затраты на страхование (КАСКО и ОСАГО):** $$З_{страх} = \sum \left( \frac{\text{Полис на 1 ТС в год}}{12} \right) \times \text{Кол-во ТС}$$
        
    * **Скрытые потери TCO от простоя при ДТП:** Включают в себя ФОТ водителя за время простоя, прямые суточные потери от неработающего ТС (упущенная маржа/подменное авто) и трудозатраты бэк-офиса на разбор инцидента:  
        $$Потери_{простой} = \frac{\text{Кол-во ДТП в год} \times \left( Дней_{простоя} \times (\text{ФОТ}_{водителя/день} + \text{Потери}_{простоя/день}) + Часы_{бэк-офиса} \times Ставка_{часа} \right)}{12}$$
        
    * **Администрирование и оплата штрафов:** Учитывает как сумму платежа, так и трудозатраты специалистов на обработку каждого постановления:  
        $$Потери_{штрафы} = \frac{\text{Штрафов на ТС в год} \times \left( Цена_{штрафа} + Время_{обработки} \times Ставка_{часа} \right)}{12} \times Всего_{ТС}$$

    ### 2. Принцип разграничения эффектов продуктов и синергия систем безопасности
    
    * **Базовый Мониторинг:** Направлен исключительно на ликвидацию прямых эксплуатационных потерь (устранение нецелевого пробега, контроль регламента ТО и скоростных лимитов для снижения штрафов). Не заявляет эффект предотвращения аварий.
    * **Видеоаналитика и Безопасное вождение:** Активные комплексы предотвращения ДТП. Их совокупная надежность рассчитывается по формуле совместных независимых вероятностей, исключающей математическое задвоение:
    $$E_{дтп} = 1 - (1 - E_{видео}) \times (1 - E_{скоринг})$$
    * **Страховой дисконт:** Скидка при ежегодной пролонгации парковых договоров КАСКО/ОСАГО признается страховыми андеррайтерами и закреплена исключительно за оснащением автопарка Видеоаналитикой.

    ### 3. Расчет удельной стоимости риска ДТП на 100 км пути
    
    Отражает удельную аварийную нагрузку на логистическое плечо автопарка:
    $$Риск_{100км} = \frac{\text{Ежемесячный ущерб от ДТП (прямой или полный TCO)}}{\text{Совокупный месячный пробег автопарка (км)}} \times 100$$
    
    ### 4. Расчет ключевых инвестиционных показателей проекта
    
    * **Стартовые инвестиции (Капитальные вложения):** Сумма затрат на покупку оборудования, монтаж или аудит и адаптацию существующего парка:  
        $$Кап.вложения = \sum (Стоимость_{модуля} \times Всего_{ТС})$$
        
    * **Операционные расходы (в месяц):** Сумма ежемесячной абонентской платы за программное обеспечение и сервисы:  
        $$Опер.расходы_{мес} = \sum (Абон.плата_{модуля} \times Всего_{ТС})$$
        
    * **Валовая экономия в месяц:** Совокупный объем сокращенных издержек:  
        $$Экономия_{валовая} = \sum Экономия_{ГСМ} + \sum Экономия_{ТО} + \sum Экономия_{ДТП} + \sum Экономия_{страхование} + \dots$$
        
    * **Чистая экономия в месяц:** $$Экономия_{чистая} = Экономия_{валовая} - Опер.расходы_{мес}$$
        
    * **Срок окупаемости проекта (Payback Period):**  
        $$Срок_{окупаемости} = \frac{\text{Капитальные вложения (Стартовые инвестиции)}}{\text{Чистая экономия в месяц}}$$
    """)

# ==========================================
# 9. ОБОСНОВАНИЕ ПОКАЗАТЕЛЕЙ ДЛЯ РАСЧЕТА
# ==========================================
st.markdown("---")
with st.expander("Обоснование показателей эффективности и источники данных", expanded=False):
    st.markdown("""
    ### Базовый мониторинг
    * **Сокращение пробега и ГСМ (%):**
        * **Источник:** Эксплуатационная статистика внедрений SKAI. Для магистральных перевозок потенциал исключения съездов с маршрута составляет 5–7%, для тяжелой техники — 8–10%, для городского развоза — 12–15%. При наличии ранее установленного GPS эффект составляет 3–6% за счет нормализации одометра и диспетчеризации.
        * **Влияние на расчет:** Мультипликатор применяется напрямую к ежемесячной статье «Затраты на ГСМ (Топливо)».
    * **Сокращение износа и ТО (%):**
        * **Источник:** Методология SKAI. Исключение перепробегов пропорционально отдаляет плановые ТО, давая экономию 3–5% бюджета на обслуживание.
        * **Влияние на расчет:** Снижает статью «Затраты на ТО и расходники».
    * **Сокращение штрафов (%):**
        * **Источник:** Статистика диспетчеризации SKAI. Контроль превышений скоростных порогов через телематику снижает штрафы на 20–40%.
        * **Влияние на расчет:** Сокращает объем прямых штрафов и трудозатраты бэк-офиса на их оплату.
    * **Затраты перехода при наличии GPS:**
        * **Источник:** Регламент сервисной службы SKAI. Перевод существующего парка требует инспекции проводки, замены SIM-карт, перепрошивки трекеров и интеграции с ПО, что формирует реальный CAPEX в размере 2 500 руб./ТС.

    ### Издержки при ДТП и простои персонала
    * **Потери от 1 дня простоя ТС:**
        * **Источник:** Практика автотранспортных предприятий. Учитывает среднесуточную чистую прибыль (маржу) ТС, которая теряется из-за срыва рейсов во время нахождения машины на кузовном ремонте, либо стоимость суточной аренды подменного автомобиля схожего класса.
        * **Влияние на расчет:** Входит в скрытые потери TCO от простоя техники при ДТП.
    * **Себестоимость часа работы бэк-офиса:**
        * **Источник:** Автоматический расчет на основе фонда оплаты труда диспетчерского центра из расчета 168 рабочих часов в месяц. Отражает трудозатраты инженера по БДД, юриста и бухгалтера на администрирование последствий ДТП (8 часов) и оформление штрафов (30 минут).
        * **Влияние на расчет:** Формирует косвенную TCO-нагрузку от инцидентов.

    ### Видеоаналитика
    * **Снижение аварийности со SKAI (%):**
        * **Источник:** Аналитическая база данных SKAI (выборка 1 000 ТС, 120 млн км пробега). Предотвращение критических засыпаний, отвлечений на смартфон и опасных сближений снижает аварийность на 80%, снижая удельную стоимость риска ДТП со 129 до 84 руб./100 км.
        * **Влияние на расчет:** Сокращает прямые затраты на ремонт/франшизы, исключает потери от простоев техники и персонала, а также дает эксклюзивное право на скидку по автострахованию.
    * **Скидка на КАСКО и ОСАГО (%):**
        * **Источник:** Требования андеррайтинга страховых компаний. Наличие видеофиксации дорожной обстановки и действий водителя снижает показатель Loss Ratio парка и дает гарантированный дисконт 15–25% при ежегодной пролонгации полисов.

    ### Безопасное вождение
    * **Снижение аварийности от скоринга (%):**
        * **Источник:** Подтвержденный кейс внедрения SKAI в FMCG-холдинге (более 6 000 ТС). Переход 98,8% водителей в зеленую зону аккуратной езды сократил число любых ДТП на 1 млн км пробега в 4 раза (-75%).
        * **Влияние на расчет:** Формирует мультипликатор снижения аварийности совместно с Видеоаналитикой.
    * **Снижение расхода топлива от стиля езды (%):**
        * **Источник:** Кейс внедрения FMCG (>6 000 ТС). Устранение резких ускорений, торможений и поддержание оптимального режима оборотов двигателя снижает расход топлива на 10%.
        * **Влияние на расчет:** Дополнительно снижает статью затрат на ГСМ поверх эффекта исключения перепробегов.
    * **Экономия на ТО от бережной езды (%):**
        * **Источник:** Данные телематики SKAI. Плавное вождение продлевает ресурс тормозных колодок, резины и элементов подвески на 15–20%.
        * **Влияние на расчет:** Снижает статью затрат на ТО и расходники.

    ### Сервис реагирования и аналитики
    * **Сокращение затрат на ФОТ диспетчеров (%):**
        * **Источник:** Практика ситуационного центра SKAI. Автоматический разбор событий и круглосуточная поддержка позволяют оптимизировать штат диспетчеров парка на 60%.
        * **Влияние на расчет:** Снижает TCO-статью расходов на собственный диспетчерский персонал.

    ### Контроль топлива
    * **Прямая экономия ГСМ (сливы/карты) (%):**
        * **Источник:** Практика интеграции цифровых ДУТ и сверки с транзакциями АЗС. Пресечение сливов и махинаций сохраняет от 8% до 12% топлива.
        * **Влияние на расчет:** Напрямую уменьшает базовые затраты на ГСМ независимо от пробега.
    """)