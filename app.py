import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Настройка страницы в строгом B2B стиле
st.set_page_config(page_title="Платформа SKAI: Расширенный калькулятор TCO и ROI", layout="wide")

# ==========================================
# 1. БАЗА ДАННЫХ ПРЕСЕТОВ (БАЗОВЫЕ ЗНАЧЕНИЯ В РУБЛЯХ)
# ==========================================
presets = {
    "Магистральный тягач (Фура)": {
        "fleet_size": 50, "mileage": 120000, "consumption": 32.0, "maintenance": 60000,
        "accidents_year": 8, "accident_cost": 800000,
        "video_capex": 120000, "video_opex": 2000, "video_eff": 55,
        "base_capex": 15000, "base_opex": 400, "base_eff_fuel": 8, "base_eff_to": 10, "base_eff_fines": 40, "base_eff_lease": 20, "base_eff_acc": 15,
        "safe_capex": 10000, "safe_opex": 500, "safe_eff_to": 15, "safe_eff_acc": 15,
        "fuel_capex": 25000, "fuel_opex": 600, "fuel_eff": 10
    },
    "Самосвал / Тяжелая спецтехника": {
        "fleet_size": 30, "mileage": 45000, "consumption": 45.0, "maintenance": 90000,
        "accidents_year": 6, "accident_cost": 600000,
        "video_capex": 130000, "video_opex": 2000, "video_eff": 50,
        "base_capex": 15000, "base_opex": 400, "base_eff_fuel": 6, "base_eff_to": 8, "base_eff_fines": 30, "base_eff_lease": 15, "base_eff_acc": 10,
        "safe_capex": 10000, "safe_opex": 500, "safe_eff_to": 20, "safe_eff_acc": 10,
        "fuel_capex": 30000, "fuel_opex": 600, "fuel_eff": 12
    },
    "Легкий коммерческий транспорт / Корпоративные авто": {
        "fleet_size": 40, "mileage": 60000, "consumption": 13.0, "maintenance": 35000,
        "accidents_year": 7, "accident_cost": 300000,
        "video_capex": 110000, "video_opex": 1800, "video_eff": 60,
        "base_capex": 12000, "base_opex": 350, "base_eff_fuel": 10, "base_eff_to": 12, "base_eff_fines": 60, "base_eff_lease": 30, "base_eff_acc": 20,
        "safe_capex": 8000, "safe_opex": 400, "safe_eff_to": 12, "safe_eff_acc": 20,
        "fuel_capex": 20000, "fuel_opex": 500, "fuel_eff": 8
    }
}

# Иконки для типов транспортных средств
fleet_icons = {
    "Магистральный тягач (Фура)": "🚛",
    "Самосвал / Тяжелая спецтехника": "🏗️",
    "Легкий коммерческий транспорт / Корпоративные авто": "🚐"
}

# Сбор списка всех финансовых ключей для умной конвертации валют
monetary_keys = [
    "fuel_price", "emp_salary", "emp_revenue", "disp_salary", 
    "manager_hourly_rate", "lease_return_cost", "fine_avg_cost", "s_cap", "s_op",
    "b_cap", "b_op", "v_cap", "v_op", "sd_cap", "sd_op", "f_cap", "f_op"
]
for name in presets.keys():
    monetary_keys.extend([f"maint_{name}", f"acost_{name}"])

# ==========================================
# 2. ИНИЦИАЛИЗАЦИЯ И КОНВЕРТАЦИЯ СОСТОЯНИЯ (SESSION STATE)
# ==========================================
if "initialized" not in st.session_state:
    st.session_state["initialized"] = True
    st.session_state["prev_currency"] = "₽ (RUB)"
    st.session_state["fuel_price"] = 65.0
    st.session_state["emp_salary"] = 100000
    st.session_state["emp_revenue"] = 1200000
    st.session_state["disp_salary"] = 80000
    st.session_state["manager_hourly_rate"] = 500
    st.session_state["lease_return_cost"] = 50000
    st.session_state["fine_avg_cost"] = 500
    st.session_state["s_cap"] = 40000
    st.session_state["s_op"] = 900
    
    for name, p_default in presets.items():
        st.session_state[f"maint_{name}"] = p_default["maintenance"]
        st.session_state[f"acost_{name}"] = p_default["accident_cost"]
        
    st.session_state["b_cap"] = 15000
    st.session_state["b_op"] = 400
    st.session_state["v_cap"] = 120000
    st.session_state["v_op"] = 2000
    st.session_state["sd_cap"] = 10000
    st.session_state["sd_op"] = 500
    st.session_state["f_cap"] = 25000
    st.session_state["f_op"] = 600

def fmt(val):
    return f"{val:,.0f}".replace(",", " ")

# ==========================================
# 3. СЕКЦИЯ САЙДБАРА: ПАРАМЕТРЫ И СТРУКТУРА ПАРКА
# ==========================================
st.sidebar.header("Параметры и конфигурация")

currency_choice = st.sidebar.radio("Валюта расчетов:", ["₽ (RUB)", "₸ (KZT)"], horizontal=True)
is_kzt = "KZT" in currency_choice
curr_symbol = "₸" if is_kzt else "₽"

# Пересчет значений ВНУТРИ сессии ТОЛЬКО при физическом переключении радио-кнопки
if currency_choice != st.session_state["prev_currency"]:
    factor = 6.13 if is_kzt else (1 / 6.13)
    for k in monetary_keys:
        if k in st.session_state:
            if k == "fuel_price":
                st.session_state[k] = round(st.session_state[k] * factor, 1)
            else:
                st.session_state[k] = round(st.session_state[k] * factor)
    st.session_state["prev_currency"] = currency_choice

# Цена топлива в блоке основной конфигурации
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
    icon = fleet_icons.get(name, "🚗")
    qty = st.sidebar.number_input(f"{icon} {name} (шт):", min_value=0, value=default_qtys[name], step=5)
    
    if qty > 0:
        fleet_quantities[name] = qty
        default_accidents = p_default["accidents_year"] * (qty / p_default["fleet_size"])
        clean_name = name.split(" (")[0]
        
        with st.sidebar.expander(f"⚙️ Настройки: {clean_name}", expanded=False):
            mileage = st.number_input("Пробег 1 ТС в год (км)", min_value=1000, value=p_default["mileage"], step=5000, key=f"mil_{name}")
            consumption = st.number_input("Расход (л/100 км)", min_value=1.0, value=p_default["consumption"], step=0.5, key=f"cons_{name}")
            
            st.session_state[f"maint_{name}"] = st.number_input(f"ТО + расходники 1 ТС/год ({curr_symbol})", min_value=0, value=int(st.session_state[f"maint_{name}"]), step=5000)
            accidents = st.number_input("ДТП этой группы в год (шт)", min_value=0.0, value=float(default_accidents), step=0.5, key=f"acc_{name}")
            st.session_state[f"acost_{name}"] = st.number_input(f"Ущерб/франшиза 1 ДТП ({curr_symbol})", min_value=0, value=int(st.session_state[f"acost_{name}"]), step=50000)
        
        custom_fleet_params[name] = {
            "qty": qty, "mileage": mileage, "consumption": consumption, 
            "maintenance": st.session_state[f"maint_{name}"],
            "accidents_year": accidents, "accident_cost": st.session_state[f"acost_{name}"],
            **{k: v for k, v in p_default.items() if "eff" in k}
        }

total_fleet_size = sum(fleet_quantities.values())
if total_fleet_size == 0:
    st.sidebar.warning("Укажите количество хотя бы для одного типа ТС.")
    st.stop()

# ==========================================
# 4. СЕКЦИЯ САЙДБАРА: УПРАВЛЕНИЕ TCO И ПЕРСОНАЛОМ
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader("Управление TCO, персоналом и лизингом")

with st.sidebar.expander("👤 Потери бэк-офиса, простои и лизинг", expanded=False):
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
    
    st.markdown("**Условия владения и штрафы**")
    lease_share = st.slider("Доля лизинговых ТС в парке (%)", min_value=0, max_value=100, value=60, step=5)
    
    if lease_share > 0:
        lease_term = st.number_input("Стандартный срок лизинга (мес)", min_value=1, value=48, step=12)
        st.session_state["lease_return_cost"] = st.number_input(f"Выплаты лизинговой при возврате (на 1 ТС, {curr_symbol})", value=int(st.session_state["lease_return_cost"]), step=5000)
    else:
        lease_term, st.session_state["lease_return_cost"] = 48, 0

    fines_per_car_year = st.number_input("Кол-во штрафов на 1 ТС в год (база)", value=12, step=2)
    st.session_state["fine_avg_cost"] = st.number_input(f"Средняя стоимость 1 штрафа ({curr_symbol})", value=int(st.session_state["fine_avg_cost"]), step=100)
    time_manager_fine = st.number_input("Время на обработку 1 штрафа (часов)", value=0.5, step=0.1)

# Математические константы на базе session_state
working_days_month = 21.7
employee_daily_cost = st.session_state["emp_salary"] / working_days_month
employee_daily_revenue = st.session_state["emp_revenue"] / working_days_month

def get_total_accident_cost(direct_cost):
    downtime_loss = downtime_days * (employee_daily_cost + employee_daily_revenue)
    management_loss = time_manager_accident * st.session_state["manager_hourly_rate"]
    return direct_cost + downtime_loss + management_loss

fine_loss_per_car_month = (fines_per_car_year * (st.session_state["fine_avg_cost"] + (time_manager_fine * st.session_state["manager_hourly_rate"]))) / 12
lease_risk_per_car_month = st.session_state["lease_return_cost"] / lease_term if lease_term > 0 else 0
total_disp_fot_before = disp_qty * st.session_state["disp_salary"]

# Базовый расчет расходов ДО внедрения системы
total_fuel_before, total_maint_before, total_accidents_year = 0, 0, 0
total_direct_accident_damage_before, total_tco_accident_damage_before = 0, 0

for name, cp in custom_fleet_params.items():
    q = cp["qty"]
    total_fuel_before += ((cp["mileage"] / 100 * cp["consumption"] * fuel_price) / 12) * q
    total_maint_before += (cp["maintenance"] / 12) * q
    total_accidents_year += cp["accidents_year"]
    total_direct_accident_damage_before += cp["accidents_year"] * cp["accident_cost"]
    total_tco_accident_damage_before += cp["accidents_year"] * get_total_accident_cost(cp["accident_cost"])

total_fines_loss_before = fine_loss_per_car_month * total_fleet_size
total_lease_risk_before = lease_risk_per_car_month * total_fleet_size * (lease_share / 100)

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

modules_payload = {}
savings_by_cat = {"fuel": 0, "maint": 0, "acc_direct": 0, "acc_tco": 0, "fines": 0, "lease": 0, "disp": 0}

# --- БАЗОВЫЙ МОНИТОРИНГ ---
if "Базовый Мониторинг" in selected_modules:
    with st.sidebar.expander("📡 Модуль: Базовый Мониторинг", expanded=False):
        st.session_state["b_cap"] = st.number_input(f"Трекер на 1 ТС ({curr_symbol})", value=int(st.session_state["b_cap"]), step=1000)
        st.session_state["b_op"] = st.number_input(f"АП на 1 ТС/мес ({curr_symbol})", value=int(st.session_state["b_op"]), step=50)
        eff_fuel = st.slider("Сокращение пробега и ГСМ (%)", 0.0, 25.0, 8.0, step=0.5) / 100
        eff_to = st.slider("Сокращение износа и ТО (%)", 0.0, 25.0, 10.0, step=0.5) / 100
        eff_fines = st.slider("Сокращение штрафов (%)", 0, 100, 40, step=5) / 100
        eff_lease = st.slider("Снижение выплат лизинговой (%)", 0, 100, 20, step=5) / 100 if lease_share > 0 else 0.0
        eff_acc = st.slider("Сокращение ДТП (геозоны) (%)", 0, 100, 15, step=5) / 100

        b_dir = (total_fuel_before * eff_fuel) + (total_maint_before * eff_to) + ((total_direct_accident_damage_before / 12) * eff_acc)
        b_tco = (total_fines_loss_before * eff_fines) + (total_lease_risk_before * eff_lease) + (((total_tco_accident_damage_before - total_direct_accident_damage_before) / 12) * eff_acc)
        modules_payload["Базовый Мониторинг"] = {"capex": st.session_state["b_cap"] * total_fleet_size, "opex": st.session_state["b_op"] * total_fleet_size, "direct": b_dir, "tco": b_tco}
        savings_by_cat["fuel"] += total_fuel_before * eff_fuel
        savings_by_cat["maint"] += total_maint_before * eff_to
        savings_by_cat["acc_direct"] += (total_direct_accident_damage_before / 12) * eff_acc
        savings_by_cat["fines"] += total_fines_loss_before * eff_fines
        savings_by_cat["lease"] += total_lease_risk_before * eff_lease
        savings_by_cat["acc_tco"] += ((total_tco_accident_damage_before - total_direct_accident_damage_before) / 12) * eff_acc

# --- СЕРВИС АНАЛИТИКИ И РЕАГИРОВАНИЯ ---
if "Сервис аналитики и реагирования" in selected_modules:
    with st.sidebar.expander("🛠️ Сервис аналитики и реагирования", expanded=False):
        st.session_state["s_cap"] = st.number_input(f"Единовременные затраты ({curr_symbol})", value=int(st.session_state["s_cap"]), step=10000)
        st.session_state["s_op"] = st.number_input(f"АП на 1 ТС/мес ({curr_symbol})", value=int(st.session_state["s_op"]), step=100)
        s_eff_disp = st.slider("Сокращение затрат на ФОТ диспетчеров (%)", 0, 100, 60, step=5) / 100
        
        modules_payload["Сервис аналитики и реагирования"] = {"capex": st.session_state["s_cap"], "opex": st.session_state["s_op"] * total_fleet_size, "direct": 0, "tco": total_disp_fot_before * s_eff_disp}
        savings_by_cat["disp"] += total_disp_fot_before * s_eff_disp

# --- ВИДЕОАНАЛИТИКА ---
if "Видеоаналитика" in selected_modules:
    with st.sidebar.expander("📷 Модуль: Видеоаналитика", expanded=False):
        st.session_state["v_cap"] = st.number_input(f"Оборудование на 1 ТС ({curr_symbol})", value=int(st.session_state["v_cap"]), step=5000)
        st.session_state["v_op"] = st.number_input(f"АП на 1 ТС/мес ({curr_symbol})", value=int(st.session_state["v_op"]), step=100)
        v_eff = st.slider("Снижение аварийности со SKAI (%)", 0, 100, 55, step=5) / 100
        
        v_dir = (total_direct_accident_damage_before / 12) * v_eff
        v_tco = ((total_tco_accident_damage_before - total_direct_accident_damage_before) / 12) * v_eff
        modules_payload["Видеоаналитика"] = {"capex": st.session_state["v_cap"] * total_fleet_size, "opex": st.session_state["v_op"] * total_fleet_size, "direct": v_dir, "tco": v_tco}
        savings_by_cat["acc_direct"] += v_dir
        savings_by_cat["acc_tco"] += v_tco

# --- БЕЗОПАСНОЕ ВОЖДЕНИЕ ---
if "Безопасное вождение" in selected_modules:
    with st.sidebar.expander("🛡️ Модуль: Безопасное вождение", expanded=False):
        st.session_state["sd_cap"] = st.number_input(f"Стоимость модуля на 1 ТС ({curr_symbol})", value=int(st.session_state["sd_cap"]), step=1000)
        st.session_state["sd_op"] = st.number_input(f"АП на 1 ТС/мес ({curr_symbol})", value=int(st.session_state["sd_op"]), step=50)
        sd_eff_to = st.slider("Доп. экономия на ТО от бережной езды (%)", 0, 40, 15, step=5) / 100
        sd_eff_acc = st.slider("Доп. снижение ДТП от скоринга (%)", 0, 40, 15, step=5) / 100
        
        sd_dir = (total_maint_before * sd_eff_to) + ((total_direct_accident_damage_before / 12) * sd_eff_acc)
        sd_tco = ((total_tco_accident_damage_before - total_direct_accident_damage_before) / 12) * sd_eff_acc
        modules_payload["Безопасное вождение"] = {"capex": st.session_state["sd_cap"] * total_fleet_size, "opex": st.session_state["sd_op"] * total_fleet_size, "direct": sd_dir, "tco": sd_tco}
        savings_by_cat["maint"] += total_maint_before * sd_eff_to
        savings_by_cat["acc_direct"] += (total_direct_accident_damage_before / 12) * sd_eff_acc
        savings_by_cat["acc_tco"] += sd_tco

# --- КОНТРОЛЬ ТОПЛИВА ---
if "Контроль топлива" in selected_modules:
    with st.sidebar.expander("⛽ Модуль: Контроль топлива", expanded=False):
        st.session_state["f_cap"] = st.number_input(f"Стоимость ДУТ на 1 ТС ({curr_symbol})", value=int(st.session_state["f_cap"]), step=2000)
        st.session_state["f_op"] = st.number_input(f"АП на 1 ТС/мес ({curr_symbol})", value=int(st.session_state["f_op"]), step=50)
        f_eff = st.slider("Прямая экономия ГСМ (сливы/карты) (%)", 0.0, 25.0, 10.0, step=0.5) / 100
        
        modules_payload["Контроль топлива"] = {"capex": st.session_state["f_cap"] * total_fleet_size, "opex": st.session_state["f_op"] * total_fleet_size, "direct": total_fuel_before * f_eff, "tco": 0}
        savings_by_cat["fuel"] += total_fuel_before * f_eff

# ==========================================
# 6. РЕНДЕРИНГ ИНТЕРФЕЙСА И РАСЧЕТ МЕТРИК (ИСПРАВЛЕННЫЙ ГРАФИК)
# ==========================================
st.title("Платформа SKAI: Расширенный калькулятор TCO и ROI")

fleet_str = " + ".join([f"**{qty}** {name.split(' (')[0]}" for name, qty in fleet_quantities.items()])
st.markdown(f"Структура парка: {fleet_str} | Всего: **{total_fleet_size} ТС**")
st.markdown("---")

calc_mode = st.radio("Аналитическая модель расчета:", ["Прямой экономический эффект (Классический)", "Полный TCO расчет (С учетом скрытых потерь, лизинга и оптимизации ФОТ)"], horizontal=True)
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

st.markdown("---")

tco_table_data = [
    ["Затраты на ГСМ (Топливо)", fmt(total_fuel_before), fmt(savings_by_cat["fuel"]), "Прямой эффект"],
    ["Затраты на ТО и расходники", fmt(total_maint_before), fmt(savings_by_cat["maint"]), "Прямой эффект"],
    ["Прямой ущерб от аварий / франшизы", fmt(total_direct_accident_damage_before / 12), fmt(savings_by_cat["acc_direct"]), "Прямой эффект"],
    ["Потери от простоя персонала и ТС при ДТП", fmt((total_tco_accident_damage_before - total_direct_accident_damage_before) / 12), fmt(savings_by_cat["acc_tco"] if is_tco else 0), "Косвенный (TCO)"],
    ["Расходы на собственный штат диспетчеров (ФОТ)", fmt(total_disp_fot_before), fmt(savings_by_cat["disp"] if is_tco else 0), "Косвенный (TCO)"],
    ["Администрирование и оплата штрафов бэк-офисом", fmt(total_fines_loss_before), fmt(savings_by_cat["fines"] if is_tco else 0), "Косвенный (TCO)"]
]
if lease_share > 0:
    tco_table_data.append([f"Риски выплат лизинговой (износ/возврат за {lease_share}% парка)", fmt(total_lease_risk_before), fmt(savings_by_cat["lease"] if is_tco else 0), "Косвенный (TCO)"])

df_tco = pd.DataFrame(tco_table_data, columns=["Фактор / Статья расходов", f"Базовые затраты до внедрения ({curr_symbol}/мес)", f"Прогноз экономии от SKAI ({curr_symbol}/мес)", "Тип фактора"])
st.dataframe(df_tco, use_container_width=True, hide_index=True)

st.markdown("---")

st.subheader(f"Динамика окупаемости и чистый эффект по продуктам ({mode_title})")
months = np.arange(1, 37)
chart_data = []
total_savings_by_module = {m_name: 0.0 for m_name in modules_payload.keys()}

for m in months:
    row = {"Месяц": m}
    for module_name, metrics in modules_payload.items():
        m_saving = metrics["direct"] + (metrics["tco"] if is_tco else 0)
        # Математически верный расчет: (Ежемесячная экономия - OPEX) * Месяц - Единовременный CAPEX
        accumulated_net_effect = (m_saving - metrics["opex"]) * m - metrics["capex"]

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

# Жесткое форматирование через lambda гарантирует разделители-пробелы
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
# 8. МЕТОДОЛОГИЯ И МАТЕМАТИЧЕСКИЙ АППАРАТ РАСЧЕТА (ИСПРАВЛЕННЫЙ RAW-STRING)
# ==========================================
st.markdown("---")
with st.expander("📝 Методология и математический аппарат расчетов", expanded=False):
    st.markdown(r"""
    ### 1. Расчет базовых ежемесячных затрат автопарка (до внедрения SKAI)
    
    * **Затраты на ГСМ (Топливо):** Вычисляются на основе годового пробега, нормативного расхода на 100 км и текущей стоимости топлива:  
        $$З_{ГСМ} = \sum \left( \frac{\text{Пробег}_{ТС} \times \text{Расход}_{ТС} \times \text{Цена топлива}}{100 \times 12} \right) \times \text{Кол-во ТС}$$
    
    * **Затраты на ТО и расходники:** $$З_{ТО} = \sum \left( \frac{\text{Стоимость ТО в год}}{12} \right) \times \text{Кол-во ТС}$$
    
    * **Прямой ущерб от ДТП:** Учитывает только прямые физические повреждения или затраты на страховую франшизу:  
        $$У_{прямой} = \sum \left( \frac{\text{Кол-во ДТП в год} \times \text{Стоимость 1 ДТП}}{12} \right)$$
        
    * **Скрытые потери TCO от простоя при ДТП:** Включают в себя ФОТ водителя за время простоя, упущенную выгоду (доход от ТС) и административные часы бэк-офиса на разбор инцидента:  
        $$Потери_{простой} = \frac{\text{Кол-во ДТП в год} \times \left( Дней_{простоя} \times (Стоимость_{водителя/день} + Доход_{ТС/день}) + Часы_{менеджера} \times Ставка_{менеджера} \right)}{12}$$
        
    * **Администрирование и оплата штрафов:** $$Потери_{штрафы} = \frac{\text{Штрафов на ТС в год} \times \left( Цена_{штрафа} + Время_{оформления} \times Ставка_{менеджера} \right)}{12} \times Всего_{ТС}$$
        
    * **Риски выплат лизинговым компаниям:** Определяют скрытые издержки при возврате ТС из-за ненормативного износа:  
        $$Риски_{лизинг} = \frac{\text{Выплата при возврате}}{\text{Срок лизинга (мес)}} \times Всего_{ТС} \times \text{Доля лизинга (\%)} $$

    ### 2. Принцип формирования финансового эффекта модулей
    
    Каждый подключенный продукт платформы SKAI выступает как мультипликатор снижения базовых издержек на определенный процент эффективности (значения регулируются ползунками):
    
    1.  **Базовый Мониторинг:** Оптимизирует пробеги (ГСМ), снижает износ (ТО), штрафы, риски лизинга и ДТП за счет контроля геозон.
    2.  **Контроль топлива:** Напрямую пресекает сливы и махинации с топливными картами.
    3.  **Видеоаналитика:** Снижает частоту критических инцидентов и ДТП (прямой ущерб + простой TCO) за счет контроля состояния водителя (усталость, телефон, ремень).
    4.  **Безопасное вождение:** Дает дополнительное снижение износа (ТО) и вероятности аварий за счет индивидуального скоринга водителей.
    5.  **Сервис аналитики и реагирования:** Оптимизирует бэк-офис, позволяя сократить ФОТ собственного диспетчерского центра.

    ### 3. Расчет ключевых инвестиционных показателей проекта
    
    * **Стартовые инвестиции (Капитальные вложения):** Сумма единовременных затрат на покупку и установку оборудования для всех ТС автопарка:  
        $$Кап.вложения = \sum (Стоимость_{модуля} \times Всего_{ТС})$$
        
    * **Операционные расходы (в месяц):** Сумма ежемесячной абонентской платы за программное обеспечение и сопутствующие сервисы:  
        $$Опер.расходы_{мес} = \sum (Абон.плата_{модуля} \times Всего_{ТС})$$
        
    * **Валовая экономия в месяц:** Сумма всех сокращенных статей затрат (включая или исключая косвенный TCO эффект в зависимости от выбранного режима):  
        $$Экономия_{валовая} = \sum Экономия_{ГСМ} + \sum Экономия_{ТО} + \sum Экономия_{ДТП} + \dots$$
        
    * **Чистая экономия в месяц:** $$Экономия_{чистая} = Экономия_{валовая} - Опер.расходы_{мес}$$
        
    * **Срок окупаемости проекта (Payback Period):** Период времени, за который чистый экономический эффект полностью покрывает первоначальные инвестиции:  
        $$Срок_{окупаемости} = \frac{\text{Капитальные вложения (Стартовые инвестиции)}}{\text{Чистая экономия в месяц}}$$
    """)