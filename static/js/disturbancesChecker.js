// static/js/disturbancesChecker.js
document.addEventListener('DOMContentLoaded', function() {
    const disturbancesImage = document.getElementById('disturbances-image')
    const imageContainer = document.querySelector('.image-container')
    
    if (disturbancesImage) {
        // Проверяем, загружается ли изображение
        disturbancesImage.onerror = function() {
            // Если изображение не загружено, показываем сообщение
            if (imageContainer) {
                imageContainer.innerHTML = `
                    <div class="no-data-message">
                        <h3>График возмущений не доступен</h3>
                        <p>Выполните расчеты на странице "Параметры" чтобы увидеть график возмущений</p>
                        <a href="/" class="btn-calculate" style="margin-top: 15px; display: inline-block;">
                            Перейти к параметрам
                        </a>
                    </div>
                `
            }
        }
        
        // Проверяем, существует ли изображение
        const img = new Image()
        img.src = disturbancesImage.src
        
        img.onload = function() {
            // Изображение загружено успешно
            disturbancesImage.style.visibility = 'visible'
        }
        
        img.onerror = function() {
            // Изображение не найдено
            if (imageContainer) {
                imageContainer.innerHTML = `
                    <div class="no-data-message">
                        <h3>График возмущений не доступен</h3>
                        <p>Выполните расчеты на странице "Параметры" чтобы увидеть график возмущений</p>
                        <a href="/" class="btn-calculate" style="margin-top: 15px; display: inline-block;">
                            Перейти к параметрам
                        </a>
                    </div>
                `
            }
        }
    } else {
        // Если элемента изображения нет
        if (imageContainer) {
            imageContainer.innerHTML = `
                <div class="no-data-message">
                    <h3>График возмущений не доступен</h3>
                    <p>Выполните расчеты на странице "Параметры" чтобы увидеть график возмущений</p>
                    <a href="/" class="btn-calculate" style="margin-top: 15px; display: inline-block;">
                        Перейти к параметрам
                    </a>
                </div>
            `
        }
    }
})