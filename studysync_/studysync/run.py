from app import create_app
from app.extensions import db
from app.seed import seed_database
from app.handbook_importer import import_handbook_units

app = create_app()


@app.cli.command("init-db")
def init_db():
    """Create database tables and insert demo data."""
    db.drop_all()
    db.create_all()
    seed_database()
    print("Database initialised with demo StudySync data and UWA Handbook subjects.")


@app.cli.command("import-uwa-handbook")
def import_uwa_handbook():
    """Download UWA Handbook unit search data into the local catalogue."""
    db.create_all()
    downloaded, inserted = import_handbook_units()
    print(f"Downloaded {downloaded} unit records from UWA search pages.")
    print(f"Inserted {inserted} new subjects into the local catalogue.")


if __name__ == "__main__":
    app.run(debug=True)
