import sys
import os

# Пытаемся настроить логирование максимально рано
try:
    from android.storage import app_context
    # Внутренняя папка приложения, куда ВСЕГДА есть доступ на запись
    log_dir = app_context.getFilesDir().getAbsolutePath()
    log_path = os.path.join(log_dir, "crash_log.txt")
    sys.stderr = open(log_path, "w")
    print("LOGGING STARTED ON ANDROID")
except Exception as e:
    print(f"Logging setup failed: {e}")

import shutil
import threading
import webbrowser
from kivy.lang import Builder
from kivy.utils import platform
from kivy.properties import StringProperty, ListProperty, ObjectProperty, ColorProperty, NumericProperty
from kivy.clock import Clock
from kivy.uix.behaviors import ButtonBehavior
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget
from kivymd.toast import toast
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.storage.jsonstore import JsonStore

# Определение базового пути
primary_path = os.path.expanduser("~")

# Функция для запроса разрешений на Android
def ask_permissions():
    if platform == 'android':
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.MANAGE_EXTERNAL_STORAGE
        ])

KV = '''
#:import webbrowser webbrowser

<ItemConfirm>:
    on_release: root.func(root.path)
    IconLeftWidget:
        icon: root.icon_name

<CustomDrawerItem>:
    orientation: "horizontal"
    size_hint_y: None
    height: "56dp"
    padding: "20dp", 0
    spacing: "18dp"
    md_bg_color: 0, 0, 0, 0
    MDIcon:
        icon: root.icon
        theme_text_color: "Custom"
        text_color: app.drawer_text_color
        pos_hint: {"center_y": .5}
        font_size: "24dp"
    MDLabel:
        text: root.text
        theme_text_color: "Custom"
        text_color: app.drawer_text_color
        valign: "center"
        font_style: "Button"

<FileItem>:
    orientation: "vertical"
    size_hint_y: None
    height: "115dp"
    padding: "8dp"
    canvas.before:
        Color:
            rgba: (0.15, 0.15, 0.18, 1) if app.theme_cls.theme_style == "Dark" else (0.9, 0.9, 0.93, 1)
        RoundedRectangle: 
            pos: self.pos
            size: self.size
            radius: [12,]
    on_release: app.on_item_click(root.path)
    MDIcon:
        icon: root.icon
        font_size: "40dp"
        halign: "center"
        pos_hint: {"center_x": .5}
        theme_text_color: "Custom"
        text_color: app.theme_cls.primary_color
    MDLabel:
        text: root.name
        halign: "center"
        font_size: "10sp"
        shorten: True
        max_lines: 2

ScreenManager:
    id: sm
    MainScreen:
    EditorScreen:

<MainScreen>:
    name: "main"
    MDNavigationLayout:
        MDScreenManager:
            MDScreen:
                MDBoxLayout:
                    orientation: 'vertical'
                    md_bg_color: app.theme_cls.bg_normal

                    MDRelativeLayout:
                        size_hint_y: None
                        height: "56dp"
                        md_bg_color: app.theme_cls.primary_color
                        MDIconButton:
                            icon: "menu"
                            pos_hint: {"center_y": .5, "x": 0}
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 1
                            on_release: nav_drawer.set_state("open")
                        MDLabel:
                            text: "Orion Explorer"
                            halign: "center"
                            valign: "center"
                            font_style: "H6"
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 1
                            pos_hint: {"center_x": .5, "center_y": .5}
                        MDBoxLayout:
                            adaptive_width: True
                            pos_hint: {"center_y": .5, "right": 1}
                            MDIconButton:
                                icon: "magnify"
                                theme_text_color: "Custom"
                                text_color: 1, 1, 1, 1
                                on_release: app.show_search_dialog()
                            MDIconButton:
                                icon: "plus-box"
                                theme_text_color: "Custom"
                                text_color: 1, 1, 1, 1
                                on_release: app.show_main_menu()

                    MDBoxLayout:
                        orientation: "vertical"
                        size_hint_y: None
                        height: "70dp"
                        padding: "15dp", "8dp"
                        spacing: "4dp"
                        md_bg_color: app.theme_cls.bg_darkest if app.theme_cls.theme_style == "Dark" else (0.95, 0.95, 0.95, 1)
                        MDBoxLayout:
                            MDLabel:
                                text: f"Занято: {app.storage_used} ГБ / {app.storage_total} ГБ"
                                font_style: "Caption"
                                theme_text_color: "Primary"
                            MDLabel:
                                text: f"Свободно: {app.storage_free} ГБ"
                                font_style: "Caption"
                                halign: "right"
                                theme_text_color: "Secondary"
                        MDProgressBar:
                            value: app.storage_percent
                            color: app.theme_cls.primary_color
                            size_hint_y: None
                            height: "4dp"

                    MDBoxLayout:
                        orientation: 'vertical'
                        padding: "10dp"
                        spacing: "10dp"
                        MDLabel:
                            text: app.current_path
                            font_style: "Caption"
                            size_hint_y: None
                            height: "20dp"
                            shorten: True
                        RecycleView:
                            id: rv
                            viewclass: 'FileItem'
                            RecycleGridLayout:
                                cols: 3
                                default_size: None, dp(115)
                                default_size_hint: 1, None
                                size_hint_y: None
                                height: self.minimum_height
                                spacing: "10dp"

                    MDBoxLayout:
                        size_hint_y: None
                        height: "65dp"
                        padding: "10dp"
                        MDIconButton:
                            icon: "arrow-left"
                            on_release: app.go_back()
                        MDWidget:
                        MDFloatingActionButton:
                            icon: "home"
                            on_release: app.go_home()
                        MDWidget:
                        MDIconButton:
                            icon: "content-paste"
                            on_release: app.paste_item()

        MDNavigationDrawer:
            id: nav_drawer
            radius: (0, 16, 16, 0)
            MDBoxLayout:
                orientation: "vertical"
                padding: "15dp", "30dp"
                MDLabel:
                    text: "Orion Explorer"
                    size_hint_y: None
                    height: "70dp"
                    font_style: "H4"
                    theme_text_color: "Custom"
                    text_color: app.theme_cls.primary_color
                MDLabel:
                    text: "Проводник и редактор"
                    size_hint_y: None
                    height: "50dp"
                    font_style: "H6"
                    theme_text_color: "Secondary"
                MDWidget:
                    size_hint_y: None
                    height: "20dp"
                CustomDrawerItem:
                    icon: "update"
                    text: "Что нового?"
                    on_release: app.show_changelog()
                CustomDrawerItem:
                    icon: "cog"
                    text: "Сменить тему"
                    on_release: app.toggle_theme()
                CustomDrawerItem:
                    icon: "message-draw"
                    text: "Обратная связь (VK)"
                    on_release: webbrowser.open("https://vk.com/id850916439")
                CustomDrawerItem:
                    icon: "shield-check"
                    text: "Политика конфендициальности"
                    on_release: webbrowser.open("https://docs.google.com/document/d/1Y6qM3bMf-EVIgz5DOuxLbU_uPUepBkuXR1PWe2CoPsc/edit?usp=sharing")
                MDWidget:

<EditorScreen>:
    name: "editor"
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: app.theme_cls.bg_normal
        MDTopAppBar:
            title: "Редактор"
            left_action_items: [["arrow-left", lambda x: app.close_editor()]]
            right_action_items: [["content-save", lambda x: app.save_from_editor()]]
        MDTextField:
            id: text_input
            multiline: True
            mode: "fill"
            size_hint_y: 1
'''


class ItemConfirm(OneLineIconListItem):
    path = StringProperty()
    icon_name = StringProperty()
    func = ObjectProperty()


class MainScreen(Screen): pass


class EditorScreen(Screen): pass


class CustomDrawerItem(ButtonBehavior, MDBoxLayout):
    icon = StringProperty()
    text = StringProperty()


class FileItem(ButtonBehavior, MDBoxLayout):
    path, name, icon = StringProperty(), StringProperty(), StringProperty()


class OrionExplorer(MDApp):
    current_path = StringProperty(primary_path)
    clipboard, history = StringProperty(""), ListProperty([])
    drawer_text_color = ColorProperty((1, 1, 1, 1))
    storage_total, storage_used, storage_free = StringProperty("0"), StringProperty("0"), StringProperty("0")
    storage_percent = NumericProperty(0)
    editing_path, dialog = "", None

    def build(self):
        self.theme_cls.theme_style, self.theme_cls.primary_palette = "Dark", "Teal"
        self.store = JsonStore('storage.json')
        self.update_drawer_colors()
        self.update_storage_info()
        return Builder.load_string(KV)

    def on_start(self):
        ask_permissions()
        self.load_path_threaded(self.current_path)
        if not self.store.exists('settings') or not self.store.get('settings')['welcome_shown']:
            Clock.schedule_once(self.show_welcome_dialog, 0.5)

    def show_welcome_dialog(self, *args):
        welcome_text = (
            "Это бета версия приложения. и если вам что-то не понравилось, не спешите ставить низкую оценку приложению. "
            "Пишите мне в ВК, я выслушаю вас и исправлю все баги, ну или добавлю что то, даже если вы просто захотели поговорить. Пишите! "
            "Так же перед использованием приложения вы должны ознакомиться с политикой конфиденциальности. Нажимая Продолжить, вы автоматически соглашаетесь с политикой конфиденциальности."
        )
        self.dialog = MDDialog(
            title="Добро пожаловать!",
            text=welcome_text,
            auto_dismiss=False,
            buttons=[
                MDFlatButton(
                    text="VK Для связи",
                    on_release=lambda x: webbrowser.open("https://vk.com/id850916439")
                ),
                MDFlatButton(
                    text="Политика конфендициальности ",
                    on_release=lambda x: webbrowser.open("https://docs.google.com/document/d/1Y6qM3bMf-EVIgz5DOuxLbU_uPUepBkuXR1PWe2CoPsc/edit?usp=sharing")
                ),
                MDRaisedButton(
                    text="Продолжить",
                    on_release=self.close_welcome_dialog
                ),
            ],
        )
        self.dialog.open()

    def close_welcome_dialog(self, *args):
        self.store.put('settings', welcome_shown=True)
        self.dialog.dismiss()

    def show_changelog(self):
        self.root.get_screen('main').ids.nav_drawer.set_state("close")
        updates = (
            "• Приветствие теперь появляется только 1 раз.\n• Текст и кнопки входа возвращены.\n• Панель диска работает.\n• Исправлена ошибка NameError.")
        self.dialog = MDDialog(title="Обновление", text=updates,
                               buttons=[MDFlatButton(text="ОК", on_release=lambda x: self.dialog.dismiss())])
        self.dialog.open()

    def _update(self, path, data):
        if not self.root: return
        self.current_path = path
        try:
            self.root.get_screen('main').ids.rv.data = data
        except:
            pass
        self.update_storage_info()

    def update_storage_info(self):
        try:
            total, used, free = shutil.disk_usage(self.current_path)
            self.storage_total = str(round(total / (1024 ** 3), 1))
            self.storage_used = str(round(used / (1024 ** 3), 1))
            self.storage_free = str(round(free / (1024 ** 3), 1))
            self.storage_percent = (used / total) * 100
        except:
            pass

    def update_drawer_colors(self):
        self.drawer_text_color = (1, 1, 1, 1) if self.theme_cls.theme_style == "Dark" else (0, 0, 0, 1)

    def toggle_theme(self):
        self.theme_cls.theme_style = "Light" if self.theme_cls.theme_style == "Dark" else "Dark"
        self.update_drawer_colors()
        self.load_path_threaded(self.current_path)
        self.root.get_screen('main').ids.nav_drawer.set_state("close")

    def load_path_threaded(self, path, search=""):
        threading.Thread(target=self._fetch, args=(path, search), daemon=True).start()

    def _fetch(self, path, search):
        try:
            items = os.listdir(path)
            if search: items = [i for i in items if search.lower() in i.lower()]
            items.sort(key=lambda x: (not os.path.isdir(os.path.join(path, x)), x.lower()))
            data = []
            for i in items:
                p = os.path.join(path, i)
                icon = "folder" if os.path.isdir(p) else "file-outline"
                if i.lower().endswith(('.txt', '.py', '.json')): icon = "file-document"
                data.append({"path": p, "name": i, "icon": icon})
            Clock.schedule_once(lambda dt: self._update(path, data), 0)
        except:
            Clock.schedule_once(lambda dt: toast("Нет доступа"), 0)

    def on_item_click(self, path):
        if os.path.isdir(path):
            self.history.append(self.current_path); self.load_path_threaded(path)
        else:
            self.show_menu(path)

    def show_menu(self, path):
        content = MDBoxLayout(orientation='vertical', adaptive_height=True)
        items = [("pencil", "Имя", self.ren_diag), ("content-cut", "Вырезать", self.cut)]
        if path.lower().endswith(('.txt', '.py', '.json')): items.append(("file-edit", "Редактор", self.open_editor))
        items.append(("delete", "Удалить", self.delete))
        for icon, text, func in items:
            content.add_widget(ItemConfirm(text=text, icon_name=icon, path=path, func=func))
        self.dialog = MDDialog(title="Действия", type="custom", content_cls=content);
        self.dialog.open()

    def open_editor(self, path):
        if self.dialog: self.dialog.dismiss()
        self.editing_path = path
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                self.root.get_screen('editor').ids.text_input.text = f.read()
            self.root.current = "editor"
        except:
            toast("Ошибка чтения")

    def save_from_editor(self):
        try:
            with open(self.editing_path, 'w', encoding='utf-8') as f:
                f.write(self.root.get_screen('editor').ids.text_input.text)
            toast("Сохранено!");
            self.root.current = "main"
        except:
            toast("Ошибка")

    def close_editor(self):
        self.root.current = "main"

    def ren_diag(self, path):
        if self.dialog: self.dialog.dismiss()
        f = MDTextField(text=os.path.basename(path))
        self.dialog = MDDialog(title="Новое имя", type="custom", content_cls=f,
                               buttons=[MDRaisedButton(text="ОК", on_release=lambda x: self.do_ren(path, f.text))])
        self.dialog.open()

    def do_ren(self, p, n):
        try:
            os.rename(p, os.path.join(os.path.dirname(p), n)); self.load_path_threaded(self.current_path)
        except:
            toast("Ошибка")
        self.dialog.dismiss()

    def cut(self, p):
        self.clipboard = p; toast("Вырезано"); self.dialog.dismiss()

    def paste_item(self):
        if self.clipboard:
            try:
                shutil.move(self.clipboard, self.current_path); self.clipboard = ""; self.load_path_threaded(
                    self.current_path)
            except:
                toast("Ошибка")
        else:
            toast("Пусто")

    def delete(self, p):
        try:
            if os.path.isdir(p):
                shutil.rmtree(p)
            else:
                os.remove(p)
            self.load_path_threaded(self.current_path)
        except:
            toast("Ошибка")
        self.dialog.dismiss()

    def show_search_dialog(self):
        f = MDTextField(hint_text="Поиск...");
        f.bind(text=lambda i, v: self.load_path_threaded(self.current_path, v))
        self.dialog = MDDialog(title="Поиск", type="custom", content_cls=f);
        self.dialog.open()

    def show_main_menu(self):
        self.dialog = MDDialog(title="Создать", buttons=[
            MDRaisedButton(text="ФАЙЛ", on_release=lambda x: self.show_in("Файл", self.mk_f)),
            MDRaisedButton(text="ПАПКА", on_release=lambda x: self.show_in("Папка", self.mk_d))])
        self.dialog.open()

    def mk_f(self, n):
        try:
            open(os.path.join(self.current_path, n), 'a').close(); self.load_path_threaded(self.current_path)
        except:
            toast("Ошибка")
        self.dialog.dismiss()

    def mk_d(self, n):
        try:
            os.mkdir(os.path.join(self.current_path, n)); self.load_path_threaded(self.current_path)
        except:
            toast("Ошибка")
        self.dialog.dismiss()

    def show_in(self, t, c):
        if self.dialog: self.dialog.dismiss()
        f = MDTextField()
        self.dialog = MDDialog(title=t, type="custom", content_cls=f,
                               buttons=[MDRaisedButton(text="ОК", on_release=lambda x: c(f.text))])
        self.dialog.open()

    def go_back(self):
        if self.history: self.load_path_threaded(self.history.pop())

    def go_home(self):
        self.load_path_threaded(primary_path)


if __name__ == "__main__":
    try:
        OrionExplorer().run()
    except Exception as e:
        # Финальная запись, если приложение упало даже не запустившись
        with open(os.path.join(log_dir, "crash_log.txt"), "a") as f:
            f.write(f"\nCRITICAL BOOT ERROR: {str(e)}")
        raise e
