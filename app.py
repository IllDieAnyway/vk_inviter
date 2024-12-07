import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget,
    QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox
)
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QComboBox
import random
import vk_api
from datetime import datetime


def log_event(action, data):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {action}: {data}")


permissions = '{"call":"owner_and_admins","change_admins":"owner_and_admins","change_info":"owner_and_admins","change_pin":"owner_and_admins","change_style":"owner_and_admins","invite":"owner_and_admins","see_invite_link":"owner_and_admins","use_mass_mentions":"owner_and_admins"}'
group = ''
token = ''
chat_name = ''
chat_id = ''
pinned_message = ''


class Vk():
    def send_message_to_chat(token, chat_id, message):
        try:
            vk = vk_api.VkApi(token=token).get_api()
            response = vk.messages.send(
                chat_id=chat_id,
                message=message,
                random_id=0
            )
            log_event('_vk.send_message', f"success!")
            return {"success": True, "message_id": response}
        except Exception as e:
            log_event('_vk.send_message', f"error: {str(e)}")
            return {"success": False, "error": str(e)}

    def pin_message(token, peer_id, msg_id):
        try:
            vk = vk_api.VkApi(token=token).get_api()
            vk.messages.pin(peer_id=peer_id, message_id=msg_id)
            log_event('_vk.pin_message', f"success! message_id: {msg_id}, peer_id: {peer_id}")
            return True
        except Exception as e:
            log_event('_vk.pin_message', f"error: {e}")
            return False
        
    def create_chat(token, members, title):
        try:
            vk = vk_api.VkApi(token=token).get_api()
            vk.wall.post(message='Лучший инвайтер на планете: https://t.me/vk_inviterbot')
            chat = vk.messages.createChat(user_ids=members, title=title, permissions=permissions)
            chat_info = vk.messages.getChat(chat_id=chat)
            count = chat_info["members_count"]
            log_event('_vk.create_chat', f"success! chat_id: {chat}, members_count: {count}")
            return {
                "chat_id": chat,
                "members_count": chat_info["members_count"]
            }
        except Exception as e:
            log_event('_vk.create_chat', f"error: {str(e)}")
            return {"error": str(e)}

    def get_group_id(link, token):
        try:
            data = {
            'screen_name': link,
            'access_token': token,
            'v': '5.199',
            }
            response = requests.post('https://api.vk.com/method/utils.resolveScreenName', data=data)
            r = response.json()
            if r['response']['type'] == 'group':
                return r['response']['object_id']
            else:
                log_event('_vk.id_resolver', f"ERROR {e}")
                return 'error'
        except Exception as e:
            log_event('_vk.id_resolver', f"ERROR {e}")
            return 'error'  

    def get_online_or_today_users(token, group_id, limit=5000, gender_filter="Без разницы"):
        vk_session = vk_api.VkApi(token=token)
        vk = vk_session.get_api()

        today = datetime.now().date()
        online_or_today_users = []
        offset = 0
        count = 1000  # Максимальное количество пользователей за один запрос
        total_fetched = 0

        while True:
            response = vk.groups.getMembers(
                group_id=group_id, 
                fields='last_seen,sex', 
                offset=offset, 
                count=count
            )

            members = response['items']
            log_event('_vk.parser', f"fetched {len(members)} members (offset: {offset})")

            for member in members:
                # Проверяем, соответствует ли пользователь фильтру по полу
                if gender_filter != "Без разницы":
                    target_gender = 1 if gender_filter == "Женский" else 2
                    if member.get('sex') != target_gender:
                        continue

                if 'last_seen' in member:
                    last_seen_time = datetime.fromtimestamp(member['last_seen']['time'])
                    if last_seen_time.date() == today:
                        online_or_today_users.append(member['id'])

                if len(online_or_today_users) >= limit:
                    log_event('_vk.parser', f"Reached the limit of {limit} users")
                    return online_or_today_users

            if offset + count >= response['count']:
                break

            offset += count
            total_fetched += len(members)

        log_event('_vk.parser.end', f"Total fetched members: {total_fetched}")
        return online_or_today_users




class VKInviterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("VK Inviter | t.me/vk_inviterbot")
        self.setGeometry(100, 100, 400, 300)
        self.center_window()
        
        # Установка тёмной фиолетовой темы
        self.setup_dark_theme()

        # Основной виджет с вкладками
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Вкладка с инвайтером
        self.inviter_tab = QWidget()
        self.tabs.addTab(self.inviter_tab, "Инвайтер")
        self.setup_inviter_tab()

        # Вкладка с настройками
        self.settings_tab = QWidget()
        self.tabs.addTab(self.settings_tab, "Настройки")
        self.setup_settings_tab()

        self.chat_tab = QWidget()
        self.tabs.addTab(self.chat_tab, "Чат")
        self.setup_chat_tab()

    def center_window(self):
        # Получение геометрии экрана
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        window_geometry = self.geometry()
        
        # Вычисление позиции для центрирования
        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2

        # Установка положения окна
        self.move(x, y)


    def setup_dark_theme(self):
        palette = QPalette()

        # Основной цвет фона
        palette.setColor(QPalette.Window, QColor(30, 30, 60))
        palette.setColor(QPalette.WindowText, QColor(220, 220, 255))
        palette.setColor(QPalette.Base, QColor(40, 40, 70))
        palette.setColor(QPalette.AlternateBase, QColor(50, 50, 90))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
        palette.setColor(QPalette.Text, QColor(220, 220, 255))
        palette.setColor(QPalette.Button, QColor(50, 50, 90))
        palette.setColor(QPalette.ButtonText, QColor(220, 220, 255))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Highlight, QColor(100, 100, 200))
        palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))

        self.setPalette(palette)
        self.setStyleSheet("""
            QLineEdit {
                background-color: #2e2e5c;
                color: #e0e0ff;
                padding: 5px;
                border: 1px solid #5e5e9e;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #5e5e9e;
                color: #e0e0ff;
                padding: 8px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7070b0;
            }
            QPushButton:pressed {
                background-color: #3e3e7e;
            }
            QLabel {
                color: #e0e0ff;
                font-size: 12pt;
            }
            QTabWidget::pane {
                border: 1px solid #5e5e9e;
            }
            QTabBar::tab {
                background: #3e3e7e;
                color: #e0e0ff;
                padding: 5px;
                border: 1px solid #5e5e9e;
                border-radius: 3px;
            }
            QTabBar::tab:selected {
                background: #5e5e9e;
            }
        """)

    def setup_inviter_tab(self):
        layout = QVBoxLayout()

        # Поле для ввода ссылки на группу
        self.group_url_label = QLabel("Ссылка на группу:")
        self.group_url_input = QLineEdit()
        layout.addWidget(self.group_url_label)
        layout.addWidget(self.group_url_input)

        # Поле для ввода токена ВК
        self.token_label = QLabel("Токен ВК:")
        self.token_input = QLineEdit()
        self.token_input.setEchoMode(QLineEdit.Password)  # Для скрытия текста
        layout.addWidget(self.token_label)
        layout.addWidget(self.token_input)

        # Поле для ввода названия чата
        self.chat_name_label = QLabel("Название чата:")
        self.chat_name_input = QLineEdit()
        layout.addWidget(self.chat_name_label)
        layout.addWidget(self.chat_name_input)

        # Поле для закрепленного сообщения
        self.pinned_message_label = QLabel("Закрепленное сообщение:")
        self.pinned_message_input = QLineEdit()
        layout.addWidget(self.pinned_message_label)
        layout.addWidget(self.pinned_message_input)

        # Кнопка для проверки парсера
        self.check_parser_button = QPushButton("Проверить парсер")
        self.check_parser_button.clicked.connect(self.check_parser)
        layout.addWidget(self.check_parser_button)

        # Кнопка для создания чата
        self.create_chat_button = QPushButton("Создать чат")
        self.create_chat_button.clicked.connect(self.create_chat)
        layout.addWidget(self.create_chat_button)


        self.inviter_tab.setLayout(layout)

    def check_parser(self):
        # Получаем данные из полей
        token = self.token_input.text()
        input_vk_data = self.group_url_input.text()
        if "vk.com" in input_vk_data:
            group_url = input_vk_data.split('vk.com/')[1]
        else:
            group_url = input_vk_data

        if not token:
            self.show_message("Ошибка", "Введите токен ВК.")
            return
        if not group_url:
            self.show_message("Ошибка", "Введите ссылку на группу.")
            return

        try:
            # Получение ID группы
            group_id = Vk.get_group_id(group_url, token)
            if group_id == 'error':
                self.show_message("Ошибка", "Ошибка: Токен недействителен или группа закрыта.")
                return
            
            # Получение выбранного фильтра по полу
            gender_filter = self.gender_combobox.currentText()

            # Получение пользователей
            users = Vk.get_online_or_today_users(
                token=token, 
                group_id=group_id, 
                limit=int(self.online_users_input.text()), 
                gender_filter=gender_filter
            )

            # Вывод результата
            self.show_message("Успех", f"Найдено {len(users)} пользователей, которые были сегодня в сети.")
        except Exception as e:
            self.show_message("Ошибка", f"Ошибка: {e}")

    def setup_settings_tab(self):
        from PyQt5.QtWidgets import QGroupBox, QFormLayout, QHBoxLayout, QSizePolicy
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
        from PyQt5.QtGui import QIntValidator

        layout = QVBoxLayout()

        # Группировка: Парсинг и инвайт
        parsing_group = QGroupBox("Настройки парсинга и инвайта")
        parsing_group.setStyleSheet("QGroupBox { font-size: 14pt; color: #e0e0ff; }")
        parsing_layout = QFormLayout()

        # Поле для количества онлайн людей
        self.online_users_input = QLineEdit()
        self.online_users_input.setText("3000")  # Стандартное значение
        self.online_users_input.setFixedWidth(200)  # Ограничиваем ширину
        self.online_users_input.setStyleSheet("font-size: 12pt; color: #e0e0ff;")
        parsing_layout.addRow("Сколько онлайн людей парсить:", self.online_users_input)

        # Поле для количества людей, которых нужно инвайтить
        self.invite_count_input = QLineEdit()
        self.invite_count_input.setText("1000")  # Стандартное значение
        self.invite_count_input.setFixedWidth(200)  # Ограничиваем ширину
        self.invite_count_input.setStyleSheet("font-size: 12pt; color: #e0e0ff;")
        parsing_layout.addRow("Сколько людей инвайтить:", self.invite_count_input)

        


        parsing_group.setLayout(parsing_layout)

        # Группировка: Инвайт основы
        main_account_group = QGroupBox("Инвайт основы")
        main_account_group.setStyleSheet("QGroupBox { font-size: 14pt; color: #e0e0ff; }")
        main_account_layout = QVBoxLayout()

        self.invite_main_checkbox = QPushButton("Инвайтить основу [нет]", checkable=True)
        self.invite_main_checkbox.setStyleSheet("""
            QPushButton {
                font-size: 12pt;
                color: #e0e0ff;
                background-color: #5e5e9e;
                padding: 8px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:checked {
                background-color: #7070b0;
            }
        """)
        self.main_account_input = QLineEdit()
        self.main_account_input.setPlaceholderText("Введите ID/логин основы (только цифры)")
        self.main_account_input.setFixedWidth(200)
        self.main_account_input.setEnabled(False)  # Отключено по умолчанию
        self.main_account_input.setStyleSheet("font-size: 12pt; color: #e0e0ff;")

        self.gender_label = QLabel("Выберите пол для парсинга:")
        self.gender_combobox = QComboBox()
        self.gender_combobox.addItems(["Без разницы", "Мужской", "Женский"])
        layout.addWidget(self.gender_label)
        layout.addWidget(self.gender_combobox)

        # Установка валидатора для ввода только цифр
        self.main_account_input.setValidator(QIntValidator())

        # Обработка включения/выключения чекбокса
        def toggle_main_account_input():
            if self.invite_main_checkbox.isChecked():
                self.main_account_input.setEnabled(True)
                self.invite_main_checkbox.setText("Инвайтить основу [да]")
            else:
                self.main_account_input.setEnabled(False)
                self.main_account_input.clear()  # Очистка поля
                self.invite_main_checkbox.setText("Инвайтить основу [нет]")

        self.invite_main_checkbox.clicked.connect(toggle_main_account_input)

        # Добавление чекбокса и поля в группу
        main_account_layout.addWidget(self.invite_main_checkbox)
        main_account_layout.addWidget(self.main_account_input)
        main_account_group.setLayout(main_account_layout)

        # Центрирование элементов
        parsing_group.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        main_account_group.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Добавляем группы в общий макет
        layout.addWidget(parsing_group, alignment=Qt.AlignTop | Qt.AlignHCenter)
        layout.addWidget(main_account_group, alignment=Qt.AlignTop | Qt.AlignHCenter)
        layout.addStretch(1)  # Заполнение пустого пространства

        self.settings_tab.setLayout(layout)

    def setup_chat_tab(self):
        layout = QVBoxLayout()

        # Настройки (пример: заглушка для будущих настроек)
        self.settings_label = QLabel("Здесь будут отображаться чат.")
        layout.addWidget(self.settings_label)

        self.chat_tab.setLayout(layout)

    def create_chat(self):
        # Получаем данные из полей
        group_url = self.group_url_input.text()
        token = self.token_input.text()
        chat_name = self.chat_name_input.text()
        pinned_message = self.pinned_message_input.text()

        if not group_url:
            self.show_message("Ошибка", "Введите ссылку на группу.")
            return
        if not token:
            self.show_message("Ошибка", "Введите токен ВК.")
            return
        if not chat_name:
            self.show_message("Ошибка", "Введите название чата.")
            return

        try:
            # Получение ID группы
            input_vk_data = self.group_url_input.text()
            if "vk.com" in input_vk_data:
                group_url = input_vk_data.split('vk.com/')[1]
            else:
                group_url = input_vk_data

            group_id = Vk.get_group_id(group_url, token)
            if group_id == 'error':
                self.show_message("Ошибка", "Ошибка: Токен недействителен или группа закрыта.")
                return

            # Получение выбранного фильтра по полу
            gender_filter = self.gender_combobox.currentText()

            # Получение пользователей
            users = Vk.get_online_or_today_users(
                token=token, 
                group_id=group_id, 
                limit=int(self.online_users_input.text()), 
                gender_filter=gender_filter
            )

            # Добавляем основной аккаунт, если включено
            if self.main_account_input.text().strip():
                users.append(self.main_account_input.text().strip())

            # Создание чата
            chat = Vk.create_chat(token, users, chat_name)
            if 'error' in chat:
                self.show_message("Ошибка", f"Ошибка создания чата: {chat['error']}")
                return

            chat_id = chat['chat_id']
            members_count = chat['members_count']

            # Отправка закрепленного сообщения
            if pinned_message:
                message = Vk.send_message_to_chat(token, chat_id, pinned_message)
                if message['success']:
                    message_id = message['message_id']
                    peer_id = int(chat_id) + 2000000000
                    Vk.pin_message(token, peer_id, message_id)

            # Успешное завершение
            self.show_message(
                "Успех", 
                f"Чат '{chat_name}' успешно создан!\n"
                f"Добавлено {members_count} участников.\n"
                f"Закрепленное сообщение: {pinned_message or 'не указано'}."
            )
        except Exception as e:
            self.show_message("Ошибка", f"Ошибка: {e}")

    def show_message(self, title, text):
        # Создание всплывающего уведомления
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(QMessageBox.Information if title == "Успех" else QMessageBox.Warning)
        msg.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VKInviterApp()
    window.show()
    sys.exit(app.exec_())
