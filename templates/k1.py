import psycopg2


#ouvre la connexion
connecteur=psycopg2.connect(host="82.65.199.132", database="film", user="seluser", password="sel2022",port=15432)

#ouvre un curseur pour envoyer les commandes sql
cursor=connecteur.cursor()






#execute une requete SQL
req1="Select idfilm,titre,annee,genre, codepays, resume from film"

cursor.execute(req1)

# récupère ligne par ligne
ligne=cursor.fetchone()

id_film=[]
titre=[]
annee=[]
genre=[]
code_pays=[]
resume=[]

while (ligne!=None):
    #print(ligne[0], ligne[1])
    id_film.append(str(ligne[0]))
    titre.append(ligne[1])
    annee.append(str(ligne[2]))
    genre.append(ligne[3])
    code_pays.append(ligne[4])
    resume.append(ligne[5])
    
    ligne=cursor.fetchone()
    
##tests###    
print(id_film[0])
print(titre[0])
print(annee[0])    
print(genre[0])
print(code_pays[0])
print(resume[0])


#écriture du fichier html
with open ("k1.html","w") as fichierecriture:

    fichierecriture.write("<!DOCTYPE html>\n")
    fichierecriture.write("<html><head><meta charset='UTF-8'><title>Page Title</title>")
    
    #importation des librairies javascript de datables
    fichierecriture.write("<script type='text/javascript' src='https://code.jquery.com/jquery-3.5.1.js'></script><script type='text/javascript' src='https://cdn.datatables.net/1.12.0/js/jquery.dataTables.min.js'></script><script type='text/javascript' src='k1.js'></script> \n")
    
    fichierecriture.write("<link rel='stylesheet' href='k1.css'></head><body>") 
            
    #affiche le nom des colonnes de la table Film "Titre","Annee"...
    fichierecriture.write("<table id='example' class='display'style='width:100%'><thead><tr><th>ID Film</th><th>Titre</th><th>Année</th><th>Genre</th><th>Code pays</th><th>Résumé</th></tr></thead>\n")
    
    
    #affiche les lignes de la table
    for i in range (len(id_film)):
      
    
                 
            fichierecriture.write("<tr><td>"+id_film[i]+"</td><td>"+titre[i]+"</td><td>"+annee[i]+"</td><td>"+genre[i]+"</td><td>"+code_pays[i]+"</td><td>"+resume[i]+"</td></tr>\n")
        
    
    
    



#ferme la connexion
cursor.close()
connecteur.close()
