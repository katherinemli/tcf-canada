package com.katherine.tcforal;

/**
 * Les sujets d'expression orale, DANS le téléphone.
 *
 * Généré depuis tcf_simulateur/sujets_oraux.json (source : sujets officiels TCF Canada (expression orale) — copiés littéralement, sans reformulation).
 * Le téléphone n'a plus besoin de l'ordinateur pour tirer une question : il a
 * tout ici. La tâche 2 et la tâche 3 se tirent séparément, 30 et 30
 * énoncés, soit 900 combinaisons possibles.
 *
 * Pour régénérer après avoir ajouté des sujets :
 *   python3 ~/tcf_simulateur/generer_sujets_java.py
 */
final class Sujets {

    private Sujets() {}

    static final String[] TACHE2 = {
        // ⚠️ UN SEUL sujet est publié ici (dépôt public) : les sujets
        // appartiennent aux sites d'où ils viennent. Le fichier complet
        // (30 + 30 = 900 combinaisons) est régénéré en local par
        // dashboard/generer_sujets_java.py à partir de sujets_oraux.json.
        "Je suis un(e) ami(e) français(e) et je reviens d’un séjour sportif. Vous trouvez cette expérience intéressante et vous aimeriez faire la même chose. Vous me posez des questions sur ce séjour (lieu, activités, tarifs, etc.).",
    };

    static final String[] TACHE3 = {
        // ⚠️ UN SEUL sujet est publié ici (dépôt public) : les sujets
        // appartiennent aux sites d'où ils viennent. Le fichier complet
        // (30 + 30 = 900 combinaisons) est régénéré en local par
        // dashboard/generer_sujets_java.py à partir de sujets_oraux.json.
        "Selon vous, quelle influence la télévision a-t-elle sur l’éducation des enfants ?",
    };

    static int combinaisons() { return TACHE2.length * TACHE3.length; }
}
