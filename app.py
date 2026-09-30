import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import base64
import json

# Настройка страницы в строгом B2B стиле
st.set_page_config(page_title="Платформа SKAI: Калькулятор TCO и ROI", layout="wide")

# ==========================================
# ФИРМЕННЫЙ SVG ЛОГОТИП SKAI И НАСТРОЙКА ST.LOGO
# ==========================================
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

logo_b64 = base64.b64encode(SKAI_LOGO_SVG.encode("utf-8")).decode("utf-8")
st.logo(f"data:image/svg+xml;base64,{logo_b64}")

st.markdown("""<style>
[data-testid="stSidebarHeader"] {
    position: sticky !important;
    top: 0 !important;
    z-index: 999999 !important;
    background-color: var(--secondary-background-color, #f0f2f6) !important;
    height: auto !important;
    min-height: 75px !important;
    padding-top: 1rem !important;
    padding-bottom: 0.8rem !important;
    border-bottom: 1px solid rgba(15, 23, 42, 0.08) !important;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.03) !important;
}

[data-testid="stSidebarHeader"] > div,
[data-testid="stLogo"] {
    height: auto !important;
    max-height: none !important;
}

[data-testid="stSidebarHeader"] img,
[data-testid="stLogo"] img,
img[data-testid="stLogo"] {
    height: 50px !important;
    max-height: 56px !important;
    width: auto !important;
    object-fit: contain !important;
}
</style>""", unsafe_allow_html=True)

# ==========================================
# 1. БАЗА ДАННЫХ ПРЕСЕТОВ
# ==========================================
presets = {
    "Магистральный тягач (Фура)": {
        "fleet_size": 50, "mileage": 120000, "consumption": 32.0, "maintenance": 60000,
        "accidents_year": 8.0, "accident_cost": 1550000, "insurance_cost": 95000,
        "video_capex": 120000, "video_opex": 2000, "video_eff": 80,
        "base_capex": 15000, "base_opex": 400, "base_eff_fuel": 6.0, "base_eff_to": 5.0, "base_eff_fines": 40,
        "safe_capex": 10000, "safe_opex": 500, "safe_eff_fuel": 10.0, "safe_eff_to": 15, "safe_eff_acc": 75,
        "fuel_capex": 25000, "fuel_opex": 600, "fuel_eff": 10
    },
    "Самосвал / Тяжелая спецтехника": {
        "fleet_size": 30, "mileage": 45000, "consumption": 45.0, "maintenance": 90000,
        "accidents_year": 6.0, "accident_cost": 1200000, "insurance_cost": 85000,
        "video_capex": 130000, "video_opex": 2000, "video_eff": 80,
        "base_capex": 15000, "base_opex": 400, "base_eff_fuel": 9.0, "base_eff_to": 6.0, "base_eff_fines": 30,
        "safe_capex": 10000, "safe_opex": 500, "safe_eff_fuel": 10.0, "safe_eff_to": 20, "safe_eff_acc": 75,
        "fuel_capex": 30000, "fuel_opex": 600, "fuel_eff": 12
    },
    "Легкий коммерческий транспорт / Корпоративные авто": {
        "fleet_size": 40, "mileage": 60000, "consumption": 13.0, "maintenance": 35000,
        "accidents_year": 7.0, "accident_cost": 650000, "insurance_cost": 45000,
        "video_capex": 110000, "video_opex": 1800, "video_eff": 80,
        "base_capex": 12000, "base_opex": 350, "base_eff_fuel": 13.0, "base_eff_to": 8.0, "base_eff_fines": 60,
        "safe_capex": 8000, "safe_opex": 400, "safe_eff_fuel": 10.0, "safe_eff_to": 12, "safe_eff_acc": 75,
        "fuel_capex": 20000, "fuel_opex": 500, "fuel_eff": 8
    }
}

default_qtys = {
    "Магистральный тягач (Фура)": 30,
    "Самосвал / Тяжелая спецтехника": 10,
    "Легкий коммерческий транспорт / Корпоративные авто": 15
}

monetary_keys = [
    "fuel_price", "emp_salary", "downtime_loss_per_day", "disp_salary", 
    "fine_avg_cost", "s_cap", "s_op", "b_cap", "b_op", "v_cap", "v_op", 
    "sd_cap", "sd_op", "f_cap", "f_op", "reserve_cost_per_month", "total_loss_cost"
]
for name in presets.keys():
    monetary_keys.extend([f"maint_{name}", f"acost_{name}", f"ins_{name}"])

# ==========================================
# 2. ИНИЦИАЛИЗАЦИЯ СОСТОЯНИЯ (SESSION STATE)
# ==========================================
st.session_state.setdefault("initialized", True)
st.session_state.setdefault("prev_currency", "₽ (RUB)")
st.session_state.setdefault("fuel_price", 65.0)
st.session_state.setdefault("stat_period_years", 2)
st.session_state.setdefault("driver_fault_pct", 70)
st.session_state.setdefault("use_reserve_fleet", True)
st.session_state.setdefault("reserve_fleet_qty", 10)
st.session_state.setdefault("reserve_cost_per_month", 25000)
st.session_state.setdefault("reserve_reduction_rate", 35)
st.session_state.setdefault("include_total_loss", True)
st.session_state.setdefault("total_loss_cost", 2500000)
st.session_state.setdefault("total_loss_freq_years", 2.5)

st.session_state.setdefault("emp_salary", 100000)
st.session_state.setdefault("downtime_loss_per_day", 0)
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
# 3. САЙДБАР: КОНФИГУРАЦИЯ И ПАРАМЕТРЫ
# ==========================================
st.sidebar.header("Параметры и конфигурация")

# --- ЭКСПОРТ И ИМПОРТ ПАРАМЕТРОВ (JSON) ---
with st.sidebar.expander("Сохранение и загрузка параметров", expanded=False):
    uploaded_config = st.file_uploader("Загрузить файл конфигурации (.json)", type=["json"], key="fleet_config_uploader")
    if uploaded_config is not None:
        file_bytes = uploaded_config.getvalue()
        if st.session_state.get("last_loaded_config_hash") != hash(file_bytes):
            try:
                config_json = json.loads(file_bytes.decode("utf-8"))
                
                # Глобальные параметры
                if "currency" in config_json: st.session_state["prev_currency"] = config_json["currency"]
                if "fuel_price" in config_json: st.session_state["fuel_price"] = float(config_json["fuel_price"])
                if "stat_period_years" in config_json: st.session_state["stat_period_years"] = int(config_json["stat_period_years"])
                if "driver_fault_pct" in config_json: st.session_state["driver_fault_pct"] = int(config_json["driver_fault_pct"])
                if "use_reserve_fleet" in config_json: st.session_state["use_reserve_fleet"] = bool(config_json["use_reserve_fleet"])
                if "reserve_fleet_qty" in config_json: st.session_state["reserve_fleet_qty"] = int(config_json["reserve_fleet_qty"])
                if "reserve_cost_per_month" in config_json: st.session_state["reserve_cost_per_month"] = int(config_json["reserve_cost_per_month"])
                if "reserve_reduction_rate" in config_json: st.session_state["reserve_reduction_rate"] = int(config_json["reserve_reduction_rate"])
                if "include_total_loss" in config_json: st.session_state["include_total_loss"] = bool(config_json["include_total_loss"])
                if "total_loss_cost" in config_json: st.session_state["total_loss_cost"] = int(config_json["total_loss_cost"])
                if "emp_salary" in config_json: st.session_state["emp_salary"] = int(config_json["emp_salary"])
                if "downtime_loss_per_day" in config_json: st.session_state["downtime_loss_per_day"] = int(config_json["downtime_loss_per_day"])
                if "disp_salary" in config_json: st.session_state["disp_salary"] = int(config_json["disp_salary"])
                if "fine_avg_cost" in config_json: st.session_state["fine_avg_cost"] = int(config_json["fine_avg_cost"])
                
                # Группы ТС
                fleet_data = config_json.get("fleet_params", {})
                for group_name, g_params in fleet_data.items():
                    if group_name in presets:
                        qty_val = int(g_params.get("qty", default_qtys[group_name]))
                        st.session_state[f"qty_input_{group_name}"] = qty_val
                        st.session_state[f"prev_qty_{group_name}"] = qty_val
                        st.session_state[f"mil_{group_name}"] = int(g_params.get("mileage", presets[group_name]["mileage"]))
                        st.session_state[f"cons_{group_name}"] = float(g_params.get("consumption", presets[group_name]["consumption"]))
                        st.session_state[f"maint_{group_name}"] = int(g_params.get("maintenance", presets[group_name]["maintenance"]))
                        st.session_state[f"acc_{group_name}"] = float(g_params.get("accidents_year", 0.0))
                        st.session_state[f"acost_{group_name}"] = int(g_params.get("accident_cost", presets[group_name]["accident_cost"]))
                        st.session_state[f"ins_{group_name}"] = int(g_params.get("insurance_cost", presets[group_name]["insurance_cost"]))
                
                st.session_state["last_loaded_config_hash"] = hash(file_bytes)
                st.success("Параметры успешно загружены!")
                st.rerun()
            except Exception as e:
                st.error(f"Ошибка чтения файла: {e}")

    export_payload = {
        "version": "1.1",
        "currency": st.session_state.get("prev_currency", "₽ (RUB)"),
        "fuel_price": st.session_state.get("fuel_price", 65.0),
        "stat_period_years": st.session_state.get("stat_period_years", 2),
        "driver_fault_pct": st.session_state.get("driver_fault_pct", 70),
        "use_reserve_fleet": st.session_state.get("use_reserve_fleet", True),
        "reserve_fleet_qty": st.session_state.get("reserve_fleet_qty", 10),
        "reserve_cost_per_month": st.session_state.get("reserve_cost_per_month", 25000),
        "reserve_reduction_rate": st.session_state.get("reserve_reduction_rate", 35),
        "include_total_loss": st.session_state.get("include_total_loss", True),
        "total_loss_cost": st.session_state.get("total_loss_cost", 2500000),
        "emp_salary": st.session_state.get("emp_salary", 100000),
        "downtime_loss_per_day": st.session_state.get("downtime_loss_per_day", 0),
        "disp_salary": st.session_state.get("disp_salary", 80000),
        "fine_avg_cost": st.session_state.get("fine_avg_cost", 500),
        "fleet_params": {}
    }

    for name in presets.keys():
        export_payload["fleet_params"][name] = {
            "qty": st.session_state.get(f"qty_input_{name}", default_qtys[name]),
            "mileage": st.session_state.get(f"mil_{name}", presets[name]["mileage"]),
            "consumption": st.session_state.get(f"cons_{name}", presets[name]["consumption"]),
            "maintenance": st.session_state.get(f"maint_{name}", presets[name]["maintenance"]),
            "accidents_year": st.session_state.get(f"acc_{name}", round(presets[name]["accidents_year"] * (default_qtys[name] / presets[name]["fleet_size"]), 1)),
            "accident_cost": st.session_state.get(f"acost_{name}", presets[name]["accident_cost"]),
            "insurance_cost": st.session_state.get(f"ins_{name}", presets[name]["insurance_cost"])
        }

    st.download_button(
        label="Скачать параметры парка (.json)",
        data=json.dumps(export_payload, ensure_ascii=False, indent=2),
        file_name="skai_fleet_parameters.json",
        mime="application/json",
        use_container_width=True
    )

st.sidebar.markdown("---")

# ВАЛЮТА И ГОРИЗОНТ ДАННЫХ
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

stat_period = st.sidebar.selectbox(
    "Период предоставленной статистики по ДТП:",
    [1, 2, 3],
    index=int(st.session_state["stat_period_years"] - 1),
    format_func=lambda x: f"{x} {'год' if x==1 else 'года'}"
)
st.session_state["stat_period_years"] = stat_period

st.sidebar.markdown("---")
st.sidebar.subheader("Состав и параметры ТС")

fleet_quantities = {}
custom_fleet_params = {}

for name, p_default in presets.items():
    qty = st.sidebar.number_input(f"{name} (шт):", min_value=0, value=default_qtys[name], step=5, key=f"qty_input_{name}")
    
    if qty > 0:
        fleet_quantities[name] = qty
        clean_name = name.split(" (")[0]
        
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
            maintenance = st.number_input(f"ТО + расходники 1 ТС/год ({curr_symbol})", min_value=0, value=int(st.session_state[f"maint_{name}"]), step=5000, key=f"maint_{name}")
            
            raw_accidents = st.number_input(f"ДТП этой группы за {stat_period} г. (шт)", min_value=0.0, step=0.5, key=acc_key)
            annual_accidents = raw_accidents / stat_period
            
            accident_cost = st.number_input(f"Ущерб/франшиза 1 ДТП ({curr_symbol})", min_value=0, value=int(st.session_state[f"acost_{name}"]), step=5000, key=f"acost_{name}")
            insurance_cost = st.number_input(f"КАСКО и ОСАГО на 1 ТС в год ({curr_symbol})", min_value=0, value=int(st.session_state[f"ins_{name}"]), step=5000, key=f"ins_{name}")
        
        custom_fleet_params[name] = {
            "qty": qty, "mileage": mileage, "consumption": consumption, 
            "maintenance": maintenance, "accidents_year": annual_accidents, 
            "accident_cost": accident_cost, "insurance_cost": insurance_cost,
            **{k: v for k, v in p_default.items() if "eff" in k}
        }

total_fleet_size = sum(fleet_quantities.values())
if total_fleet_size == 0:
    st.sidebar.warning("Укажите количество хотя бы для одного типа ТС.")
    st.stop()

# ==========================================
# 4. САЙДБАР: TCO, РЕЗЕРВ И СТРАХОВАНИЕ
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader("Управление TCO и персоналом")

with st.sidebar.expander("Потери бэк-офиса и простои персонала", expanded=False):
    st.session_state["emp_salary"] = st.number_input(f"Затраты на 1 водителя в месяц (ФОТ, {curr_symbol})", value=int(st.session_state["emp_salary"]), step=5000)
    st.session_state["downtime_loss_per_day"] = st.number_input(f"Потери от 1 дня простоя 1 ТС ({curr_symbol}/день)", value=int(st.session_state["downtime_loss_per_day"]), step=1000)
    st.caption("Если используется подменный транспорт — укажите 0 ₽ (затраты будут учтены в блоке резервного фонда).")

    st.markdown("**Диспетчеризация и администрирование**")
    st.session_state["disp_salary"] = st.number_input(f"ФОТ 1 диспетчера парка в месяц ({curr_symbol})", value=int(st.session_state["disp_salary"]), step=5000)
    calculated_disp_qty = max(1.0, round(total_fleet_size / 25, 1))
    disp_qty = st.number_input("Текущее кол-во диспетчеров в штате (база)", value=float(calculated_disp_qty), step=0.5)
    manager_hourly_rate = round(st.session_state["disp_salary"] / 168)
    st.caption(f"Себестоимость часа работы бэк-офиса: {manager_hourly_rate} {curr_symbol}/час.")
    
    downtime_days = st.number_input("Средний простой ТС после ДТП (дней)", value=14, step=1)
    time_manager_accident = 8
    
    st.markdown("**Штрафы автопарка**")
    fines_per_car_year = st.number_input("Кол-во штрафов на 1 ТС в год (база)", value=12, step=2)
    st.session_state["fine_avg_cost"] = st.number_input(f"Средняя стоимость 1 штрафа ({curr_symbol})", value=int(st.session_state["fine_avg_cost"]), step=100)
    time_manager_fine = 0.5

# МОДЕЛЬ РЕЗЕРВНОГО АВТОПАРКА
with st.sidebar.expander("Модель подменного/резервного фонда", expanded=True):
    st.session_state["use_reserve_fleet"] = st.checkbox("В парке содержится резервный транспорт", value=st.session_state["use_reserve_fleet"])
    if st.session_state["use_reserve_fleet"]:
        default_res_qty = max(2, int(total_fleet_size * 0.05))
        st.session_state["reserve_fleet_qty"] = st.number_input("Количество ТС в резерве (шт)", min_value=1, value=int(st.session_state["reserve_fleet_qty"]), step=1)
        st.session_state["reserve_cost_per_month"] = st.number_input(f"Стоимость владения 1 резервным ТС ({curr_symbol}/мес)", value=int(st.session_state["reserve_cost_per_month"]), step=2000)
        st.caption("Амортизация, налоги, страховка и плановое содержание стоящего в резерве автомобиля.")
        st.session_state["reserve_reduction_rate"] = st.slider("Потенциал высвобождения резерва при снижении ДТП (%)", 0, 60, int(st.session_state["reserve_reduction_rate"]), step=5) / 100
    else:
        st.session_state["reserve_fleet_qty"] = 0
        st.session_state["reserve_cost_per_month"] = 0
        st.session_state["reserve_reduction_rate"] = 0.0

# АНАЛИЗ АВАРИЙНОСТИ И АКТУАРНЫЙ РИСК
with st.sidebar.expander("Анализ причин аварий и Total Loss", expanded=True):
    st.session_state["driver_fault_pct"] = st.slider("Доля ДТП по вине водителей компании (%)", 10, 100, int(st.session_state["driver_fault_pct"]), step=5) / 100
    st.caption("По статистике филиала: 7 из 10 ДТП (70%) происходят по вине водителя. Именно на них влияют системы SKAI.")
    
    st.session_state["include_total_loss"] = st.checkbox("Учитывать актуарный риск тяжелых ДТП (Total Loss)", value=st.session_state["include_total_loss"])
    if st.session_state["include_total_loss"]:
        st.session_state["total_loss_cost"] = st.number_input(f"Средний ущерб от катастрофического ДТП ({curr_symbol})", value=int(st.session_state["total_loss_cost"]), step=250000)
        st.caption("Полное списание ТС, ущерб перевозимому грузу и материальные претензии третьих лиц.")

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

# Базовые расходы ДО внедрения
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

# Затраты на содержание резервного флота
total_reserve_cost_monthly_before = st.session_state["reserve_fleet_qty"] * st.session_state["reserve_cost_per_month"]

# Актуарный месячный риск тяжелого ДТП
total_loss_monthly_risk = (st.session_state["total_loss_cost"] / (st.session_state["total_loss_freq_years"] * 12)) if st.session_state["include_total_loss"] else 0.0

# ==========================================
# 5. САЙДБАР: МОДУЛИ SKAI
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader("Модули платформы SKAI")
available_modules = ["Видеоаналитика", "Базовый Мониторинг", "Безопасное вождение", "Контроль топлива", "Сервис аналитики и реагирования"]
selected_modules = [m for m in available_modules if st.sidebar.checkbox(m, value=(m in ["Видеоаналитика", "Базовый Мониторинг"]))]

if not selected_modules:
    st.sidebar.warning("Выберите хотя бы один модуль.")
    st.stop()

modules_raw = {}
savings_by_cat = {"fuel": 0, "maint": 0, "acc_direct": 0, "acc_tco": 0, "fines": 0, "disp": 0, "insurance": 0, "reserve": 0, "total_loss": 0}

# --- БАЗОВЫЙ МОНИТОРИНГ ---
if "Базовый Мониторинг" in selected_modules:
    with st.sidebar.expander("Модуль: Базовый Мониторинг", expanded=False):
        has_gps_status = st.radio("Оснащенность автопарка GPS:", ["GPS-оборудование отсутствует", "GPS уже установлен на ТС"], key="has_gps_status")
        is_gps_installed = (has_gps_status == "GPS уже установлен на ТС")
        
        default_b_capex = int(2500 * (6.13 if is_kzt else 1.0)) if is_gps_installed else int(15000 * (6.13 if is_kzt else 1.0))
        capex_label = f"Затраты на аудит/перевод 1 ТС ({curr_symbol})" if is_gps_installed else f"Затраты на трекер + монтаж 1 ТС ({curr_symbol})"

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
# СИНЕРГЕТИЧЕСКИЙ РАСЧЕТ И ИНТЕГРАЦИЯ НОВЫХ ФАКТОРОВ
# ==========================================
acc_eff_va = modules_raw.get("Видеоаналитика", {}).get("acc_weight", 0.0)
acc_eff_sd = modules_raw.get("Безопасное вождение", {}).get("acc_weight", 0.0)

combined_no_accident_prob = (1.0 - acc_eff_va) * (1.0 - acc_eff_sd)
total_combined_acc_eff = 1.0 - combined_no_accident_prob

# Эффект предотвращения применяется только к виновным ДТП
fault_ratio = st.session_state["driver_fault_pct"]
real_prevention_rate = total_combined_acc_eff * fault_ratio

total_direct_acc_saving = (total_direct_accident_damage_before / 12) * real_prevention_rate
total_tco_acc_saving = ((total_tco_accident_damage_before - total_direct_accident_damage_before) / 12) * real_prevention_rate

# Экономия от высвобождения резервного фонда (активируется при снижении ДТП)
reserve_saving = (total_reserve_cost_monthly_before * st.session_state["reserve_reduction_rate"]) if total_combined_acc_eff > 0 else 0.0

# Предотвращение катастрофических убытков Total Loss
total_loss_saving = (total_loss_monthly_risk * real_prevention_rate)

savings_by_cat["acc_direct"] = total_direct_acc_saving
savings_by_cat["acc_tco"] = total_tco_acc_saving
savings_by_cat["reserve"] = reserve_saving
savings_by_cat["total_loss"] = total_loss_saving

# Скидка по КАСКО и ОСАГО закреплена за Видеоаналитикой
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
        m_res = reserve_saving * weight_ratio
        m_tl = total_loss_saving * weight_ratio
    else:
        m_dir_acc, m_tco_acc, m_res, m_tl = 0.0, 0.0, 0.0, 0.0
        
    m_ins = total_ins_saving if m_name == "Видеоаналитика" else 0.0
        
    modules_payload[m_name] = {
        "capex": m_data["capex"],
        "opex": m_data["opex"],
        "direct": m_data["direct_base"] + m_dir_acc + m_ins + m_tl,
        "tco": m_data["tco_base"] + m_tco_acc + m_res
    }

# ==========================================
# 6. РЕНДЕРИНГ ИНТЕРФЕЙСА И РАСЧЕТ МЕТРИК
# ==========================================
st.title("Платформа SKAI: Калькулятор TCO и ROI")

bar_colors = ["#2563EB", "#0EA5E9", "#64748B", "#F59E0B"]

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

# ОЦЕНКА ЗОНЫ ПОТЕРЬ
annual_direct_accidents = total_direct_accident_damage_before
annual_iceberg_hidden = annual_direct_accidents * 3.0
annual_fuel_total = total_fuel_before * 12
annual_waste_fuel = annual_fuel_total * 0.12
annual_reserve_waste = total_reserve_cost_monthly_before * 12

st.markdown(
    f"""
    <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #2563EB; border-radius: 6px; padding: 14px 18px; margin-bottom: 24px;">
        <div style="font-size: 13px; font-weight: 700; color: #1E293B; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px;">
            Оценка структуры рисков автопарка до внедрения платформы SKAI
        </div>
        <div style="display: flex; gap: 16px; flex-wrap: wrap;">
            <div style="flex: 1 1 210px; background-color: #FFFFFF; border: 1px solid #FEE2E2; border-radius: 6px; padding: 10px 14px;">
                <div style="font-size: 12px; font-weight: 600; color: #991B1B;">Прямой ущерб от ДТП</div>
                <div style="font-size: 20px; font-weight: 700; color: #DC2626; margin: 2px 0;">~{fmt(annual_direct_accidents)} {curr_symbol}/год</div>
                <div style="font-size: 11px; color: #64748B;">Счета СТО при {total_accidents_year:.1f} ДТП/год (вина: {int(fault_ratio*100)}%)</div>
            </div>
            <div style="flex: 1 1 210px; background-color: #FFFFFF; border: 1px solid #FFE4E6; border-radius: 6px; padding: 10px 14px;">
                <div style="font-size: 12px; font-weight: 600; color: #9F1239;">Содержание резерва ТС</div>
                <div style="font-size: 20px; font-weight: 700; color: #E11D48; margin: 2px 0;">~{fmt(annual_reserve_waste)} {curr_symbol}/год</div>
                <div style="font-size: 11px; color: #64748B;">Скрытые расходы на {st.session_state['reserve_fleet_qty']} подменных ТС фонда</div>
            </div>
            <div style="flex: 1 1 210px; background-color: #FFFFFF; border: 1px solid #FEF3C7; border-radius: 6px; padding: 10px 14px;">
                <div style="font-size: 12px; font-weight: 600; color: #92400E;">Балласт по ГСМ (ХХ и съезды)</div>
                <div style="font-size: 20px; font-weight: 700; color: #D97706; margin: 2px 0;">~{fmt(annual_waste_fuel)} {curr_symbol}/год</div>
                <div style="font-size: 11px; color: #64748B;">10–14% топлива сжигается впустую на стоянках и приписках</div>
            </div>
            <div style="flex: 1 1 210px; background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 6px; padding: 10px 14px;">
                <div style="font-size: 12px; font-weight: 600; color: #334155;">Актуарный риск Total Loss</div>
                <div style="font-size: 20px; font-weight: 700; color: #475569; margin: 2px 0;">~{fmt(total_loss_monthly_risk * 12)} {curr_symbol}/год</div>
                <div style="font-size: 11px; color: #64748B;">Вероятность 1 тяжелого ДТП раз в {st.session_state['total_loss_freq_years']} г.</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("---")

calc_mode = st.radio("Аналитическая модель расчета:", ["Прямой экономический эффект (Классический)", "Полный TCO расчет (С учетом скрытых потерь, резерва и ФОТ)"], horizontal=True)
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
rc2.metric("Стоимость риска ДТП со SKAI", f"{risk_per_100km_after:.1f} {curr_symbol} / 100 км", delta=f"-{real_prevention_rate*100:.0f}% к виновным ДТП", delta_color="inverse")
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
    ["Защита от риска Total Loss (тяжелых ДТП)", fmt(total_loss_monthly_risk), fmt(savings_by_cat["total_loss"]), "Прямой эффект"],
    ["Содержание подменного/резервного фонда ТС", fmt(total_reserve_cost_monthly_before), fmt(savings_by_cat["reserve"] if is_tco else 0), "Косвенный (TCO)"],
    ["Потери от простоя персонала при ДТП", fmt((total_tco_accident_damage_before - total_direct_accident_damage_before) / 12), fmt(savings_by_cat["acc_tco"] if is_tco else 0), "Косвенный (TCO)"],
    ["Расходы на собственный штат диспетчеров (ФОТ)", fmt(total_disp_fot_before), fmt(savings_by_cat["disp"] if is_tco else 0), "Косвенный (TCO)"],
    ["Администрирование и оплата штрафов бэк-офисом", fmt(total_fines_loss_before), fmt(savings_by_cat["fines"] if is_tco else 0), "Косвенный (TCO)"]
]

df_tco = pd.DataFrame(tco_table_data, columns=["Фактор / Статья расходов", f"Базовые затраты до внедрения ({curr_symbol}/мес)", f"Прогноз экономии от SKAI ({curr_symbol}/мес)", "Тип фактора"])
st.dataframe(df_tco, use_container_width=True, hide_index=True)

st.markdown("---")

# ==========================================
# ГРАФИКИ ОКУПАЕМОСТИ И ЧИСТОГО ЭФФЕКТА
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
        st.info("К 36-му месяцу выбранные модули еще не вышли в чистую прибыль.")

# ==========================================
# 7. ПОДРОБНЫЙ ГРАФИК ОКУПАЕМОСТИ ПО МЕСЯЦАМ
# ==========================================
st.markdown("---")
st.subheader("Подробный график окупаемости проекта (моделирование по месяцам)")
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
# 8. МЕТОДОЛОГИЯ И МАТЕМАТИЧЕСКИЙ АППАРАТ
# ==========================================
st.markdown("---")
with st.expander("Методология и математический аппарат расчетов", expanded=False):
    st.markdown(r"""
    ### 1. Нормализация периода и коэффициент вины
    * **Приведение к годовому темпу:**
      $$ДТП_{год} = \frac{ДТП_{период}}{Период_{лет}}$$
    * **Контролируемая аварийность:** Эффект предотвращения применяется только к виновным ДТП:
      $$E_{факт} = E_{системы} \times Доля_{вины}$$

    ### 2. Модель подменного/резервного фонда
    * **Базовые затраты на резерв:** 
      $$З_{резерв} = Кол-во_{резерв} \times Стоимость_{содержания/мес}$$
    * **Экономия от высвобождения резерва:**
      $$Экономия_{резерв} = З_{резерв} \times \%Высвобождения$$

    ### 3. Актуарный риск Total Loss (тяжелых ДТП)
    * **Месячная актуарная нагрузка риска:**
      $$Риск_{TotalLoss} = \frac{\text{Ущерб Total Loss}}{Период_{лет} \times 12}$$
    """)