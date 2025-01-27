from flask import Flask
from flask import render_template, request
import os
import psycopg2
import datetime #module permettant de récupérer la date et heure actuelle
import itertools 


### PROJET POO2 INTERFACE GRAPHIQUE DE LA BDD FILM ###



BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.abspath(os.path.join(BASE_DIR,"templates"))
print(TEMPLATE_DIR)

myapp = Flask(__name__, template_folder = TEMPLATE_DIR	) #créer l'application



##1##
#méthode qui affiche une page de connexion permettant d'entrer son nom, prénom, le nom de la base, l'idf seluser et le mdp sel2022
@myapp.route("/login")
def login():
    return render_template("login.html") #utilise un template (html/css/js) du site colorlib : https://colorlib.com/wp/template/login-form-20/  , j'ai réutiliser ce template pour certaines pages comme artiste, film par titre...
    
    
##2## 
##méthode qui récupère les idf saisi dans la page login et traite en renvoyant une page   
@myapp.route("/traitement", methods=["POST"])
def traitement():
    #récupère ce qui a été saisi dans la page login.html
    donnees=request.form
    genre=donnees.get("genre")
    nom=donnees.get("nom")
    prenom=donnees.get("prenom")
    
    
    global nom_bdd,idf_bdd,mdp_bdd #on garde en mémoire les idf pour se co à la base pour faire les requetes après
    nom_bdd=donnees.get("nom_bdd")
    idf_bdd=donnees.get('idf_bdd')
    mdp_bdd=donnees.get('mdp_bdd')
   
    
    #vérifie si les idf sont bien saisie, si oui se connecte à la BDD film en affichant la page d'accueuil de la BDD avec msg personnalisé
    if (nom_bdd=="film" and idf_bdd=="seluser" and mdp_bdd=="sel2022"):
        return render_template("home_page.html", genre=genre, prenom=prenom, nom=nom)#renvoie vers la page de bienvenue à la BDD Film
        
    #sinon affiche un msg d'erreur de saisie   
    else:
        return "Identifiant ou/et mot de passe ou nom de la bdd saisis incorrects."
    
  
  
##F1##    
# quand on décide de rechercher un FILM
@myapp.route("/films")
def films():
    
    return render_template("films.html") #renvoit la page de recherche de Films (par titre/genre/année) 
    
    
    
##F2## 
  
@myapp.route("/recherche_films", methods=["POST"])
def recherche_films():
    #récupère ce qui a été coché par l'utilisateur dans la page films.html
    selection=request.form
    recherche_films=selection.get("rech_films")
    
    #si on décide d'effectuer une recherche par Titre
    if (recherche_films=="titre"):
        return render_template("titre_filtre.html")
    #si on décide d'effectuer une recherche par genre
    elif (recherche_films=="genre"):
        return render_template("recherche_films_par_genre.html")
    #si on décide d'effectuer une recherche par année   
    else:
        return render_template("recherche_films_par_annee.html")
    
##FT1## on rechercche un film par titre
#affichage différents de la barre de recherche selon le bouton séléctionné
@myapp.route("/traitement_recherche_films_par_titre", methods=["POST"])
def traitement_recherche_films_par_titre():
    #récupère ce qui a été sélectionné par l'utilisateur
    selection=request.form
    recherche_films_titre=selection.get("rech_films_titre")
    
    #selon si on va saisir un titre entier/ titre partiel... ça va nous afficher une barre de recherche différente dans une nelle page
    if(recherche_films_titre=="titre_exacte"):
        return render_template("recherche_films_titre_exacte.html")
        
    elif(recherche_films_titre=="titre_commence_par"):
        return render_template("recherche_films_titre_commence_par.html")
    
    else:
        return render_template("recherche_films_titre_contient.html")



##FT2## on rechercche un film par titre en saisissant le titre exacte
#recherche tout les films avec le "titre" saisi
@myapp.route("/results_films_par_titre/<num_choix>", methods=["POST"])
def results_films_par_titre(num_choix): #num_choix correspond à si c'est un titre excate(num_choix=1)/début de titre(num_choix=2)/qq mots(num_choix=3)

    #connexion à la base avec les identifiants saisies précedemment dans la page login et récupérable par les variables globales !!! revoir ça marche pas les var glob...
        connecteur = psycopg2.connect(host="82.65.199.132", database="film", user="seluser", password="sel2022", port=15432)
        
        
        #récupère ce qui a été saisi dans la barre de recherche de Titre
        global titre_saisi
        titre_saisi=request.form
        titre_saisi=titre_saisi.get("rech_titre")
        t1=titre_saisi
        t2=titre_saisi+"%"
        t3="%"+titre_saisi+"%"
        #print(type(titre_saisi))
        #print(titre_saisi)
        cursor = connecteur.cursor()
          
        if (num_choix == 1): #titre exacte saisi -- fais comme la 2eme req à revoir!!!
            cursor.execute("select idfilm, titre, annee, genre, codepays, resume from film where titre = 't1'", (t1 ,))
            
        elif (num_choix == 2): #début du titre saisi
            cursor.execute("select idfilm,titre,annee,genre, codepays, resume from film where titre like %s", (t2,))
        
        else: #qq mots du titre saisi
            cursor.execute("select idfilm,titre,annee,genre, codepays, resume from film where titre like %s", (t3,))
   
        
        #initialise une liste vide de chaque attribut de la table film
        id_film=[]
        titre=[]
        annee=[]
        genre=[]
        code_pays=[]
        resume=[]
        
        #récupère ligne par ligne
        ligne = cursor.fetchone()
        
        
        #rajoute chq date, id_film, titre pour chaque film 
        while (ligne!=None):
            
            id_film.append(str(ligne[0]))
            titre.append(ligne[1])
            annee.append(str(ligne[2]))
            genre.append(ligne[3])
            code_pays.append(ligne[4])
            resume.append(ligne[5])
            
            
            ligne = cursor.fetchone()
        cursor.close()
        connecteur.close()
        #print(id_film)
        #print(titre)
          
        #créer un fichier html qui va afficher les attributs de tt les films répondant à la requetes   
        with open ("templates/results_films.html","w") as fichierecriture:
        
            
            fichierecriture.write("<!DOCTYPE html>\n")
            fichierecriture.write("<html><head><meta charset='UTF-8'><title>Résultats de Films par titre</title>")
    
            #importation des librairies javascript de datables pour un affichage de chaque attribut d'un film en tableau interactif
            fichierecriture.write("<script type='text/javascript' src='https://code.jquery.com/jquery-3.5.1.js'></script><script type='text/javascript' src='https://cdn.datatables.net/1.12.0/js/jquery.dataTables.min.js'></script><script src='{{url_for('static',filename='js/k1.js')}}'></script> \n")
            #liaison au fichier k1.css correspondant au css du datables
            fichierecriture.write("<link rel='stylesheet' href='{{url_for('static',filename='css/k1.css')}}'></head><body> \n") 
           
            
            
            #affiche le nom des colonnes de la table Film "Titre","Annee"...
            fichierecriture.write("<table id='example' class='display'style='width:100%'><thead><tr><th>ID Film</th><th>Titre</th><th>Année</th><th>Genre</th><th>Code pays</th><th>Résumé</th></tr></thead>\n")
    
    
            #affiche le contenu des lignes de la table
            for i in range (len(id_film)):
          
                fichierecriture.write("<tr><td>"+id_film[i]+"</td><td>"+titre[i]+"</td><td>"+annee[i]+"</td><td>"+genre[i]+"</td><td>"+code_pays[i]+"</td><td>"+resume[i]+"</td></tr>\n")
                
                
        return render_template("results_films.html") # affiche la page  results_films.html créée précedemment
    
    
    
    
##FA## on recherche un film avec son année de sortie
#recherche tout les films avec l'annee saisie
@myapp.route("/results_films_par_annee", methods=["POST"])
def results_films_par_annee():

    #connexion à la base avec les identifiants saisies précedemment dans la page login et récupérable par les variables globales !!! revoir ça marche pas les var glob...
        connecteur = psycopg2.connect(host="82.65.199.132", database="film", user="seluser", password="sel2022", port=15432)
        
        
        #récupère ce qui a été saisi dans la barre de recherche de Annee
        global annee_saisie
        annee_saisie=request.form
        annee_saisie=annee_saisie.get("rech_annee")
        
    
        print(type(annee_saisie))
        cursor = connecteur.cursor()
        
        cursor.execute("select idfilm,titre,annee, genre, codepays, resume from film where annee= %s", (annee_saisie,))
        ligne=cursor.fetchone()
        
        #initialise une liste vide de chaque attribut de la table film
        id_film=[]
        titre=[]
        annee=[]
        genre=[]
        code_pays=[]
        resume=[]
        
        #récupère ligne par ligne
        ligne = cursor.fetchone()
        
        
        #rajoute chq date, id_film, titre pour chaque film 
        while (ligne!=None):
            
            id_film.append(str(ligne[0]))
            titre.append(ligne[1])
            annee.append(str(ligne[2]))
            genre.append(ligne[3])
            code_pays.append(ligne[4])
            resume.append(ligne[5])
            
            
            ligne = cursor.fetchone()
        cursor.close()
        connecteur.close()
        print(id_film)
        print(titre)
           
            
            
        #écriture d'un fichier html par le script python ici présent qui va nous permettre d'afficher les résultats des requetes sous forme d'une table "jolie" . La table se rempli en fonction de ce qui a été saisi par l'utilisatuer dans la barre de recherche   
        with open ("templates/results_films_par_annee.html","w") as fichierecriture:
        
            
            fichierecriture.write("<!DOCTYPE html>\n")
            fichierecriture.write("<html><head><meta charset='UTF-8'><title>Résultats de Films par Année</title>")
    
            #importation des librairies javascript de Datables (https://datatables.net/) pour un affiche plus "convivial"
            fichierecriture.write("<script type='text/javascript' src='https://code.jquery.com/jquery-3.5.1.js'></script><script type='text/javascript' src='https://cdn.datatables.net/1.12.0/js/jquery.dataTables.min.js'></script><script src='{{url_for('static',filename='js/k1.js')}}'></script> \n")
            #liaison au fichier k1.css
            fichierecriture.write("<link rel='stylesheet' href='{{url_for('static',filename='css/k1.css')}}'></head><body> \n") 
           
            #affiche le nom des colonnes de la table Film "Titre","Annee"...
            fichierecriture.write("<table id='example' class='display'style='width:100%'><thead><tr><th>ID Film</th><th>Titre</th><th>Année</th><th>Genre</th><th>Code pays</th><th>Résumé</th></tr></thead>\n")
    
    
            #affiche les attributs du résulats de la requete pour chaque colonne de la table( avc nb de col=nb d'id film répondant à la requete)
            for i in range (len(id_film)):
          
                fichierecriture.write("<tr><td>"+id_film[i]+"</td><td>"+titre[i]+"</td><td>"+annee[i]+"</td><td>"+genre[i]+"</td><td>"+code_pays[i]+"</td><td>"+resume[i]+"</td></tr>\n")
                
                
        return render_template("results_films_par_annee.html")
    


##FG## On recherche un film en choissant son genre au préalable

#recherche tout les films avec le genre saisi
@myapp.route("/results_films_par_genre", methods=["POST"])
def results_films_par_genre():

    #connexion à la base avec les identifiants saisies précedemment dans la page login et récupérable par les variables globales !!! revoir ça marche pas les var glob...
        connecteur = psycopg2.connect(host="82.65.199.132", database="film", user="seluser", password="sel2022", port=15432)
        
        
        #récupère ce qui a été saisi dans la barre de recherche de Titre
        global genre_saisi
        genre_saisi=request.form
        print("genre", genre_saisi)
        genre_saisi=genre_saisi.get("rech_genre")
        
       
        cursor = connecteur.cursor()
        
        cursor.execute("select idfilm,titre, annee, genre, codepays, resume from film where genre= %s", (genre_saisi,))
          
        
        #initialise une liste vide de chaque attribut de la table film
        id_film=[]
        titre=[]
        annee=[]
        genre=[]
        code_pays=[]
        resume=[]
        
        #récupère ligne par ligne
        ligne = cursor.fetchone()
        
        
        #rajoute chq date, id_film, titre pour chaque film 
        while (ligne!=None):
            
            id_film.append(str(ligne[0]))
            titre.append(str(ligne[1]))
            annee.append(str(ligne[2]))
            genre.append(str(ligne[3]))
            code_pays.append(str(ligne[4]))
            resume.append(str(ligne[5]))
            
            
            #resume.append(str(ligne[5]))
            
            
            ligne = cursor.fetchone()
        cursor.close()
        connecteur.close()
      
       
        #créer un fichier html  results_films_par_genre.html qui contient tout les films correspondant à la requête 
        with open ("templates/results_films_par_genre.html","w") as fichierecriture:
        
            
            fichierecriture.write("<!DOCTYPE html>\n")
            fichierecriture.write("<html><head><meta charset='UTF-8'><title>Résultats de Films par genre</title>")
    
            #importation des librairies javascript de datables
            fichierecriture.write("<script type='text/javascript' src='https://code.jquery.com/jquery-3.5.1.js'></script><script type='text/javascript' src='https://cdn.datatables.net/1.12.0/js/jquery.dataTables.min.js'></script><script src='{{url_for('static',filename='js/k1.js')}}'></script> \n")
            #liaison au fichier k1.css
            fichierecriture.write("<link rel='stylesheet' href='{{url_for('static',filename='css/k1.css')}}'></head><body> \n") 
           
            
            
            #affiche le nom des colonnes de la table Film "Titre","Annee"...
            fichierecriture.write("<table id='example' class='display'style='width:100%'><thead><tr><th>ID Film</th><th>Titre</th><th>Année</th><th>Genre</th><th>Code pays</th><th>Résumé</th></thead>\n")
    
    
            #affiche les lignes de la table
            for i in range (len(id_film)):
          
                fichierecriture.write("<tr><td>"+id_film[i]+"</td><td>"+titre[i]+"</td><td>"+annee[i]+"</td><td>"+genre[i]+"</td><td>"+code_pays[i]+"</td><td>"+resume[i]+"</td></tr>\n")
                
                
        return render_template("results_films_par_genre.html")
    
    
    
####

##A1## quand on décide de rechercher un ARTISTE   
@myapp.route("/artistes")
def artistes():
    
    return render_template("artistes.html") #renvoit la page de recherche d'artiste par Nom/role/film
    
    

##A2## quand on décide de rechercher un ARTISTE
  
@myapp.route("/recherche_artistes", methods=["POST"])
def recherche_artistes():
    #récupère ce qui a été sélectionné par l'utilisateur
    selection=request.form
    recherche_artistes=selection.get("rech_art")
    
    #si on décide d'effectuer une recherche d'Artiste en tappant son nom  ou un rôle qu'il a joué, un film dans lequel il a joué, à chaque choix séléctionné, ça nous renvoit vers une page pour tapper le nom/nom du film/role etc
    if (recherche_artistes=="nom"):
        return render_template("recherche_art_par_nom.html")
        
    elif (recherche_artistes=="role"):
        return render_template("recherche_art_par_role.html")
        
    else:
        return render_template("recherche_art_par_film.html")
       
  

#recherche de tout les films avec le nom saisi
@myapp.route("/results_art_par_nom", methods=["POST"])
def results_art_par_nom():

    #connexion à la base avec les identifiants saisies précedemment dans la page login et récupérable par les variables globales !!! revoir ça marche pas les var glob...
        connecteur = psycopg2.connect(host="82.65.199.132", database="film", user="seluser", password="sel2022", port=15432)
        
        
        #récupère ce qui a été saisi dans la barre de recherche de Titre
        global nom_saisi
        nom_saisi=request.form
        #print(nom_saisi)
        nom_saisi=nom_saisi.get("rech_nom")
        #print(nom_saisi)
        n=nom_saisi
        
       
        cursor = connecteur.cursor()
        cursor.execute("select idartiste,nom,prenom, anneenaiss, film.idfilm,titre,nomrole from artiste,film,role where nom =%s and artiste.idartiste=role.idacteur and role.idfilm=film.idfilm", (n,))
          
        
        #initialise une liste vide de chaque attribut de la table Artiste
        id_artiste=[]
        nom=[]
        prenom=[]
        anneenaiss=[]
        id_film=[]
        titre=[]
        nom_role=[]
        
        
        #récupère ligne par ligne
        ligne = cursor.fetchone()
        
        
        #rajoute chq date, id_film, titre pour chaque film 
        while (ligne!=None):
            
            id_artiste.append(str(ligne[0]))
            nom.append(str(ligne[1]))
            prenom.append(str(ligne[2]))
            anneenaiss.append(str(ligne[3]))
            id_film.append(str(ligne[4]))
            titre.append(str(ligne[5]))
            nom_role.append(str(ligne[6]))
            
            
            ligne = cursor.fetchone()
        cursor.close()
        connecteur.close()
      
        
            
        #créer un fichier html results_artistes_par_nom.html qui renvoit tout les caractéristiques de l'artistes et du film dans lesquel il a joué  
        with open ("templates/results_artistes_par_nom.html","w") as fichierecriture:
        
            
            fichierecriture.write("<!DOCTYPE html>\n")
            fichierecriture.write("<html><head><meta charset='UTF-8'><title>Résultats d'Artiste par nom</title>")
    
            #importation des librairies javascript de datables
            fichierecriture.write("<script type='text/javascript' src='https://code.jquery.com/jquery-3.5.1.js'></script><script type='text/javascript' src='https://cdn.datatables.net/1.12.0/js/jquery.dataTables.min.js'></script><script src='{{url_for('static',filename='js/k1.js')}}'></script> \n")
            #liaison au fichier k1.css
            fichierecriture.write("<link rel='stylesheet' href='{{url_for('static',filename='css/k1.css')}}'></head><body> \n") 
           
            
            
            #affiche le nom des colonnes de la table Film "Titre","Annee"...
            fichierecriture.write("<table id='example' class='display'style='width:100%'><thead><tr><th>ID Artiste</th><th>Nom</th><th>Prénom</th><th>Année de naissance</th><th>Id Film</th><th>Titre</th><th>Nom du rôle</th></thead>\n")
    
    
            #affiche les lignes de la table
            for i in range (len(id_artiste)):
          
                fichierecriture.write("<tr><td>"+id_artiste[i]+"</td><td>"+nom[i]+"</td><td>"+prenom[i]+"</td><td>"+anneenaiss[i]+"</td><td>"+id_film[i]+"</td><td>"+titre[i]+"</td><td>"+nom_role[i]+"</td></tr>\n")
                
                
        return render_template("results_artistes_par_nom.html")
    
    
    
    

#recherche tout les artistes avec le role saisi
@myapp.route("/results_art_par_role", methods=["POST"])
def results_art_par_role():

    #connexion à la base avec les identifiants saisies précedemment dans la page login et récupérable par les variables globales !!! revoir ça marche pas les var glob...
        connecteur = psycopg2.connect(host="82.65.199.132", database="film", user="seluser", password="sel2022", port=15432)
        
        
        #récupère ce qui a été saisi dans la barre de recherche de Titre
        global role_saisi
        role_saisi=request.form
        #print(role_saisi)
        role_saisi=role_saisi.get("rech_role")
        #print(role_saisi)
        r=role_saisi
        
        cursor = connecteur.cursor()
        
        cursor.execute("select idartiste,nom,prenom, anneenaiss, film.idfilm,titre,nomrole from artiste,film,role where nomrole=%s and artiste.idartiste=role.idacteur and role.idfilm=film.idfilm", (r,))
          
        
        #initialise une liste vide de chaque attribut de la table Artiste
        id_artiste=[]
        nom=[]
        prenom=[]
        anneenaiss=[]
        id_film=[]
        titre=[]
        nom_role=[]
        
        
        #récupère ligne par ligne
        ligne = cursor.fetchone()
        
        
        #rajoute chq date, id_film, titre pour chaque film 
        while (ligne!=None):
            
            id_artiste.append(str(ligne[0]))
            nom.append(str(ligne[1]))
            prenom.append(str(ligne[2]))
            anneenaiss.append(str(ligne[3]))
            id_film.append(str(ligne[4]))
            titre.append(str(ligne[5]))
            nom_role.append(str(ligne[6]))
            
            
            ligne = cursor.fetchone()
        cursor.close()
        connecteur.close()
      
         
        #créer un fichier html  results_artistes_par_role.html qui récupère tout les artistes et les films qu'il a joué avec le role qui a été saisi   
        with open ("templates/results_artistes_par_role.html","w") as fichierecriture:
        
            
            fichierecriture.write("<!DOCTYPE html>\n")
            fichierecriture.write("<html><head><meta charset='UTF-8'><title>Résultats d'Artiste par rôle</title>")
    
            #importation des librairies javascript de datables
            fichierecriture.write("<script type='text/javascript' src='https://code.jquery.com/jquery-3.5.1.js'></script><script type='text/javascript' src='https://cdn.datatables.net/1.12.0/js/jquery.dataTables.min.js'></script><script src='{{url_for('static',filename='js/k1.js')}}'></script> \n")
            #liaison au fichier k1.css
            fichierecriture.write("<link rel='stylesheet' href='{{url_for('static',filename='css/k1.css')}}'></head><body> \n") 
           
            
            
            #affiche le nom des colonnes de la table Film "Titre","Annee"...
            fichierecriture.write("<table id='example' class='display'style='width:100%'><thead><tr><th>ID Artiste</th><th>Nom</th><th>Prénom</th><th>Année de naissance</th><th>Id Film</th><th>Titre</th><th>Nom du rôle</th></thead>\n")
    
    
            #affiche les lignes de la table
            for i in range (len(id_artiste)):
          
                fichierecriture.write("<tr><td>"+id_artiste[i]+"</td><td>"+nom[i]+"</td><td>"+prenom[i]+"</td><td>"+anneenaiss[i]+"</td><td>"+id_film[i]+"</td><td>"+titre[i]+"</td><td>"+nom_role[i]+"</td></tr>\n")
                
                
        return render_template("results_artistes_par_role.html")
    
    
    

#recherche tout les artistes avec le film saisi dans lequel l'artiste a joué
@myapp.route("/results_art_par_film", methods=["POST"])
def results_art_par_film():

    #connexion à la base avec les identifiants saisies précedemment dans la page login et récupérable par les variables globales !!! revoir ça marche pas les var glob...
        connecteur = psycopg2.connect(host="82.65.199.132", database="film", user="seluser", password="sel2022", port=15432)
        
        
        #récupère ce qui a été saisi dans la barre de recherche de Titre
        global film_saisi
        film_saisi=request.form
        #print(film_saisi)
        film_saisi=film_saisi.get("rech_film")
        #print(film_saisi)
        f=film_saisi
        
        
       
        cursor = connecteur.cursor()
        
        cursor.execute("select idartiste,nom,prenom, anneenaiss, film.idfilm,titre,nomrole from artiste,film,role where titre=%s and artiste.idartiste=role.idacteur and role.idfilm=film.idfilm", (f,))
          
        
        #initialise une liste vide de chaque attribut de la table Artiste
        id_artiste=[]
        nom=[]
        prenom=[]
        anneenaiss=[]
        id_film=[]
        titre=[]
        nom_role=[]
        
        
        #récupère ligne par ligne
        ligne = cursor.fetchone()
        
        
        #rajoute chq date, id_film, titre pour chaque film 
        while (ligne!=None):
            
            id_artiste.append(str(ligne[0]))
            nom.append(str(ligne[1]))
            prenom.append(str(ligne[2]))
            anneenaiss.append(str(ligne[3]))
            id_film.append(str(ligne[4]))
            titre.append(str(ligne[5]))
            nom_role.append(str(ligne[6]))
            
            
            ligne = cursor.fetchone()
        cursor.close()
        connecteur.close()
      
        
        #créer un fichier html results_artistes_par_film.html qui récupère tout les artites qui ont joués dans le film saisi par exp Mary Jane, Peter parker dans Spider-man   
        with open ("templates/results_artistes_par_film.html","w") as fichierecriture:
        
            
            fichierecriture.write("<!DOCTYPE html>\n")
            fichierecriture.write("<html><head><meta charset='UTF-8'><title>Résultats d'Artiste par Film</title>")
    
            #importation des librairies javascript de datables
            fichierecriture.write("<script type='text/javascript' src='https://code.jquery.com/jquery-3.5.1.js'></script><script type='text/javascript' src='https://cdn.datatables.net/1.12.0/js/jquery.dataTables.min.js'></script><script src='{{url_for('static',filename='js/k1.js')}}'></script> \n")
            #liaison au fichier k1.css
            fichierecriture.write("<link rel='stylesheet' href='{{url_for('static',filename='css/k1.css')}}'></head><body> \n") 
           
            
            
            #affiche le nom des colonnes de la table Film "Titre","Annee"...
            fichierecriture.write("<table id='example' class='display'style='width:100%'><thead><tr><th>ID Artiste</th><th>Nom</th><th>Prénom</th><th>Année de naissance</th><th>Id Film</th><th>Titre</th><th>Nom du rôle</th></thead>\n")
    
    
            #affiche les lignes de la table
            for i in range (len(id_artiste)):
          
                fichierecriture.write("<tr><td>"+id_artiste[i]+"</td><td>"+nom[i]+"</td><td>"+prenom[i]+"</td><td>"+anneenaiss[i]+"</td><td>"+id_film[i]+"</td><td>"+titre[i]+"</td><td>"+nom_role[i]+"</td></tr>\n")
                
                
        return render_template("results_artistes_par_film.html")
    
    
  
# quand on décide de rechercher un FILM
@myapp.route("/recherche_avancee")
def recherche_avancee():
    
    return render_template("rech_av_film.html") #renvoit la page de recherche de Films (par genre/année/pays) 
    
# quand on décide de rechercher un FILM
@myapp.route("/results_rech_av", methods=["POST"])
def results_rech_av():
        connecteur = psycopg2.connect(host="82.65.199.132", database="film", user="seluser", password="sel2022", port=15432)
        print("kakaka1")
        
        #récupère ce qui a été saisi dans la page de la recherche avancée
        global genre_saisi
        genre_saisi=request.form
        print(genre_saisi)
        genre_saisi=genre_saisi.get("genre")
        
        #récupère ce qui a été saisi dans la barre de recherche de Annee
        global annee_saisie
        annee_saisie=request.form
        annee_saisie=annee_saisie.get("annee")
        
       
        global code_saisi
        code_saisi=request.form
        print(code_saisi)
        code_saisi=code_saisi.get("code_pays")
       
       
        print(type(annee_saisie),type(genre_saisi), type(code_saisi))
        cursor = connecteur.cursor()
        
        #requete sql qui va retourner tt les id_film, titre, genre, code pays et resume de film qui ont l'année, le code pays et le genre sélectionné par l'user
        
        
        
        #cursor.execute("select idfilm,titre,annee, genre, codepays, resume from film where genre= %s AND codepays= %s AND annee= %s", (genre_saisi,code_saisi,annee_saisie,))
        
        #ca marche pas, je sais pas comment mettre plusieurs paramètres... 
        cursor.executemany("select idfilm,titre,annee, genre, codepays, resume from film where genre= %s and codepays= %s and annee= %s",  (genre_saisi,code_saisi,annee_saisie))
        
        ligne=cursor.fetchone()
        
        #initialise une liste vide de chaque attribut 
        id_film=[]
        titre=[]
        annee=[]
        genre=[]
        code_pays=[]
        resume=[]
        
        
        
        #récupère ligne par ligne
        ligne = cursor.fetchone()
        
        
        #rajoute chq date, id_film, titre pour chaque film 
        while (ligne!=None):
            
            id_film.append(str(ligne[0]))
            titre.append(str(ligne[1]))
            annee.append(str(ligne[2]))
            genre.append(str(ligne[3]))
            code_pays.append(str(ligne[4]))
            resume.append(str(ligne[5]))
            
            
            
            ligne = cursor.fetchone()
        cursor.close()
        connecteur.close()
       
        #créer un fichier results_rech_av.html contenant les films qui ont les caractéristiques qu'on a saisi    
        with open ("templates/results_rech_av.html","w") as fichierecriture:
        
            
            fichierecriture.write("<!DOCTYPE html>\n")
            fichierecriture.write("<html><head><meta charset='UTF-8'><title>Résultats de la recherche avancée</title>")
    
            #importation des librairies javascript de datables
            fichierecriture.write("<script type='text/javascript' src='https://code.jquery.com/jquery-3.5.1.js'></script><script type='text/javascript' src='https://cdn.datatables.net/1.12.0/js/jquery.dataTables.min.js'></script><script src='{{url_for('static',filename='js/k1.js')}}'></script> \n")
            #liaison du fichier k1.css
            fichierecriture.write("<link rel='stylesheet' href='{{url_for('static',filename='css/k1.css')}}'></head><body> \n") 
           
            
            
            #affiche le nom des colonnes de la table Film "Titre","Annee"...
            fichierecriture.write("<table id='example' class='display'style='width:100%'><thead><tr><th>ID Film</th><th>Titre</th><th>Année</th><th>Genre</th><th>Code pays</th><th>Résumé</th></thead>\n")
    
    
            #affiche les lignes de la table
            for i in range (len(id_film)):
          
                fichierecriture.write("<tr><td>"+id_film[i]+"</td><td>"+titre[i]+"</td><td>"+annee[i]+"</td><td>"+genre[i]+"</td><td>"+code_pays[i]+"</td><td>"+resume[i]+"</td></tr>\n")
                
        return render_template("results_rech_av.html") #renvoit la page de de résultats de la recherche avancée 
    
       
  


#lance l'application quand on execute le script avec le terminal	
if __name__ == "__main__":
    myapp.run(port=3000,debug=True)
	
	
	
	
	
	
