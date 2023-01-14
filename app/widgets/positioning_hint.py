from kivymd.uix.widget import Widget
from kivy.graphics import Rectangle, Color


class PositioningHint(Widget):
    def __init__(self, **kwargs):
        super(PositioningHint, self).__init__(size_hint=(1, None), **kwargs)
        with self.canvas:
            Color(.3, .3, .3, .3)
            self.rectangle = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_rectangle)
        self.bind(size=self.update_rectangle)

    def update_rectangle(self, *args):
        self.rectangle.pos = self.pos
        self.rectangle.size = self.size