from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QTimer, Qt

class AnimatedPanel:
    def __init__(self, panel, splitter):
        self.panel = panel
        self.splitter = splitter
        self.animation = None
        self._is_animating = False
        self._default_width = 250
        self.duration = 250
        self._is_collapsed = False
        print("AnimatedPanel initialized")  # Отладка
        
    def is_animating(self) -> bool:
        """Проверяет, идет ли анимация в данный момент"""
        return self._is_animating

    def animate(self, show=True, animate=True):
        """
        Анимирует панель.
        show: True для показа, False для скрытия
        animate: True для плавной анимации, False для мгновенного изменения
        """
        print(f"Animate called: show={show}, animate={animate}")  # Отладка
        
        if self._is_animating:
            print("Animation already in progress")  # Отладка
            return
            
        # Получаем индекс панели и текущие размеры
        panel_index = self.splitter.indexOf(self.panel)
        sizes = list(self.splitter.sizes())
        
        # Проверяем текущее состояние панели
        is_visible = self.panel.isVisible() and sizes[panel_index] > 0
        
        # Проверяем, нужно ли что-то делать
        if show and is_visible:  # Если панель уже показана и нужно показать
            print("Panel already visible, ignoring")  # Отладка
            return
        if not show and not is_visible:  # Если панель уже скрыта и нужно скрыть
            print("Panel already hidden, ignoring")  # Отладка
            return
            
        current_width = sizes[panel_index]
        target_width = self._default_width if show else 0
        print(f"Current width: {current_width}, Target width: {target_width}")  # Отладка
        
        # Если анимация не нужна, просто устанавливаем размеры
        if not animate:
            print("Instant resize")  # Отладка
            self._set_panel_size(target_width, show)
            return
            
        self._is_animating = True
        print("Starting animation")  # Отладка
        
        # Если показываем панель, подготавливаем её
        if show:
            self.panel.show()
            if current_width == 0:
                self.panel.setFixedWidth(0)
                sizes[panel_index] = 0
                self.splitter.setSizes(sizes)
        
        # Создаем и настраиваем анимацию
        self.animation = QPropertyAnimation(self.panel, b"minimumWidth")
        self.animation.setDuration(self.duration)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.setStartValue(current_width)
        self.animation.setEndValue(target_width)
        
        # Обновляем splitter во время анимации
        def on_value_changed(width):
            # print(f"Animation progress: width={width}")  # Убираем логирование прогресса
            self._set_panel_size(width, True)
            
        self.animation.valueChanged.connect(on_value_changed)
        
        def on_finished():
            print("Animation finished")  # Отладка
            self._is_animating = False
            if not show:
                self.panel.hide()
                self._is_collapsed = True
            else:
                self._is_collapsed = False
            self.animation = None
            
        self.animation.finished.connect(on_finished)
        self.animation.start()
        
    def _set_panel_size(self, width, keep_visible=False):
        """Устанавливает размер панели и обновляет splitter"""
        # Получаем текущие размеры
        sizes = list(self.splitter.sizes())
        panel_index = self.splitter.indexOf(self.panel)
        center_index = 1
        
        # Вычисляем разницу
        width_diff = width - sizes[panel_index]
        
        # Обновляем размеры
        sizes[panel_index] = width
        sizes[center_index] = max(400, sizes[center_index] - width_diff)
        
        # Применяем новые размеры
        self.panel.setFixedWidth(width)
        self.splitter.setSizes(sizes)
        
        # Управляем видимостью
        if not keep_visible and width == 0:
            self.panel.hide()
            self._is_collapsed = True
        elif width > 0:
            self.panel.show()
            self._is_collapsed = False 