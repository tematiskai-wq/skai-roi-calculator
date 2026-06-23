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
# 2. БАЗОВАЯ ДАННЫХ И ПРЕСЕТЫ ПО ТИПАМ ТС
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

# ==========================================
# 3. ПАНЕЛЬ НАСТРОЕК (НИЗ СТРАНИЦЫ)
# ==========================================
st.header("⚙️ Панель конфигурации проекта")

# Общие глобальные параметры
col_g1, col_g2 = st.columns(2)
with col_g1:
    selected_preset = st.selectbox("1. Выберите шаблон под тип ТС:", list(presets.keys()))
    p = presets[selected_preset]
with col_g2:
    fleet_size = st.number_input("2. Размер автопарка (шт.):", min_value=1, value=p["fleet_size"], step=5)

st.markdown("---")

# СЕКЦИЯ: ВЫБОР МОДУЛЕЙ СКАЙ ПЛАТФОРМЫ
st.subheader("🧩 Конструктор модулей SKAI Платформы")
st.caption("Отметьте модули, которые входят в периметр проекта. Ниже откроются только релевантные для них настройки.")

available_modules = [
    "Видеоаналитика",
    "Базовый Мониторинг",
    "Безопасное вождение",
    "Контроль топлива",
    "Сервис аналитики и реагирования"
]

# Создаем удобную сетку чекбоксов для выбора модулей
m_cols = st.columns(5)
selected_modules = []
for i, module_name in enumerate(available_modules):
    with m_cols[i]:
        # По умолчанию выберем Видеоаналитику и Базовый мониторинг для демонстрации
        default_checked = True if module_name in ["Видеоаналитика", "Базовый Мониторинг"] else False
        if st.checkbox(module_name, value=default_checked):
            selected_modules.append(module_name)

if not selected_modules:
    st.warning("⚠️ Выберите хотя бы один модуль SKAI Платформы для расчета окупаемости.")
    st.stop()

st.markdown("---")

# ПОДРАЗДЕЛ: ГЛОБАЛЬНЫЕ ТЕКУЩИЕ ПОКАЗАТЕЛИ ПАРКА
st.subheader("📊 Базовые операционные показатели парка")
col_b1, col_b2, col_b3, col_b4 = st.columns(4)
with col_b1:
    annual_mileage = st.number_input("Пробег 1 ТС в год (км)", min_value=1000, value=p["mileage"], step=5000)
with col_b2:
    fuel_consumption = st.number_input("Расход топлива (л/100 км)", min_value=1.0, value=p["consumption"], step=0.5)
with col_b3:
    fuel_price = st.number_input("Цена топлива (руб./литр)", min_value=1.0, value=65.0, step=1.0)
with col_b4:
    annual_maintenance_cost = st.number_input("Затраты на ТО и ремонт 1 ТС в год (руб.)", min_value=0, value=p["maintenance"], step=5000)

# Фоновые расчеты затрат до внедрения
fleet_monthly_fuel_before = ((annual_mileage / 100 * fuel_consumption * fuel_price) / 12) * fleet_size
fleet_monthly_maintenance_before = (annual_maintenance_cost / 12) * fleet_size

# Инициализация переменных затрат и эффектов
total_capex = 0
total_opex_monthly = 0
monthly_savings_dict = {}

# Данные для сводной таблицы
current_params_table = [
    ["Размер автопарка", f"{fleet_size}", "шт."],
    ["Тип ТС (Профиль)", selected_preset.split(" ")[1], "-"],
    ["Пробег 1 ТС в год", f"{annual_mileage:,.0f}", "км"],
    ["Базовый расход топлива", f"{fuel_consumption}", "л/100 км"],
    ["Стоимость топлива", f"{fuel_price}", "руб./л"],
    ["Затраты на ТО 1 ТС в год", f"{annual_maintenance_cost:,.0f}", "руб."]
]

# ==========================================
# 4. ДИНАМИЧЕСКИЕ НАСТРОЙКИ ПО КАЖДОМУ МОДУЛЮ
# ==========================================

# Модуль 1: Видеоаналитика
if "Видеоаналитика" in selected_modules:
    with st.expander("👁️ Настройки модуля: Видеоаналитика", expanded=True):
        st.caption("ADAS/DSM детекция опасных состояний, засыпания, отвлечения внимания водителя.")
        c1, c2, c3, c4 = st.columns(4)
        with c1: v_capex = st.number_input("Capex: Оборудование + монтаж на 1 ТС (Видео)", value=p["video_capex"], step=5000)
        with c2: v_opex = st.number_input("Opex: Лицензия в месяц за 1 ТС (Видео)", value=p["video_opex"], step=100)
        with c3: accidents_year = st.number_input("Количество ДТП в автопарке в год (всего шт.)", min_value=0, value=p["accidents_year"], step=1)
        with c4: accident_cost = st.number_input("Средний ущерб от одного ДТП (руб.)", min_value=0, value=p["accident_cost"], step=50000)
        
        v_eff = st.slider("Снижение аварийности благодаря SKAI ADAS/DSM (%)", min_value=0, max_value=100, value=p["video_eff"], step=5) / 100
        
        # Расчет эффекта видеоаналитики
        fleet_monthly_accident_before = (accidents_year * accident_cost) / 12
        v_saving = fleet_monthly_accident_before * v_eff
        
        total_capex += v_capex * fleet_size
        total_opex_monthly += v_opex * fleet_size
        monthly_savings_dict["Видеоаналитика"] = v_saving
        
        current_params_table.extend([
            ["Количество ДТП в парке в год", f"{accidents_year}", "шт."],
            ["Средний ущерб от 1 ДТП", f"{accident_cost:,.0f}", "руб."],
            ["Эффективность снижения ДТП (Видео)", f"{v_eff*100:.0f}", "%"]
        ])

# Модуль 2: Базовый Мониторинг
if "Базовый Мониторинг" in selected_modules:
    with st.expander("📍 Настройки модуля: Базовый Мониторинг", expanded=True):
        st.caption("Контроль маршрутов, геозоны, исключение «левых» рейсов и нецелевого использования ТС.")
        c1, c2, c3 = st.columns(3)
        with c1: b_capex = st.number_input("Capex: Оборудование + монтаж на 1 ТС (Мониторинг)", value=p["base_capex"], step=1000)
        with c2: b_opex = st.number_input("Opex: ПО в месяц за 1 ТС (Мониторинг)", value=p["base_opex"], step=50)
        with c3: b_eff = st.slider("Сокращение нецелевого пробега и простоев (%)", min_value=0.0, max_value=25.0, value=p["base_eff"], step=0.5) / 100
        
        # Базовый мониторинг сокращает общий пробег, уменьшая траты на топливо и пропорционально износ (ТО)
        b_saving = (fleet_monthly_fuel_before + fleet_monthly_maintenance_before) * b_eff
        
        total_capex += b_capex * fleet_size
        total_opex_monthly += b_opex * fleet_size
        monthly_savings_dict["Базовый Мониторинг"] = b_saving
        
        current_params_table.extend([
            ["Сокращение нецелевого пробега", f"{b_eff*100:.1f}", "%"]
        ])

# Модуль 3: Безопасное вождение
if "Безопасное вождение" in selected_modules:
    with st.expander("🛡️ Настройки модуля: Безопасное вождение", expanded=True):
        st.caption("Телематический скоринг, фиксация резких ускорений, торможений и опасных перестроений.")
        c1, c2, c3, c4 = st.columns(4)
        with c1: sd_capex = st.number_input("Capex: Модуль на 1 ТС (Безопасность)", value=p["safe_capex"], step=1000)
        with c2: sd_opex = st.number_input("Opex: Подписка в месяц за 1 ТС (Безопасность)", value=p["safe_opex"], step=50)
        with c3: sd_eff_to = st.slider("Экономия на ремонте/ТО за счет бережной езды (%)", min_value=0, max_value=40, value=p["safe_eff_to"], step=5) / 100
        with c4: sd_eff_acc = st.slider("Доп. снижение ДТП за счет контроля ПДД (%)", min_value=0, max_value=40, value=p["safe_eff_acc"], step=5) / 100
        
        # Бережное вождение снижает затраты на ТО, а также вносит вклад в предотвращение ДТП
        sd_saving_to = fleet_monthly_maintenance_before * sd_eff_to
        # Если видеоаналитики нет, то считаем от полной базы ДТП, если есть — от остатка после видеоаналитики
        base_accident_for_sd = (fleet_monthly_accident_before - v_saving) if "Видеоаналитика" in selected_modules else fleet_monthly_accident_before
        sd_saving_acc = base_accident_for_sd * sd_eff_acc
        
        sd_saving = sd_saving_to + sd_saving_acc
        total_capex += sd_capex * fleet_size
        total_opex_monthly += sd_opex * fleet_size
        monthly_savings_dict["Безопасное вождение"] = sd_saving
        
        current_params_table.extend([
            ["Экономия на ТО от стиля езды", f"{sd_eff_to*100:.0f}", "%"],
            ["Доп. снижение ДТП (Скоринг)", f"{sd_eff_acc*100:.0f}", "%"]
        ])

# Модуль 4: Контроль топлива
if "Контроль топлива" in selected_modules:
    with st.expander("⛽ Настройки модуля: Контроль топлива", expanded=True):
        st.caption("ML-аналитика заправок, выявление скрытых сливов, недоливов на АЗС и махинаций с топливными картами.")
        c1, c2, c3 = st.columns(3)
        with c1: f_capex = st.number_input("Capex: ДУТ + тарировка на 1 ТС (Топливо)", value=p["fuel_capex"], step=2000)
        with c2: f_opex = st.number_input("Opex: ML-модуль анализа ГСМ / мес за 1 ТС", value=p["fuel_opex"], step=50)
        with c3: f_eff = st.slider("Прямая экономия ГСМ (исключение махинаций и сливов) (%)", min_value=0.0, max_value=25.0, value=p["fuel_eff"], step=0.5) / 100
        
        f_saving = fleet_monthly_fuel_before * f_eff
        total_capex += f_capex * fleet_size
        total_opex_monthly += f_opex * fleet_size
        monthly_savings_dict["Контроль топлива"] = f_saving
        
        current_params_table.extend([
            ["Экономия ГСМ от контроля сливов", f"{f_eff*100:.1f}", "%"]
        ])

# Модуль 5: Сервис аналитики и реагирования
if "Сервис аналитики и реагирования" in selected_modules:
    with st.expander("🎧 Настройки: Сервис аналитики и реагирования", expanded=True):
        st.caption("Аутсорсинг Ситуационного центра SKAI: разбор инцидентов экспертами, регулярные заказные отчеты.")
        c1, c2, c3 = st.columns(3)
        with c1: s_capex = st.number_input("Capex: Настройка интеграции (Сервис)", value=p["service_capex"], step=1000)
        with c2: s_opex = st.number_input("Opex: Сопровождение диспетчерами / мес за 1 ТС", value=p["service_opex"], step=100)
        with c3: s_eff_val = st.number_input("Снижение скрытых издержек на 1 ТС в месяц (штрафы, администрирование) (руб.)", value=p["service_eff"], step=100)
        
        s_saving = s_eff_val * fleet_size
        total_capex += s_capex * fleet_size
        total_opex_monthly += s_opex * fleet_size
        monthly_savings_dict["Сервис аналитики и реагирования"] = s_saving
        
        current_params_table.extend([
            ["Снижение скрытых издержек на 1 ТС", f"{s_eff_val:,.0f}", "руб./мес."]
        ])


# ==========================================
# 5. МАТЕМАТИЧЕСКИЙ ПЕРЕСЧЕТ РЕЗУЛЬТАТОВ
# ==========================================
fleet_monthly_saving = sum(monthly_savings_dict.values())
net_monthly_benefit = fleet_monthly_saving - total_opex_monthly

if net_monthly_benefit > 0:
    payback_period = total_capex / net_monthly_benefit
else:
    payback_period = float('inf')


# ==========================================
# 6. ЗАПОЛНЕНИЕ ВЕРХНИХ КОНТЕЙНЕРОВ (РЕЗУЛЬТАТЫ И ГРАФИКИ)
# ==========================================
with title_container:
    st.title("📊 SKAI платформа: калькулятор окупаемости (ROI)")
    st.markdown(f"Выбранный профиль техники: **{selected_preset}** | Активных модулей платформы: **{len(selected_modules)}**")
    st.caption("Настраивайте параметры и состав платформы внизу страницы — результаты обновляются налету.")
    st.markdown("---")

with metrics_container:
    st.subheader("💰 Экономический итог проекта")
    m1, m2, m3 = st.columns(3)
    m1.metric("Стартовые инвестиции (Capex)", f"{total_capex:,.0f} ₽".replace(",", " "))
    m2.metric("Чистая прибыль парка в месяц (после Opex)", f"{net_monthly_benefit:,.0f} ₽".replace(",", " "))
    
    if payback_period != float('inf'):
        m3.metric("Срок окупаемости платформы", f"{payback_period:.1f} мес.")
    else:
        m3.metric("Срок окупаемости платформы", "Проект не окупается при текущих настройках")
    st.markdown("---")

with table_container:
    st.subheader("📋 Сводная таблица текущих показателей расчета")
    df_params = pd.DataFrame(current_params_table, columns=["Параметр расчета", "Текущее значение", "Ед. изм."])
    st.dataframe(df_params, use_container_width=True, hide_index=True)
    st.markdown("---")

with chart_container:
    st.subheader("📈 График кумулятивного эффекта и баланса проекта (36 месяцев)")
    st.caption("Линия баланса показывает окупаемость с учетом стартовых затрат. Линии модулей показывают чистую накопленную экономию от каждого решения (кликните на имя в легенде, чтобы спрятать линию).")
    
    months = np.arange(0, 37)
    chart_data_dict = {"Месяц": months}
    
    # 1. Считаем общий баланс проекта (минус капекс на старте + рост прибыли)
    project_balance = []
    for m in months:
        if m == 0:
            project_balance.append(-total_capex)
        else:
            project_balance.append(project_balance[m-1] + net_monthly_benefit)
    chart_data_dict["Общий баланс проекта (с учетом затрат)"] = project_balance
    
    # 2. Добавляем на график индивидуальные кумулятивные кривые экономии по каждому продукту
    for module_name, monthly_save_val in monthly_savings_dict.items():
        chart_data_dict[f"Эффект: {module_name}"] = [monthly_save_val * m for m in months]
        
    df_chart = pd.DataFrame(chart_data_dict).set_index("Месяц")
    st.line_chart(df_chart)