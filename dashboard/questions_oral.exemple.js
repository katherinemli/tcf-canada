// ============================================================
// QUESTIONS DU SIMULATEUR — EXPRESSION ORALE (TCF Canada)
// Chaque "combinaison" = un examen oral complet de 3 tâches.
//
// L'épreuve réelle dure ~12 minutes en tout :
//   Tâche 1 — Présentation personnelle · 2 min      · AUCUNE préparation
//   Tâche 2 — Interaction orale        · 3 min 30 s · 2 min de préparation
//   Tâche 3 — Argumentation (point de vue) · 4 min 30 s · AUCUNE préparation
//
// Les durées sont en SECONDES (prep = préparation, duree = temps de parole).
// Pour ajouter : copier un bloc { ... } et changer les textes.
// (Voir le TEMPLATE tout en bas.)
// ============================================================

// Descriptions standard réutilisées pour chaque type de tâche.
const O_PRESENTATION =
  "L'examinateur vous invite à parler de vous. Présentez-vous de manière structurée pendant 2 minutes, sans temps de préparation.";
const O_INTERACTION =
  "C'est VOUS qui posez les questions. Vous devez obtenir des informations auprès de l'examinateur, qui joue un rôle. Posez au moins 5 ou 6 questions variées.";
const O_ARGUMENTATION =
  "Vous donnez votre point de vue et vous le défendez. Structurez : introduction, 2 ou 3 arguments avec des exemples, puis conclusion.";

// Points à aborder pour la Tâche 1 — identiques à chaque examen,
// c'est la même consigne au TCF (seul ton texte change).
const POINTS_PRESENTATION = [
  { titre: "Identité", detail: "Nom, âge, ville, nationalité" },
  { titre: "Formation", detail: "Études, travail, expérience" },
  { titre: "Loisirs", detail: "Passions, hobbies, week-ends" },
  { titre: "Projets", detail: "Objectifs, immigration, TCF" },
];

// Petite boîte à outils affichée seulement si tu cliques « 💡 Aide ».
// Elle n'existe pas à l'examen réel : à n'utiliser que les premières fois.
const AIDE_PRESENTATION = [
  "Bonjour, je m'appelle… J'ai … ans et je suis originaire de…",
  "Actuellement, je vis à … depuis … ans.",
  "En ce qui concerne mes études, j'ai obtenu un diplôme en…",
  "Sur le plan professionnel, je travaille comme… / j'ai travaillé pendant … ans.",
  "Pendant mon temps libre, j'aime … et je m'intéresse beaucoup à…",
  "Mon projet, c'est de… C'est pour cette raison que je passe le TCF.",
];
const AIDE_INTERACTION = [
  "Bonjour ! Excusez-moi de vous déranger, j'aurais besoin d'un renseignement.",
  "Est-ce que vous pourriez me dire… ? / Pourriez-vous m'expliquer… ?",
  "J'aimerais savoir combien ça coûte. / Quel est le tarif exactement ?",
  "Est-ce qu'il y a une réduction pour les étudiants ?",
  "Ça se passe où, exactement ? / C'est loin du centre-ville ?",
  "Et au niveau des horaires, comment ça marche ?",
  "Qu'est-ce que vous me conseillez ?",
  "Très bien, merci beaucoup pour toutes ces informations !",
];
const AIDE_ARGUMENTATION = [
  "Introduction : « C'est une question intéressante. À mon avis, … »",
  "1er argument : « Tout d'abord, … Par exemple, dans mon pays, … »",
  "2e argument : « De plus, … C'est le cas de … »",
  "Nuance : « Cependant, il ne faut pas oublier que… »",
  "Exemple perso : « Personnellement, j'ai remarqué que… »",
  "Conclusion : « Pour conclure, je pense donc que… »",
];

window.QUESTIONS_ORAL = [
  // ⚠️ UN SEUL exemple est publié ici. La banque complète reste en local.
  // Copie ce fichier en questions_oral.js et ajoute les tiens.
  {
    id: "oral-1",
    titre: "Oral — Combinaison 1",
    sousTitre: "3 tâches",
    taches: [
      {
        type: "Présentation personnelle",
        description: O_PRESENTATION,
        prep: 0,
        duree: 120,
        sujet: "Bonjour, présentez-vous. Parlez-moi de vous pendant deux minutes.",
        points: POINTS_PRESENTATION,
        aide: AIDE_PRESENTATION,
      },
      {
        type: "Interaction orale",
        description: O_INTERACTION,
        prep: 120,
        duree: 210,
        sujet:
          "Je suis un(e) ami(e) français(e) et je reviens d’un séjour sportif. Vous trouvez cette expérience intéressante et vous aimeriez faire la même chose. Vous me posez des questions sur ce séjour (lieu, activités, tarifs, etc.).",
        aide: AIDE_INTERACTION,
      },
      {
        type: "Argumentation",
        description: O_ARGUMENTATION,
        prep: 0,
        duree: 270,
        sujet:
          "Selon vous, quelle influence la télévision a-t-elle sur l’éducation des enfants ?",
        aide: AIDE_ARGUMENTATION,
      },
    ],
  },
];

// ============================================================
// TEMPLATE — pour ajouter une combinaison, copie ceci DANS le [ ]
// au-dessus (avant le ] final) et remplace les deux sujets :
//
//   {
//     id: "oral-6",
//     titre: "Oral — Combinaison 6",
//     sousTitre: "3 tâches",
//     taches: [
//       { type: "Présentation personnelle", description: O_PRESENTATION,
//         prep: 0, duree: 120,
//         sujet: "Bonjour, présentez-vous. Parlez-moi de vous pendant deux minutes.",
//         points: POINTS_PRESENTATION, aide: AIDE_PRESENTATION },
//       { type: "Interaction orale", description: O_INTERACTION,
//         prep: 120, duree: 210, sujet: "…", aide: AIDE_INTERACTION },
//       { type: "Argumentation", description: O_ARGUMENTATION,
//         prep: 0, duree: 270, sujet: "…", aide: AIDE_ARGUMENTATION },
//     ],
//   },
// ============================================================
