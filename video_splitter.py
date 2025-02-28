import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import sys

class VideoSplitterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Відео Розділювач")
        self.root.geometry("400x350")  # Збільшено розмір для нового чекбокса

        if getattr(sys, 'frozen', False):
            icon_path = os.path.join(sys._MEIPASS, "icon.ico")
        else:
            icon_path = "icon.ico"
        self.root.iconbitmap(icon_path)

        self.frame_input = tk.Frame(root)
        self.frame_input.pack(pady=5)

        self.frame_split = tk.Frame(root)
        self.frame_split.pack(pady=5)

        self.frame_controls = tk.Frame(root)
        self.frame_controls.pack(pady=10)

        self.file_label = tk.Label(self.frame_input, text="Відео файл:")
        self.file_label.grid(row=0, column=0, padx=5, pady=5)

        self.file_entry = tk.Entry(self.frame_input, width=30)
        self.file_entry.grid(row=0, column=1, padx=5, pady=5)

        self.file_button = tk.Button(self.frame_input, text="Огляд", command=self.browse_file)
        self.file_button.grid(row=0, column=2, padx=5, pady=5)

        self.folder_label = tk.Label(self.frame_input, text="Папка для фрагментів:")
        self.folder_label.grid(row=1, column=0, padx=5, pady=5)

        self.folder_entry = tk.Entry(self.frame_input, width=30)
        self.folder_entry.grid(row=1, column=1, padx=5, pady=5)

        self.folder_button = tk.Button(self.frame_input, text="Огляд", command=self.browse_folder)
        self.folder_button.grid(row=1, column=2, padx=5, pady=5)

        self.mode_label = tk.Label(self.frame_split, text="Режим:")
        self.mode_label.grid(row=0, column=0, columnspan=2, pady=5)

        self.mode_var = tk.StringVar(value="time")
        self.time_radio = tk.Radiobutton(self.frame_split, text="Час", variable=self.mode_var, value="time", command=self.toggle_mode)
        self.time_radio.grid(row=1, column=0, padx=5, pady=5)

        self.parts_radio = tk.Radiobutton(self.frame_split, text="Частини", variable=self.mode_var, value="parts", command=self.toggle_mode)
        self.parts_radio.grid(row=1, column=1, padx=5, pady=5)

        self.param_label = tk.Label(self.frame_split, text="Параметр:")
        self.param_label.grid(row=2, column=0, padx=5, pady=5)

        self.param_entry = tk.Entry(self.frame_split, width=10)
        self.param_entry.grid(row=2, column=1, padx=5, pady=5)

        # Чекбокс для видалення аудіо
        self.remove_audio_var = tk.BooleanVar()
        self.remove_audio_checkbox = tk.Checkbutton(self.frame_split, text="Видалити аудіо", variable=self.remove_audio_var)
        self.remove_audio_checkbox.grid(row=3, column=0, columnspan=2, pady=5)

        self.split_button = tk.Button(self.frame_controls, text="Розділити", command=self.split_video)
        self.split_button.pack(pady=5)

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
        remove_audio = self.remove_audio_var.get()

        if getattr(sys, 'frozen', False):
            ffmpeg_path = os.path.join(sys._MEIPASS, "ffmpeg", "bin", "ffmpeg.exe")
        else:
            ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg", "bin", "ffmpeg.exe")

        input_filename = os.path.splitext(os.path.basename(input_file))[0]

        command = []

        if mode == "time":
            try:
                minutes, seconds = map(int, param.split(":"))
                segment_time = f"{minutes:02}:{seconds:02}"
                output_pattern = os.path.join(output_folder, f"{input_filename}_%03d.mp4")

                command = [
                    ffmpeg_path, "-i", input_file, "-c", "copy",
                    "-segment_time", segment_time, "-f", "segment", "-reset_timestamps", "1",
                    output_pattern
                ]
                if remove_audio:
                    command.insert(5, "-an")

            except ValueError:
                messagebox.showerror("Помилка", "Невірний формат часу. Використовуйте MM:SS.")
                return

        elif mode == "parts":
            try:
                num_parts = int(param)
                probe_cmd = [ffmpeg_path, "-i", input_file, "-hide_banner"]
                probe_result = subprocess.run(probe_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                duration_line = [line for line in probe_result.stderr.decode().split("\n") if "Duration" in line]

                if not duration_line:
                    raise ValueError("Неможливо отримати тривалість відео.")

                duration = duration_line[0].split(",")[0].split("Duration:")[1].strip()
                hours, minutes, seconds = map(float, duration.split(":"))
                total_seconds = int(hours * 3600 + minutes * 60 + seconds)
                segment_time = round(total_seconds / num_parts)

                output_pattern = os.path.join(output_folder, f"{input_filename}_%03d.mp4")

                command = [
                    ffmpeg_path, "-i", input_file, "-c", "copy",
                    "-segment_time", str(segment_time), "-f", "segment", "-reset_timestamps", "1",
                    output_pattern
                ]
                if remove_audio:
                    command.insert(5, "-an")

            except ValueError:
                messagebox.showerror("Помилка", "Невірна кількість частин.")
                return

        else:
            messagebox.showerror("Помилка", "Оберіть режим.")
            return

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
