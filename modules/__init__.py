import os
import importlib

# Получаем путь к текущей папке (modules)
modules_dir = os.path.dirname(__file__)

# Перебираем все .py-файлы в папке, кроме служебных
for filename in os.listdir(modules_dir):
    if filename.endswith(".py") and not filename.startswith("_") and filename != "__init__.py":
        module_name = f"{__name__}.{filename[:-3]}"
        importlib.import_module(module_name)
        print(f"✅ Импортирован модуль: {module_name}")
