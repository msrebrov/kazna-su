import os
import json
import time
import signal
import urllib.request

API = "https://platform-api.max.ru"
TOKEN = os.environ["MAX_BOT_TOKEN"]
SITE_URL = "https://kazna.su"

running = True
signal.signal(signal.SIGTERM, lambda *_: globals().update(running=False))


def api(method, path, data=None):
    url = f"{API}{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", TOKEN)
    if body:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def send_welcome(user_id):
    api("POST", "/messages", {
        "text": "Добро пожаловать в Казну!\n\nПрозрачные групповые финансы для любого коллектива. Создайте группу, приглашайте участников и ведите учёт общих денег — всё в мессенджере.\n\nНажмите кнопку ниже, чтобы узнать больше:",
        "format": "markdown",
        "attachments": [
            {
                "type": "inline_keyboard",
                "payload": {
                    "buttons": [
                        [
                            {
                                "type": "link",
                                "text": "Открыть Казну",
                                "url": SITE_URL
                            }
                        ]
                    ]
                }
            }
        ]
    })


def main():
    marker = None
    print("Kazna Max Bot started")
    while running:
        try:
            params = "?limit=100&timeout=30"
            if marker is not None:
                params += f"&marker={marker}"
            result = api("GET", f"/updates{params}")
            updates = result.get("updates", [])
            marker = result.get("marker", marker)
            for update in updates:
                if update.get("type") == "message_created":
                    msg = update.get("message", {})
                    sender = msg.get("sender", {})
                    user_id = sender.get("user_id")
                    if user_id:
                        send_welcome(user_id)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
