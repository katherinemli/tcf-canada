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
  // ---------------------------------------------------------
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

  // ---------------------------------------------------------
  {
    id: "combinaison-2",
    titre: "Combinaison 2",
    sousTitre: "3 tâches",
    dureeMinutes: 60,
    taches: [
      {
        type: "Message court",
        description: D_MESSAGE,
        motsMin: 60,
        motsMax: 120,
        sujet:
          "Vous souhaitez assister à un festival de cinéma dans votre ville. Vous écrivez un message à votre ami(e) pour lui proposer de venir avec vous. Vous lui donnez toutes les informations nécessaires sur l'événement (films, dates et horaires, tarifs, etc.).",
      },
      {
        type: "Narration / Blog",
        description: D_NARRATION,
        motsMin: 120,
        motsMax: 150,
        sujet:
          "Vous avez accueilli un(e) étudiant(e) étranger(e) pendant une semaine chez vous. Sur votre blog, vous écrivez un article pour raconter cette semaine. Vous expliquez pourquoi vous avez aimé cette expérience.",
      },
      {
        type: "Argumentation",
        description: D_ARGUMENTATION,
        motsMin: 120,
        motsMax: 180,
        sujet: "La Restauration Rapide.",
        documents: [
          "Les restaurants rapides se distinguent par leur engagement à proposer une variété de plats équilibrés, respectant strictement les normes d'hygiène. En laissant aux clients la liberté de composer leur propre menu, ces établissements les responsabilisent dans leurs choix alimentaires, tout en satisfaisant leurs préférences gustatives.",
          "Les spécialistes affirment que manger régulièrement dans des restaurants de fast-food, qui proposent de la restauration rapide, est dangereux pour la santé. La nourriture servie est souvent la même : frites, hamburgers et boissons sucrées. Ces aliments contiennent une grande quantité de calories, bien trop pour un seul repas. De plus, la plupart des produits dans ces restaurants sont emballés dans du plastique. Par conséquent, manger dans un fast-food augmente la production de déchets plastiques, ce qui est nuisible pour l'environnement.",
        ],
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "combinaison-3",
    titre: "Combinaison 3",
    sousTitre: "3 tâches",
    dureeMinutes: 60,
    taches: [
      {
        type: "Message court",
        description: D_MESSAGE,
        motsMin: 60,
        motsMax: 120,
        sujet:
          "Votre ami souhaite commencer à faire du sport. Rédigez un message pour lui recommander une salle de sport située dans votre quartier (localisation, tarifs, types d'activités, etc.).",
      },
      {
        type: "Narration / Blog",
        description: D_NARRATION,
        motsMin: 120,
        motsMax: 150,
        sujet:
          "Vous avez participé à un événement qui vous a marqué (anniversaire, mariage, etc.). Racontez votre souvenir en décrivant ce qui vous a le plus marqué.",
      },
      {
        type: "Argumentation",
        description: D_ARGUMENTATION,
        motsMin: 120,
        motsMax: 180,
        sujet: "La lecture pour les enfants.",
        documents: [
          "Avec l'avancée technologique et les produits high-tech qui envahissent de plus en plus notre quotidien, nos enfants oublient la lecture et s'intéressent davantage aux jeux vidéo, aux sports, à la musique… Contrairement à nous, les adultes, dont beaucoup d'entre nous ont lu des milliers de pages, la génération actuelle est toujours occupée par les réseaux sociaux et le gaming ou prend du plaisir à pratiquer du sport qui attire davantage de jeunes grâce aux stars internationales du football, du tennis, de l'athlétisme… alors avec tout ça, pourquoi devons-nous forcer les enfants à lire un bouquin ? Et comme le dit un proverbe, \"le goût de la lecture ne peut pas s'imposer\"… il faut laisser l'enfant choisir ce qu'il veut lire et surtout ne pas l'obliger à lire quand il n'en a pas envie.",
          "L'amour de la lecture se transmet de génération en génération bien que, ces dernières années, on ne trouve plus beaucoup de bouquins entre les mains des enfants, laissant la place aux smartphones et aux tablettes. En apprenant à lire régulièrement, l'enfant acquiert le langage plus aisément tout en développant sa capacité d'audition et de concentration. De plus, et pour prendre du plaisir ensemble, les parents peuvent consacrer quotidiennement 10 minutes à leurs enfants pour lire des bouquins ; une activité qui renforcera à coup sûr la complicité parent-enfant.",
        ],
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "combinaison-4",
    titre: "Combinaison 4",
    sousTitre: "3 tâches",
    dureeMinutes: 60,
    taches: [
      {
        type: "Message court",
        description: D_MESSAGE,
        motsMin: 60,
        motsMax: 120,
        sujet:
          "Écrivez un message pour inviter vos amis à une fête de fin d'année.",
      },
      {
        type: "Narration / Blog",
        description: D_NARRATION,
        motsMin: 120,
        motsMax: 150,
        sujet:
          "Vous avez passé des vacances au Canada par le biais d'une agence de voyage. Écrivez un commentaire pour raconter votre expérience que vous avez vécue durant ce voyage.",
      },
      {
        type: "Argumentation",
        description: D_ARGUMENTATION,
        motsMin: 120,
        motsMax: 180,
        sujet: "Limitation des voitures dans les centres-villes.",
        documents: [
          "Avec des taux de pollution alarmants constatés dans plusieurs endroits dans le monde, plusieurs villes ont réussi leur pari d'interdire la circulation des voitures en zones urbaines. La capitale de Norvège, Oslo, a récemment opté pour cette solution et s'en félicite, estimant que c'est une décision bénéfique pour tout le monde. Après un certain temps, les accidents diminueront, la dépendance au pétrole baissera et la qualité d'air sera meilleure !",
          "Beaucoup de villes se lancent dans des projets d'interdiction de voitures en zone urbaine sans mettre en place les outils et les infrastructures nécessaires pour réussir cette transition. Certes, en diminuant les voitures, on aura moins de pollution, mais en contrepartie, il faut prévoir entre autres de gigantesques parkings pour garer les voitures, opter davantage pour le transport en commun (métros et bus) et prévoir des autorisations de circulation pour certains corps de métier (comme la police, les urgentistes, les livreurs, etc.).",
        ],
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "combinaison-5",
    titre: "Combinaison 5",
    sousTitre: "3 tâches",
    dureeMinutes: 60,
    taches: [
      {
        type: "Message court",
        description: D_MESSAGE,
        motsMin: 60,
        motsMax: 120,
        sujet:
          "Écrivez un message à votre ami(e) qui souhaite suivre des cours de langue dans votre école. Donnez les détails spécifiques pour aider votre ami(e) à faire son choix. (lieu, tarifs, types de cours disponibles, etc.).",
      },
      {
        type: "Narration / Blog",
        description: D_NARRATION,
        motsMin: 120,
        motsMax: 150,
        sujet:
          "Vous travaillez dans une association qui aide les personnes âgées. Rédigez un article de blog pour raconter vos expériences et convaincre d'autres personnes de rejoindre l'association.",
      },
      {
        type: "Argumentation",
        description: D_ARGUMENTATION,
        motsMin: 120,
        motsMax: 180,
        sujet: "Les animaux de compagnie pour les enfants, pour ou contre ?",
        documents: [
          "Offrir un animal de compagnie à un enfant présente de nombreux avantages, comme le soulignent beaucoup de psychologues. Pour des enfants qui n'ont pas des frères et/ou des sœurs, l'animal est un compagnon qui leur évitera la solitude. Grâce à lui, un enfant prendra confiance en lui et il apprendra vite qu'un animal est un être vivant qui a besoin d'attention et de respect. En sa présence, l'enfant se sentira en sécurité et pourra agir de manière autonome, sans l'aide de ses parents.",
          "Beaucoup d'enfants demandent, un jour ou l'autre, un animal à leurs parents, le plus souvent un chien ou un chat. Mais même si vous avez envie de faire plaisir à votre enfant, il vaut mieux réfléchir sérieusement avant d'acheter un animal domestique. L'animal devient un nouveau membre de la famille et représente un engagement sur de nombreuses années. Or, avoir un animal coûte souvent très cher, et c'est une grande responsabilité. On ne peut pas le traiter comme un jouet que l'on met à la poubelle quand l'enfant s'en désintéresse.",
        ],
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "combinaison-6",
    titre: "Combinaison 6",
    sousTitre: "3 tâches",
    dureeMinutes: 60,
    taches: [
      {
        type: "Message court",
        description: D_MESSAGE,
        motsMin: 60,
        motsMax: 120,
        sujet:
          "Vous souhaitez fêter votre anniversaire dans un restaurant. Vous invitez vos amis. Vous leur écrivez un courriel pour leur donner toutes les informations nécessaires (lieu, date, horaires, menus, prix) et vous leur demandez une réponse.",
      },
      {
        type: "Narration / Blog",
        description: D_NARRATION,
        motsMin: 120,
        motsMax: 150,
        sujet:
          "Vous avez quitté la ville pour vous installer à la campagne. Sur un forum internet, vous expliquez pourquoi vous avez fait ce choix et vous présentez les avantages de votre nouvelle vie (120 mots minimum/150 mots maximum).",
      },
      {
        type: "Argumentation",
        description: D_ARGUMENTATION,
        motsMin: 120,
        motsMax: 180,
        sujet: "« Les caméras de surveillance à l'école sont-elles utiles ? »",
        documents: [
          "À Montréal, dans l'école où j'enseigne, des caméras sont présentes un peu partout. L'installation de ces appareils permet de faire comprendre aux jeunes que tout acte de violence sera puni. Ce mode de surveillance est très bien accepté par les parents, les enseignants et la plupart des élèves. Si les parents sont rassurés concernant la sécurité de leurs enfants, les professeurs y voient une garantie de pouvoir exercer leur métier dans les meilleures conditions possibles. Seuls certains élèves critiquent ces caméras en disant qu'elles ne respectent pas leur vie privée.",
          "Je suis contre la présence de caméras de surveillance dans nos écoles de Montréal. Dans les pays où ce système a été mis en place, les résultats ne sont pas très positifs. Comme les caméras sont très visibles, les personnes extérieures qui voudraient entrer dans l'école peuvent le faire en passant par des endroits non surveillés. Pour résoudre les problèmes de discipline, il suffit souvent d'améliorer la communication entre les élèves, l'administration et les enseignants. Au lieu de placer des caméras, il suffirait de bien faire comprendre et appliquer le règlement intérieur de l'école par tous.",
        ],
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "combinaison-7",
    titre: "Combinaison 7",
    sousTitre: "3 tâches",
    dureeMinutes: 60,
    taches: [
      {
        type: "Message court",
        description: D_MESSAGE,
        motsMin: 60,
        motsMax: 120,
        sujet:
          "Vous souhaitez proposer à un(e) ami(e) de faire du sport avec vous. Vous lui écrivez un message pour décrire votre projet (type d'activités, lieu, équipement, etc.).",
      },
      {
        type: "Narration / Blog",
        description: D_NARRATION,
        motsMin: 120,
        motsMax: 150,
        sujet:
          "Vous avez étudié dans une université à l'étranger pendant six mois. Vous écrivez un message à vos amis pour raconter votre expérience et vous expliquez ce que vous avez aimé (120 mots minimum/150 mots maximum).",
      },
      {
        type: "Argumentation",
        description: D_ARGUMENTATION,
        motsMin: 120,
        motsMax: 180,
        sujet: "L'uniforme à l'école : Pour ou contre ?",
        documents: [
          "Aujourd'hui, les goûts des enfants sont influencés par la mode et les parents doivent souvent leur acheter de nouveaux vêtements. L'uniforme est une solution à ce problème et permet aux parents d'économiser de l'argent. De plus, les jeunes qui portent un uniforme ont un sentiment fort d'appartenance à leur école et ressentent une certaine fierté. Par ailleurs, une tenue identique pour tous les élèves permet de masquer les différences de classe sociale et la discrimination basée sur le style. Le port de l'uniforme est donc positif pour tout le monde !",
          "Au Québec, l'uniforme scolaire n'est plus réservé uniquement aux écoles privées : de plus en plus d'écoles publiques font ce choix pour leurs élèves. Mais il représente un problème pour les adolescents qui ne sont pas toujours d'accord avec ce choix. Ils disent souvent que ces uniformes ne sont pas confortables, qu'ils ne sont pas beaux car ils manquent de couleurs et qu'ils tiennent trop chaud en été. De plus, comme tous les élèves de l'école sont habillés de la même manière, les jeunes trouvent que cela ne leur permet pas d'exprimer leur personnalité.",
        ],
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "combinaison-8",
    titre: "Combinaison 8",
    sousTitre: "3 tâches",
    dureeMinutes: 60,
    taches: [
      {
        type: "Message court",
        description: D_MESSAGE,
        motsMin: 60,
        motsMax: 120,
        sujet:
          "Vous habitez dans un grand appartement et vous recherchez un colocataire. Décrivez le type de colocation que vous proposez ainsi que les caractéristiques de votre appartement.",
      },
      {
        type: "Narration / Blog",
        description: D_NARRATION,
        motsMin: 120,
        motsMax: 150,
        sujet:
          "Une troupe de théâtre s'est installée dans votre ville, et vous avez assisté à l'un de ses spectacles. Rédigez un article de blog pour décrire cette expérience.",
      },
      {
        type: "Argumentation",
        description: D_ARGUMENTATION,
        motsMin: 120,
        motsMax: 180,
        sujet: "L'influence de la publicité sur les enfants : pour ou contre ?",
        documents: [
          "Une étude a révélé que les enfants sont constamment exposés à de nombreuses publicités, que ce soit à la télévision, dans les magazines ou sur Internet, et ce, dans des endroits vulnérables à l'influence publicitaire. Les enfants sont particulièrement ciblés par des publicités pour des produits alimentaires peu sains, des jouets, des jeux vidéo et autres produits, ce qui peut influencer leurs choix de consommation et leurs demandes envers leurs parents.",
          "Un article de recherche publié dans une revue scientifique souligne que les enfants ont des capacités cognitives limitées pour comprendre et interpréter les messages publicitaires, et qu'ils ne sont généralement pas conscients du caractère persuasif de la publicité. Toutefois, d'autres facteurs tels que l'éducation parentale, les influences sociales et culturelles ont un rôle plus important dans les choix de consommation des enfants que la publicité elle-même.",
        ],
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "combinaison-9",
    titre: "Combinaison 9",
    sousTitre: "3 tâches",
    dureeMinutes: 60,
    taches: [
      {
        type: "Message court",
        description: D_MESSAGE,
        motsMin: 60,
        motsMax: 120,
        sujet:
          "Vous avez passé un week-end à la campagne. Écrivez un message à votre ami(e) pour lui décrire ce qui s'est passé.",
      },
      {
        type: "Narration / Blog",
        description: D_NARRATION,
        motsMin: 120,
        motsMax: 150,
        sujet:
          "Votre direction est à la recherche d'une salle pour la fête de fin d'année, capable d'accueillir 100 invités. Rédigez un message à la direction pour leur dire que vous avez trouvé un local idéal (lieu, tarifs, services, etc.).",
      },
      {
        type: "Argumentation",
        description: D_ARGUMENTATION,
        motsMin: 120,
        motsMax: 180,
        sujet: "Utilisation des nouvelles technologies dans les écoles : pour ou contre ?",
        documents: [
          "Jean : Je suis fermement convaincu que l'intégration des nouvelles technologies dans les écoles est cruciale pour préparer les élèves à un avenir numérique. Je pense que l'usage des tablettes et des ordinateurs stimule non seulement l'engagement des élèves mais enrichit également leur expérience éducative en leur offrant un accès facile à une variété de ressources, encourageant ainsi leur créativité et leur autonomie.",
          "Sara : Je suis sceptique quant à l'usage intensif des technologies dans l'enseignement. Je crois que cela peut réduire les interactions humaines essentielles et favoriser une dépendance préoccupante aux écrans. À mon avis, les méthodes d'enseignement traditionnelles et le contact direct entre enseignants et élèves restent indispensables pour un développement équilibré et complet des compétences des jeunes.",
        ],
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "combinaison-10",
    titre: "Combinaison 10",
    sousTitre: "3 tâches",
    dureeMinutes: 60,
    taches: [
      {
        type: "Message court",
        description: D_MESSAGE,
        motsMin: 60,
        motsMax: 120,
        sujet:
          "Vous avez invité votre ami Cédric à votre mariage au Château de Chombony et il vous a répondu qu'il ne connaît pas ce château. Décrivez-le à votre ami (lieu, localisation, transports, etc.).",
      },
      {
        type: "Narration / Blog",
        description: D_NARRATION,
        motsMin: 120,
        motsMax: 150,
        sujet:
          "Dans votre blog, racontez votre expérience de l'apprentissage d'une langue étrangère (vous écrivez sur un forum internet en racontant votre expérience en apprenant une langue étrangère).",
      },
      {
        type: "Argumentation",
        description: D_ARGUMENTATION,
        motsMin: 120,
        motsMax: 180,
        sujet: "Cuisinier amateur ou cuisinier professionnel ?",
        documents: [
          "Les amateurs ont fait des recettes réussies, mais ils manquent toujours de compétences et de technique, c'est pourquoi la formation et l'expérience sont nécessaires pour être un vrai cuisinier.",
          "Il parle des cuisiniers qui ont appris le métier de cuisinier sur internet et qui ont eu le buzz sur les réseaux sociaux ; il raconte aussi l'histoire d'une amatrice qui est devenue professionnelle et qui a rédigé plusieurs livres sur la cuisine pour les amateurs de cuisine à la maison.",
        ],
      },
    ],
  },

  // ---------------------------------------------------------
  {
    id: "combinaison-11",
    titre: "Combinaison 11",
    sousTitre: "3 tâches",
    dureeMinutes: 60,
    taches: [
      {
        type: "Message court",
        description: D_MESSAGE,
        motsMin: 60,
        motsMax: 120,
        sujet:
          "Je suis votre amie Anna et je compte passer un weekend dans ta ville. Donnez-moi des informations sur les moyens de transport pour explorer la ville. Répondez à Anna dans un message.",
      },
      {
        type: "Narration / Blog",
        description: D_NARRATION,
        motsMin: 120,
        motsMax: 150,
        sujet:
          "Vous avez assisté à une fête de voisins du quartier. Écrivez un blog pour montrer pourquoi vous avez aimé cette fête.",
      },
      {
        type: "Argumentation",
        description: D_ARGUMENTATION,
        motsMin: 120,
        motsMax: 180,
        sujet:
          "L'utilisation des distributeurs automatiques au sein des établissements scolaires, pour ou contre ?",
        documents: [
          "Je suis en faveur des distributeurs de boissons dans les lycées. Premièrement, ils offrent une commodité supplémentaire pour les élèves, notamment pour ceux qui n'ont pas le temps de passer à la cafétéria pendant les pauses. Deuxièmement, s'ils sont bien gérés, ces distributeurs peuvent offrir une gamme de boissons saines, comme de l'eau, du jus de fruits pur et des boissons aux fruits sans sucre ajouté. Ces distributeurs peuvent être une source de revenus supplémentaire pour l'école, qui peut être réinvestie dans l'amélioration des infrastructures ou des programmes scolaires.",
          "Je suis contre l'installation de distributeurs de boissons dans les lycées. Ma principale préoccupation est liée à la santé des élèves. Malheureusement, beaucoup de ces distributeurs sont remplis de boissons sucrées et de sodas qui contribuent à l'obésité infantile et à d'autres problèmes de santé comme le diabète. Même les jus de fruits, qui peuvent sembler sains, contiennent souvent beaucoup de sucre. Les écoles devraient être des lieux qui encouragent des habitudes alimentaires saines et je crains que la présence de ces distributeurs n'encourage une consommation excessive de boissons sucrées.",
        ],
      },
    ],
  },

  // ▼▼▼ Combinaison 12+ viendront ici — envoie-moi les captures ▼▼▼
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
