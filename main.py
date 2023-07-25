from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

class HelloWorldApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        button = Button(text='Say Hello', on_release=self.show_popup)
        layout.add_widget(button)
        return layout

    def show_popup(self, instance):
        content = "Hello, Kivy!"
        return content

if __name__ == "__main__":
    HelloWorldApp().run()
