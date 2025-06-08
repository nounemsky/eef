from PyQt6.QtWidgets import QStackedWidget
from PyQt6.QtCore import QPropertyAnimation, QParallelAnimationGroup, QEasingCurve, Qt, QPoint, QRect

class AnimatedStackedWidget(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.animation_duration = 200  # Уменьшаем длительность анимации
        self._animation_running = False
        self._next_index = 0
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        
    def setCurrentIndex(self, index: int):
        """Переопределяем метод для использования анимации"""
        if self._animation_running or index == self.currentIndex() or not self.isVisible():
            super().setCurrentIndex(index)
            return
            
        if index > self.currentIndex():
            self.slide_in_index(index, "right")
        else:
            self.slide_in_index(index, "left")
            
    def slide_in_index(self, index: int, direction: str = "right"):
        """Анимация слайда к конкретному индексу"""
        if self._animation_running or index == self.currentIndex() or index >= self.count():
            return
            
        self._next_index = index
        self._animate_transition(direction)
        
    def _animate_transition(self, direction: str):
        """Выполняет анимацию перехода"""
        if self._animation_running:
            return
            
        self._animation_running = True
        
        # Получаем виджеты
        current = self.currentWidget()
        next_widget = self.widget(self._next_index)
        
        if not current or not next_widget:
            self._animation_running = False
            super().setCurrentIndex(self._next_index)
            return
            
        # Определяем направление
        width = self.width()
        offset = width if direction == "right" else -width
        
        # Устанавливаем начальное положение
        next_widget.setGeometry(QRect(width if direction == "right" else -width, 0, width, self.height()))
        next_widget.show()
        next_widget.raise_()
        
        # Создаем анимации
        self.anim_group = QParallelAnimationGroup(self)
        
        # Анимация текущего виджета
        current_anim = QPropertyAnimation(current, b"pos", self)
        current_anim.setDuration(self.animation_duration)
        current_anim.setStartValue(current.pos())
        current_anim.setEndValue(QPoint(-offset, 0))
        current_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # Анимация следующего виджета
        next_anim = QPropertyAnimation(next_widget, b"pos", self)
        next_anim.setDuration(self.animation_duration)
        next_anim.setStartValue(QPoint(offset, 0))
        next_anim.setEndValue(QPoint(0, 0))
        next_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        self.anim_group.addAnimation(current_anim)
        self.anim_group.addAnimation(next_anim)
        self.anim_group.finished.connect(self._on_animation_finished)
        self.anim_group.start(QParallelAnimationGroup.DeletionPolicy.DeleteWhenStopped)
        
    def _on_animation_finished(self):
        """Обработчик завершения анимации"""
        # Устанавливаем текущий индекс без анимации
        QStackedWidget.setCurrentIndex(self, self._next_index)
        
        # Сбрасываем положение всех виджетов
        for i in range(self.count()):
            widget = self.widget(i)
            if widget:
                widget.move(0, 0)
        
        self._animation_running = False 