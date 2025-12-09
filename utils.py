# utils.py
import os

def clear_graphics():
    """Удаляет сохраненные графики и диаграммы"""
    image_files = [
        'static/images/figure.png',
        'static/images/disturbances.png',
        'static/images/diagram.png',
        'static/images/diagram2.png', 
        'static/images/diagram3.png',
        'static/images/diagram4.png',
        'static/images/diagram5.png'
    ]
    
    for file_path in image_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Удален файл: {file_path}")
            except Exception as e:
                print(f"Ошибка при удалении файла {file_path}: {e}")

def get_initial_equations_from_inputs(ui):
    return [float(ui.lineEdits[f"u{i}"].text()) for i in range(1, 9)]

def get_faks_from_inputs(ui):
    result = []
    for i in range(1, 6):
        a = float(ui.lineEdits[f"fak{i}_a"].text())
        b = float(ui.lineEdits[f"fak{i}_b"].text())
        result.append([a, b])
    return result

def get_equations_from_inputs(ui):
    result = []
    for i in range(1, 19):
        a = float(ui.lineEdits[f"f{i}_k"].text())
        b = float(ui.lineEdits[f"f{i}_b"].text())
        result.append([a, b])
    return result

def get_restrictions(ui):
    return [float(ui.lineEdits[f"u_restrictions{i}"].text()) for i in range(1, 9)]