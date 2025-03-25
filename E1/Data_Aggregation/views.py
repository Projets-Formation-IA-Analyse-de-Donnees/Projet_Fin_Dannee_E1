from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .form import CSVUploadForm
from django.db import connection
import csv, io
import psycopg2
import os
import requests
from Data_Aggregation.models import Etudiant, Cours, Inscription,CommentaireCours,StatCours
from pymongo import MongoClient
from datetime import datetime

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


@login_required
def importer_etudiants_source(request):
    log_ajoutes = []
    log_doublons = []

    # --- SUPPRESSION ---
    if request.method == 'POST' and 'supprimer' in request.POST:
        etudiant_id = request.POST['etudiant_id']
        cours_id = request.POST['cours_id']
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM "Data_Aggregation_inscription"
                WHERE etudiant_id = %s AND cours_id = %s
            """, [etudiant_id, cours_id])
        messages.success(request, "Inscription supprimée.")
        return redirect('importer_etudiants_source')

    # --- MODIFICATION ---
    elif request.method == 'POST' and 'modifier' in request.POST:
        etudiant_id = request.POST['etudiant_id']
        cours_id = request.POST['cours_id']
        nouvelle_note = request.POST['note']
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE "Data_Aggregation_inscription"
                SET note = %s
                WHERE etudiant_id = %s AND cours_id = %s
            """, [nouvelle_note, etudiant_id, cours_id])
        messages.success(request, "Note modifiée avec succès.")
        return redirect('importer_etudiants_source')

    # --- IMPORTATION depuis db_source ---
    elif request.method == 'POST' and 'importer' in request.POST:
        try:
            conn = psycopg2.connect(
                dbname=os.getenv("SOURCE_DB_NAME", "sourcedb"),
                user=os.getenv("SOURCE_DB_USER", "source_user"),
                password=os.getenv("SOURCE_DB_PASSWORD", "source_pass"),
                host=os.getenv("SOURCE_DB_HOST", "db_source"),
                port=os.getenv("SOURCE_DB_PORT", "5432")
            )
            cursor = conn.cursor()
            cursor.execute("SELECT nom_complet, email, cours_suivi, note FROM etudiants_source")
            rows = cursor.fetchall()

            for nom_complet, email, cours_nom, note in rows:
                cours, _ = Cours.objects.get_or_create(nom=cours_nom)
                etudiant, _ = Etudiant.objects.get_or_create(email=email, defaults={'nom': nom_complet})

                if not Inscription.objects.filter(etudiant=etudiant, cours=cours).exists():
                    Inscription.objects.create(etudiant=etudiant, cours=cours, note=note)
                    log_ajoutes.append((etudiant.nom, etudiant.email, cours.nom, note))
                else:
                    log_doublons.append((etudiant.nom, etudiant.email, cours.nom))  # ✅ correct ici

            cursor.close()
            conn.close()

            if log_ajoutes:
                messages.success(request, f"{len(log_ajoutes)} inscription(s) ajoutée(s).")
            if log_doublons:
                messages.warning(request, f"{len(log_doublons)} doublon(s) détecté(s).")

        except Exception as e:
            messages.error(request, f"Erreur de connexion à la base source : {str(e)}")

        return redirect('importer_etudiants_source')

    # --- SELECT pour affichage ---
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT e.id, e.nom, e.email, c.id, c.nom, i.note
            FROM "Data_Aggregation_inscription" i
            JOIN "Data_Aggregation_etudiant" e ON i.etudiant_id = e.id
            JOIN "Data_Aggregation_cours" c ON i.cours_id = c.id
        """)
        inscriptions = cursor.fetchall()

    return render(request, 'import_etudiants_source.html', {
        'log_ajoutes': log_ajoutes,
        'log_doublons': log_doublons,
        'inscriptions': inscriptions,
    })




@login_required
def commentaires_crud(request):
    # --- IMPORT depuis MongoDB ---
    if request.method == 'POST' and 'importer' in request.POST:
        logs_ajoutes = []
        logs_doublons = []
        try:
            client = MongoClient(
                host=os.getenv("MONGO_HOST", "mongo"),
                port=int(os.getenv("MONGO_PORT", "27017"))
            )
            db = client["edulink_mongo"]
            collection = db["commentaires"]
            commentaires = collection.find()

            for doc in commentaires:
                email = doc.get("etudiant_email")
                cours_nom = doc.get("cours_nom")
                commentaire = doc.get("commentaire")
                note_pedagogie = doc.get("note_pedagogie")
                date = doc.get("date")

                etudiant = Etudiant.objects.filter(email=email).first()
                cours = Cours.objects.filter(nom=cours_nom).first()

                if etudiant and cours:
                    existe = CommentaireCours.objects.filter(etudiant=etudiant, cours=cours, date=date).exists()
                    if not existe:
                        CommentaireCours.objects.create(
                            etudiant=etudiant,
                            cours=cours,
                            commentaire=commentaire,
                            note_pedagogie=note_pedagogie,
                            date=date
                        )
                        logs_ajoutes.append((etudiant.nom, cours.nom))
                    else:
                        logs_doublons.append((etudiant.nom, email, cours.nom))
                else:
                    logs_doublons.append((email, email, cours_nom))

            if logs_ajoutes:
                messages.success(request, f"{len(logs_ajoutes)} commentaire(s) importé(s).")
            if logs_doublons:
                messages.warning(request, f"{len(logs_doublons)} doublon(s) ou erreurs détecté(s).")

        except Exception as e:
            messages.error(request, f"Erreur MongoDB : {str(e)}")

        return redirect('commentaires')

    # --- MODIFICATION d’un commentaire ---
    elif request.method == 'POST' and 'modifier' in request.POST:
        commentaire_id = request.POST.get('commentaire_id')
        nouveau_commentaire = request.POST.get('commentaire')
        nouvelle_note = request.POST.get('note_pedagogie')
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE "Data_Aggregation_commentairecours"
                SET commentaire = %s, note_pedagogie = %s
                WHERE id = %s
            """, [nouveau_commentaire, nouvelle_note, commentaire_id])
        messages.success(request, "Commentaire modifié.")
        return redirect('commentaires')

    # --- SUPPRESSION d’un commentaire ---
    elif request.method == 'POST' and 'supprimer' in request.POST:
        commentaire_id = request.POST.get('commentaire_id')
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM "Data_Aggregation_commentairecours"
                WHERE id = %s
            """, [commentaire_id])
        messages.success(request, "Commentaire supprimé.")
        return redirect('commentaires')

    # --- AFFICHAGE des commentaires ---
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT c.id, e.nom, e.email, co.nom, c.commentaire, c.note_pedagogie, c.date
            FROM "Data_Aggregation_commentairecours" c
            JOIN "Data_Aggregation_etudiant" e ON c.etudiant_id = e.id
            JOIN "Data_Aggregation_cours" co ON c.cours_id = co.id
            ORDER BY c.date DESC
        """)
        commentaires = cursor.fetchall()

    return render(request, 'commentaires.html', {
        'commentaires': commentaires
    })








@login_required
def stats_vue(request):
    if request.method == 'POST':
        # Suppression
        if 'supprimer' in request.POST:
            stat_id = request.POST.get('stat_id')
            StatCours.objects.filter(id=stat_id).delete()
            messages.success(request, "Statistique supprimée avec succès.")
            return redirect('stats_vue')

        # Modification
        elif 'modifier' in request.POST:
            stat_id = request.POST.get('stat_id')
            try:
                stat = StatCours.objects.get(id=stat_id)
                stat.satisfaction = float(request.POST.get('satisfaction'))
                stat.nb_participants = int(request.POST.get('nb_participants'))
                stat.save()
                messages.success(request, "Statistique modifiée avec succès.")
            except StatCours.DoesNotExist:
                messages.error(request, "Statistique introuvable.")
            return redirect('stats_vue')

        # Importation API Flask avec remplacement par cours_nom
        elif 'importer' in request.POST:
            try:
                response = requests.get('http://api:5001/api/stats')
                response.raise_for_status()
                data = response.json()

                for item in data:
                    cours_nom = item['cours_nom']
                    satisfaction = item['satisfaction']
                    nb_participants = item['nb_participants']
                    date_val = datetime.strptime(item['date'], "%Y-%m-%d").date()

                    # Supprimer les anciennes données pour ce cours
                    StatCours.objects.filter(cours_nom=cours_nom).delete()

                    # Ajouter la nouvelle ligne
                    StatCours.objects.create(
                        cours_nom=cours_nom,
                        satisfaction=satisfaction,
                        nb_participants=nb_participants,
                        date=date_val
                    )

                messages.success(request, "Les données ont été importées et remplacées avec succès.")

            except Exception as e:
                messages.error(request, f"Erreur lors de l'importation depuis l'API Flask : {e}")

            return redirect('stats_vue')

    stats = StatCours.objects.all().order_by('-date')
    return render(request, 'stats.html', {'stats': stats})
