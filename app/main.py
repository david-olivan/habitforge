from kivy.app import App
from kivy.uix.label import Label


class HabitForgeApp(App):
    def build(self):
        return Label(text='Hello World - HabitForge')


if __name__ == '__main__':
    HabitForgeApp().run()