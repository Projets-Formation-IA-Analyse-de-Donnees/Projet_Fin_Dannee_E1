from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .form import CSVUploadForm
from django.db import connection
import csv, io

@login_required
def import_formateurs_csv(request):
    form = CSVUploadForm()
    formateurs_existants = []

    # ---- SUPPRESSION d’un formateur ----
    if request.method == 'POST' and 'supprimer' in request.POST:
        nom = request.POST['nom']
        email = request.POST['email']
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM "Data_Aggregation_formateur"
                WHERE nom = %s AND email = %s
            """, [nom, email])
        messages.success(request, f"Formateur {nom} supprimé avec succès.")
        return redirect('import_formateurs')

    # ---- MODIFICATION d’un formateur ----
    elif request.method == 'POST' and 'modifier' in request.POST:
        nom = request.POST['nom']
        email = request.POST['email']
        nouvelle_bio = request.POST['bio']
        nouvelle_competence = request.POST['competence']
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE "Data_Aggregation_formateur"
                SET bio = %s, competence = %s
                WHERE nom = %s AND email = %s
            """, [nouvelle_bio, nouvelle_competence, nom, email])
        messages.success(request, f"Formateur {nom} modifié avec succès.")
        return redirect('import_formateurs')

    # ---- IMPORTATION CSV ----
    elif request.method == 'POST' and request.FILES.get('fichier'):
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            fichier = request.FILES['fichier']
            decoded_file = fichier.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(decoded_file))

            for row in reader:
                nom = row['nom']
                email = row['email']
                bio = row['bio']
                competence = row['competence']

                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT COUNT(*) FROM "Data_Aggregation_formateur"
                        WHERE nom = %s AND email = %s
                    """, [nom, email])
                    existe = cursor.fetchone()[0]

                    if existe == 0:
                        cursor.execute("""
                            INSERT INTO "Data_Aggregation_formateur" (nom, email, bio, competence)
                            VALUES (%s, %s, %s, %s)
                        """, [nom, email, bio, competence])
                    else:
                        formateurs_existants.append((nom, email))

            if not formateurs_existants:
                messages.success(request, "Tous les formateurs ont été importés avec succès.")
            else:
                messages.warning(request, "Certains formateurs étaient déjà présents et n'ont pas été importés.")

    # ---- SELECT pour afficher les formateurs existants ----
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT nom, email, bio, competence
            FROM "Data_Aggregation_formateur"
        """)
        formateurs = cursor.fetchall()

    return render(request, 'upload_form.html', {
        'form': form,
        'formateurs': formateurs,
        'formateurs_existants': formateurs_existants
    })
