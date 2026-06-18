import streamlit as st
import pandas as pd
import numpy as np

# Настройка страницы
st.set_page_config(page_title="SKAI Видеоаналитика: Калькулятор ROI", layout="wide", page_icon="📊")

# ==========================================
# 1. ОБЪЯВЛЕНИЕ КОНТЕЙНЕРОВ ДЛЯ ВЕРХА СТРАНИЦЫ
# ==========================================
title_container = st.container()
metrics_container = st.container()
effects_container = st.container()
chart_container = st.container()

# Визуальный разделитель перед настройками
st.markdown("<br><br><br><hr style='border:1px solid #1E88E5;'>", unsafe_allow_html=True)

# ==========================================
# 2. ПАНЕЛЬ НАСТРОЕК И ПРЕСЕТОВ (НИЗ СТРАНИЦЫ)
# ==========================================
st.header("⚙️ Панель настроек и пресетов ТС")
st.caption("Выберите шаблон под ваш тип транспорта или скорректируйте любые цифры. Справа от полей ввода сразу отображается сумма на весь автопарк.")

# База данных пресетов (средние рыночные показатели)
presets = {
    "🚛 Магистральный тягач (Фура)": {
        "fleet_size": 50,
        "mileage": 120000,
        "consumption": 32.0,
        "accident_rate": 15.0,
        "accident_cost": 800000,
        "hardware_cost": 160000,
        "monthly_sub": 2000,
        "accident_reduction": 55,
        "fuel_economy": 4.0,
        "other_savings": 2000
    },
    "🏗️ Самосвал / Тяжелая спецтехника": {
        "fleet_size": 30,
        "mileage": 45000,
        "consumption": 45.0,
        "accident_rate": 25.0,
        "accident_cost": 600000,
        "hardware_cost": 170000,
        "monthly_sub": 2000,
        "accident_reduction": 50,
        "fuel_economy": 5.0,
        "other_savings": 1500
    },
    "📦 Легкий коммерческий транспорт (LCV / Газель)": {
        "fleet_size": 40,
        "mileage": 60000,
        "consumption": 13.0,
        "accident_rate": 20.0,
        "accident_cost": 300000,
        "hardware_cost": 130000,
        "monthly_sub": 1800,
        "accident_reduction": 60,
        "fuel_economy": 3.0,
        "other_savings": 1200
    }
}

# Выбор пресета ТС
selected_preset = st.selectbox("Шаблон под тип транспортного средства:", list(presets.keys()))
p = presets[selected_preset]

# ------------------------------------------
# ГЛАВНЫЙ МНОЖИТЕЛЬ: РАЗМЕР АВТОПАРКА
# ------------------------------------------
fleet_size = st.number_input("Размер автопарка (шт.) — базовый множитель для расчета итогов", min_value=1, value=p["fleet_size"], step=5)

st.markdown("---")

# ПОДРАЗДЕЛ: СТОИМОСТЬ СИСТЕМЫ
st.subheader("💰 Стоимость решения SKAI и прямые расходы")

col_hw1, col_hw2 = st.columns([2, 1])
with col_hw1:
    hardware_cost = st.number_input("Стоимость комплекта + монтаж на 1 авто (руб.)", min_value=0, value=p["hardware_cost"], step=5000)
with col_hw2:
    st.metric("Итого стартовые вложения (Capex)", f"{hardware_cost * fleet_size:,.0f} ₽".replace(",", " "))

col_sub1, col_sub2 = st.columns([2, 1])
with col_sub1:
    monthly_sub = st.number_input("Абонентская плата за 1 авто в месяц (руб.)", min_value=0, value=p["monthly_sub"], step=100)
with col_sub2:
    st.metric("Итого абон. плата парка / мес (Opex)", f"{monthly_sub * fleet_size:,.0f} ₽".replace(",", " "))

st.markdown("---")

# ПОДРАЗДЕЛ: ТОПЛИВО
st.subheader("⛽ Топливо и пробег")

col_f1, col_f2, col_f3, col_f4 = st.columns([2, 2, 2, 3])
with col_f1:
    annual_mileage = st.number_input("Пробег 1 авто в год (км)", min_value=1000, value=p["mileage"], step=5000)
with col_f2:
    fuel_consumption = st.number_input("Расход (л/100 km)", min_value=1.0, value=p["consumption"], step=0.5)
with col_f3:
    fuel_price = st.number_input("Цена топлива (руб./литр)", min_value=1.0, value=65.0, step=1.0)
with col_f4:
    # Базовые затраты парка на топливо в месяц ДО внедрения
    monthly_fuel_cost_per_car = (annual_mileage / 100 * fuel_consumption * fuel_price) / 12
    fleet_monthly_fuel_before = monthly_fuel_cost_per_car * fleet_size
    st.metric("Текущие траты парка на топливо / мес", f"{fleet_monthly_fuel_before:,.0f} ₽".replace(",", " "))

col_fe1, col_fe2 = st.columns([2, 1])
with col_fe1:
    fuel_economy = st.slider("Экономия топлива за счет контроля вождения (%)", min_value=0.0, max_value=20.0, value=p["fuel_economy"], step=0.5) / 100
with col_fe2:
    monthly_fuel_saving_total = fleet_monthly_fuel_before * fuel_economy
    st.metric("Итого экономия на топливе / мес", f"{monthly_fuel_saving_total:,.0f} ₽".replace(",", " "))

st.markdown("---")

# ПОДРАЗДЕЛ: БЕЗОПАСНОСТЬ И ДТП
st.subheader("🛡️ Безопасность и предотвращение ДТП")

col_acc1, col_acc2, col_acc3 = st.columns([3, 3, 3])
with col_acc1:
    accident_rate = st.slider("Доля машин, попадающих в ДТП за год (%)", min_value=0.0, max_value=100.0, value=p["accident_rate"], step=1.0) / 100
with col_acc2:
    accident_cost = st.number_input("Средний ущерб от одного ДТП (руб.)", min_value=1000, value=p["accident_cost"], step=50000)
with col_acc3:
    # Текущие средние убытки парка от ДТП в месяц
    fleet_monthly_accident_before = (fleet_size * accident_rate * accident_cost) / 12
    st.metric("Текущие убытки парка от ДТП / мес", f"{fleet_monthly_accident_before:,.0f} ₽".replace(",", " "))

col_acr1, col_acr2 = st.columns([2, 1])
with col_acr1:
    accident_reduction = st.slider("Снижение аварийности благодаря SKAI ADAS/DSM (%)", min_value=0, max_value=100, value=p["accident_reduction"], step=5) / 100
with col_acr2:
    monthly_accident_saving_total = fleet_monthly_accident_before * accident_reduction
    st.metric("Итого сберегаем на ДТП / мес", f"{monthly_accident_saving_total:,.0f} ₽".replace(",", " "))

st.markdown("---")

# ПОДРАЗДЕЛ: СКРЫТЫЕ ИЗДЕРЖКИ
st.subheader("🧾 Дополнительные скрытые издержки")

col_oth1, col_oth2 = st.columns([2, 1])
with col_oth1:
    other_savings = st.number_input("Экономия на штрафах и прочих рисках на 1 авто в месяц (руб.)", min_value=0, value=p["other_savings"], step=100)
with col_oth2:
    st.metric("Итого экономия на штрафах / мес", f"{other_savings * fleet_size:,.0f} ₽".replace(",", " "))


# ==========================================
# 3. МАТЕМАТИЧЕСКИЙ ПЕРЕСЧЕТ ДЛЯ ФИНАЛЬНЫХ СУММ
# ==========================================
total_capex = fleet_size * hardware_cost
total_opex_monthly = fleet_size * monthly_sub

# Расчет эффектов на 1 машину для верхней панели структуры
monthly_accident_saving_per_car = monthly_accident_saving_total / fleet_size
monthly_fuel_saving_per_car = monthly_fuel_saving_total / fleet_size

# Итоговые показатели по всему парку
fleet_monthly_saving = monthly_accident_saving_total + monthly_fuel_saving_total + (other_savings * fleet_size)
net_monthly_benefit = fleet_monthly_saving - total_opex_monthly

# Срок окупаемости
if net_monthly_benefit > 0:
    payback_period = total_capex / net_monthly_benefit
else:
    payback_period = float('inf')


# ==========================================
# 4. ЗАПОЛНЕНИЕ ВЕРХНИХ КОНТЕЙНЕРОВ (РЕЗУЛЬТАТЫ)
# ==========================================
with title_container:
    st.title("📊 Калькулятор окупаемости (ROI) видеоаналитики SKAI")
    st.markdown(f"Выбранный профиль техники: **{selected_preset}**")
    st.caption("Меняйте параметры внизу страницы — верхняя панель результатов и графики пересчитываются мгновенно.")
    st.markdown("---")

with metrics_container:
    st.subheader("💰 Экономический итог проекта")
    m1, m2, m3 = st.columns(3)
    m1.metric("Стартовые инвестиции (Capex)", f"{total_capex:,.0f} ₽".replace(",", " "))
    m2.metric("Чистая прибыль парка в месяц (после Opex)", f"{net_monthly_benefit:,.0f} ₽".replace(",", " "))
    
    if payback_period != float('inf'):
        m3.metric("Срок окупаемости системы", f"{payback_period:.1f} мес.")
    else:
        m3.metric("Срок окупаемости системы", "Проект не окупается при текущих настройках")
    st.markdown("---")

with effects_container:
    st.subheader("🔍 Структура ежемесячной экономии (на 1 автомобиль)")
    col_eff1, col_eff2, col_eff3 = st.columns(3)
    col_eff1.info(f"🛡️ **Предотвращение ДТП:**\n\n {monthly_accident_saving_per_car:,.0f} ₽ / мес.")
    col_eff2.info(f"⛽ **Экономия топлива:**\n\n {monthly_fuel_saving_per_car:,.0f} ₽ / мес.")
    col_eff3.info(f"🧾 **Штрафы и скрытые расходы:**\n\n {other_savings:,.0f} ₽ / мес.")
    
    st.markdown(f"**Полная экономия на весь автопарк ({fleet_size} ТС):** {fleet_monthly_saving:,.0f} ₽ в месяц (до вычета абонентской платы).")
    st.markdown("---")

with chart_container:
    st.subheader("📈 График кумулятивного денежного потока (36 месяцев)")
    
    months = np.arange(0, 37)
    cash_flow = []
    for m in months:
        if m == 0:
            cash_flow.append(-total_capex)
        else:
            cash_flow.append(cash_flow[m-1] + net_monthly_benefit)
            
    df_chart = pd.DataFrame({
        "Месяц": months,
        "Баланс проекта (₽)": cash_flow
    })
    
    st.line_chart(df_chart.set_index("Месяц"))