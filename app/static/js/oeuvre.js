// Fonction d'échappement contre les attaques XSS
function escapeHTML(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

document.addEventListener('click', function(event) {
    const isClickInsideMenu = event.target.closest('.dropdown') || event.target.closest('.menu-toggle');
    if (!isClickInsideMenu) {
        const checkboxes = document.querySelectorAll('.menu-toggle');
        checkboxes.forEach(checkbox => {
            checkbox.checked = false;
        });
    }
});

document.addEventListener("DOMContentLoaded", function () {
    let boutonsOuvrir = document.querySelectorAll(".ouvrir-fenetre-commentaire");

    boutonsOuvrir.forEach(bouton => {
        bouton.addEventListener("click", function (event) {
            event.preventDefault();
            
            let authorId = bouton.getAttribute("data-id");
            let fenetre = document.getElementById("fenetre-commentaire-" + authorId);

            if (!fenetre) return;

            fenetre.classList.add("fenetre-active");

            let commentContainer = fenetre.querySelector(".commentaires-liste");
            if (!commentContainer) return;

            fetch(`/envoyer_commentaires_bio/${authorId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.error) return;

                    commentContainer.innerHTML = "";

                    data.commentaires.forEach(commentaire => {
                        let commentHTML = `
                            <div class="commentaire-item" data-id="${escapeHTML(commentaire.id_comment)}">
                                <span class="commentaire-text">${escapeHTML(commentaire.comment)}</span>
                                <span class="commentaire-date">${escapeHTML(commentaire.date_comment)}</span>
                                <span class="commentaire-user">${escapeHTML(commentaire.id_user)}</span>
                                <img class="delete-comment" src="/static/photo/croix.png" alt="Supprimer" title="Supprimer">
                            </div>`;
                        commentContainer.innerHTML += commentHTML;
                    });

                    ajouterEcouteurSuppression(commentContainer);

                    const boutonEnvoyer = fenetre.querySelector("#envoyer-commentaire");
                    if (boutonEnvoyer) {
                        boutonEnvoyer.addEventListener("click", function(event) {
                            event.preventDefault();
                            const formulaire = fenetre.querySelector("#formulaire-commentaire");
                            const formData = new FormData(formulaire);
                            const authorId = formulaire.getAttribute("action").split("/").pop();

                            fetch(`/charger_commentaire_bio/${authorId}`, {
                                method: "POST",
                                body: formData
                            })
                            .then(response => response.json())
                            .then(data => {
                                if (data.error) return;

                                commentContainer.innerHTML = "";
                                data.commentaires.forEach(commentaire => {
                                    let commentHTML = `
                                        <div class="commentaire-item" data-id="${escapeHTML(commentaire.id_comment)}">
                                            <span class="commentaire-text">${escapeHTML(commentaire.comment)}</span>
                                            <span class="commentaire-date">${escapeHTML(commentaire.date_comment)}</span>
                                            <span class="commentaire-user">${escapeHTML(commentaire.id_user)}</span>
                                            <img class="delete-comment" src="/static/photo/croix.png" alt="Supprimer" title="Supprimer">
                                        </div>`;
                                    commentContainer.innerHTML += commentHTML;
                                });

                                formulaire.reset();
                            });
                        });
                    }
                });
        });
    });

    function ajouterEcouteurSuppression(commentContainer) {
        commentContainer.addEventListener('click', function (event) {
            if (event.target && event.target.classList.contains('delete-comment')) {
                let commentElement = event.target.closest('.commentaire-item');
                let commentId = commentElement.getAttribute('data-id');
                let requestBody = JSON.stringify({ id_user: currentUserId });

                fetch(`/supprimer_commentaire/${commentId}/${currentUserId}`, {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' },
                    body: requestBody
                })
                .then(response => response.json())
                .then(data => {
                    if (data.message.includes("✅")) {
                        commentElement.remove();
                    } else {
                        alert("Erreur : " + data.message);
                    }
                });
            }
        });
    }

    document.querySelectorAll(".fermer").forEach(boutonFermer => {
        boutonFermer.addEventListener("click", function () {
            let fenetre = boutonFermer.closest(".fenetre-modale");
            fenetre.classList.remove("fenetre-active");
        });
    });

    window.addEventListener("click", function (event) {
        document.querySelectorAll(".fenetre-modale").forEach(fenetre => {
            if (event.target === fenetre) {
                fenetre.classList.remove("fenetre-active");
            }
        });
    });

    // Gestion du clic sur les images des auteurs pour télécharger une biographie
    document.querySelectorAll(".livre").forEach(image => {
        image.addEventListener("click", function (event) {
            event.preventDefault();
            let authorId = this.getAttribute("data-id");

            fetch(`/bio/${authorId}`)
                .then(response => response.json())
                .then(data => {
                    if (!data.error) {
                        const lien = document.createElement("a");
                        lien.href = data.link;
                        lien.download = "biographie.pdf";
                        document.body.appendChild(lien);
                        lien.click();
                        document.body.removeChild(lien);
                    } else {
                        afficherMessageErreur(data.error);
                    }
                });
        });
    });

    function afficherMessageErreur(message) {
        let modal = document.createElement("div");
        modal.classList.add("modal-overlay");
        modal.innerHTML = `
            <div class="modal-erreur">
                <p class="black">${escapeHTML(message)}</p>
            </div>
        `;
        modal.addEventListener("click", function (event) {
            if (event.target === modal) {
                modal.remove();
            }
        });
        document.body.appendChild(modal);
    }
});
