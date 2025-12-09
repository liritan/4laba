// static/js/graphicChecker.js
document.addEventListener('DOMContentLoaded', function() {
    const graphicImage = document.getElementById('graphic-image')
    const imageContainer = document.querySelector('.image-container')
    
    // Проверяем наличие файла
    if (graphicImage) {
        // Проверяем, загружается ли изображение
        graphicImage.onerror = function() {
            // Если изображение не загружено, показываем сообщение
            if (imageContainer) {
                imageContainer.innerHTML = `
                    <div class="no-data-message">
                        <h3>График не доступен</h3>
                        <p>Выполните расчеты на странице "Параметры" чтобы увидеть график</p>
                        <a href="/" class="btn-calculate" style="margin-top: 15px; display: inline-block;">
                            Перейти к параметрам
                        </a>
                    </div>
                `
            }
        }
        
        // Проверяем, существует ли изображение
        const img = new Image()
        img.src = graphicImage.src
        
        img.onload = function() {
            // Изображение загружено успешно
            graphicImage.style.visibility = 'visible'
        }
        
        img.onerror = function() {
            // Изображение не найдено
            if (imageContainer) {
                imageContainer.innerHTML = `
                    <div class="no-data-message">
                        <h3>График не доступен</h3>
                        <p>Выполните расчеты на странице "Параметры" чтобы увидеть график</p>
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
                    <h3>График не доступен</h3>
                    <p>Выполните расчеты на странице "Параметры" чтобы увидеть график</p>
                    <a href="/" class="btn-calculate" style="margin-top: 15px; display: inline-block;">
                        Перейти к параметрам
                    </a>
                </div>
            `
        }
    }
})