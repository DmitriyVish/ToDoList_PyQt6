import os
import subprocess
import sys

# Имя исполняемого файла
APP_NAME = "ToDoListApp"

# Точка входа (ваш основной файл)
MAIN_SCRIPT = "main.py"

# Папки и файлы, которые нужно включить
ADD_DATA = [
    ("gui/styles", "gui/styles"),  # Папка со стилями
    ("icon", "icon"),              # Папка с иконкой
]

# Иконка приложения (если есть)
ICON_FILE = "icon/icon.png" # Укажите путь к вашему файлу иконки

# Дополнительные параметры PyInstaller
PYINSTALLER_ARGS = [
    "--onefile",        # Создать один исполняемый файл
    "--windowed",       # Не открывать консоль (для GUI приложений)
    "--name", APP_NAME, # Имя исполняемого файла
]

if os.path.exists(ICON_FILE):
    PYINSTALLER_ARGS.extend(["--icon", ICON_FILE])
else:
    print(f"Предупреждение: Иконка {ICON_FILE} не найдена. Исполняемый файл будет без иконки.")

for src, dst in ADD_DATA:
    PYINSTALLER_ARGS.extend(["--add-data", f"{src}{os.pathsep}{dst}"])

PYINSTALLER_ARGS.append(MAIN_SCRIPT)

print("Запуск PyInstaller с аргументами:", " ".join(PYINSTALLER_ARGS))
subprocess.run([sys.executable, "-m", "PyInstaller"] + PYINSTALLER_ARGS)
