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
st.caption("Выберите готовый шаблон под ваш тип транспорта (параметры подставятся автоматически) или скорректируйте любые цифры вручную.")

# База данных пресетов (средние рыночные показатели)
presets = {
    "🚛 Магистральный тягач (Фура)": {
        "fleet_size": 50,
        "mileage": 120000,
        "consumption": 32.0,
        "accident_rate": 15.0,  # 15% парка в год имеют ДТП
        "accident_cost": 800000, # Тяжелые последствия на трассе
        "hardware_cost": 160000,
        "monthly_sub": 2000,
        "accident_reduction": 55,
        "fuel_economy": 4.0,
        "other_savings": 2000
    },
    "🏗️ Самосвал / Тяжелая спецтехника": {
        "fleet_size": 30,
        "mileage": 45000,       # Пробег меньше, но моточасы и износ выше
        "consumption": 45.0,
        "accident_rate": 25.0,  # Выше риски на объектах/карьерах
        "accident_cost": 600000,
        "hardware_cost": 170000, # Требуются антивандальные / защищенные камеры
        "monthly_sub": 2000,
        "accident_reduction": 50,
        "fuel_economy": 5.0,     # Высокий потенциал экономии на холостом ходу
        "other_savings": 1500
    },
    "📦 Легкий коммерческий транспорт (LCV / Газель / Доставка)": {
        "fleet_size": 40,
        "mileage": 60000,       # Активная городская езда
        "consumption": 13.0,
        "accident_rate": 20.0,  # Частые мелкие ДТП в городе
        "accident_cost": 300000,
        "hardware_cost": 130000, # Меньше камер / проще монтаж
        "monthly_sub": 1800,
        "accident_reduction": 60, # Городские засыпания и телефоны отлично ловятся DSM
        "fuel_economy": 3.0,
        "other_savings": 1200
    }
}

# Выбор пресета ТС
selected_preset = st.selectbox("Шаблон под тип транспортного средства:", list(presets.keys()))
p = presets[selected_preset]

# Вывод полей для ручной корректировки
col_tech, col_costs = st.columns(2)

with col_tech:
    st.subheader("Характеристики автопарка")
    fleet_size = st.number_input("Размер автопарка (шт.)", min_value=1, value=p["fleet_size"], step=5)
    annual_mileage = st.number_input("Средний пробег 1 авто в год (км)", min_value=1000, value=p["mileage"], step=5000)
    fuel_consumption = st.number_input("Средний расход топлива (л/100 км)", min_value=1.0, value=p["consumption"], step=0.5)
    fuel_price = st.number_input("Цена топлива (руб./литр)", min_value=1.0, value=65.0, step=1.0)
    
    st.subheader("Статистика рисков и ДТП")
    accident_rate = st.slider("Доля машин, попадающих в ДТП за год (%)", min_value=0.0, max_value=100.0, value=p["accident_rate"], step=1.0) / 100
    accident_cost = st.number_input("Средний ущерб от одного ДТП (руб.)", min_value=1000, value=p["accident_cost"], step=50000)

with col_costs:
    st.subheader("Стоимость решения SKAI")
    hardware_cost = st.number_input("Стоимость комплекта + монтаж на 1 авто (руб.)", min_value=0, value=p["hardware_cost"], step=5000)
    monthly_sub = st.number_input("Абонентская плата за 1 авто в месяц (руб.)", min_value=0, value=p["monthly_sub"], step=100)
    
    st.subheader("Целевые эффекты видеоаналитики SKAI")
    accident_reduction = st.slider("Снижение аварийности (DSM/ADAS эффекты, %)", min_value=0, max_value=100, value=p["accident_reduction"], step=5) / 100
    fuel_economy = st.slider("Экономия топлива за счет плавного вождения (%)", min_value=0.0, max_value=20.0, value=p["fuel_economy"], step=0.5) / 100
    other_savings = st.number_input("Экономия на штрафах и скрытых издержках на 1 авто в месяц (руб.)", min_value=0, value=p["other_savings"], step=100)


# ==========================================
# 3. ЛОГИКА МАТЕМАТИЧЕСКОГО РАСЧЕТА
# ==========================================
total_capex = fleet_size * hardware_cost
total_opex_monthly = fleet_size * monthly_sub

# Экономия на ДТП в месяц на 1 авто
monthly_accident_saving_per_car = (accident_rate * accident_cost * accident_reduction) / 12

# Экономия на топливе в месяц на 1 авто
monthly_fuel_cost_per_car = (annual_mileage / 100 * fuel_consumption * fuel_price) / 12
monthly_fuel_saving_per_car = monthly_fuel_cost_per_car * fuel_economy

# Суммарные финансовые результаты
monthly_total_saving_per_car = monthly_accident_saving_per_car + monthly_fuel_saving_per_car + other_savings
fleet_monthly_saving = monthly_total_saving_per_car * fleet_size
net_monthly_benefit = fleet_monthly_saving - total_opex_monthly

# Расчет окупаемости
if net_monthly_benefit > 0:
    payback_period = total_capex / net_monthly_benefit
else:
    payback_period = float('inf')


# ==========================================
# 4. ЗАПОЛНЕНИЕ ВЕРХНИХ КОНТЕЙНЕРОВ (РЕЗУЛЬТАТЫ)
# ==========================================
with title_container:
    st.title("📊 Калькулятор окупаемости (ROI) видеоаналитики SKAI")
    st.markdown(f"Текущий расчет построен для типа ТС: **{selected_preset}**")
    st.caption("Результаты пересчитываются мгновенно при изменении любых параметров на панели настроек внизу страницы.")
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
    
    st.markdown(f"**Полная экономия на 1 автомобиль:** {monthly_total_saving_per_car:,.0f} ₽ в месяц (до вычета абонентской платы).")
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
    st.caption("Точка, где график пересекает нулевую отметку и уходит вверх — это точный момент полной окупаемости оборудования.")