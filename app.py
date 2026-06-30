import streamlit as st
import pandas as pd
import numpy as np

# Настройка страницы
st.set_page_config(page_title="SKAI Платформа: Расширенный калькулятор TCO и ROI", layout="wide", page_icon="📊")

# ==========================================
# 1. БАЗА ДАННЫХ И ДЕФОЛТНЫЕ НАСТРОЙКИ ТС
# ==========================================
presets = {
    "🚛 Магистральный тягач (Фура)": {
        "fleet_size": 50, "mileage": 120000, "consumption": 32.0, "maintenance": 60000,
        "accidents_year": 8, "accident_cost": 800000,
        "video_capex": 120000, "video_opex": 2000, "video_eff": 55,
        "base_capex": 15000, "base_opex": 400, "base_eff_fuel": 8, "base_eff_to": 10, "base_eff_fines": 40, "base_eff_lease": 20, "base_eff_acc": 15,
        "safe_capex": 10000, "safe_opex": 500, "safe_eff_to": 15, "safe_eff_acc": 15,
        "fuel_capex": 25000, "fuel_opex": 600, "fuel_eff": 10
    },
    "🏗️ Самосвал / Тяжелая спецтехника": {
        "fleet_size": 30, "mileage": 45000, "consumption": 45.0, "maintenance": 90000,
        "accidents_year": 6, "accident_cost": 600000,
        "video_capex": 130000, "video_opex": 2000, "video_eff": 50,
        "base_capex": 15000, "base_opex": 400, "base_eff_fuel": 6, "base_eff_to": 8, "base_eff_fines": 30, "base_eff_lease": 15, "base_eff_acc": 10,
        "safe_capex": 10000, "safe_opex": 500, "safe_eff_to": 20, "safe_eff_acc": 10,
        "fuel_capex": 30000, "fuel_opex": 600, "fuel_eff": 12
    },
    "📦 Легкий коммерческий транспорт / Корпоративные авто": {
        "fleet_size": 40, "mileage": 60000, "consumption": 13.0, "maintenance": 35000,
        "accidents_year": 7, "accident_cost": 300000,
        "video_capex": 110000, "video_opex": 1800, "video_eff": 60,
        "base_capex": 12000, "base_opex": 350, "base_eff_fuel": 10, "base_eff_to": 12, "base_eff_fines": 60, "base_eff_lease": 30, "base_eff_acc": 20,
        "safe_capex": 8000, "safe_opex": 400, "safe_eff_to": 12, "safe_eff_acc": 20,
        "fuel_capex": 20000, "fuel_opex": 500, "fuel_eff": 8
    }
}

def fmt(val):
    return f"{val:,.0f}".replace(",", " ")

# ==========================================
# 2. СЕКЦИЯ САЙДБАРА: ОСНОВНЫЕ НАСТРОЙКИ
# ==========================================
st.sidebar.header("⚙️ Параметры и конфигурация")
st.sidebar.subheader("🚚 Состав и параметры ТС")

fuel_price = st.sidebar.number_input("Цена топлива (руб./литр)", min_value=1.0, value=65.0, step=1.0)
st.sidebar.markdown("---")

fleet_quantities = {}
custom_fleet_params = {}

default_qtys = {
    "🚛 Магистральный тягач (Фура)": 30,
    "🏗️ Самосвал / Тяжелая спецтехника": 10,
    "📦 Легкий коммерческий транспорт / Корпоративные авто": 15
}

for name, p_default in presets.items():
    qty = st.sidebar.number_input(f"{name} (кол-во, шт):", min_value=0, value=default_qtys[name], step=5)
    
    if qty > 0:
        fleet_quantities[name] = qty
        default_accidents = p_default["accidents_year"] * (qty / p_default["fleet_size"])
        
        with st.sidebar.expander(f"🛠️ Настройки: {name.split(' ')[1]}", expanded=False):
            mileage = st.number_input("Пробег 1 ТС в год (км)", min_value=1000, value=p_default["mileage"], step=5000, key=f"mil_{name}")
            consumption = st.number_input("Расход (л/100 км)", min_value=1.0, value=p_default["consumption"], step=0.5, key=f"cons_{name}")
            maintenance = st.number_input("ТО + расходники 1 ТС в год (руб.)", min_value=0, value=p_default["maintenance"], step=5000, key=f"maint_{name}")
            accidents = st.number_input("ДТП этой группы в год (шт)", min_value=0.0, value=float(default_accidents), step=0.5, key=f"acc_{name}")
            acc_cost = st.number_input("Прямой ущерб/франшиза 1 ДТП (руб.)", min_value=0, value=p_default["accident_cost"], step=50000, key=f"acost_{name}")
        
        custom_fleet_params[name] = {
            "qty": qty, "mileage": mileage, "consumption": consumption, "maintenance": maintenance,
            "accidents_year": accidents, "accident_cost": acc_cost,
            **{k: v for k, v in p_default.items() if "capex" in k or "opex" in k or "eff" in k}
        }
        st.sidebar.markdown("---")

total_fleet_size = sum(fleet_quantities.values())

if total_fleet_size == 0:
    st.sidebar.warning("⚠️ Укажите количество хотя бы для одного типа ТС.")
    st.stop()

# ==========================================
# 3. СЕКЦИЯ САЙДБАРА: TCO, ПЕРСОНАЛ И ЛИЗИНГ
# ==========================================
st.sidebar.subheader("💼 Управление TCO, персоналом и лизингом")

with st.sidebar.expander("🔍 Потери бэк-офиса, простои и лизинг", expanded=True):
    st.caption("Параметры для расчета скрытых издержек компании (модель EBITDA)")
    emp_salary = st.number_input("Затраты на 1 сотрудника/водителя в месяц (ФОТ+налоги)", value=100000, step=5000)
    emp_revenue = st.number_input("Месячный доход/выработка от 1 сотрудника на ТС", value=1200000, step=50000)
    
    st.markdown("**👥 Диспетчеризация и администрирование**")
    disp_salary = st.number_input("ФОТ 1 диспетчера/оператора парка в месяц", value=80000, step=5000)
    # Норматив: ориентировочно 1 диспетчер на 25 машин в базовом сценарии
    calculated_disp_qty = max(1.0, round(total_fleet_size / 25, 1))
    disp_qty = st.number_input("Текущее кол-во диспетчеров в штате (база)", value=float(calculated_disp_qty), step=0.5)
    
    st.markdown("**🚨 Издержки при инцидентах**")
    downtime_days = st.number_input("Средний простой ТС после ДТП (дней)", value=14, step=1)
    manager_hourly_rate = st.number_input("Стоимость 1 часа работы бэк-офиса", value=500, step=50)
    time_manager_accident = st.number_input("Время менеджера на 1 ДТП (часов)", value=8, step=1)
    
    st.markdown("**📜 Лизинг и штрафы**")
    lease_term = st.number_input("Стандартный срок лизинга (мес)", value=48, step=12)
    lease_return_cost = st.number_input("Выплаты лизинговой при возврате (на 1 ТС)", value=50000, step=5000)
    fines_per_car_year = st.number_input("Кол-во штрафов на 1 ТС в год (база)", value=12, step=2)
    fine_avg_cost = st.number_input("Средняя стоимость 1 штрафа (руб)", value=500, step=100)
    time_manager_fine = st.number_input("Время на обработку 1 штрафа (часов)", value=0.5, step=0.1)

st.sidebar.markdown("---")

# Расчет производных параметров TCO
working_days_month = 21.7
employee_daily_cost = emp_salary / working_days_month
employee_daily_revenue = emp_revenue / working_days_month

def get_total_accident_cost(direct_cost):
    downtime_loss = downtime_days * (employee_daily_cost + employee_daily_revenue)
    management_loss = time_manager_accident * manager_hourly_rate
    return direct_cost + downtime_loss + management_loss

fine_loss_per_car_month = (fines_per_car_year * (fine_avg_cost + (time_manager_fine * manager_hourly_rate))) / 12
lease_risk_per_car_month = lease_return_cost / lease_term
total_disp_fot_before = disp_qty * disp_salary

# Базовые финансовые показатели ДО внедрения
total_fuel_before = 0
total_maint_before = 0
total_accidents_year = 0
total_direct_accident_damage_before = 0
total_tco_accident_damage_before = 0

for name, cp in custom_fleet_params.items():
    q = cp["qty"]
    total_fuel_before += ((cp["mileage"] / 100 * cp["consumption"] * fuel_price) / 12) * q
    total_maint_before += (cp["maintenance"] / 12) * q
    total_accidents_year += cp["accidents_year"]
    total_direct_accident_damage_before += cp["accidents_year"] * cp["accident_cost"]
    total_tco_accident_damage_before += cp["accidents_year"] * get_total_accident_cost(cp["accident_cost"])

total_fines_loss_before = fine_loss_per_car_month * total_fleet_size
total_lease_risk_before = lease_risk_per_car_month * total_fleet_size

# ==========================================
# 4. СЕКЦИЯ САЙДБАРА: МОДУЛИ SKAI
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
    st.sidebar.warning("⚠️ Выберите хотя бы один модуль.")
    st.stop()

def get_weighted_value(field):
    # Безопасный фолбек, если поля нет в пресетах (например для новых сервисных модулей)
    vals = [cp[field] * cp["qty"] for cp in custom_fleet_params.values() if field in cp]
    return sum(vals) / total_fleet_size if vals else 0

total_capex = 0
total_opex_monthly = 0

direct_savings_dict = {}
tco_savings_dict = {}

st.sidebar.markdown("---")
st.sidebar.subheader("🔧 Тонкие настройки эффектов модулей")

# --- МОДУЛЬ: БАЗОВЫЙ МОНИТОРИНГ ---
if "Базовый Мониторинг" in selected_modules:
    with st.sidebar.expander("📍 Модуль: Базовый Мониторинг", expanded=True):
        b_capex = st.number_input("Capex трекера на 1 ТС", value=int(get_weighted_value("base_capex")), step=1000, key="b_cap")
        b_opex = st.number_input("Opex ПО на 1 ТС / мес", value=int(get_weighted_value("base_opex")), step=50, key="b_op")
        
        st.markdown("**📊 Целевые эффекты базового контроля:**")
        eff_fuel = st.slider("Сокращение пробега и расхода ГСМ (%)", 0.0, 25.0, float(get_weighted_value("base_eff_fuel")), step=0.5) / 100
        eff_to = st.slider("Сокращение избыточного износа и ТО (%)", 0.0, 25.0, float(get_weighted_value("base_eff_to")), step=0.5) / 100
        eff_fines = st.slider("Сокращение числа штрафов (%)", 0, 100, int(get_weighted_value("base_eff_fines")), step=5) / 100
        eff_lease = st.slider("Снижение выплат лизинговой (сохранение ТС) (%)", 0, 100, int(get_weighted_value("base_eff_lease")), step=5) / 100
        eff_acc = st.slider("Сокращение ДТП (контроль геозон) (%)", 0, 100, int(get_weighted_value("base_eff_acc")), step=5) / 100

        b_direct_saving = (total_fuel_before * eff_fuel) + (total_maint_before * eff_to) + ((total_direct_accident_damage_before / 12) * eff_acc)
        b_tco_saving = (total_fines_loss_before * eff_fines) + (total_lease_risk_before * eff_lease) + (((total_tco_accident_damage_before - total_direct_accident_damage_before) / 12) * eff_acc)
        
        total_capex += b_capex * total_fleet_size
        total_opex_monthly += b_opex * total_fleet_size
        direct_savings_dict["Базовый Мониторинг"] = b_direct_saving
        tco_savings_dict["Базовый Мониторинг"] = b_tco_saving

# --- МОДУЛЬ: СЕРВИС АНАЛИТИКИ И РЕАГИРОВАНИЯ ---
if "Сервис аналитики и реагирования" in selected_modules:
    with st.sidebar.expander("🎧 Сервис аналитики и реагирования", expanded=True):
        s_capex = st.number_input("Capex настройки интеграций и SLA", value=40000, step=10000, key="s_cap")
        s_opex = st.number_input("Opex ситуационного центра на 1 ТС / мес", value=900, step=100, key="s_op")
        
        st.markdown("**👥 Оптимизация операционной службы:**")
        s_eff_disp = st.slider("Сокращение затрат на ФОТ диспетчеров за счет аутсорсинга событий и контроля SLA (%)", 0, 100, 60, step=5) / 100
        
        # Экономия ФОТ диспетчеров относится к косвенным TCO-эффектам управления
        s_direct_saving = 0
        s_tco_saving = total_disp_fot_before * s_eff_disp
        
        total_capex += s_capex  # Фиксированная стоимость развертывания на весь проект
        total_opex_monthly += s_opex * total_fleet_size
        direct_savings_dict["Сервис аналитики и реагирования"] = s_direct_saving
        tco_savings_dict["Сервис аналитики и реагирования"] = s_tco_saving

# --- МОДУЛЬ: ВИДЕОАНАЛИТИКА ---
if "Видеоаналитика" in selected_modules:
    with st.sidebar.expander("👁️ Модуль: Видеоаналитика", expanded=True):
        v_capex = st.number_input("Capex оборудования на 1 ТС", value=int(get_weighted_value("video_capex")), step=5000, key="v_cap")
        v_opex = st.number_input("Opex лицензии на 1 ТС / мес", value=int(get_weighted_value("video_opex")), step=100, key="v_op")
        v_eff = st.slider("Снижение аварийности со SKAI (%)", 0, 100, int(get_weighted_value("video_eff")), step=5) / 100
        
        v_direct_saving = (total_direct_accident_damage_before / 12) * v_eff
        v_tco_saving = ((total_tco_accident_damage_before - total_direct_accident_damage_before) / 12) * v_eff
        
        total_capex += v_capex * total_fleet_size
        total_opex_monthly += v_opex * total_fleet_size
        direct_savings_dict["Видеоаналитика"] = v_direct_saving
        tco_savings_dict["Видеоаналитика"] = v_tco_saving

# --- МОДУЛЬ: БЕЗОПАСНОЕ ВОЖДЕНИЕ ---
if "Безопасное вождение" in selected_modules:
    with st.sidebar.expander("🛡️ Модуль: Безопасное вождение", expanded=True):
        sd_capex = st.number_input("Capex модуля на 1 ТС", value=int(get_weighted_value("safe_capex")), step=1000, key="sd_cap")
        sd_opex = st.number_input("Opex подписки на 1 ТС / мес", value=int(get_weighted_value("safe_opex")), step=50, key="sd_op")
        sd_eff_to = st.slider("Доп. экономия на ТО от бережной езды (%)", 0, 40, int(get_weighted_value("safe_eff_to")), step=5) / 100
        sd_eff_acc = st.slider("Доп. снижение ДТП от скоринга (%)", 0, 40, int(get_weighted_value("safe_eff_acc")), step=5) / 100
        
        sd_direct_saving = (total_maint_before * sd_eff_to) + ((total_direct_accident_damage_before / 12) * sd_eff_acc)
        sd_tco_saving = ((total_tco_accident_damage_before - total_direct_accident_damage_before) / 12) * sd_eff_acc
        
        total_capex += sd_capex * total_fleet_size
        total_opex_monthly += sd_opex * total_fleet_size
        direct_savings_dict["Безопасное вождение"] = sd_direct_saving
        tco_savings_dict["Безопасное вождение"] = sd_tco_saving

# --- МОДУЛЬ: КОНТРОЛЬ ТОПЛИВА ---
if "Контроль топлива" in selected_modules:
    with st.sidebar.expander("⛽ Модуль: Контроль топлива", expanded=True):
        f_capex = st.number_input("Capex ДУТ на 1 ТС", value=int(get_weighted_value("fuel_capex")), step=2000, key="f_cap")
        f_opex = st.number_input("Opex ML-модуля на 1 ТС / мес", value=int(get_weighted_value("fuel_opex")), step=50, key="f_op")
        f_eff = st.slider("Прямая экономия ГСМ (сливы/карты) (%)", 0.0, 25.0, float(get_weighted_value("fuel_eff")), step=0.5) / 100
        
        f_direct_saving = total_fuel_before * f_eff
        
        total_capex += f_capex * total_fleet_size
        total_opex_monthly += f_opex * total_fleet_size
        direct_savings_dict["Контроль топлива"] = f_direct_saving
        tco_savings_dict["Контроль топлива"] = 0

# ==========================================
# 5. ОСНОВНАЯ ЧАСТЬ СТРАНИЦЫ (ИНТЕРФЕЙС)
# ==========================================
st.title("📊 SKAI Платформа: Расширенный калькулятор TCO & ROI")
fleet_structure_str = " + ".join([f"**{qty}** {name.split(' (')[0]}" for name, qty in fleet_quantities.items()])
st.markdown(f"Текущая структура парка: {fleet_structure_str} | Всего: **{total_fleet_size} ТС**")
st.markdown("---")

# Главный переключатель режима отображения
calc_mode = st.radio(
    "Выбор аналитической модели:",
    ["🔹 Только Прямой Экономический Эффект (Классический)", "🔥 Полный TCO Расчет (С учетом скрытых потерь, лизинга и оптимизации ФОТ)"],
    horizontal=True
)

if "Только Прямой" in calc_mode:
    monthly_saving = sum(direct_savings_dict.values())
    mode_title = "Прямого эффекта"
else:
    monthly_saving = sum(direct_savings_dict.values()) + sum(tco_savings_dict.values())
    mode_title = "Полного TCO расчета"

net_monthly_benefit = monthly_saving - total_opex_monthly
payback_period = total_capex / net_monthly_benefit if net_monthly_benefit > 0 else float('inf')

# Блок финансовых метрик
st.subheader("💰 Экономические показатели проекта")
m1, m2, m3 = st.columns(3)
m1.metric("Стартовые инвестиции (Capex)", f"{fmt(total_capex)} ₽")
m2.metric("Чистая прибыль парка / мес (после Opex)", f"{fmt(net_monthly_benefit)} ₽")
m3.metric("Срок окупаемости системы", f"{payback_period:.1f} мес." if payback_period != float('inf') else "Проект не окупается")

st.markdown("---")

# Сводный детализированный анализ факторов влияния
st.subheader("📋 Детализация влияния факторов на экономику автопарка (в месяц)")

tco_table_data = [
    ["Затраты на ГСМ (Топливо)", fmt(total_fuel_before), fmt(sum([v for k, v in direct_savings_dict.items() if k in ["Базовый Мониторинг", "Контроль топлива"]])), "Прямой эффект"],
    ["Затраты на ТО и расходники", fmt(total_maint_before), fmt(sum([v for k, v in direct_savings_dict.items() if k in ["Базовый Мониторинг", "Безопасное вождение"]])), "Прямой эффект"],
    ["Прямой ущерб от аварий / франшизы", fmt(total_direct_accident_damage_before / 12), fmt(sum(direct_savings_dict.values()) - (direct_savings_dict.get("Контроль топлива", 0) + total_fuel_before * (eff_fuel if "Базовый Мониторинг" in selected_modules else 0) if "Базовый Мониторинг" in selected_modules else 0)), "Прямой эффект"],
    ["Потери от простоя персонала и ТС при ДТП", fmt((total_tco_accident_damage_before - total_direct_accident_damage_before) / 12), fmt(sum([v for k, v in tco_savings_dict.items() if k in ["Базовый Мониторинг", "Видеоаналитика", "Безопасное вождение"]])), "Косвенный (TCO)"],
    ["Расходы на собственный штат диспетчеров (ФОТ)", fmt(total_disp_fot_before), fmt(tco_savings_dict.get("Сервис аналитики и реагирования", 0)), "Косвенный (TCO)"],
    ["Администрирование и оплата штрафов бэк-офисом", fmt(total_fines_loss_before), fmt(tco_savings_dict.get("Базовый Мониторинг", 0) if "Базовый Мониторинг" in selected_modules else 0), "Косвенный (TCO)"],
    ["Риски выплат лизинговой (износ/возврат)", fmt(total_lease_risk_before), fmt(tco_savings_dict.get("Базовый Мониторинг", 0) * 0.5 if "Базовый Мониторинг" in selected_modules else 0), "Косвенный (TCO)"]
]

df_tco = pd.DataFrame(tco_table_data, columns=["Фактор / Статья расходов", "Базовые затраты до внедрения (₽/мес)", "Прогноз экономии от SKAI (₽/мес)", "Тип фактора"])
st.dataframe(df_tco, use_container_width=True, hide_index=True)

st.markdown("---")

# График накопленного итога
st.subheader(f"📈 Накопительный финансовый результат за 36 месяцев ({mode_title})")

months = np.arange(1, 37)
accumulated_benefit = []
for m in months:
    accumulated_benefit.append((net_monthly_benefit * m) - total_capex)

df_chart = pd.DataFrame({"Чистый финансовый эффект (накопительный)": accumulated_benefit}, index=months)
df_chart.index.name = "Месяц"
st.line_chart(df_chart)

st.markdown(f"""
> **💡 Анализ добавленной ценности Ситуационного центра:**
> * **Защита ФОТ диспетчеров:** Включение Сервиса аналитики и реагирования переносит фокус расчетов на внутреннюю операционную эффективность. Экономия на администрировании событий штатными сотрудниками напрямую отражается в строке «Расходы на собственный штат диспетчеров».
> * **Сквозная синергия:** Оцифровка базовой стоимости диспетчеризации позволяет показать клиенту, что SKAI работает не просто как софт, а как полноценный инструмент оптимизации процессов бэк-офиса.
""")