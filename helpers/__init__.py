# helpers/__init__.py
import os
import importlib

helpers_dir = os.path.dirname(__file__)

for filename in os.listdir(helpers_dir):
    if filename.endswith(".py") and not filename.startswith("_") and filename != "__init__.py":
        module_name = f"{__name__}.{filename[:-3]}"
        importlib.import_module(module_name)
        print(f"✅ Импортирован helper-модуль: {module_name}")


