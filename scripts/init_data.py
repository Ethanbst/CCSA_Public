import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CCSA.settings')
django.setup()

# Ajouter le chemin du projet au sys.path
# Ceci est une solution moins robuste, préférez les management commands
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_path)

from datetime import date
from django.core.files import File
from journal.models import Journal  # Assurez-vous que c'est le bon import


def create_journal(title, document_path, cover_path, number, release_date, page_number):
    """Crée un journal avec les données et les fichiers spécifiés."""
    journal = Journal(
        title=title,
        number=number,
        release_date=release_date,
        page_number=page_number
    )

    with open(document_path, 'rb') as doc_file:
        journal.document.save(os.path.basename(document_path), File(doc_file), save=False)

    with open(cover_path, 'rb') as cover_file:
        journal.cover.save(os.path.basename(cover_path), File(cover_file), save=False)

    journal.save()
    print(f"Journal '{title}' créé.")


# Chemins d'accès à vos fichiers (remplacez par les vrais chemins)
document1_path = r"C:\Users\ethan\Downloads\CCSA_Data\Journaux\MSA-17.pdf"
cover1_path = r"C:\Users\ethan\Downloads\CCSA_Data\Journaux\MSA17.jpg"
document2_path = r"C:\Users\ethan\Downloads\CCSA_Data\Journaux\MSA-18-Juin-2024.pdf"
cover2_path = r"C:\Users\ethan\Downloads\CCSA_Data\Journaux\MSA18.png"
document3_path = r"C:\Users\ethan\Downloads\CCSA_Data\Journaux\MSA-19-Dec-2024.pdf"
cover3_path = r"C:\Users\ethan\Downloads\CCSA_Data\Journaux\MSA19.jpg"

# Créer les journaux
create_journal(
    title="Mon Sud Avesnois",
    document_path=document1_path,
    cover_path=cover1_path,
    number=17,
    release_date=date(2024, 1, 1),
    page_number=20
)

create_journal(
    title="Mon Sud Avesnois",
    document_path=document2_path,
    cover_path=cover2_path,
    number=18,
    release_date=date(2024, 6, 1),
    page_number=24
)

create_journal(
    title="Mon Sud Avesnois",
    document_path=document3_path,
    cover_path=cover3_path,
    number=19,
    release_date=date(2024, 12, 1),
    page_number=13
)

print("Script terminé.")
