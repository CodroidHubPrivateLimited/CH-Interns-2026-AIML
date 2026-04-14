from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle

import cv2
from detection import process_frame


class DrowsyApp(App):

    def build(self):
        self.capture = cv2.VideoCapture(0)

        self.layout = FloatLayout()

        # BACKGROUND
        self.bg = Image(
            source="assets/background.jpg",
            allow_stretch=True,
            keep_ratio=False
        )
        self.layout.add_widget(self.bg)

        # DARK OVERLAY
        with self.layout.canvas:
            Color(0, 0, 0, 0.4)
            self.overlay = Rectangle(size=self.layout.size, pos=self.layout.pos)

        self.layout.bind(size=self.update_rect, pos=self.update_rect)

        # TITLE
        self.title_label = Label(
            text="iSense Drive AI",
            pos_hint={'center_x': 0.5, 'y': 0.92},
            font_size=28,
            bold=True,
            color=(1, 1, 1, 1)
        )
        self.layout.add_widget(self.title_label)

        # CAMERA (Top Right Corner)
        self.img = Image(
            size_hint=(0.3, 0.22),
            pos_hint={'right': 0.97, 'top': 0.93}
        )
        self.layout.add_widget(self.img)


        # STATUS
        self.status_label = Label(
            text="Status: AWAKE",
            pos_hint={'x': 0.05, 'y': 0.08},
            font_size=22,
            color = (0, 0, 0, 0)
        )
        # self.layout.add_widget(self.status_label)

        # BLINKS
        self.blink_label = Label(
            text="Blinks: 0",
            pos_hint={'x': 0.35, 'y': 0.08},
            font_size=22,
            color=(1, 1, 1, 1)
        )
        # self.layout.add_widget(self.blink_label)

        # START BUTTON
        self.start_btn = Button(
            text="ENGINE START",
            size_hint=(0.2, 0.08),
            pos_hint={'x': 0.7, 'y': 0.05},
            background_color=(0, 0.7, 0, 1)
        )
        self.start_btn.bind(on_press=self.start_camera)
        self.layout.add_widget(self.start_btn)

        # STOP BUTTON
        self.stop_btn = Button(
            text="ENGINE STOP",
            size_hint=(0.2, 0.08),
            pos_hint={'x': 0.7, 'y': 0.15},
            background_color=(1, 0, 0, 1)
        )
        self.stop_btn.bind(on_press=self.stop_camera)
        self.layout.add_widget(self.stop_btn)

        return self.layout

    def update_rect(self, *args):
        self.overlay.pos = self.layout.pos
        self.overlay.size = self.layout.size

    def start_camera(self, instance):
        Clock.schedule_interval(self.update, 1.0 / 30.0)

    def stop_camera(self, instance):
        Clock.unschedule(self.update)

    def update(self, dt):
        ret, frame = self.capture.read()

        if not ret:
            return

        frame = cv2.flip(frame, 1)

        # PROCESS FRAME
        frame, status, blinks = process_frame(frame)

        # UPDATE TEXT
        self.status_label.text = f"Status: {status}"
        self.blink_label.text = f"Blinks: {blinks}"

        # COLOR CHANGE
        if status == "DROWSY":
            self.status_label.color = (1, 0, 0, 1)
        else:
            self.status_label.color = (0, 1, 0, 1)

        # FRAME TO TEXTURE
        buf = cv2.flip(frame, 0).tobytes()
        texture = Texture.create(
            size=(frame.shape[1], frame.shape[0]),
            colorfmt='bgr'
        )
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

        self.img.texture = texture


if __name__ == "__main__":
    DrowsyApp().run()
