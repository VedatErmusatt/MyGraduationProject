# Kronik Sağlık Uygulaması

## Projeyi Çalıştırmak İçin

Öncelikle `uv` kurulumu yapılmalıdır. Bakınız: <https://docs.astral.sh/uv/>

Ardından virtual environment oluşturulmalıdır.

```bash
uv venv
uv sync
```

Ardından database oluşturulmalıdır.

```bash
uv run python manage.py migrate
```

Proje çalıştırılır.

```bash
uv run python manage.py runserver
```


celery -A chronicle.celery worker -l INFO -f app.log --beat
