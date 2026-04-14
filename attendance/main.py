import cv2
import os
import face_recognition
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

# ================= THEME =================
Window.clearcolor = (0.96, 0.97, 0.98, 1)

# ================= DATASET =================
DATASET = "dataset"
os.makedirs(DATASET, exist_ok=True)

# ================= LOGIN =================
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout()

        card = BoxLayout(orientation='vertical',
                         size_hint=(0.35, None),
                         height=350,
                         padding=25,
                         spacing=15,
                         pos_hint={'center_x': 0.5, 'center_y': 0.5})

        from kivy.graphics import Color, RoundedRectangle
        with card.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = RoundedRectangle(radius=[15],
                                         size=card.size,
                                         pos=card.pos)
            card.bind(size=self.update_rect, pos=self.update_rect)

        title = Label(text="[b]Face Attendance System[/b]",
                      markup=True,
                      font_size=20,
                      color=(0.15, 0.2, 0.25, 1))
        card.add_widget(title)

        self.username = TextInput(hint_text="Username",
                                 multiline=False,
                                 size_hint=(1, None),
                                 height=45,
                                 background_color=(0.95, 0.95, 0.95, 1))

        self.password = TextInput(hint_text="Password",
                                 password=True,
                                 multiline=False,
                                 size_hint=(1, None),
                                 height=45,
                                 background_color=(0.95, 0.95, 0.95, 1))

        card.add_widget(self.username)
        card.add_widget(self.password)

        btn = Button(text="Login",
                     background_normal='',
                     background_color=(0.16, 0.47, 1, 1),
                     color=(1, 1, 1, 1),
                     size_hint=(1, None),
                     height=45)

        btn.bind(on_press=self.login)
        card.add_widget(btn)

        self.status = Label(text="", color=(1, 0.2, 0.2, 1))
        card.add_widget(self.status)

        root.add_widget(card)
        self.add_widget(root)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def login(self, instance):
        user = self.username.text.strip()
        pwd = self.password.text.strip()

        if user == "admin" and pwd == "admin123":
            self.manager.current = "admin"

        elif user != "" and pwd != "":
            self.manager.current = "main"
            self.manager.get_screen("main").set_user(user)

        else:
            self.status.text = "Invalid credentials"

# ================= MAIN =================
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.capture = None
        self.user_name = ""
        self.marked = set()

        self.known_encodings = []
        self.known_names = []

        root = BoxLayout(orientation='horizontal')

        # SIDEBAR
        sidebar = BoxLayout(orientation='vertical',
                            size_hint=(0.22, 1),
                            padding=15,
                            spacing=15)

        from kivy.graphics import Color, Rectangle
        with sidebar.canvas.before:
            Color(0.12, 0.23, 0.37, 1)
            self.rect = Rectangle(size=sidebar.size, pos=sidebar.pos)
            sidebar.bind(size=self.update_rect, pos=self.update_rect)

            

        def btn(text, func=None):
            b = Button(text=text,
                       background_normal='',
                       background_color=(0.16, 0.47, 1, 1),
                       color=(1, 1, 1, 1),
                       size_hint=(1, None),
                       height=45)
            if func:
                b.bind(on_press=func)
            return b

        sidebar.add_widget(Label(text="MENU", color=(1,1,1,1)))
        sidebar.add_widget(btn("Register", self.register))
        sidebar.add_widget(btn("Start", self.start))
        sidebar.add_widget(btn("Stop", self.stop))
        sidebar.add_widget(btn("Back", lambda x: setattr(self.manager, 'current', 'login')))

        root.add_widget(sidebar)

        # CENTER
        center = BoxLayout(orientation='vertical', padding=15, spacing=10)
        

        self.header = Label(text="Face Attendance Dashboard",
                            font_size=18,
                            size_hint=(1, 0.08),
                            color=(0.15, 0.2, 0.25, 1))
        center.add_widget(self.header)

        # Employee Name Input
        self.emp_input = TextInput(
            hint_text="Enter Employee Name",
            size_hint=(1, 0.08),
            height=40
        )
        center.add_widget(self.emp_input)

        #camer view
        self.img = Image(size_hint=(1, 0.70))
        center.add_widget(self.img)

        # status label
        self.status = Label(text="Status: Idle",
                            size_hint=(1, 0.08),
                            color=(0.2, 0.3, 0.4, 1))
        center.add_widget(self.status)

        root.add_widget(center)
        self.add_widget(root)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def set_user(self, name):
        self.user_name = name
        self.header.text = f"Welcome {name}"
        self.load_faces()

    def load_faces(self):
        self.known_encodings = []
        self.known_names = []

        for file in os.listdir(DATASET):
            img = face_recognition.load_image_file(f"{DATASET}/{file}")
            enc = face_recognition.face_encodings(img)
            if enc:
                self.known_encodings.append(enc[0])
                self.known_names.append(file.split(".")[0])

    def register(self, instance):
        emp_name = self.emp_input.text.strip()

        if emp_name == "":
            self.status.text = "Enter Employee Name First"
            return

        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()

        if ret:
            path = f"{DATASET}/{emp_name}.jpg"
            cv2.imwrite(path, frame)

            self.status.text = f"{emp_name} Registered"
            self.load_faces()
        else:
            self.status.text = "Camera Error"

        cap.release()

    def start(self, instance):
        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update, 1.0 / 30.0)
        self.status.text = "Camera Started"

    def stop(self, instance):
        if self.capture:
            self.capture.release()
        Clock.unschedule(self.update)
        self.img.texture = None
        self.status.text = "Camera Stopped"

    def mark_attendance(self, name):
        file = datetime.now().strftime("%Y-%m-%d") + ".csv"

        if name not in self.marked:
            with open(file, "a") as f:
                if os.stat(file).st_size == 0:
                    f.write("Name,Date,Time\n")

                now = datetime.now()
                f.write(f"{name},{now.strftime('%Y-%m-%d')},{now.strftime('%H:%M:%S')}\n")

            self.marked.add(name)
            self.status.text = f"{name} Marked"

    def update(self, dt):
        ret, frame = self.capture.read()
        if not ret:
            return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, faces)

        for encoding, face in zip(encodings, faces):
            name = "Unknown"

            if self.known_encodings:
                distances = face_recognition.face_distance(self.known_encodings, encoding)
                best = np.argmin(distances)

                if distances[best] < 0.5:
                    name = self.known_names[best]
                    self.mark_attendance(name)

            top, right, bottom, left = face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 200, 255), 2)
            cv2.putText(frame, name, (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 255), 2)

        buf = cv2.flip(frame, 0).tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.img.texture = texture

# ================= ADMIN =================
class AdminScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        layout.add_widget(Label(text="Admin Dashboard"))

        btn_view = Button(text="View Attendance")
        btn_chart = Button(text="Show Chart")
        btn_back = Button(text="Logout")

        btn_view.bind(on_press=self.view)
        btn_chart.bind(on_press=self.chart)
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'login'))

        layout.add_widget(btn_view)
        layout.add_widget(btn_chart)
        layout.add_widget(btn_back)

        scroll = ScrollView()
        self.output = Label(size_hint_y=None)
        self.output.bind(texture_size=self.output.setter('size'))

        scroll.add_widget(self.output)
        layout.add_widget(scroll)

        self.add_widget(layout)

    def view(self, instance):
        file = datetime.now().strftime("%Y-%m-%d") + ".csv"

        if not os.path.exists(file):
            self.output.text = "No Data"
            return

        df = pd.read_csv(file)
        self.output.text = df.to_string()

    def chart(self, instance):
        file = datetime.now().strftime("%Y-%m-%d") + ".csv"

        if not os.path.exists(file):
            return

        df = pd.read_csv(file)
        df["Name"].value_counts().plot(kind="bar")
        plt.show()

# ================= APP =================
class FaceApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(AdminScreen(name="admin"))
        return sm

if __name__ == "__main__":
    FaceApp().run()