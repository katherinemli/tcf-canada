// ============================================================
// QUESTIONS DU SIMULATEUR — vraies combinaisons du site
// Chaque "combinaison" = un examen complet de 3 tâches.
// Pour ajouter : copier un bloc { ... } et changer les textes.
// (Voir le TEMPLATE tout en bas.)
//
// ⚠️ Numéros : ce sont NOS numéros, pas ceux du site. Le site
// renumérote ses combinaisons de 1 à 5 selon la page ; ici chaque
// examen garde un numéro fixe pour que tes réponses archivées
// (mes_reponses/combinaison-N_date.md) restent liées au bon sujet.
// Les combinaisons 8 à 11 viennent des captures du 29/07/2026
// (la « Combinaison 2 » du site y était un doublon de notre n° 1).
// ============================================================

// Descriptions standard réutilisées pour chaque type de tâche.
const D_MESSAGE =
  "Il s'agit de rédiger un message, un courriel ou une annonce adressé à un ou plusieurs destinataires dans le but d'inviter, décrire, raconter, informer ou exprimer une demande.";
const D_NARRATION =
  "Il s'agit de rédiger un article de blog, un courriel, un commentaire, etc., destiné à plusieurs destinataires, dans le but de raconter et décrire une expérience vécue dans le passé.";
const D_ARGUMENTATION =
  "Il s'agit de rédiger un article argumentatif qui compare deux points de vue opposés sur un sujet donné.";

window.QUESTIONS = [
  // ⚠️ UN SEUL exemple est publié ici. La banque complète (11 combinaisons)
  // reste en local : ce sont des sujets appartenant à des sites tiers.
  // Copie ce fichier en questions.js et ajoute les tiens.
  {
    id: "combinaison-1",
    titre: "Combinaison 1",
    sousTitre: "3 tâches",
    dureeMinutes: 60,
    taches: [
      {
        type: "Message court",
        description: D_MESSAGE,
        motsMin: 60,
        motsMax: 120,
        sujet:
          "Votre ami(e) va fêter son anniversaire. Écrivez un message à vos amis pour lui acheter un cadeau commun.",
      },
      {
        type: "Narration / Blog",
        description: D_NARRATION,
        motsMin: 120,
        motsMax: 150,
        sujet:
          "La direction d'une école de musique cherche un endroit où organiser une fête pour 100 personnes. Écrivez un courriel pour les informer que vous avez trouvé un local (lieu, tarifs, service, etc…).",
      },
      {
        type: "Argumentation",
        description: D_ARGUMENTATION,
        motsMin: 120,
        motsMax: 180,
        sujet: "La sévérité des enfants",
        documents: [
          "Je vais bientôt avoir 22 ans et j'habite chez mes parents. Malgré ma majorité, mes parents restent autoritaires avec moi. Lorsque j'étais mineure et que je sortais avec des amies, je n'avais pas le droit de dormir dehors ni même de dépasser 21 h. Aujourd'hui, peu de choses ont changé. Certes, j'ai le droit de veiller plus tard, mais ma mère ne cesse de m'appeler sur mon téléphone portable jusqu'à ce que je sois de retour chez nous.",
          "Les parents ont parfois peur d'être trop sévères avec leurs enfants. Ils craignent qu'à cause d'un excès d'autorité, leurs enfants ne s'épanouissent pas et manquent de personnalité plus tard. Même si, par amour, les parents acceptent tout ce que leurs enfants demandent, cela pourrait avoir des effets négatifs lorsqu'ils passent à l'âge adulte. En effet, pour vivre en communauté, il est nécessaire de respecter certaines règles.",
        ],
      },
    ],
  },
];

// ============================================================
// TEMPLATE — pour ajouter une combinaison, copie ceci DANS le [ ]
// au-dessus (avant le ] final) et remplace les textes :
//
//   {
//     id: "combinaison-8",
//     titre: "Combinaison 8",
//     sousTitre: "3 tâches",
//     dureeMinutes: 60,
//     taches: [
//       { type: "Message court",   description: D_MESSAGE,       motsMin: 60,  motsMax: 120, sujet: "…" },
//       { type: "Narration / Blog", description: D_NARRATION,     motsMin: 120, motsMax: 150, sujet: "…" },
//       { type: "Argumentation",   description: D_ARGUMENTATION, motsMin: 120, motsMax: 180,
//         sujet: "Le titre du sujet",
//         documents: ["Point de vue 1 …", "Point de vue 2 …"] },
//     ],
//   },
// ============================================================
