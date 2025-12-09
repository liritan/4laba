// static/js/diagramsChecker.js
document.addEventListener('DOMContentLoaded', function() {
    const diagramsGrid = document.querySelector('.diagrams-grid')
    const diagramImages = document.querySelectorAll('.diagram-img')
    
    if (diagramsGrid && diagramImages.length > 0) {
        let allImagesLoaded = true
        
        // Проверяем каждое изображение
        diagramImages.forEach((img, index) => {
            const testImg = new Image()
            testImg.src = img.src
            
            testImg.onerror = function() {
                allImagesLoaded = false
            }
        })
        
        // Если не все изображения загружены, показываем сообщение
        setTimeout(() => {
            if (!allImagesLoaded) {
                diagramsGrid.innerHTML = `
                    <div class="no-data-message" style="grid-column: 1 / -1; width: 100%;">
                        <h3>Диаграммы не доступны</h3>
                        <p>Выполните расчеты на странице "Параметры" чтобы увидеть диаграммы</p>
                        <a href="/" class="btn-calculate" style="margin-top: 15px; display: inline-block;">
                            Перейти к параметрам
                        </a>
                    </div>
                `
            }
        }, 1000)
    }
})