// static/js/script.js
const input = document.getElementById("status-input")
input.value = sessionStorage.getItem("status") || ""

function random() {
    return Math.round(((Math.random() * 0.7 + 0.01) + Number.EPSILON) * 100) / 100
}

// Заполнение при загрузке, если есть сохраненные данные
if (input.value !== "Выполнено") {
    refill()
}
else {
    // Загружаем сохраненные данные для возмущений (линейная форма: a + b*t)
    for (let i=1; i<=5; i++) {
        document.getElementById(`fak${i}_a`).value = sessionStorage.getItem(`fak${i}_a`) || ""
        document.getElementById(`fak${i}_b`).value = sessionStorage.getItem(`fak${i}_b`) || ""
    }

    // Загружаем сохраненные данные для начальных условий
    for (let i=1; i<=8; i++) {
        let el = document.getElementById(`init-eq-${i}`)
        if (el) {
            el.value = sessionStorage.getItem(`init-eq-${i}`) || ""
        }
    }

    // Загружаем сохраненные данные для уравнений (линейная форма: k*x + b)
    for (let i=1; i<=18; i++) {
        document.getElementById(`f${i}_k`).value = sessionStorage.getItem(`f${i}_k`) || ""
        document.getElementById(`f${i}_b`).value = sessionStorage.getItem(`f${i}_b`) || ""
    }
}

function getFaks() {
    const faks = []
    for (let i=1; i<=5; i++) {
        const a = document.getElementById(`fak${i}_a`).value || "0.5"
        const b = document.getElementById(`fak${i}_b`).value || "0.0"
        faks.push([parseFloat(a), parseFloat(b)])
    }
    return faks
}

function getInitialEquations() {
    const init_eq = []
    for (let i=1; i<=8; i++) {
        let el = document.getElementById(`init-eq-${i}`)
        if (el) init_eq.push(el.value || "0.5")
    }
    return init_eq
}

function getRestrictions() {
    const restrictions = []
    for (let i=1; i<=8; i++) {
        let el = document.getElementById(`restrictions-${i}`)
        if (el) restrictions.push(el.value || "1.0")
    }
    return restrictions
}

function getEquations() {
    const equations = []
    for (let i=1; i<=18; i++) {
        const k = document.getElementById(`f${i}_k`).value || "0.3"
        const b = document.getElementById(`f${i}_b`).value || "0.5"
        equations.push([parseFloat(k), parseFloat(b)])
    }
    return equations
}

async function process() {
    const faks = getFaks()
    const init_eq = getInitialEquations()
    const restrictions = getRestrictions()
    const equations = getEquations()

    // Сохраняем данные в sessionStorage
    for (let i=1; i<=5; i++) {
        sessionStorage.setItem(`fak${i}_a`, faks[i-1][0])
        sessionStorage.setItem(`fak${i}_b`, faks[i-1][1])
    }
    
    for (let i=1; i<=8; i++) {
        sessionStorage.setItem(`init-eq-${i}`, init_eq[i-1])
    }
    
    for (let i=1; i<=18; i++) {
        sessionStorage.setItem(`f${i}_k`, equations[i-1][0])
        sessionStorage.setItem(`f${i}_b`, equations[i-1][1])
    }

    // Отправляем данные на сервер
    const response = await fetch('/draw_graphics', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            "faks": faks,
            "initial_equations": init_eq,
            "restrictions": restrictions,
            "equations": equations
        })
    })

    const result = await response.json()
    input.value = result.status
    sessionStorage.setItem("status", result.status)
    
    // Автоматически переходим на страницу графиков
    if (result.status === "Выполнено") {
        setTimeout(() => {
            window.location.href = "/graphic"
        }, 1000)
    }
}

function refill() {
    // Заполняем случайными значениями возмущения (a + b*t)
    for (let i=1; i<=5; i++) {
        const aValue = (Math.random() * 0.5 + 0.3).toFixed(2)
        const bValue = (Math.random() * 0.4 - 0.2).toFixed(2)
        
        document.getElementById(`fak${i}_a`).value = aValue
        document.getElementById(`fak${i}_b`).value = bValue
        
        sessionStorage.setItem(`fak${i}_a`, aValue)
        sessionStorage.setItem(`fak${i}_b`, bValue)
    }

    // Заполняем случайными значениями начальные условия
    for (let i=1; i<=8; i++) {
        const value = (Math.random() * 0.7 + 0.1).toFixed(2)
        document.getElementById(`init-eq-${i}`).value = value
        sessionStorage.setItem(`init-eq-${i}`, value)
        
        // Предельные значения (немного выше начальных)
        const restrictionValue = (parseFloat(value) + Math.random() * 0.2 + 0.05).toFixed(2)
        document.getElementById(`restrictions-${i}`).value = restrictionValue
    }

    // Заполняем случайными значениями уравнения
    for (let i=1; i<=18; i++) {
        const kValue = (Math.random() * 1.6 - 0.8).toFixed(2)
        const bValue = (Math.random() * 0.8 + 0.1).toFixed(2)
        
        document.getElementById(`f${i}_k`).value = kValue
        document.getElementById(`f${i}_b`).value = bValue
        
        sessionStorage.setItem(`f${i}_k`, kValue)
        sessionStorage.setItem(`f${i}_b`, bValue)
    }
    
    sessionStorage.removeItem("status")
    input.value = "Заполнено случайно"
}

// Обработчик для кнопки "Вычислить" в форме
document.addEventListener('DOMContentLoaded', function() {
    const calculateBtn = document.querySelector('.btn-calculate')
    if (calculateBtn) {
        calculateBtn.addEventListener('click', function(e) {
            if (!document.getElementById('fullForm')) {
                e.preventDefault()
                process()
            }
        })
    }
})