//------------------------------------------------------------------------------------------
// FICHIER : personnages.js
// Description : Gère les interactions utilisateurs de la page Personnages
//------------------------------------------------------------------------------------------

// Fonction d'échappement pour éviter les attaques XSS
function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, function (tag) {
        const chars = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return chars[tag] || tag;
    });
}

//--------------------------------------------- FERMETURE DES MENUS DÉROULANTS -----------------------------------------------
document.addEventListener('click', function(event) {
    const isClickInsideMenu = event.target.closest('.dropdown') || event.target.closest('.menu-toggle');
    if (!isClickInsideMenu) {
        const checkboxes = document.querySelectorAll('.menu-toggle');
        checkboxes.forEach(checkbox => {
            checkbox.checked = false; // Ferme les menus si clic en dehors
        });
    }
});

//------------------------------------------------------------ OUVERTURE FENÊTRE COMMENTAIRE ------------------------------------
document.addEventListener("DOMContentLoaded", function () {
    let boutonsOuvrir = document.querySelectorAll(".ouvrir-fenetre-commentaire");

    boutonsOuvrir.forEach(bouton => {
        bouton.addEventListener("click", function (event) {
            event.preventDefault();
            let authorId = bouton.getAttribute("data-id");
            let fenetre = document.getElementById("fenetre-commentaire-" + authorId);
            if (!fenetre) return;

            fenetre.classList.add("fenetre-active"); // Affiche la fenêtre modale

            let commentContainer = fenetre.querySelector(".commentaires-liste");
            if (!commentContainer) return;

            // Récupération des commentaires depuis le serveur (AJAX)
            fetch(`/envoyer_commentaires_audio/${authorId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.error) return;

                    commentContainer.innerHTML = ""; // Nettoie l'affichage

                    // Ajout des commentaires un par un
                    data.commentaires.forEach(commentaire => {
                        let commentHTML = `
                            <div class="commentaire-item" data-id="${commentaire.id_comment}">
                                <span class="commentaire-text">${escapeHTML(commentaire.comment)}</span>
                                <span class="commentaire-date">${escapeHTML(commentaire.date_comment)}</span>
                                <span class="commentaire-user">${escapeHTML(commentaire.id_user)}</span>
                                <img class="delete-comment" src="/static/photo/croix.png" alt="Supprimer" title="Supprimer">
                            </div>`;
                        commentContainer.innerHTML += commentHTML;
                    });

                    ajouterEcouteurSuppression(commentContainer); // Ajoute la suppression
                })
                .catch(error => console.error("Erreur AJAX :", error));
        });
    });

    // Fonction pour supprimer un commentaire
    function ajouterEcouteurSuppression(commentContainer) {
        commentContainer.addEventListener('click', function (event) {
            if (event.target && event.target.classList.contains('delete-comment')) {
                let commentElement = event.target.closest('.commentaire-item');
                let commentId = commentElement.getAttribute('data-id');
                let userId = currentUserId;  // Variable définie dans le template HTML

                fetch(`/supprimer_commentaire/${commentId}/${userId}`, {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id_user: userId })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.message.includes("✅")) {
                        commentElement.remove();
                    } else {
                        alert("Erreur : " + data.message);
                    }
                })
                .catch(error => console.error("Erreur suppression:", error));
            }
        });
    }

    // Fermeture de la modale via le bouton "fermer"
    document.querySelectorAll(".fermer").forEach(btn => {
        btn.addEventListener("click", function () {
            let fenetre = btn.closest(".fenetre-modale");
            fenetre.classList.remove("fenetre-active");
        });
    });

    // Fermeture de la modale via clic à l'extérieur
    window.addEventListener("click", function (event) {
        document.querySelectorAll(".fenetre-modale").forEach(fenetre => {
            if (event.target === fenetre) {
                fenetre.classList.remove("fenetre-active");
            }
        });
    });
});

//-------------------------------------------- SUPPRESSION D'AUTEUR ---------------------------------------------------
document.addEventListener("DOMContentLoaded", function () {
    let boutonsSupprimer = document.querySelectorAll(".supprimer-auteur");

    boutonsSupprimer.forEach(bouton => {
        bouton.addEventListener("click", function (event) {
            event.preventDefault();
            let authorId = parseInt(bouton.getAttribute("data-id"), 10);

            if (confirm("Voulez-vous vraiment supprimer cet auteur ?")) {
                fetch(`/supprimer_auteur/${authorId}`, {
                    method: "DELETE",
                    headers: { "Content-Type": "application/json" }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.message.includes("✅")) {
                        window.location.href = "/Personnage";
                    } else {
                        alert("Erreur : " + data.error);
                    }
                })
                .catch(error => console.error("Erreur suppression auteur:", error));
            }
        });
    });
});
