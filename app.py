# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify
import numpy as np
import os
from web_core import run_simulation, build_default_inputs, get_u_variable_for_equation, U_LABELS, parse_form
from utils import clear_graphics  # Импорт из utils, а не из process

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

os.makedirs('static/images', exist_ok=True)

def subscript(number):
    """Convert number to subscript string"""
    subscripts = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    return str(number).translate(subscripts)

@app.template_filter('subscript')
def subscript_filter(s):
    return subscript(s)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        if request.args.get('run') == '1':
            defaults = build_default_inputs()
            try:
                outputs = run_simulation(
                    defaults['u'], 
                    defaults['faks'], 
                    defaults['equations'], 
                    defaults['u_restrictions']
                )
                
                values = {
                    'u': defaults['u'],
                    'faks': defaults['faks'], 
                    'equations': defaults['equations'],
                    'u_restrictions': defaults['u_restrictions']
                }
                
                return render_template('index.html', 
                                    defaults=defaults, 
                                    values=values,
                                    ran=True, 
                                    outputs=outputs,
                                    u_labels=U_LABELS,
                                    get_u_variable_for_equation=get_u_variable_for_equation,
                                    success="Модель успешно выполнена с фиксированными значениями")
            except Exception as exc:
                return render_template('index.html', 
                                    defaults=defaults, 
                                    values=None, 
                                    ran=False, 
                                    error=str(exc),
                                    u_labels=U_LABELS,
                                    get_u_variable_for_equation=get_u_variable_for_equation)
        
        defaults = build_default_inputs()
        return render_template('index.html', 
                            defaults=defaults, 
                            values=None, 
                            ran=False,
                            u_labels=U_LABELS,
                            get_u_variable_for_equation=get_u_variable_for_equation)
    
    elif request.method == 'POST':
        try:
            u, faks, equations, restrictions = parse_form(request.form)
            
            for i in range(len(u)):
                if restrictions[i] <= u[i]:
                    raise ValueError(
                        f"Предел для X{i+1} должен быть больше начального значения. "
                        f"Начальное: {u[i]:.2f}, Предел: {restrictions[i]:.2f}"
                    )
            
            # Запуск симуляции
            outputs = run_simulation(u, faks, equations, restrictions)
            
            values = {
                'u': u,
                'faks': faks, 
                'equations': equations,
                'u_restrictions': restrictions
            }
            
            # Сохраняем изображения в static/images
            import base64
            
            # Сохраняем графики характеристик
            if 'images_b64' in outputs:
                # График характеристик
                fig1_data = base64.b64decode(outputs['images_b64']['figure1'])
                with open('static/images/figure.png', 'wb') as f:
                    f.write(fig1_data)
                
                # График возмущений
                fig2_data = base64.b64decode(outputs['images_b64']['figure2'])
                with open('static/images/disturbances.png', 'wb') as f:
                    f.write(fig2_data)
                
                # Диаграммы радара
                for i, key in enumerate(['diagram1', 'diagram2', 'diagram3', 'diagram4', 'diagram5']):
                    img_data = base64.b64decode(outputs['images_b64'][key])
                    filename = f'static/images/diagram{"" if i==0 else i+1}.png'
                    with open(filename, 'wb') as f:
                        f.write(img_data)
            
            return render_template('index.html', 
                                defaults=None, 
                                values=values, 
                                ran=True, 
                                outputs=outputs,
                                u_labels=U_LABELS,
                                get_u_variable_for_equation=get_u_variable_for_equation,
                                success="Модель успешно выполнена с пользовательскими значениями")
            
        except Exception as exc:
            defaults = build_default_inputs()
            return render_template('index.html', 
                                defaults=defaults, 
                                values=None, 
                                ran=False, 
                                error=str(exc),
                                u_labels=U_LABELS,
                                get_u_variable_for_equation=get_u_variable_for_equation)

@app.route('/graphic')
def get_graphic():
    return render_template('graphic.html')

@app.route('/diagrams')
def get_diagrams():
    return render_template('diagrams.html')

@app.route('/facks')
def get_facks():
    return render_template('facks.html')

@app.route('/clear')
def clear():
    clear_graphics()
    return redirect('/')

@app.route('/draw_graphics', methods=['POST'])
def draw_graphics():
    try:
        data = request.get_json()
        
        # Импортируем process здесь, чтобы избежать циклических импортов
        from process import process
        
        # Запускаем обработку
        process(
            data.get("initial_equations", []),
            data.get("faks", []),
            data.get("equations", []),
            data.get("restrictions", [])
        )
        
        return jsonify({"status": "Выполнено"})
    except Exception as e:
        print(f"Ошибка в draw_graphics: {e}")
        return jsonify({"status": "Ошибка", "error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)