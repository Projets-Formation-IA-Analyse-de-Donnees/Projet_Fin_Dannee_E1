from django.db import models

class Formateur(models.Model):
    nom = models.CharField(max_length=100)
    email = models.EmailField()
    bio = models.TextField()
    competence = models.CharField(max_length=100)

    def __str__(self):
        return self.nom


class Cours(models.Model):
    nom = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.nom

class Etudiant(models.Model):
    nom = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.nom

class Inscription(models.Model):
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE)
    note = models.FloatField()

    class Meta:
        unique_together = ('etudiant', 'cours')

