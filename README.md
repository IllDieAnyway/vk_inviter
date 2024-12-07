# VK Inviter

VK Inviter — это приложение для автоматизации приглашений участников в чаты ВКонтакте.  
Создавайте чаты, парсите участников по активности и отправляйте закрепленные сообщения.

## 🛠 Функционал

- **Парсинг пользователей:** возможность выбрать участников, которые были онлайн сегодня или недавно.
- **Создание чатов:** автоматическое создание чатов с заданным названием.
- **Закрепленные сообщения:** отправка сообщения в чат с его последующим закреплением.
- **Фильтрация по полу:** парсинг участников по заданному полу (мужчины, женщины или без разницы).
- **Поддержка основных аккаунтов:** возможность указать основной аккаунт для включения в чат.

## 🖥 Интерфейс
Приложение создано на основе библиотеки `PyQt5` и имеет темную тему оформления для комфортной работы.

![Интерфейс приложения](https://github.com/user-attachments/assets/394a67b6-42ac-48d2-b021-5c53097f98aa)


## 🚀 Установка и запуск

### Требования
- Python 3.8 или выше
- Установленные библиотеки из файла `requirements.txt`

### Установка

1. Клонируйте репозиторий:
    ```bash
    git clone https://github.com/IllDieAnyway/vk_inviter.git
    cd vk_inviter
    ```

2. Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```

3. Запустите приложение:
    ```bash
    python app.py
    ```

## 🧰 Используемые библиотеки

- [PyQt5](https://pypi.org/project/PyQt5/) — библиотека для создания GUI.
- [vk-api](https://pypi.org/project/vk-api/) — клиент для работы с API ВКонтакте.
- [requests](https://pypi.org/project/requests/) — для отправки HTTP-запросов.

## 📚 Как использовать

1. **Токен ВК:** создайте токен через [VK API Token Management](https://vkhost.github.io/).
2. **Запуск:** запустите приложение и введите данные:
   - Ссылка на группу.
   - Токен ВК.
   - Название создаваемого чата.
   - Закрепленное сообщение (опционально).
3. **Парсинг:** проверьте парсер и найдите участников.
4. **Создание чата:** нажмите «Создать чат».

## ⚠️ Примечания
- Приложение работает только с группами ВКонтакте, которые открыты для парсинга участников.
- Убедитесь, что ваш токен имеет права для работы с API (например, `messages`, `groups`, `wall`).

---

**Автор:** [LostSouls](https://t.me/lostsouls_crypto)  
Telegram-бот: [t.me/vk_inviterbot](https://t.me/vk_inviterbot)
