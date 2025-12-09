# process.py
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import odeint
import logging

from functions import pend
from radar_diagram import RadarDiagram

data_sol = []
logger = logging.getLogger(__name__)

def fill_diagrams(data, initial_equations, restrictions):
    radar = RadarDiagram()
    
    clipped_initial = np.clip(initial_equations, 0, 1.0)
    clipped_data = np.clip(data, 0, 1.0)
    clipped_restrictions = np.clip(restrictions, 0, 1.0)

    time_indices = [
        0,
        int(len(data) / 4),
        int(len(data) / 2),
        int(3 * len(data) / 4),
        -1
    ]
    
    titles = [
        "Характеристики системы: начальный момент времени",
        "Характеристики системы при t=0.25",
        "Характеристики системы при t=0.5",
        "Характеристики системы при t=0.75",
        "Характеристики системы при t=1"
    ]
    
    filenames = [
        './static/images/diagram.png',
        './static/images/diagram2.png',
        './static/images/diagram3.png',
        './static/images/diagram4.png',
        './static/images/diagram5.png'
    ]

    for i, (idx, title, fname) in enumerate(zip(time_indices, titles, filenames)):
        current_vals = clipped_data[idx]
        
        if i == 0:
            radar.draw(
                filename=fname,
                initial_data=clipped_initial,
                current_data=current_vals,
                label="",
                title=title,
                restrictions=clipped_restrictions,
                show_both_lines=False
            )
        else:
            radar.draw(
                filename=fname,
                initial_data=clipped_initial,
                current_data=current_vals,
                label="",
                title=title,
                restrictions=clipped_restrictions,
                show_both_lines=True
            )

def create_graphic(t, data):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))
    
    # 8 характеристик для авиационной модели
    labels_x1_x4 = [
        "X₁: Среднее количество нарушений инструкций пилотами",
        "X₂: Доля частных судов в авиации", 
        "X₃: Показатель активности органов контроля за оборотом контрафакта",
        "X₄: Количество сотрудников в метеорологических службах"
    ]
    
    labels_x5_x8 = [
        "X₅: Катастрофы из-за метеоусловий",
        "X₆: Катастрофы из-за технических неисправностей",
        "X₇: Катастрофы из-за человеческого фактора",
        "X₈: Общее количество катастроф"
    ]
    
    line_labels_x1_x4 = ["X₁", "X₂", "X₃", "X₄"]
    line_labels_x5_x8 = ["X₅", "X₆", "X₇", "X₈"]
    
    colors_x1_x4 = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    colors_x5_x8 = ['#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
    
    # График для X1-X4
    for i in range(4):
        y_data = np.clip(data[:, i], 0, 1.0)
        line = ax1.plot(t, y_data, color=colors_x1_x4[i], linewidth=2.5, label=labels_x1_x4[i])
        
        mid_idx = len(t) // 2
        if mid_idx > 0:
            ax1.text(t[mid_idx], y_data[mid_idx], f' {line_labels_x1_x4[i]}', 
                    color=colors_x1_x4[i], fontsize=9, va='center', ha='left',
                    bbox=dict(boxstyle="round,pad=0.1", facecolor='white', alpha=0.7, edgecolor='none'))
    
    ax1.set_xlim([0, 1])
    ax1.set_ylim([0, 1.0])
    ax1.set_ylabel("Значения характеристик", fontsize=14, fontweight='bold')
    ax1.set_title("График 1: Характеристики системы (X₁-X₄)", fontsize=16, fontweight='bold', pad=20)
    ax1.legend(loc='upper left', fontsize=12, framealpha=0.9, 
               edgecolor='gray', fancybox=True)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.tick_params(axis='both', which='major', labelsize=12)
    ax1.axhline(y=1.0, color='red', linestyle=':', alpha=0.7, linewidth=1, label='Предел')
    
    # График для X5-X8
    for i in range(4):
        y_data = np.clip(data[:, i+4], 0, 1.0)
        line = ax2.plot(t, y_data, color=colors_x5_x8[i], linewidth=2.5, label=labels_x5_x8[i])
        
        mid_idx = len(t) // 2
        if mid_idx > 0:
            ax2.text(t[mid_idx], y_data[mid_idx], f' {line_labels_x5_x8[i]}', 
                    color=colors_x5_x8[i], fontsize=9, va='center', ha='left',
                    bbox=dict(boxstyle="round,pad=0.1", facecolor='white', alpha=0.7, edgecolor='none'))
    
    ax2.set_xlim([0, 1])
    ax2.set_ylim([0, 1.0])
    ax2.set_xlabel("t, время", fontsize=14, fontweight='bold')
    ax2.set_ylabel("Значения характеристик", fontsize=14, fontweight='bold')
    ax2.set_title("График 2: Характеристики системы (X₅-X₈)", fontsize=16, fontweight='bold', pad=20)
    ax2.legend(loc='upper left', fontsize=12, framealpha=0.9, 
               edgecolor='gray', fancybox=True)
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.tick_params(axis='both', which='major', labelsize=12)
    ax2.axhline(y=1.0, color='red', linestyle=':', alpha=0.7, linewidth=1, label='Предел')
    
    plt.tight_layout(pad=3.0)
    fig.savefig('./static/images/figure.png', bbox_inches='tight', dpi=150)
    plt.close(fig)

def cast_to_float(initial_equations, faks, equations, restrictions):
    for i in range(len(initial_equations)):
        initial_equations[i] = float(initial_equations[i])

    for i in range(len(faks)):
        for j in range(len(faks[i])):
            faks[i][j] = float(faks[i][j])

    for i in range(len(equations)):
        for j in range(len(equations[i])):
            equations[i][j] = float(equations[i][j])

    for i in range(len(restrictions)):
        restrictions[i] = float(restrictions[i])

    return initial_equations, faks, restrictions

def process(initial_equations, faks, equations, restrictions):
    global data_sol

    initial_equations, faks, restrictions = cast_to_float(initial_equations, faks, equations, restrictions)
    t = np.linspace(0, 1, 100)
    
    # Запуск симуляции с 8 характеристиками
    data_sol = odeint(pend, initial_equations[:8], t, args=(faks, equations))
    
    data_sol = np.clip(data_sol, 1e-3, 1.0)
    
    create_graphic(t, data_sol)
    create_disturbances_graphic(t, faks)  
    fill_diagrams(data_sol, initial_equations[:8], restrictions[:8])

def create_disturbances_graphic(t, faks):
    fig, axs = plt.subplots(figsize=(16, 8))
    
    disturbances_labels = [
        "F₁: Средняя выработка ресурса до списания",
        "F₂: Доля иностранных воздушных судов", 
        "F₃: Средний лётный стаж пилотов",
        "F₄: Стоимость авиационного топлива",
        "F₅: Количество нормативно-правовых актов"
    ]
    
    line_labels = ["F₁", "F₂", "F₃", "F₄", "F₅"]
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    # Построение линейных функций F_i(t) = a + b*t
    for i in range(len(faks)):
        a = faks[i][0]
        b = faks[i][1]
        curve = a + b * t
        curve = np.clip(curve, 0, 1.0)  # Ограничиваем значения
        
        line = axs.plot(t, curve, color=colors[i], linewidth=2.5, label=disturbances_labels[i])
        
        mid_idx = len(t) // 2
        if mid_idx > 0:
            axs.text(t[mid_idx], curve[mid_idx], f' {line_labels[i]}', 
                    color=colors[i], fontsize=9, va='center', ha='left',
                    bbox=dict(boxstyle="round,pad=0.1", facecolor='white', alpha=0.7, edgecolor='none'))
    
    axs.set_xlim([0, 1])
    axs.set_ylim([0, 1])
    axs.set_xlabel("t, время", fontsize=14, fontweight='bold')
    axs.set_ylabel("Значения возмущений", fontsize=14, fontweight='bold')
    axs.set_title("График внешних воздействий на систему (возмущения)", fontsize=16, fontweight='bold', pad=20)
    axs.legend(loc='upper right', fontsize=10, framealpha=0.9)
    axs.grid(True, alpha=0.3, linestyle='--')
    axs.tick_params(axis='both', which='major', labelsize=12)
    
    plt.tight_layout()
    fig.savefig('./static/images/disturbances.png', bbox_inches='tight', dpi=150)
    plt.close(fig)