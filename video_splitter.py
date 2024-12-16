import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

class VideoSplitterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Відео Розділювач")
        self.root.geometry("400x300")  # Зменшено розмір вікна

        # Визначення шляху до іконки після компіляції
        if getattr(sys, 'frozen', False):
            # Якщо програма запущена після компіляції
            icon_path = os.path.join(sys._MEIPASS, "icon.ico")
        else:
            # Якщо програма запущена як звичайний скрипт
            icon_path = "icon.ico"

        # Встановлення іконки для вікна
        self.root.iconbitmap(icon_path)


        # Створення фрейму для організації елементів
        self.frame_input = tk.Frame(root)
        self.frame_input.pack(pady=5)

        self.frame_split = tk.Frame(root)
        self.frame_split.pack(pady=5)

        self.frame_controls = tk.Frame(root)
        self.frame_controls.pack(pady=10)

        # Вибір файлу та папки
        self.file_label = tk.Label(self.frame_input, text="Відео файл:")
        self.file_label.grid(row=0, column=0, padx=5, pady=5)

        self.file_entry = tk.Entry(self.frame_input, width=30)
        self.file_entry.grid(row=0, column=1, padx=5, pady=5)

        self.file_button = tk.Button(self.frame_input, text="Огляд", command=self.browse_file)
        self.file_button.grid(row=0, column=2, padx=5, pady=5)

        self.folder_label = tk.Label(self.frame_input, text="Папка:")
        self.folder_label.grid(row=1, column=0, padx=5, pady=5)

        self.folder_entry = tk.Entry(self.frame_input, width=30)
        self.folder_entry.grid(row=1, column=1, padx=5, pady=5)

        self.folder_button = tk.Button(self.frame_input, text="Огляд", command=self.browse_folder)
        self.folder_button.grid(row=1, column=2, padx=5, pady=5)

        # Режим розділення
        self.mode_label = tk.Label(self.frame_split, text="Режим:")
        self.mode_label.grid(row=0, column=0, columnspan=2, pady=5)

        self.mode_var = tk.StringVar(value="time")
        self.time_radio = tk.Radiobutton(self.frame_split, text="Час", variable=self.mode_var, value="time", command=self.toggle_mode)
        self.time_radio.grid(row=1, column=0, padx=5, pady=5)

        self.parts_radio = tk.Radiobutton(self.frame_split, text="Частини", variable=self.mode_var, value="parts", command=self.toggle_mode)
        self.parts_radio.grid(row=1, column=1, padx=5, pady=5)

        # Параметри розділення
        self.param_label = tk.Label(self.frame_split, text="Параметр:")
        self.param_label.grid(row=2, column=0, padx=5, pady=5)

        self.param_entry = tk.Entry(self.frame_split, width=10)
        self.param_entry.grid(row=2, column=1, padx=5, pady=5)

        # Кнопка розділення
        self.split_button = tk.Button(self.frame_controls, text="Розділити", command=self.split_video)
        self.split_button.pack(pady=5)

        # Сповіщення
        self.notification_label = tk.Label(self.frame_controls, text="", fg="blue")
        self.notification_label.pack()

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Відео файли", "*.mp4 *.mov *.avi")])
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)

    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder_path)

    def toggle_mode(self):
        """Перемикає текст підказок залежно від вибраного режиму."""
        if self.mode_var.get() == "time":
            self.param_label.config(text="Тривалість (MM:SS):")
            self.param_entry.delete(0, tk.END)
        elif self.mode_var.get() == "parts":
            self.param_label.config(text="Кількість частин:")
            self.param_entry.delete(0, tk.END)

    def split_video(self):
        input_file = self.file_entry.get()
        if not os.path.isfile(input_file):
            messagebox.showerror("Помилка", "Файл не знайдено!")
            return

        output_folder = self.folder_entry.get()
        if not os.path.isdir(output_folder):
            messagebox.showerror("Помилка", "Вкажіть існуючу папку для збереження!")
            return

        mode = self.mode_var.get()
        param = self.param_entry.get()
        if getattr(sys, 'frozen', False):  # Для виконуваного файлу (після компіляції)
          ffmpeg_path = os.path.join(sys._MEIPASS, "ffmpeg", "bin", "ffmpeg.exe")
        else:  # Для звичайного запуску з Python
          ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg", "bin", "ffmpeg.exe")

        # Формування команди залежно від режиму
        if mode == "time":
            try:
                # Перевірка формату часу MM:SS
                minutes, seconds = map(int, param.split(":"))
                segment_time = f"{minutes:02}:{seconds:02}"
                command = [
                    ffmpeg_path, "-i", input_file, "-c", "copy", "-map", "0:v", "-map", "0:a",
                    "-segment_time", segment_time, "-f", "segment", "-reset_timestamps", "1",
                    os.path.join(output_folder, "%03d.mp4")
                ]
            except ValueError:
                messagebox.showerror("Помилка", "Невірний формат часу. Використовуйте MM:SS.")
                return

        elif mode == "parts":
            try:
                num_parts = int(param)
                # Отримання загальної тривалості відео
                probe_cmd = [ffmpeg_path, "-i", input_file, "-hide_banner"]
                probe_result = subprocess.run(probe_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                duration_line = [line for line in probe_result.stderr.decode().split("\n") if "Duration" in line]
                if not duration_line:
                    raise ValueError("Неможливо отримати тривалість відео.")
                duration = duration_line[0].split(",")[0].split("Duration:")[1].strip()
                hours, minutes, seconds = map(float, duration.split(":"))
                total_seconds = int(hours * 3600 + minutes * 60 + seconds)
                segment_time = total_seconds // num_parts
                segment_time_str = f"{segment_time // 3600:02}:{(segment_time % 3600) // 60:02}:{segment_time % 60:02}"

                command = [
                    ffmpeg_path, "-i", input_file, "-c", "copy", "-map", "0:v", "-map", "0:a",
                    "-segment_time", segment_time_str, "-f", "segment", "-reset_timestamps", "1",
                    os.path.join(output_folder, "%03d.mp4")
                ]
            except ValueError:
                messagebox.showerror("Помилка", "Невірна кількість частин.")
                return

        else:
            messagebox.showerror("Помилка", "Оберіть режим.")
            return

        # Виконання команди ffmpeg
        def run_ffmpeg():
            try:
                self.notification_label.config(text="Розпочато обробку відео...")
                subprocess.run(command, check=True)
                self.notification_label.config(text="Відео успішно розділено!\nФайли збережено в " + output_folder)
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Помилка", f"Сталася помилка: {e}")

        threading.Thread(target=run_ffmpeg).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoSplitterApp(root)
    root.mainloop()
