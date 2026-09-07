import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Настройка страницы в строгом B2B стиле
st.set_page_config(page_title="Платформа SKAI: Калькулятор TCO и ROI", layout="wide")

# ==========================================
# 1. БАЗА ДАННЫХ ПРЕСЕТОВ (БАЗОВЫЕ ЗНАЧЕНИЯ В РУБЛЯХ)
# ==========================================
presets = {
    "Магистральный тягач (Фура)": {
        "fleet_size": 50, "mileage": 120000, "consumption": 32.0, "maintenance": 60000,
        "accidents_year": 8, "accident_cost": 1550000, "insurance_cost": 95000,
        "video_capex": 120000, "video_opex": 2000, "video_eff": 80,
        "base_capex": 15000, "base_opex": 400, "base_eff_fuel": 22.0, "base_eff_to": 6.0, "base_eff_fines": 40, "base_eff_acc": 15,
        "safe_capex": 10000, "safe_opex": 500, "safe_eff_fuel": 10.0, "safe_eff_to": 15, "safe_eff_acc": 75,
        "fuel_capex": 25000, "fuel_opex": 600, "fuel_eff": 10
    },
    "Самосвал / Тяжелая спецтехника": {
        "fleet_size": 30, "mileage": 45000, "consumption": 45.0, "maintenance": 90000,
        "accidents_year": 6, "accident_cost": 1200000, "insurance_cost": 85000,
        "video_capex": 130000, "video_opex": 2000, "video_eff": 80,
        "base_capex": 15000, "base_opex": 400, "base_eff_fuel": 22.0, "base_eff_to": 6.0, "base_eff_fines": 30, "base_eff_acc": 10,
        "safe_capex": 10000, "safe_opex": 500, "safe_eff_fuel": 10.0, "safe_eff_to": 20, "safe_eff_acc": 75,
        "fuel_capex": 30000, "fuel_opex": 600, "fuel_eff": 12
    },
    "Легкий коммерческий транспорт / Корпоративные авто": {
        "fleet_size": 40, "mileage": 60000, "consumption": 13.0, "maintenance": 35000,
        "accidents_year": 7, "accident_cost": 650000, "insurance_cost": 45000,
        "video_capex": 110000, "video_opex": 1800, "video_eff": 80,
        "base_capex": 12000, "base_opex": 350, "base_eff_fuel": 22.0, "base_eff_to": 6.0, "base_eff_fines": 60, "base_eff_acc": 20,
        "safe_capex": 8000, "safe_opex": 400, "safe_eff_fuel": 10.0, "safe_eff_to": 12, "safe_eff_acc": 75,
        "fuel_capex": 20000, "fuel_opex": 500, "fuel_eff": 8
    }
}

monetary_keys = [
    "fuel_price", "emp_salary", "emp_revenue", "disp_salary", 
    "manager_hourly_rate", "fine_avg_cost", "s_cap", "s_op",
    "b_cap", "b_op", "v_cap", "v_op", "sd_cap", "sd_op", "f_cap", "f_op"
]
for name in presets.keys():
    monetary_keys.extend([f"maint_{name}", f"acost_{name}", f"ins_{name}"])

# ==========================================
# 2. ИНИЦИАЛИЗАЦИЯ И КОНВЕРТАЦИЯ СОСТОЯНИЯ (SESSION STATE)
# ==========================================
# Безопасная инициализация: ключи создаются, только если их еще нет в текущей сессии
st.session_state.setdefault("initialized", True)
st.session_state.setdefault("prev_currency", "₽ (RUB)")
st.session_state.setdefault("fuel_price", 65.0)
st.session_state.setdefault("emp_salary", 100000)
st.session_state.setdefault("emp_revenue", 1200000)
st.session_state.setdefault("disp_salary", 80000)
st.session_state.setdefault("manager_hourly_rate", 500)
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
    qty = st.sidebar.number_input(f"{name} (шт):", min_value=0, value=default_qtys[name], step=5)
    
    if qty > 0:
        fleet_quantities[name] = qty
        default_accidents = p_default["accidents_year"] * (qty / p_default["fleet_size"])
        clean_name = name.split(" (")[0]
        
        with st.sidebar.expander(f"Настройки: {clean_name}", expanded=False):
            mileage = st.number_input("Пробег 1 ТС в год (км)", min_value=1000, value=p_default["mileage"], step=5000, key=f"mil_{name}")
            consumption = st.number_input("Расход (л/100 км)", min_value=1.0, value=p_default["consumption"], step=0.5, key=f"cons_{name}")
            
            st.session_state[f"maint_{name}"] = st.number_input(f"ТО + расходники 1 ТС/год ({curr_symbol})", min_value=0, value=int(st.session_state[f"maint_{name}"]), step=5000)
            accidents = st.number_input("ДТП этой группы в год (шт)", min_value=0.0, value=float(default_accidents), step=0.5, key=f"acc_{name}")
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
    st.session_state["emp_revenue"] = st.number_input(f"Месячный доход от 1 сотрудника на ТС ({curr_symbol})", value=int(st.session_state["emp_revenue"]), step=50000)
    
    st.markdown("**Диспетчеризация и администрирование**")
    st.session_state["disp_salary"] = st.number_input(f"ФОТ 1 диспетчера парка в месяц ({curr_symbol})", value=int(st.session_state["disp_salary"]), step=5000)
    calculated_disp_qty = max(1.0, round(total_fleet_size / 25, 1))
    disp_qty = st.number_input("Текущее кол-во диспетчеров в штате (база)", value=float(calculated_disp_qty), step=0.5)
    
    st.markdown("**Издержки при инцидентах**")
    downtime_days = st.number_input("Средний простой ТС после ДТП (дней)", value=14, step=1)
    st.session_state["manager_hourly_rate"] = st.number_input(f"Стоимость 1 часа работы бэк-офиса ({curr_symbol})", value=int(st.session_state["manager_hourly_rate"]), step=50)
    time_manager_accident = st.number_input("Время менеджера на 1 ДТП (часов)", value=8, step=1)
    
    st.markdown("**Штрафы автопарка**")
    fines_per_car_year = st.number_input("Кол-во штрафов на 1 ТС в год (база)", value=12, step=2)
    st.session_state["fine_avg_cost"] = st.number_input(f"Средняя стоимость 1 штрафа ({curr_symbol})", value=int(st.session_state["fine_avg_cost"]), step=100)
    time_manager_fine = st.number_input("Время на обработку 1 штрафа (часов)", value=0.5, step=0.1)

with st.sidebar.expander("Страхование автопарка (КАСКО и ОСАГО)", expanded=False):
    st.caption("Снижение аварийности уменьшает коэффициент убыточности (Loss Ratio) и стоимость пролонгации полисов")
    insurance_discount = st.slider("Прогноз скидки на КАСКО/ОСАГО при снижении ДТП (%)", 0, 40, 15, step=5) / 100

working_days_month = 21.7
employee_daily_cost = st.session_state["emp_salary"] / working_days_month
employee_daily_revenue = st.session_state["emp_revenue"] / working_days_month

def get_total_accident_cost(direct_cost):
    downtime_loss = downtime_days * (employee_daily_cost + employee_daily_revenue)
    management_loss = time_manager_accident * st.session_state["manager_hourly_rate"]
    return direct_cost + downtime_loss + management_loss

fine_loss_per_car_month = (fines_per_car_year * (st.session_state["fine_avg_cost"] + (time_manager_fine * st.session_state["manager_hourly_rate"]))) / 12
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

# Мультипликаторы снижения аварийности для исключения двойного учета
acc_eff_bm = 0.0
acc_eff_va = 0.0
acc_eff_sd = 0.0

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
        
        default_b_capex = 0 if is_gps_installed else int(15000 * (6.13 if is_kzt else 1.0))
        default_b_fuel = 10.0 if is_gps_installed else 22.0
        default_b_to = 4.0 if is_gps_installed else 6.0
        default_b_fines = 20 if is_gps_installed else 40
        default_b_acc = 10 if is_gps_installed else 15

        b_capex_input = st.number_input(f"Затраты на оснащение/трекер на 1 ТС ({curr_symbol})", min_value=0, value=default_b_capex, step=1000, key=f"b_cap_{is_gps_installed}")
        b_opex_input = st.number_input(f"АП на 1 ТС/мес ({curr_symbol})", value=int(st.session_state["b_op"]), step=50, key="b_op_input")
        
        eff_fuel = st.slider("Сокращение пробега и ГСМ (%)", 0.0, 30.0, float(default_b_fuel), step=0.5, key=f"eff_fuel_{is_gps_installed}") / 100
        eff_to = st.slider("Сокращение износа и ТО (%)", 0.0, 20.0, float(default_b_to), step=0.5, key=f"eff_to_{is_gps_installed}") / 100
        eff_fines = st.slider("Сокращение штрафов (%)", 0, 100, int(default_b_fines), step=5, key=f"eff_fines_{is_gps_installed}") / 100
        eff_acc_bm = st.slider("Сокращение ДТП (геозоны) (%)", 0, 100, int(default_b_acc), step=5, key=f"eff_acc_{is_gps_installed}") / 100
        acc_eff_bm = eff_acc_bm

        b_dir_non_acc = (total_fuel_before * eff_fuel) + (total_maint_before * eff_to)
        b_tco_non_acc = total_fines_loss_before * eff_fines
        
        modules_raw["Базовый Мониторинг"] = {
            "capex": b_capex_input * total_fleet_size, 
            "opex": b_opex_input * total_fleet_size, 
            "direct_base": b_dir_non_acc, 
            "tco_base": b_tco_non_acc,
            "acc_weight": eff_acc_bm
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
    with st.sidebar.expander("Модуль: Видеоаналитика", expanded=False):
        st.session_state["v_cap"] = st.number_input(f"Оборудование на 1 ТС ({curr_symbol})", value=int(st.session_state["v_cap"]), step=5000)
        st.session_state["v_op"] = st.number_input(f"АП на 1 ТС/мес ({curr_symbol})", value=int(st.session_state["v_op"]), step=100)
        
        # Целевой показатель снижения ДТП 80%
        v_eff_acc = st.slider("Снижение аварийности со SKAI (%)", 0, 100, 80, step=5) / 100
        acc_eff_va = v_eff_acc
        
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
        acc_eff_sd = sd_eff_acc
        
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
# Мультипликативный расчет предотвращения ДТП
combined_no_accident_prob = (1.0 - acc_eff_bm) * (1.0 - acc_eff_va) * (1.0 - acc_eff_sd)
total_combined_acc_eff = 1.0 - combined_no_accident_prob

total_direct_acc_saving = (total_direct_accident_damage_before / 12) * total_combined_acc_eff
total_tco_acc_saving = ((total_tco_accident_damage_before - total_direct_accident_damage_before) / 12) * total_combined_acc_eff

savings_by_cat["acc_direct"] = total_direct_acc_saving
savings_by_cat["acc_tco"] = total_tco_acc_saving

# Экономия на КАСКО и ОСАГО при снижении аварийности
has_safety_system = ("Видеоаналитика" in selected_modules or "Безопасное вождение" in selected_modules)
total_ins_saving = (total_insurance_before * insurance_discount) if has_safety_system else 0.0
savings_by_cat["insurance"] = total_ins_saving

# Распределение синергетической экономии по модулям пропорционально их вкладу
sum_acc_weights = sum(m["acc_weight"] for m in modules_raw.values())
modules_payload = {}

for m_name, m_data in modules_raw.items():
    if sum_acc_weights > 0 and m_data["acc_weight"] > 0:
        weight_ratio = m_data["acc_weight"] / sum_acc_weights
        m_dir_acc = total_direct_acc_saving * weight_ratio
        m_tco_acc = total_tco_acc_saving * weight_ratio
        m_ins = total_ins_saving * weight_ratio
    else:
        m_dir_acc, m_tco_acc, m_ins = 0.0, 0.0, 0.0
        
    modules_payload[m_name] = {
        "capex": m_data["capex"],
        "opex": m_data["opex"],
        "direct": m_data["direct_base"] + m_dir_acc + m_ins,
        "tco": m_data["tco_base"] + m_tco_acc
    }

# ==========================================
# 6. РЕНДЕРИНГ ИНТЕРФЕЙСА И РАСЧЕТ МЕТРИК
# ==========================================
st.title("Платформа SKAI: Расширенный калькулятор TCO и ROI")

fleet_str = " + ".join([f"**{qty}** {name.split(' (')[0]}" for name, qty in fleet_quantities.items()])
st.markdown(f"Структура парка: {fleet_str} | Всего: **{total_fleet_size} ТС**")
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
rc1.metric("Стоимость риска ДТП до внедрения", f"{risk_per_100km_before:.1f} {curr_symbol} / 100 км")
rc2.metric("Стоимость риска ДТП со SKAI", f"{risk_per_100km_after:.1f} {curr_symbol} / 100 км")
rc3.metric("Чистая экономия на 100 км пути", f"{risk_saving_per_100km:.1f} {curr_symbol} / 100 км", delta=f"-{total_combined_acc_eff*100:.0f}% к риску")

st.markdown("---")

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
        
    * **Скрытые потери TCO от простоя при ДТП:** Включают в себя ФОТ водителя за время простоя, упущенную выгоду (доход от ТС) и административные часы бэк-офиса на разбор инцидента:  
        $$Потери_{простой} = \frac{\text{Кол-во ДТП в год} \times \left( Дней_{простоя} \times (Стоимость_{водителя/день} + Доход_{ТС/день}) + Часы_{менеджера} \times Ставка_{менеджера} \right)}{12}$$
        
    * **Администрирование и оплата штрафов:** $$Потери_{штрафы} = \frac{\text{Штрафов на ТС в год} \times \left( Цена_{штрафа} + Время_{оформления} \times Ставка_{менеджера} \right)}{12} \times Всего_{ТС}$$

    ### 2. Мультипликативная модель предотвращения аварийности (Исключение двойного счета)
    
    При одновременном внедрении нескольких систем безопасности (видеоконтроль засыпания, скоринг стиля езды и контроль геозон) суммировать проценты напрямую некорректно. В калькуляторе применяется формула совместной надежности:
    $$E_{дтп} = 1 - (1 - E_{видео}) \times (1 - E_{скоринг}) \times (1 - E_{геозоны})$$
    
    ### 3. Расчет удельной стоимости риска ДТП на 100 км пути
    
    Показатель отражает аварийную нагрузку на каждый километр логистического плеча:
    $$Риск_{100км} = \frac{\text{Ежемесячный ущерб от ДТП (прямой или полный TCO)}}{\text{Совокупный месячный пробег автопарка (км)}} \times 100$$
    
    ### 4. Расчет ключевых инвестиционных показателей проекта
    
    * **Стартовые инвестиции (Капитальные вложения):** Сумма единовременных затрат на покупку и установку оборудования для всех ТС автопарка:  
        $$Кап.вложения = \sum (Стоимость_{модуля} \times Всего_{ТС})$$
        
    * **Операционные расходы (в месяц):** Сумма ежемесячной абонентской платы за программное обеспечение и сопутствующие сервисы:  
        $$Опер.расходы_{мес} = \sum (Абон.плата_{модуля} \times Всего_{ТС})$$
        
    * **Валовая экономия в месяц:** Сумма всех сокращенных статей затрат (включая или исключая косвенный TCO эффект в зависимости от выбранного режима):  
        $$Экономия_{валовая} = \sum Экономия_{ГСМ} + \sum Экономия_{ТО} + \sum Экономия_{ДТП} + \sum Экономия_{страхование} + \dots$$
        
    * **Чистая экономия в месяц:** $$Экономия_{чистая} = Экономия_{валовая} - Опер.расходы_{мес}$$
        
    * **Срок окупаемости проекта (Payback Period):** Период времени, за который чистый экономический эффект полностью покрывает первоначальные инвестиции:  
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
        * **Источник:** Методология внедрения SKAI при максимальном сценарии использования (подключение CAN-шины и аналитического отчета «Поездки водителей»)[cite: 2]. Для неоснащенных парков экономия достигает 15–22% за счет полного исключения нецелевых рейсов, приписок и оптимизации холостого хода[cite: 2]. Для парков с уже установленным сторонним GPS максимальный эффект составляет 7–10% за счет исключения завышений одометра и перевода контроля на платформу SKAI[cite: 2].
        * **Влияние на расчет:** Мультипликатор применяется напрямую к ежемесячной статье «Затраты на ГСМ (Топливо)».
    * **Сокращение износа и ТО (%):**
        * **Источник:** Методология внедрения SKAI[cite: 2]. Ликвидация перепробегов и снижения моточасов холостого хода отодвигает межсервисные интервалы. Максимальный эффект составляет 4–6% для новых парков и 3–4% для парков с существующим GPS[cite: 2].
        * **Влияние на расчет:** Снижает статью «Затраты на ТО и расходники».
    * **Сокращение штрафов (%):**
        * **Источник:** Статистика диспетчеризации SKAI. Контроль скоростного порога ТС и уведомления диспетчерам снижают объемы дорожных штрафов на 20–40%.
        * **Влияние на расчет:** Сокращает объем прямых штрафов и трудозатраты бэк-офиса на их администрирование в TCO-модели.
    * **Сокращение ДТП (геозоны) (%):**
        * **Источник:** Отраслевая аналитика телематических систем. Контроль опасных участков, съездов и скоростных лимитов в геозонах предотвращает 10–15% инцидентов.
        * **Влияние на расчет:** Снижает базовые риски аварийности в синергетической формуле безопасности.

    ### Видеоаналитика
    * **Снижение аварийности со SKAI (%):**
        * **Источник:** Аналитическая база данных SKAI. На выборке в 1 000 ТС с общим пробегом 120 млн км подтверждено снижение частоты и тяжести ДТП (системы контроля усталости, отвлечения на телефон, соблюдения дистанции) со снижением стоимости риска ДТП со 129 до 84 руб. на каждые 100 км пути (чистая экономия 45 руб./100 км). При целевой настройке чувствительности алгоритмов снижение инцидентов достигает 80%.
        * **Влияние на расчет:** Сокращает прямой ущерб от аварий, дни простоя техники/персонала и является основанием для скидки по парковому страхованию.

    ### Безопасное вождение
    * **Снижение аварийности от скоринга (%):**
        * **Источник:** Подтвержденный кейс внедрения SKAI в FMCG-холдинге (автопарк более 6 000 ТС, 6 стран СНГ). За счет перехода 98,8% водителей в зеленую зону скоринга общее число ДТП на 1 млн км сократилось в 4 раза (снижение на 75%), а ДТП с пострадавшими — в 12 раз.
        * **Влияние на расчет:** Входит в мультипликатор снижения аварийности парка.
    * **Снижение расхода топлива от стиля езды (%):**
        * **Источник:** Кейс внедрения SKAI в FMCG-холдинге (>6 000 ТС). Исключение резких разгонов, торможений и поддержание оптимального режима оборотов двигателя снизило средний расход топлива парка на 10%.
        * **Влияние на расчет:** Увеличивает суммарный процент экономии топлива по статье «Затраты на ГСМ».
    * **Экономия на ТО от бережной езды (%):**
        * **Источник:** Эксплуатационная статистика SKAI. Снижение динамических ударных нагрузок продлевает ресурс тормозных колодок, резины и подвески на 15–20%.
        * **Влияние на расчет:** Снижает расходы по статье «Затраты на ТО и расходники».

    ### Страхование (КАСКО и ОСАГО)
    * **Скидка на страховые полисы при пролонгации (%):**
        * **Источник:** Практика андеррайтинга страховых компаний при работе с телематикой. Снижение коэффициента убыточности (Loss Ratio) парка позволяет зафиксировать скидку 15–25% на страхование парка при наличии активных систем безопасности (Видеоаналитика / Безопасное вождение).
        * **Влияние на расчет:** Уменьшает прямую статью расходов «Затраты на страхование (КАСКО и ОСАГО)».

    ### Сервис реагирования и аналитики
    * **Сокращение затрат на ФОТ диспетчеров (%):**
        * **Источник:** Статистика диспетчерского центра SKAI. Аутсорсинг первичного мониторинга, автоматическая эскалация критических событий и интеграции позволяют оптимизировать штат собственных операторов парка на 60%.
        * **Влияние на расчет:** Снижает TCO-статью «Расходы на собственный штат диспетчеров (ФОТ)».

    ### Контроль топлива
    * **Прямая экономия ГСМ (сливы/карты) (%):**
        * **Источник:** Статистика внедрений высокоточных цифровых датчиков уровня топлива (ДУТ) и сверок с транзакциями топливных карт. Ликвидирует физические сливы и махинации с чеками на 8–12%.
        * **Влияние на расчет:** Напрямую уменьшает статью ежемесячных базовых затрат на ГСМ независимо от пробега.
    """)