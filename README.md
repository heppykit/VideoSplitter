# VideoSplitter

**VideoSplitter** — це простий графічний інтерфейс для розділення відеофайлів за допомогою програми ffmpeg. Вона дозволяє вам розділити відео на частини або за заданий час.

## Функціональність:

- Розділення відео на частини по тривалості або за кількістю частин.
- Використовує ffmpeg для обробки відео.
- Програму можна скомпілювати у єдиний файл за допомогою PyInstaller.
- Підтримує GUI (Графічний Інтерфейс Користувача) за допомогою Tkinter.
  
## Вимоги

Для компіляції та запуску програми на вашому комп'ютері потрібно:

- Python 3.x
- PyInstaller
- ffmpeg

## Варіанти запуску програми
### 1. Для запуску програми можна просто завантажити .exe файл та запусти його


### 2. Для запуску компіляції

Відкрийте термінал і виконайте:

```bash
pyinstaller --onefile --windowed --add-data "ffmpeg;ffmpeg" --add-data "icon.ico;." --icon="icon.ico" --name="VideoSplitter" video_splitter.py
