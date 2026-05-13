# Migrations

Flask-Migrate is configured. Generate real migrations with:

```bash
flask --app run.py db init
flask --app run.py db migrate -m "initial schema"
flask --app run.py db upgrade
```
