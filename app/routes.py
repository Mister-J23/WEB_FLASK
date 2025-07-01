from flask import Flask, render_template, abort, redirect, url_for, request, session, flash, jsonify
from sqlalchemy import text
from app import app, db
from app.requete import login_required, login_required_Admin, media, user, insert, acquis, supp
from datetime import datetime
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv
PEPPER = os.getenv('PEPPER')





# ===================== AUTHENTIFICATION & SESSION ======================

# Route de connexion (authentification)
@app.route('/login', methods=['POST'])
def login():
    # Récupération des données saisies dans le formulaire HTML
    username = request.form.get('username')
    password = request.form.get('password')

    # Vérification des identifiants via une fonction externe (fichier requete.py)
    lien = user.se_connecter(username, password)

    # Si les identifiants sont corrects, rediriger vers la page d'accueil
    if lien :
        return redirect(url_for('Home'))

    # Sinon, réafficher le formulaire avec un message d'erreur
    return render_template('connexion.html', message="Identifiants incorrects")

# Permet d’injecter automatiquement certaines variables (id, username, groupe)
# dans tous les templates HTML, sans avoir à les passer manuellement dans chaque render_template()
@app.context_processor
def inject_user():
    return dict(
        id=session.get('id'), 
        username=session.get('username'), 
        groupe=session.get('groupe')
    )

# Page de connexion (page d'accueil par défaut)
@app.route('/')
def Connexion():
    return render_template('connexion.html')

# Route de déconnexion
@app.route('/Déconnexion')
def déconnexion():
    # Supprimer toutes les variables de session (id, username, etc.)
    session.clear()
    print(session)
    # Rediriger vers la page de connexion
    return redirect(url_for('Connexion'))


# ====================== PAGES PROTÉGÉES PAR LOGIN ======================

# Page d’accueil après connexion (protégée par le décorateur @login_required)
@app.route('/Home')
@login_required
def Home():
    return render_template('Home.html')

# Page affichant la liste des personnages (autrement dit les auteurs)
@app.route('/Personnage')
@login_required
def personnages():
    # Appel à une fonction du module media pour récupérer les auteurs
    all_items = media.obtenir_personnages()

    # Si des éléments ont été récupérés, les passer au template HTML
    if all_items:
        return render_template('Personnages.html', items=all_items)
    else:
        return "Erreur lors de la récupération des auteurs"


    

@app.route('/Oeuvres')
@login_required
def Oeuvres():
    # Récupérer tout le contenu de la table des auteurs
    all_items = media.obtenir_personnages()
    if all_items:
        return render_template('Oeuvres.html', items=all_items)
    else:
        return "Erreur lors de la récupération des auteurs"
    



@app.route('/Chargement') # Charger des éléments dans la base
@login_required_Admin
def Page_chargement():
    courant = acquis.select_courant()  # Fonction qui récupère la liste des courants en BDD
    return render_template('charger.html', courants=courant)


@app.route('/Utilisateur')
@login_required_Admin
def Utilisateur():
    test= acquis.select_utilisateurs()
    if test:
        test1= acquis.select_groupe()
        if test1:
            return render_template('Utilisateurs.html',utilisateurs=test, groupes=test1)
        return render_template('home.html')
    else:
        return render_template('home.html')


    


@app.route('/Erreur/<int:nb>')
def Erreur(nb):
    if nb==0:
        mes= ""
    if nb==1:
        mes= "Problème de connexion"
    if nb==2:
        mes= "Nom d'utilisateur ou Mot de passe non valide"
    if nb==3:
        mes= "Page réservé aux administrateurs"
    if nb==4:
        mes= "Le POST n'a pas marché"
    if nb==5:
        mes= "Le POST a marché mais pas la requête"
    return mes




@app.route('/bio/<int:id>')
@login_required
def get_bio(id):
    test = media.obtenir_lien_bio(id)
    
    if "error" in test:
        return jsonify({"error": "Biographie introuvable"}), 404  # Retourne un JSON en cas d'erreur
    print("✅ Biographie ouverte")
    lien = test['link_text']  # Le lien du fichier PDF
    return jsonify({"link": lien})  # Envoie le lien en JSON




# Get Audio
@app.route('/audio/<int:id>')
@login_required
def get_audio(id):
    test = media.obtenir_lien_audio(id)
    if test:
        lien = test['speech_link']  # Le lien du fichier audio
 

        # Rediriger vers l'URL du fichier audio (par exemple, le lien de téléchargement)
        return redirect(lien)
        
    return "Audio introuvable", 404


#Get photo extrait-audio
@app.route('/photo/<int:id>')
@login_required
def get_photo(id):
    lien = media.obtenir_lien_photo(id)
    if lien:
        return redirect(lien)  # Redirection vers le lien du fichier audio
    return "Photo introuvable", 404
        

#Get photo Oeuvres
@app.route('/photoOeuvres/<int:id>')
@login_required
def get_photoOeuvres(id):
    lien = media.obtenir_lien_photoOeuvre(id)
    if lien:
        return redirect(lien)  # Redirection vers le lien du fichier audio
    return "Photo introuvable", 404
    

@app.route('/delete/<int:id>', methods=['POST']) #Supprimer des éléments de la base
def delete_item(id):
    # Supprimer l'élément de la base de données
    db.session.execute(text("DELETE FROM authors WHERE id_author = :id"), {'id': id})
    db.session.commit()
    flash('Élément supprimé avec succès.', 'success')
    return redirect(url_for('personnages'))





#Envoyer commentaires à la page
@app.route('/envoyer_commentaires_bio/<int:id>')
def envoyer_commentaires_bio(id):
    # Récupération de l'id_bio depuis la table des biographies
    test = media.obtenir_lien_bio(id)
    
    # Vérifie si l'erreur est présente dans la réponse
    if "error" in test:
        return jsonify(test), 404  # Envoie l'erreur au client avec le code HTTP 404
    
    
    idbio = test['id_bio']  # 

    # Récupération des commentaires associés
    commentaires = acquis.select_commentaire_bio(idbio)

    if isinstance(commentaires, str):  # Vérifie si une erreur SQL est retournée
        return jsonify({"error": commentaires}), 500  

    if not commentaires:
        return jsonify({"commentaires": []})  # Retourne une liste vide si aucun commentaire trouvé

    # Récupérer les noms d'utilisateur pour chaque id_user
    utilisateurs = {c["id_user"]: acquis.select_nomutilisateurs(c["id_user"]) for c in commentaires}

    # Ajoute les noms d'utilisateur dans la réponse JSON
    commentaires_json = [
        {
            "id_comment": c["id_comment"],
            "comment": c["comment"],
            "date_comment": c["date_comment"],
            "id_user": utilisateurs.get(c["id_user"], "Inconnu")  # Ajoute "Inconnu" si le nom d'utilisateur n'est pas trouvé
        }
        for c in commentaires
    ]

    print("👍 Affichage réussi")

    return jsonify({"commentaires": commentaires_json})

@app.route('/envoyer_commentaires_audio/<int:id>')
def envoyer_commentaires_audio(id):
    # Récupération de l'id_bio depuis la table des biographies
    test = media.obtenir_lien_audio(id)
    
    # Vérifie si l'erreur est présente dans la réponse
    if "error" in test:
        return jsonify(test), 404  # Envoie l'erreur au client avec le code HTTP 404
    
    
    idaudio = test['id_audio']  # 

    # Récupération des commentaires associés
    commentaires = acquis.select_commentaire_audio(idaudio)

    if isinstance(commentaires, str):  # Vérifie si une erreur SQL est retournée
        return jsonify({"error": commentaires}), 500  

    if not commentaires:
        return jsonify({"commentaires": []})  # Retourne une liste vide si aucun commentaire trouvé

    # Récupérer les noms d'utilisateur pour chaque id_user
    utilisateurs = {c["id_user"]: acquis.select_nomutilisateurs(c["id_user"]) for c in commentaires}

    # Ajoute les noms d'utilisateur dans la réponse JSON
    commentaires_json = [
        {
            "id_comment": c["id_comment"],
            "comment": c["comment"],
            "date_comment": c["date_comment"],
            "id_user": utilisateurs.get(c["id_user"], "Inconnu")  # Ajoute "Inconnu" si le nom d'utilisateur n'est pas trouvé
        }
        for c in commentaires
    ]

    print("👍 Affichage réussi")

    return jsonify({"commentaires": commentaires_json})

#--------------------------------------------------------------------ECRITURE DANS LA TABLE ------------------------------------------------------------


# Chargement
@app.route('/charge', methods=['POST','GET'])
@login_required_Admin
def charge():
    print("La méthode charge() a été appelée")
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom = request.form['nom']
        naissance = request.form['naissance']
        mort = request.form['mort']
        courant_philo = request.form['courant']

        # Récupérer les fichiers uploadés
        photo = '/static/photo/' + request.form['photo'] + '.jpg'
        photoOeuvre = '/static/photo/' + request.form['photo'] + '.png'
        audio = '/static/audio/' + request.form['audio'] + '.mp3'
        fichier = '/static/fichier/' + request.form['fichier'] + '.pdf'

        # Récupérer l'heure actuelle
        tempo = datetime.now()

        # Insérer l'auteur et récupérer l'ID retourné
        id_auteur = insert.inserer_auteur(nom, naissance, mort, photo, courant_philo)

        # Vérifier si l'insertion de l'auteur a réussi
        if isinstance(id_auteur, int):  # Vérifie que l'ID retourné est bien un entier
            insertaudio = insert.inserer_audio(audio, tempo, id_auteur) #insérer l'audio
            if insertaudio and insertaudio > 0: 
                insertbio = insert.inserer_bio(fichier,photoOeuvre, tempo, id_auteur) #insérer la biographie
                if insertbio and insertbio > 0: 
                    db.session.commit()  # Valider l'insertion dans la base
                    courant = acquis.select_courant()  # Fonction qui récupère la liste des courants en BDD
                    
                    return render_template('charger.html',courants=courant, message=f"Auteur {nom}, ID: {id_auteur} ajouté avec succès :-) ")
                else:
                    db.session.rollback()  # Annuler la transaction en cas d'erreur
                    courant = acquis.select_courant()  # Fonction qui récupère la liste des courants en BDD
                    return render_template('charger.html',courants=courant, message="Erreur lors de l'ajout du fichier pdf")

            else:
                db.session.rollback()  # Annuler la transaction en cas d'erreur
                courant = acquis.select_courant()  # Fonction qui récupère la liste des courants en BDD
                return render_template('charger.html',courants=courant, message="Erreur lors de l'ajout de l'audio")
            
        else:
            db.session.rollback()  # Annuler la transaction en cas d'erreur
            courant = acquis.select_courant()  # Fonction qui récupère la liste des courants en BDD
            return render_template('charger.html',courants=courant, message="Erreur lors de l'ajout de l'auteur")
    

#Chargement du courant
@app.route('/charger_courant', methods=['POST','GET'])
@login_required_Admin
def charger_courant():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom_courant = request.form['nom_courant']
        lien_courant = '/static/courants/' +  request.form['lien_courant']+'.pdf'
        test = insert.inserer_courant(nom_courant, lien_courant)
        

        if test and test > 0:
            db.session.commit()  # Valider l'insertion dans la base
            courant = acquis.select_courant()  # Fonction qui récupère la liste des courants en BDD

            return render_template('charger.html',courants=courant, message=f"{nom_courant} ajouté avec succès :-) ")
        else:
            db.session.rollback()  # Valider l'insertion dans la base
            courant = acquis.select_courant()  # Fonction qui récupère la liste des courants en BDD
            return render_template('charger.html',courants=courant, message="Erreur lors de l'ajout du courant")
        



#Chargement du commentaire audio
@app.route('/charger_commentaire_audio/<int:id>', methods=['POST','GET'])
@login_required
def charger_commentaire_audio(id):
    if request.method == 'POST':
        # Récupérer les données du formulaire
        comm = request.form['commentaire']
        
        # Récupérer l'heure actuelle
        tempo = datetime.now()

        #récupérer l'ID User
        iduser= session.get('id')

        #Récupérer l'ID audio pour l'id_auteur correspondant
        test1 = media.obtenir_lien_audio(id) 
        print(f"ID AUTEUR:{id}")
        
        if test1:

            idaudio= test1['id_audio']

            #Insérer le commentaire
            test = insert.inserer_commentaire_audio(tempo, comm, iduser, idaudio)


            

            if test and test > 0:
                db.session.commit()  # Valider l'insertion dans la base
                print("commentaire ajouté avec succes 👍")
                return redirect(url_for('personnages'))
            else:
                db.session.rollback()  # Valider l'insertion dans la base
                return redirect(url_for('personnages'))
        else:
            print("§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§ERREUR§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§")
            return redirect(url_for('personnages'))
        




@app.route('/charger_commentaire_bio/<int:id>', methods=['POST'])
@login_required
def charger_commentaire_bio(id):
    comm = request.form.get('commentaire', '').strip()
    if not comm:
        return jsonify({'error': 'Le commentaire est vide !'}), 400

    tempo = datetime.now()  # Heure actuelle
    iduser = session.get('id')  # ID de l'utilisateur connecté

    if not iduser:
        return jsonify({'error': 'Utilisateur non authentifié'}), 403

    test1 = media.obtenir_lien_bio(id)
    if not test1:
        return jsonify({'error': 'Auteur introuvable'}), 404

    idbio = test1['id_bio']

    # Insérer le commentaire
    test = insert.inserer_commentaire_bio(tempo, comm, iduser, idbio)

    if test != "✅ Commentaire inséré avec succès":
        db.session.rollback()
        return jsonify({'error': 'Échec de l’ajout du commentaire'}), 500
    
    db.session.commit()

    # Une fois le commentaire inséré, on récupère tous les commentaires associés à cet auteur
    commentaires = acquis.select_commentaire_bio(idbio)

    # Récupérer les noms d'utilisateur pour chaque id_user
    utilisateurs = {c["id_user"]: acquis.select_nomutilisateurs(c["id_user"]) for c in commentaires}

    # Ajoute les noms d'utilisateur dans la réponse JSON
    commentaires_json = [
        {
            "id_comment": c["id_comment"],
            "comment": c["comment"],
            "date_comment": c["date_comment"],
            "id_user": utilisateurs.get(c["id_user"], "Inconnu")  # Ajoute "Inconnu" si le nom d'utilisateur n'est pas trouvé
        }
        for c in commentaires
    ]

    return jsonify({
        'success': 'Commentaire inséré avec succès',
        'commentaires': commentaires_json
    })







#Chargement du courant
@app.route('/charger_utilisateur', methods=['POST','GET'])
@login_required_Admin
def charger_utilisateur():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom = request.form['nom']
        motpasse = request.form['motpasse'] + PEPPER
        groupe = request.form['groupe']

        motpassehache = generate_password_hash(motpasse)

        #écriture dans la table utilisateur
        test = insert.inserer_utilisateur(nom, motpassehache, groupe)
        

        if test and test > 0:
            db.session.commit()  # Valider l'insertion dans la base
            return redirect(url_for('Utilisateur', message="Utilisateur ajouté avec succès 👍")) #Relancer la page Utilisateur
        else:
            db.session.rollback()  # Valider l'insertion dans la base
            return redirect(url_for('Utilisateur', message="Erreur lors de l'ajout de l'utilisateur ❌")) #Relancer la page Utilisateur

       
    
#--------------------------------------------------------------------------------------SUPPRESSIONS------------------------------------------------
#SUPPRIMER COMMENTAIRE
@app.route('/supprimer_commentaire/<int:id_comment>/<int:id_user>', methods=['DELETE'])
@login_required
def supprimer_commentaire(id_comment, id_user):

    message = supp.supprimer_commentaire(id_comment, id_user)
    return jsonify({"message": message})

#SUPPRIMER UTILISATEUR
@app.route('/supprimer_utilisateur/<int:id_user>', methods=['DELETE'])
@login_required
def supprimer_utilisateur(id_user):

    message = supp.supprimer_utilisateur(id_user)
    return jsonify({"message": message})

#SUPPRIMER AUTEUR
@app.route('/supprimer_auteur/<int:id_auteur>', methods=['DELETE'])
@login_required_Admin
def supprimer_auteur(id_auteur):
    print("Fetch lancé 👍")

    message = supp.supprimer_auteur(id_auteur)
    return jsonify({"message": message})




@app.route('/Contact') # decorators
def Contact():
    return render_template('Contact.html')

# Désactiver le cache pour toutes les pages si l'utilisateur est connecté
@app.after_request
def add_header(response):
    if 'username' in session:
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

