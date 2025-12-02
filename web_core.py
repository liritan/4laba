import os
import base64
import io
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
try:
    from labellines import labelLines
except ImportError:
    def labelLines(*args, **kwargs):
        return None
from scipy.integrate import odeint
from scipy import interpolate
from functions import pend, F1, F2, F3, F4, F5
from radar_diagram import RadarDiagram

# Исправленные метки для 8 переменных АТС (согласно документу)
U_LABELS = [
    "X₁: Среднее количество нарушений инструкций пилотами",
    "X₂: Доля частных судов в авиации", 
    "X₃: Показатель активности органов контроля за оборотом контрафакта",
    "X₄: Количество сотрудников в метеорологических службах",
    "X₅: Катастрофы из-за метеоусловий",
    "X₆: Катастрофы из-за технических неисправностей",
    "X₇: Катастрофы из-за человеческого фактора",
    "X₈: Общее количество катастроф"
]

# Внешние факторы (линейные функции)
F_FUNCTIONS = [F1, F2, F3, F4, F5]

def _fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('ascii')

def smooth_data(values, window_size=5):
    if len(values) < window_size:
        return values
    window = np.ones(window_size) / window_size
    smoothed = np.convolve(values, window, mode='same')
    half_window = window_size // 2
    for i in range(half_window):
        smoothed[i] = np.mean(values[:i*2+1])
        smoothed[-(i+1)] = np.mean(values[-(i*2+1):])
    return smoothed

def normalize_line_for_plot(values, threshold_min=0.05, threshold_max=0.95):
    if len(values) == 0:
        return values
    min_val = np.min(values)
    max_val = np.max(values)
    if min_val < 0 or max_val > 1:
        if max_val - min_val > 0:
            normalized = 0.1 + 0.8 * (values - min_val) / (max_val - min_val)
        else:
            normalized = np.full_like(values, 0.5)
        return np.clip(normalized, 0.1, 0.9)
    else:
        return values

def normalize_for_radar(values, restrictions=None):
    if len(values) == 0:
        return values
    smoothed = smooth_data(values, window_size=3)
    if restrictions is not None:
        capped_values = np.minimum(smoothed, restrictions)
        min_val = np.min(capped_values)
        max_val = np.max(capped_values)
        if max_val - min_val > 0:
            normalized = 0.05 + 0.9 * (capped_values - min_val) / (max_val - min_val)
        else:
            normalized = capped_values
        return np.clip(normalized, 0.05, 0.95)
    else:
        min_val = np.min(smoothed)
        max_val = np.max(smoothed)
        if max_val > 0.95 or min_val < 0.05:
            if max_val - min_val > 0:
                normalized = 0.05 + 0.9 * (smoothed - min_val) / (max_val - min_val)
            else:
                normalized = smoothed
            return np.clip(normalized, 0.05, 0.95)
        else:
            return smoothed

def create_smooth_line(t_original, values, num_points=1000):
    if len(t_original) < 4:
        return t_original, values
    try:
        interp_func = interpolate.interp1d(t_original, values, kind='cubic', fill_value="extrapolate")
        t_smooth = np.linspace(t_original[0], t_original[-1], num_points)
        values_smooth = interp_func(t_smooth)
        return t_smooth, values_smooth
    except:
        return t_original, values

def draw_factors(t, factors):
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Используем фиксированные названия внешних факторов из документа
    line_labels = ["F₁", "F₂", "F₃", "F₄", "F₅"]
    legend_labels = [
        "F₁:0,63+0,37t",
        "F₂:1-0,23t", 
        "F₃:1-0,33t",
        "F₄:0,51+0,46t",
        "F₅:0,6+0,4t"
    ]



    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    for i, (F_func, color, line_label) in enumerate(zip(F_FUNCTIONS, colors, line_labels)):
        y_values = []
        for v in t:
            y_values.append(F_func(v, factors[i]))
        y_values = np.array(y_values)
        
        t_smooth, y_smooth = create_smooth_line(t, y_values)
        line, = ax.plot(t_smooth, y_smooth, color=color, label=line_label, linewidth=2.5, antialiased=True, alpha=0.8)
        
        if len(t_smooth) >= 10:
            x_pos = t_smooth[-10]
            y_pos = y_smooth[-10]
        else:
            x_pos = t_smooth[-1]
            y_pos = y_smooth[-1]
            
        ax.text(
            x_pos, y_pos, line_label,
            color=color,
            fontsize=8,
            verticalalignment='center',
            horizontalalignment='left',
            bbox=dict(facecolor='white', edgecolor='none', alpha=0.6, pad=0.3)
        )
    
    ax.set_xlabel("Время (t)")
    ax.set_ylabel("Значения")
    ax.set_title("Графики возмущений")
    
    # Создаем легенду с описанием
    from matplotlib.lines import Line2D
    legend_elements = []
    for i in range(len(legend_labels)):
        legend_elements.append(Line2D([0], [0], color=colors[i], lw=2, label=legend_labels[i]))
    
    ax.legend(handles=legend_elements, fontsize=8, loc='upper left', bbox_to_anchor=(0, 1))
    
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1.5)
    plt.tight_layout()
    return fig

def create_graphics(t, data, factors):
    figs_b64 = []
    
    # Словарь для нижних индексов
    subscript_numbers = {
        1: '₁', 2: '₂', 3: '₃', 4: '₄', 5: '₅', 6: '₆', 7: '₇', 8: '₈'
    }
    
    # Нормализация данных для отображения
    normalized_data = np.zeros_like(data)
    for i in range(8):
        y_data = np.maximum(0.01, data[:, i])
        normalized_data[:, i] = normalize_line_for_plot(y_data)
    
    # График всех 8 переменных
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    colors = plt.cm.tab10(np.linspace(0, 1, 8))
    
    for i in range(8):
        y_data = normalized_data[:, i]
        label = f"X{subscript_numbers[i+1]}"
        ax1.plot(t, y_data, color=colors[i], label=label, linewidth=2.0, antialiased=True, alpha=0.8)
        
        if len(t) > 0:
            x_pos = t[len(t)//2]
            y_pos = y_data[len(y_data)//2]
            ax1.text(x_pos, y_pos, label, color=colors[i], fontsize=8,
                     verticalalignment='center', horizontalalignment='left',
                     bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=0.3))
    
    ax1.set_xlabel("Время (t)")
    ax1.set_ylabel("Значения характеристик")
    ax1.set_title("Характеристики X₁–X₈")
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 1.0)
    figs_b64.append(_fig_to_base64(fig1))
    plt.close(fig1)
    
    # График внешних факторов
    fig2 = draw_factors(t, factors)
    figs_b64.append(_fig_to_base64(fig2))
    plt.close(fig2)
    
    return figs_b64

def draw_radar_series(data, initial_equations, restrictions):
    radar = RadarDiagram()
    imgs = []
    normalized_initial = normalize_for_radar(np.array(initial_equations), restrictions)
    time_points = [int(len(data) / 4), int(len(data) / 2), int(len(data) * 3 / 4), -1]
    normalized_points = []
    for point_idx in time_points:
        point_data = data[point_idx, :]
        normalized_point = normalize_for_radar(point_data, restrictions)
        normalized_points.append(normalized_point)
    labels = [f"X$_{i+1}$" for i in range(8)]
    titles = [
        "Характеристики системы в начальный момент времени",
        "Характеристики системы при t=0.25",
        "Характеристики системы при t=0.5",
        "Характеристики системы при t=0.75",
        "Характеристики системы при t=1"
    ]
    imgs.append(base64.b64encode(radar.draw_bytes(normalized_initial, labels, titles[0], restrictions, normalized_initial)).decode('ascii'))
    for i, pt in enumerate(normalized_points):
        imgs.append(base64.b64encode(radar.draw_bytes(pt, labels, titles[i+1], restrictions, normalized_initial)).decode('ascii'))
    return imgs

def run_simulation(initial_equations, factors, equations, restrictions):
    # Убедимся, что initial_equations имеет 8 элементов
    init_eq = np.array(initial_equations[:8], dtype=float)
    
    # Добавим небольшой шум для устойчивости
    noise = np.random.uniform(-0.05, 0.05, size=8)
    init_eq = np.clip(init_eq + noise, 0.05, 0.95)
    
    # Временной интервал 0-1 (нормированные годы от 2011 до 2025)
    # t=0 соответствует 2011 году, t=1 соответствует 2025 году
    t = np.linspace(0, 1, 50)
    
    # Решение системы уравнений
    data_sol = odeint(pend, init_eq, t, args=(factors, equations))
    data_sol = np.maximum(data_sol, 0)
    
    # Создание графиков
    figure_b64 = create_graphics(t, data_sol, factors)
    
    # Создание радарных диаграмм
    radar_imgs = draw_radar_series(data_sol, initial_equations[:8], restrictions[:8])
    
    return {
        'images_b64': {
            'figure1': figure_b64[0],
            'figure2': figure_b64[1],
            'diagram1': radar_imgs[0],
            'diagram2': radar_imgs[1],
            'diagram3': radar_imgs[2],
            'diagram4': radar_imgs[3],
            'diagram5': radar_imgs[4],
        },
    }

def build_default_inputs():
    rng = np.random.default_rng()
    # Начальные значения для 8 переменных АТС (по умолчанию)
    u_values = [
            round(rng.uniform(0.05, 0.95), 2),  # X1
            round(rng.uniform(0.05, 0.95), 2),  # X2  
            round(rng.uniform(0.05, 0.95), 2),  # X3
            round(rng.uniform(0.05, 0.95), 2),  # X4
            round(rng.uniform(0.05, 0.95), 2),  # X5
            round(rng.uniform(0.05, 0.95), 2),  # X6
            round(rng.uniform(0.05, 0.95), 2),  # X7
            round(rng.uniform(0.05, 0.95), 2)   # X8
        ]
        
        # Генерируем случайные ограничения
    u_restrictions = [
            round(rng.uniform(0.3, 1.0), 2),    # X1
            round(rng.uniform(0.3, 1.0), 2),    # X2
            round(rng.uniform(0.3, 1.0), 2),    # X3
            round(rng.uniform(0.3, 1.0), 2),    # X4
            round(rng.uniform(0.3, 0.6), 2),    # X5 (более строгое ограничение)
            round(rng.uniform(0.3, 0.6), 2),    # X6
            round(rng.uniform(0.3, 0.6), 2),    # X7
            round(rng.uniform(0.2, 0.4), 2)     # X8 (самое строгое)
        ]
    
    defaults = {
        'u': u_values,
        'u_restrictions': u_restrictions,
        'faks': [],  # Внешние факторы (5 штук) - ФИКСИРОВАННЫЕ
        'equations': []  # Уравнения f1-f18 - ФИКСИРОВАННЫЕ
    }
    
    # 5 внешних факторов - ФИКСИРОВАННЫЕ значения из системы (3)
    # Каждый фактор: [свободный член, коэффициент при t]
    fixed_factors = [
        [0.63, 0.37],    # F1: Средняя выработка ресурса до списания
        [1.00, -0.23],   # F2: Доля иностранных воздушных судов
        [1.00, -0.33],   # F3: Средний лётный стаж пилотов
        [0.51, 0.46],    # F4: Стоимость авиационного топлива 
        [0.60, 0.40]     # F5: Количество нормативно-правовых актов
    ]
    
    for factor_vals in fixed_factors:
        defaults['faks'].append([round(float(factor_vals[0]), 2), 
                                round(float(factor_vals[1]), 2)])
    
    # 18 уравнений f1-f18 - ФИКСИРОВАННЫЕ коэффициенты из системы (3)
    fixed_equations = [
        [-0.49, 0.97],   # f1(X2) = 0,97 - 0,49*X2
        [0.10, 0.53],    # f2(X3) = 0,53 + 0,1*X3
        [0.06, 0.53],    # f3(X4) = 0,53 + 0,06*X4
        [0.08, 0.75],    # f4(X4) = 0,75 + 0,08*X4
        [0.20, 0.72],    # f5(X6) = 0,72 + 0,2*X6
        [-0.20, 0.97],   # f6(X7) = 0,97 - 0,2*X7
        [0.38, 0.52],    # f7(X8) = 0,52 + 0,38*X8
        [-0.37, 0.78],   # f8(X7) = 0,78 - 0,37*X7
        [0.09, 0.45],    # f9(X1) = 0,45 + 0,09*X1
        [0.17, 0.55],    # f10(X2) = 0,55 + 0,17*X2
        [-0.44, 1.02],   # f11(X7) = 1,02 - 0,44*X7
        [0.05, 0.66],    # f12(X1) = 0,66 + 0,05*X1
        [0.48, 0.45],    # f13(X2) = 0,45 + 0,48*X2
        [-0.47, 1.18],   # f14(X2) = 1,18 - 0,47*X2
        [-0.77, 1.37],   # f15(X2) = 1,37 - 0,77*X2
        [0.22, 0.59],    # f16(X3) = 0,59 + 0,22*X3
        [-0.71, 1.24],   # f17(X4) = 1,24 - 0,71*X4
        [-0.02, 0.87]    # f18(X2) = 0,87 - 0,02*X2
    ]
    
    for eq_vals in fixed_equations:
        defaults['equations'].append([round(float(eq_vals[0]), 2), 
                                     round(float(eq_vals[1]), 2)])
    
    return defaults

def get_u_variable_for_equation(equation_number):
    # Маппинг уравнений f1-f18 на переменные X1-X8
    mapping = {
        1: 2,   # f1 зависит от X2
        2: 3,   # f2 зависит от X3
        3: 4,   # f3 зависит от X4
        4: 4,   # f4 зависит от X4
        5: 6,   # f5 зависит от X6
        6: 7,   # f6 зависит от X7
        7: 8,   # f7 зависит от X8
        8: 7,   # f8 зависит от X7
        9: 1,   # f9 зависит от X1
        10: 2,  # f10 зависит от X2
        11: 7,  # f11 зависит от X7
        12: 1,  # f12 зависит от X1
        13: 2,  # f13 зависит от X2
        14: 2,  # f14 зависит от X2
        15: 2,  # f15 зависит от X2
        16: 3,  # f16 зависит от X3
        17: 4,  # f17 зависит от X4
        18: 2   # f18 зависит от X2
    }
    return mapping.get(equation_number, "?")

def parse_form(form):
    u = []
    u_restrictions = []
    
    # Считываем 8 начальных значений
    for i in range(1, 9):
        field_name = f'u{i}'
        value = form.get(field_name, '0.1')
        u.append(float(value or 0.1))
        
        # Ограничения
        restriction_field = f'u_restrictions{i}'
        restriction_value = form.get(restriction_field, '1.0')
        u_restrictions.append(float(restriction_value or 1.0))
    
    # 5 внешних факторов - ИСПОЛЬЗУЕМ ФИКСИРОВАННЫЕ значения
    factors = build_default_inputs()['faks']
    
    # 18 уравнений f1-f18 - ИСПОЛЬЗУЕМ ФИКСИРОВАННЫЕ значения
    equations = build_default_inputs()['equations']
    
    return u[:8], factors[:5], equations[:18], u_restrictions[:8]