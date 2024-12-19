from flask import Flask, render_template, jsonify, url_for
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import time

app = Flask(__name__)

# 감시할 폴더 정의
WATCH_FOLDERS = [f'static/image{i}' for i in range(1, 10)]
for folder in WATCH_FOLDERS:
    os.makedirs(folder, exist_ok=True)

latest_files = {f'image{i}': f'{folder}/Place{i}.jpg' for i, folder in enumerate(WATCH_FOLDERS, start=1)}  # 기본 파일 설정


class WatchdogHandler(FileSystemEventHandler):
    def __init__(self, folder_name):
        super().__init__()
        self.folder_name = folder_name

    def on_created(self, event):
        global latest_files
        if not event.is_directory and event.src_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            latest_files[self.folder_name] = event.src_path
            print(f"New image detected in {self.folder_name}: {event.src_path}")


def start_watchdogs():
    observer = Observer()
    for folder in WATCH_FOLDERS:
        folder_name = os.path.basename(folder)
        event_handler = WatchdogHandler(folder_name)
        observer.schedule(event_handler, folder, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


@app.route('/')
def index():
    return render_template('index.html')  # templates/index.html 반환


@app.route('/latest-images')
def latest_images():
    global latest_files
    image_urls = {}
    for folder, path in latest_files.items():
        if path:
            static_path = os.path.relpath(path, os.path.join(os.getcwd(), 'static'))
            image_urls[folder] = url_for('static', filename=static_path.replace("\\", "/"))
    return jsonify(image_urls)


if __name__ == '__main__':
    threading.Thread(target=start_watchdogs, daemon=True).start()
    app.run(debug=True)
