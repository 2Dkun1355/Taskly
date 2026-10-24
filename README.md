![Python](https://img.shields.io/badge/python-3.12+-3776AB.svg?style=flat&logo=python&logoColor=white)
![Kivy](https://img.shields.io/badge/kivy-2.3.1-3776AB.svg?style=flat&logo=python&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-testing-0A9EDC.svg?style=flat&logo=pytest&logoColor=white)

# Taskly

## Встановлення

```bash
git clone git@github.com:2Dkun1355/Taskly.git
cd Taskly
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Запуск

```bash
PYTHONPATH=app python -m presentation.kivy_ui.main
```

Застосунок використовує `data/tasks.json` як файл даних за замовчуванням. Файл створюється під час першого збереження.

## Тести

```bash
pytest
```


