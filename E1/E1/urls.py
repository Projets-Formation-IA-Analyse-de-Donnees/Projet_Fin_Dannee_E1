"""
URL configuration for E1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Authentification import views as authviews
from Data_Aggregation import views as dataviews

urlpatterns = [
    path('admin/', admin.site.urls),
    path('connexion/', authviews.connexion , name='connexion'),
    path('', authviews.connexion , name='connexion'),
    path('inscription/', authviews.inscription , name='inscription'),
    path('deconnexion/', authviews.deconnexion , name='deconnexion'),
    path('accueil/', authviews.accueil , name='accueil'),
    path('import-formateurs/', dataviews.import_formateurs_csv, name='import_formateurs'),
    path('inscriptions/', dataviews.importer_etudiants_source, name='importer_etudiants_source'),
    path('commentaires/', dataviews.commentaires_crud, name='commentaires'),
    path('stats/', dataviews.stats_vue, name='stats_vue'),
]
