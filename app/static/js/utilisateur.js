

//-------------------------------------------------------SUPRIMER L'UTILISATEUR--------------------------------
document.addEventListener("DOMContentLoaded", function () {
    // Sélectionne tous les boutons de suppression
    const boutonsSupprimer = document.querySelectorAll(".bouton-supprimer");

    boutonsSupprimer.forEach(bouton => {
        bouton.addEventListener("click", function () {
            // Récupère l'ID de l'utilisateur depuis l'attribut data-id
            let userId = this.getAttribute("data-id");
            authorId = parseInt(userId, 10);  // Force l'ID à être un entier

            console.log(`Suppression lancée pour l'utilisateur ID : ${userId}`);
            

            // Vérifie avant suppression
            if (confirm("Voulez-vous vraiment supprimer cet utilisateur ?")) {
                fetch(`/supprimer_utilisateur/${userId}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.message.includes("✅")) {
                        // Supprime la ligne du tableau dans le DOM
                        this.closest("tr").remove();
                    } else {
                        alert("Erreur : " + data.message);
                    }
                })
                .catch(error => console.error("Erreur lors de la suppression :", error));
            } else {
                console.log("Confirm annulé !");
            }
        });
    });
});


//-------------------------------------AJOUT UTILISATEUR------------------------
document.addEventListener("DOMContentLoaded", function () {
    // Sélectionner les éléments
    const ajouterBtn = document.getElementById("ajouter-btn");
    const fenetreAjouterUtilisateur = document.getElementById("fenetre-ajouter-utilisateur");

    // Vérifier si les éléments existent
    if (!ajouterBtn || !fenetreAjouterUtilisateur) {
        console.error("Les éléments n'ont pas été trouvés.");
        return;
    }

    // Ajouter un écouteur pour afficher la fenêtre modale
    ajouterBtn.addEventListener("click", function (event) {
        event.preventDefault();
        fenetreAjouterUtilisateur.classList.add("fenetre-activeUtilisateur");
    });

    // Ajouter un écouteur pour fermer la fenêtre si on clique en dehors
    window.addEventListener("click", function (event) {
        // Vérifie si le clic se produit en dehors de la fenêtre modale
        if (!fenetreAjouterUtilisateur.contains(event.target) && event.target !== ajouterBtn) {
            fenetreAjouterUtilisateur.classList.remove("fenetre-activeUtilisateur");
        }
    });
});


