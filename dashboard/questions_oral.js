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
  // ⚠️ Bloc fabriqué par generer_sujets_java.py depuis
  //    sujets_oraux.json — ne pas le corriger à la main :
  //    corrige le JSON, puis relance le script.
  // ---------------------------------------------------------
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

  // ---------------------------------------------------------
  {
    id: "oral-2",
    titre: "Oral — Combinaison 2",
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
          "Je travaille à l’accueil d’une billetterie de spectacles. Vous êtes en vacances au Canada et vous souhaitez assister à un spectacle. Vous me posez des questions pour faire votre choix (types de spectacles, horaires, prix, etc.).",
        aide: AIDE_INTERACTION,
      },
      {
        type: "Argumentation",
        description: O_ARGUMENTATION,
        prep: 0,
        duree: 270,
        sujet:
          "Pourquoi certaines personnes choisissent-elles d’avoir un animal domestique chez elles ?",
        aide: AIDE_ARGUMENTATION,
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "oral-3",
    titre: "Oral — Combinaison 3",
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
          "Je suis un(e) ami(e) et vous souhaitez vous installer dans ma ville. Vous cherchez un quartier agréable pour y vivre. Vous me posez des questions afin de choisir celui qui vous convient le mieux (environnement, prix, services, etc.).",
        aide: AIDE_INTERACTION,
      },
      {
        type: "Argumentation",
        description: O_ARGUMENTATION,
        prep: 0,
        duree: 270,
        sujet:
          "Aujourd’hui, beaucoup de personnes cherchent à rester jeunes le plus longtemps possible. Que pensez-vous de cette tendance ?",
        aide: AIDE_ARGUMENTATION,
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "oral-4",
    titre: "Oral — Combinaison 4",
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
          "Je travaille à l’accueil dans une école de langue. Vous souhaitez suivre une formation en français et vous me posez des questions pour choisir le stage le plus adapté (type de formation, durée, tarifs, etc.).",
        aide: AIDE_INTERACTION,
      },
      {
        type: "Argumentation",
        description: O_ARGUMENTATION,
        prep: 0,
        duree: 270,
        sujet:
          "Comment évaluez-vous les mesures prises pour réduire la pollution dans votre ville ?",
        aide: AIDE_ARGUMENTATION,
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "oral-5",
    titre: "Oral — Combinaison 5",
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
          "Je suis un(e) ami(e) et je travaille dans une entreprise canadienne. Vous souhaitez travailler au Canada et vous me posez des questions sur mon expérience (formation, tâches, relations professionnelles, conditions de travail, etc.).",
        aide: AIDE_INTERACTION,
      },
      {
        type: "Argumentation",
        description: O_ARGUMENTATION,
        prep: 0,
        duree: 270,
        sujet:
          "Que pensez-vous de la qualité de l’alimentation dans votre pays ? Pouvez-vous expliquer votre réponse ?",
        aide: AIDE_ARGUMENTATION,
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "oral-6",
    titre: "Oral — Combinaison 6",
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
          "Je suis votre collègue. J’organise des séances de yoga pour les employé(e)s de l’entreprise. Vous êtes intéressé(e). Vous me posez des questions pour obtenir des informations (lieux, horaires, équipements, etc.).",
        aide: AIDE_INTERACTION,
      },
      {
        type: "Argumentation",
        description: O_ARGUMENTATION,
        prep: 0,
        duree: 270,
        sujet:
          "De nombreuses personnes deviennent végétariennes. Que pensez-vous de ce choix alimentaire ?",
        aide: AIDE_ARGUMENTATION,
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "oral-7",
    titre: "Oral — Combinaison 7",
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
          "Je suis votre voisin(e). Je prends des cours de photographie dans l’association du quartier. Vous êtes intéressé(e). Vous me posez des questions sur le cours (prix, horaires, matériel, etc.).",
        aide: AIDE_INTERACTION,
      },
      {
        type: "Argumentation",
        description: O_ARGUMENTATION,
        prep: 0,
        duree: 270,
        sujet:
          "Peut-on vraiment faire tous ses achats sur Internet ? Qu’en pensez-vous ?",
        aide: AIDE_ARGUMENTATION,
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "oral-8",
    titre: "Oral — Combinaison 8",
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
          "Je travaille à l’accueil du nouveau centre culturel de votre ville. Vous êtes intéressé(e). Vous me posez des questions sur les activités proposées par le centre (horaires, prix, etc.).",
        aide: AIDE_INTERACTION,
      },
      {
        type: "Argumentation",
        description: O_ARGUMENTATION,
        prep: 0,
        duree: 270,
        sujet:
          "Le salaire est-il l’élément le plus important dans un travail ? Êtes-vous d’accord ?",
        aide: AIDE_ARGUMENTATION,
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "oral-9",
    titre: "Oral — Combinaison 9",
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
          "Je travaille à l’office de tourisme de votre lieu de vacances. Vous me posez des questions sur les activités à faire dans la région (parcs, musées, restaurants, etc.).",
        aide: AIDE_INTERACTION,
      },
      {
        type: "Argumentation",
        description: O_ARGUMENTATION,
        prep: 0,
        duree: 270,
        sujet:
          "Les membres de la famille peuvent-ils être nos meilleurs amis ? Expliquez pourquoi.",
        aide: AIDE_ARGUMENTATION,
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "oral-10",
    titre: "Oral — Combinaison 10",
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
          "Vous êtes mon ami(e). Vous allez m’aider à déménager dans mon nouveau logement. Vous me posez des questions sur l’organisation de la journée (lieu, date, participants, etc.).",
        aide: AIDE_INTERACTION,
      },
      {
        type: "Argumentation",
        description: O_ARGUMENTATION,
        prep: 0,
        duree: 270,
        sujet:
          "Pour les personnes âgées, la vie en ville est-elle plus facile qu’à la campagne ? Êtes-vous d’accord ?",
        aide: AIDE_ARGUMENTATION,
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "oral-11",
    titre: "Oral — Combinaison 11",
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
          "Je suis une amie / un ami(e). Je pars pour le week-end et je vous demande de garder ma fille de 3 ans. Vous la connaissez un peu. Je vous indique les horaires et les choses à faire. Vous me posez des questions pour bien vous organiser (repas, jeux, sieste, etc.).",
        aide: AIDE_INTERACTION,
      },
      {
        type: "Argumentation",
        description: O_ARGUMENTATION,
        prep: 0,
        duree: 270,
        sujet:
          "La mission principale de l’école est d’enseigner les matières scolaires. Que pensez-vous de cette idée ? Pourquoi ?",
        aide: AIDE_ARGUMENTATION,
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "oral-12",
    titre: "Oral — Combinaison 12",
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
          "Je suis une collègue. Je vous propose d’aller voir un spectacle. Vous me posez des questions sur ce spectacle (genre, lieu, heure, etc.) et sur la sortie (transport, personnes présentes, etc.).",
        aide: AIDE_INTERACTION,
      },
      {
        type: "Argumentation",
        description: O_ARGUMENTATION,
        prep: 0,
        duree: 270,
        sujet:
          "La lecture est souvent liée à la culture. Faut-il lire pour être cultivé ? Qu’en pensez-vous ?",
        aide: AIDE_ARGUMENTATION,
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "oral-13",
    titre: "Oral — Combinaison 13",
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
          "Je travaille au service culturel de la mairie. Vous voulez en savoir plus sur les activités culturelles de la ville. Vous me posez des questions (expositions, musées, ateliers, prix, accès, etc.).",
        aide: AIDE_INTERACTION,
      },
      {
        type: "Argumentation",
        description: O_ARGUMENTATION,
        prep: 0,
        duree: 270,
        sujet:
          "Lorsqu’une personne quitte son pays pour vivre ailleurs, c’est souvent une décision imposée. Qu’en pensez-vous ?",
        aide: AIDE_ARGUMENTATION,
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "oral-14",
    titre: "Oral — Combinaison 14",
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
          "Je travaille dans une agence de voyage. Vous êtes client(e) et vous cherchez un séjour au Canada. Vous me posez des questions (endroits à visiter, prix, hébergements, activités, etc.).",
        aide: AIDE_INTERACTION,
      },
      {
        type: "Argumentation",
        description: O_ARGUMENTATION,
        prep: 0,
        duree: 270,
        sujet:
          "D’après vous, la liberté d’expression doit-elle avoir des limites ? Pourquoi ?",
        aide: AIDE_ARGUMENTATION,
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "oral-15",
    titre: "Oral — Combinaison 15",
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
          "Vous êtes en voiture au Canada et vous tombez en panne. Vous appelez votre assurance pour savoir comment elle peut vous aider (dépannage, réparations, retour, etc.). Je suis l’agent qui vous répond.",
        aide: AIDE_INTERACTION,
      },
      {
        type: "Argumentation",
        description: O_ARGUMENTATION,
        prep: 0,
        duree: 270,
        sujet:
          "Est-il possible, selon vous, de bien connaître un pays sans parler sa langue ? Pourquoi ?",
        aide: AIDE_ARGUMENTATION,
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "oral-16",
    titre: "Oral — Combinaison 16",
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
          "Je suis votre ami(e). J’ai commencé un nouvel emploi et vous voulez savoir comment s’est déroulée ma première journée : l’ambiance, les collègues, les tâches, etc.",
        aide: AIDE_INTERACTION,
      },
      {
        type: "Argumentation",
        description: O_ARGUMENTATION,
        prep: 0,
        duree: 270,
        sujet:
          "Avoir vécu dans un pays étranger constitue-t-il un atout pour réussir sa carrière professionnelle ?",
        aide: AIDE_ARGUMENTATION,
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "oral-17",
    titre: "Oral — Combinaison 17",
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
          "Je suis votre voisin(e). Je connais quelqu’un qui propose des cours de musique à domicile. Vous êtes intéressé(e) et vous me posez des questions sur cette personne : ses tarifs, sa disponibilité, son expérience, etc.",
        aide: AIDE_INTERACTION,
      },
      {
        type: "Argumentation",
        description: O_ARGUMENTATION,
        prep: 0,
        duree: 270,
        sujet:
          "Le tourisme représente-t-il une voie de développement intéressante pour tous les pays ? Pourquoi ?",
        aide: AIDE_ARGUMENTATION,
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "oral-18",
    titre: "Oral — Combinaison 18",
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
          "Je suis votre voisin(e). Vous souhaitez organiser une sortie à la campagne avec vos amis. Vous me demandez des conseils pour l’organisation : les activités, le transport, le lieu, etc.",
        aide: AIDE_INTERACTION,
      },
      {
        type: "Argumentation",
        description: O_ARGUMENTATION,
        prep: 0,
        duree: 270,
        sujet:
          "Selon vous, est-il difficile de s’installer à l’étranger ? Pourquoi ?",
        aide: AIDE_ARGUMENTATION,
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "oral-19",
    titre: "Oral — Combinaison 19",
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
          "Je travaille dans un magasin d’alimentation. Vous êtes client(e) et vous voulez faire livrer vos courses chez vous. Vous me posez des questions sur les conditions offertes : délais, tarifs, mode de livraison, etc.",
        aide: AIDE_INTERACTION,
      },
      {
        type: "Argumentation",
        description: O_ARGUMENTATION,
        prep: 0,
        duree: 270,
        sujet:
          "Est-il préférable de commencer l’apprentissage des langues étrangères dès l’enfance ? Pourquoi ?",
        aide: AIDE_ARGUMENTATION,
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "oral-20",
    titre: "Oral — Combinaison 20",
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
          "Je travaille dans une agence immobilière. Vous voulez louer votre appartement pour les vacances afin de gagner plus d’argent. Vous me demandez des conseils sur les prix, la durée de location, le type de locataires, etc.",
        aide: AIDE_INTERACTION,
      },
      {
        type: "Argumentation",
        description: O_ARGUMENTATION,
        prep: 0,
        duree: 270,
        sujet:
          "D’après vous, pour quelles raisons les gens aiment-ils découvrir la vie des célébrités ?",
        aide: AIDE_ARGUMENTATION,
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "oral-21",
    titre: "Oral — Combinaison 21",
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
          "Sujet 1 : Je suis chef cuisinier/cheffe cuisinière à domicile. Vous souhaitez organiser un repas de famille. Vous me posez des questions sur ce que je peux vous proposer (plats, matériel, prix, etc.).",
        aide: AIDE_INTERACTION,
      },
      {
        type: "Argumentation",
        description: O_ARGUMENTATION,
        prep: 0,
        duree: 270,
        sujet:
          "Il est plus facile de partir vivre dans un pays étranger quand on est jeune. Êtes-vous d’accord avec cette affirmation ?",
        aide: AIDE_ARGUMENTATION,
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "oral-22",
    titre: "Oral — Combinaison 22",
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
          "Je suis votre voisin(e). Je suis conductrice/conducteur et je propose de partager des allers-retours avec ma voiture. Vous êtes intéressé(e) et me posez des questions sur ce type de service (prix, horaires, organisation, etc.).",
        aide: AIDE_INTERACTION,
      },
      {
        type: "Argumentation",
        description: O_ARGUMENTATION,
        prep: 0,
        duree: 270,
        sujet:
          "Le télétravail permet d’avoir un bon équilibre entre vie professionnelle et vie personnelle. Qu’en pensez-vous ?",
        aide: AIDE_ARGUMENTATION,
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "oral-23",
    titre: "Oral — Combinaison 23",
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
          "Je travaille à l’accueil dans une école de musique. Vous voulez vous inscrire à un cours. Vous me posez des questions (types de cours, horaires, tarifs, etc.) et je vous communique des informations.",
        aide: AIDE_INTERACTION,
      },
      {
        type: "Argumentation",
        description: O_ARGUMENTATION,
        prep: 0,
        duree: 270,
        sujet:
          "Les caméras de surveillance permettent d’améliorer la sécurité des citoyens dans les lieux publics. Est-ce que vous êtes d’accord ?",
        aide: AIDE_ARGUMENTATION,
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "oral-24",
    titre: "Oral — Combinaison 24",
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
          "Je travaille à l’accueil d’un club de sport. Vous êtes intéressé(e). Vous me posez des questions pour obtenir des informations (types de sports, horaires, tarifs, etc.).",
        aide: AIDE_INTERACTION,
      },
      {
        type: "Argumentation",
        description: O_ARGUMENTATION,
        prep: 0,
        duree: 270,
        sujet:
          "Pensez-vous que le choix des vêtements est important dans la vie ? Expliquez pourquoi.",
        aide: AIDE_ARGUMENTATION,
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "oral-25",
    titre: "Oral — Combinaison 25",
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
          "Je travaille à l’accueil d’un hôtel. Vous voulez réserver une chambre. Vous me posez des questions et je vous communique des informations (prix, type de chambre, petit-déjeuner, etc.).",
        aide: AIDE_INTERACTION,
      },
      {
        type: "Argumentation",
        description: O_ARGUMENTATION,
        prep: 0,
        duree: 270,
        sujet:
          "Pour sauver l’environnement, les actions de chaque personne (tri, économie d’eau, économie d’énergie, etc.) sont efficaces. Qu’en pensez-vous ?",
        aide: AIDE_ARGUMENTATION,
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "oral-26",
    titre: "Oral — Combinaison 26",
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
          "Je travaille à la réception d’une école de musique. Vous voulez vous inscrire à des cours. Vous me posez des questions sur ce que l’école propose (leçons, prix, emploi du temps, instruments, etc.).",
        aide: AIDE_INTERACTION,
      },
      {
        type: "Argumentation",
        description: O_ARGUMENTATION,
        prep: 0,
        duree: 270,
        sujet:
          "Travailler avec des amis ou des membres de la famille est-il une bonne idée ? Qu’en pensez-vous ?",
        aide: AIDE_ARGUMENTATION,
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "oral-27",
    titre: "Oral — Combinaison 27",
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
          "Je suis votre ami(e) et j’habite à Ottawa. Vous venez d’arriver dans la ville et vous souhaitez circuler à vélo. Vous me posez des questions pour savoir si c’est pratique (pistes, location, matériel, etc.).",
        aide: AIDE_INTERACTION,
      },
      {
        type: "Argumentation",
        description: O_ARGUMENTATION,
        prep: 0,
        duree: 270,
        sujet:
          "Internet a-t-il modifié les comportements au travail ? Qu’en pensez-vous ?",
        aide: AIDE_ARGUMENTATION,
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "oral-28",
    titre: "Oral — Combinaison 28",
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
          "Je suis votre ami(e). Vous avez envie de partir un week-end pour vous reposer. Vous me posez des questions pour avoir des suggestions (endroits, activités, transport, etc.).",
        aide: AIDE_INTERACTION,
      },
      {
        type: "Argumentation",
        description: O_ARGUMENTATION,
        prep: 0,
        duree: 270,
        sujet:
          "Un monde sans frontière, sans passeport ni visa est-il possible ? Pourquoi ?",
        aide: AIDE_ARGUMENTATION,
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "oral-29",
    titre: "Oral — Combinaison 29",
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
          "Je suis votre ami(e). Je vis au Canada depuis deux ans. Vous êtes en train de préparer votre arrivée au Canada. Vous me posez des questions sur mon vécu (habitudes, vie courante, adaptation, etc.).",
        aide: AIDE_INTERACTION,
      },
      {
        type: "Argumentation",
        description: O_ARGUMENTATION,
        prep: 0,
        duree: 270,
        sujet:
          "S’installer dans un nouveau pays est difficile. Qu’en pensez-vous ?",
        aide: AIDE_ARGUMENTATION,
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "oral-30",
    titre: "Oral — Combinaison 30",
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
          "Je suis votre voisin(e). Je connais une personne qui fait des petits services à domicile. Vous voulez en savoir plus et vous me posez des questions (compétences, horaires, tarifs, etc.).",
        aide: AIDE_INTERACTION,
      },
      {
        type: "Argumentation",
        description: O_ARGUMENTATION,
        prep: 0,
        duree: 270,
        sujet:
          "Que pensez-vous de l’internet en général ?",
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
