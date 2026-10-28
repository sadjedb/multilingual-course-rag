# Forme normale (bases de données relationnelles)

Dans une base de données relationnelle, une forme normale caractérise le fait que la structure de la base respecte certaines contraintes de modélisation. Le respect par une base de données d'une forme normale permet de garantir certaines propriétés. 
La normalisation consiste à restructurer une base de données pour respecter certaines formes normales, afin d'éviter la redondance des données (des données apparaissent plusieurs fois) et d'assurer l'intégrité des données.

## Objectif
Le but de la normalisation est de structurer les données afin d'éliminer la redondance et de garantir la cohérence des informations lors de leur manipulation ou utilisation. Son principal intérêt est de s'assurer qu'aucune anomalie de lecture, d’écriture ou d'insertion (regroupées sous le terme d'anomalies transactionnelles), ne vienne impacter l'efficacité opérationnelle, notamment la performance et la maintenabilité du système.
En pratique, ce processus permet de valider la robustesse d'une conception en vérifiant la pertinence des données au sein des entités et des relations . Cette décomposition facilite l'évolution du modèle sans compromettre l'intégrité des données existantes.

## Panorama des formes normales
Codd a introduit le concept de normalisation et qui est maintenant connu comme première forme normale en 1970. Puis Codd a défini la deuxième forme normale (2NF) puis la troisième (3NF) en 1971. Codd et Raymond F. Boyce ont défini la forme normale de Boyce-Codd notée FNBC (BCNF en anglais) en 1974. Les formes normales s’emboîtent les unes dans les autres : le respect d’une forme normale de niveau supérieur implique le respect des formes normales des niveaux inférieurs. En tout dans le modèle relationnel de type OLTP (OnLine Transaction Processing), il existe plusieurs formes normales :

La première forme normale notée 1FN (1NF en anglais) ;
La deuxième forme normale notée 2FN (2NF en anglais) ;
La troisième forme normale notée 3FN (3NF en anglais) ;
La forme normale clé élémentaire (EKNF pour Elementary key normal form en anglais) ;
La forme normale de Boyce-Codd notée FNBC (BCNF en anglais) ;
La quatrième forme normale notée 4FN (4NF en anglais) ;
La cinquième forme normale notée 5FN (5NF en anglais) ;
La forme normale domaine clef notée FNDC (DKNF en anglais) ;
La sixième forme normale notée 6FN (6NF en anglais) rarement présentée.
Les trois premières étant les plus connues et utilisées. D'ailleurs, généralement, on dit qu'une base de données est normalisée si elle respecte la 3FN.

La forme normale vient après la simple validité d’un modèle relationnel, c’est-à-dire que les valeurs des différents attributs soient bien en dépendance fonctionnelle avec l'identifiant (c'est-à-dire la clef primaire au niveau tabulaire), ils sont complètement déterminés par l'identifiant.

## Avantages et inconvénients
En pratique, la première et la deuxième forme normale sont nécessaires pour avoir un modèle relationnel juste. L’usage est de modéliser au moins en 3e forme normale. Les formes normales supplémentaires ont leurs avantages et leurs inconvénients.
Les principaux avantages d'une modélisation en 3e forme normale sont :

d'éviter la redondance de données;
d’interdire les incohérences de données venant des redondances dont une partie seulement a été mise à jour, ce qui rendrait de fait les données inutilisables (différentes versions d’une même information, sans que l’on sache laquelle est valide) ;
donc de diminuer la volumétrie globale;
de limiter grandement le nombre et la durée des mises à jour qui sont des processus bloquants (écritures).
L’inconvénient essentiel d'une base en 3e forme normale tient aux temps d’accès potentiellement plus longs si les requêtes portent sur des attributs (colonnes) de plusieurs entités (tables) associées, là où une base en 2e forme normale pourrait être optimisée pour répondre à ce type de requête en ne lisant qu'une table.
Pour des petites bases de données, se limiter à la troisième forme normale est généralement une bonne solution d’un point de vue architecture de base de données, mais pour des bases de données plus importantes, il est nécessaire d’aller plus loin, voire — après normalisation et étalonnage — d’effectuer une dénormalisation intelligente dont un benchmark prouve globalement les gains. 
La normalisation est importante essentiellement pour les bases OLTP par opposition aux bases OLAP. Et même au sein des bases OLTP il est possible qu’un arbitrage doive être effectué sur le niveau de normalisation selon que les tables de la base de données sont plus sollicitées en lecture ou plus en écriture. Si une table est notablement très intensivement écrite et peu lue, il sera préférable de normaliser le plus possible. À contrario, si une table très intensivement lue est peu écrite, il pourra être judicieux d’être moins strict sur le respect de la normalisation pour permettre d’améliorer les performances d’accès aux données. Mais même dans ces principes généraux, l’inverse peut s’avérer intéressant. C’est le cas par exemple des tables de "log" dans lesquelles généralement la structure est souvent dénormalisée afin d’effectuer l’insertion de ligne en une seule passe, alors qu’elles sont fortement écrites et généralement peu lues. Notons qu’il arrive fréquemment, au sein d’une base OLTP, que des tables soient en lecture seulement, comme ce peut être le cas d’une table servant de calendrier... Dans ce dernier cas, la dénormalisation pourrait être extrême.
Il convient d’être prudent lorsqu’on renonce à la forme normale. Il n’est pas garanti qu’une forme dénormalisée améliore les temps d’accès. En effet, la redondance peut entraîner une explosion des volumes de données qui peuvent écrouler les performances ou saturer les disques durs. Il est donc nécessaire de commencer par une normalisation, étalonner les métriques de temps de réponse sur des volumes réels puis dénormaliser, entreprendre une nouvelle campagne de mesure, comparer, et si le gain est globalement avéré, alors conserver la dénormalisation. Il est important de comprendre que les gains de dénormalisation entraînent systématiquement des pertes sur d’autres objets, ce pourquoi il ne faut pas se contenter de regarder l’arbre qui masque la forêt et donc effectuer des mesures sur l’ensemble des objets de la base et non se consacrer à mesurer uniquement les objets cibles de la dénormalisation.
La normalisation des modèles de données a été popularisée principalement par la méthode Merise. 

## Les différentes formes normales
Les formes normales sont construites selon le principe des dépendances fonctionnelles. On dit qu’un ensemble d’attributs détermine un autre ensemble d’attributs si : pour deux tuples distincts toute projection des deux tuples sur le premier ensemble d'attributs donnant les mêmes valeurs, induit obligatoirement que les valeurs projetées des tuples sur le deuxième ensemble d'attributs soient identiques. Soient deux tuples t1 et t2, soient deux ensembles d’attributs X, Y (à intersection vide) si la projection de t1 sur X est égale à la projection de t2 sur X alors la projection de t1 sur Y doit être égale à la projection de t2 sur Y. Dans ce cas X détermine Y ou Y dépend fonctionnellement de X (X → Y). On dit aussi que X est le déterminant et Y le déterminé et plus généralement on parle de partie gauche et de partie droite. La partie gauche (déterminant) compose l'identifiant de la relation, tandis que la partie droite compose les informations dépendantes de la connaissance des valeurs des attributs d’un identifiant.
Ceci se note généralement : partie gauche (ou déterminant) → partie droite (ou déterminé)
Dans les articles qui suivent, nous prendrons comme exemple théorique, une relation notée R ayant les attributs A1, A2, A3, A4, A5, A6 dont les trois premiers sont le déterminant et les trois derniers le déterminé.

### 1FN – Première forme normale
Une relation (ayant par définition un identifiant) est en première forme normale si tous les attributs possèdent tous une valeur sémantiquement atomique.
Une autre définition serait : un attribut est dit « atomique » si aucune subdivision de la donnée initiale n’apporte une information supplémentaire ou complémentaire.
Remarques :

une valeur atomique n’est pas forcément scalaire. Par exemple une donnée géographique constituée par un ensemble de points formant un polygone définissant une zone géographique précise, n’est à l’évidence pas scalaire, mais parfaitement atomique, car la suppression d’un seul des points du polygone, ne donne plus la même forme géographique. Il y a donc perte du sens initial de l’information ;
la notion d’atomicité s’apprécie par rapport à la possibilité de découper l’information en différents éléments ayant chacun un sens propre au regard de l’information initiale que l’on souhaite modéliser. Un exemple concret est donné par le numéro de sécurité sociale français qui est bien non atomique, car découpé en 4 parties distinctes : le sexe (un seul caractère), la date de naissance exprimée de façon partielle (année et mois, 4 caractères), la référence INSEE de la commune de naissance (5 caractères) et enfin, le rang de naissance dans cette commune et à cette date partielle (3 caractères).
Violent l’atomicité, les attributs :

constitués par un ensemble de valeurs énumérées (liste, tableaux...) dont les différentes valeurs sont sémantiquement indépendantes ;
n’ayant aucune valeur  (le « NULL » n’existe pas en algèbre relationnelle) ;
Certains attributs apparaissent posséder plusieurs éléments, mais ne sont pas toujours pour autant, non atomique :

c’est le cas en particulier de la date. Les différentes composantes d’une date ne sont pas indépendantes les unes des autres, tant s’en faut. En fait une date peut avoir plus ou moins de précision. Elle peut être une simple année, une année et un mois, l’an, le mois et la date du jour, comporter en sus l’heure, etc. Il est alors clair qu’une date constituée par exemple d’une année et d’un jour de mois n’a aucun sens. On voit bien que chacun des éléments dépend des autres en ce sens qu’une date peut être plus ou moins précise dans le sens de sa composition naturelle qui est AMJhms... Mais une date partielle comme le 13 de l’an 1456 ne veut strictement rien dire. Nous devons alors comprendre qu’une date est plus ou moins précise, tout comme l’est un nombre présentant plus ou moins de chiffres après la virgule. La précision d’une date étant donnée en fonction des éléments qu’elle comporte dans le sens de la plus grande période (souvent l’année) à la plus petite période (souvent le tantième de seconde), sans omettre aucune des périodes intermédiaires qui la composent ;
c’est aussi le cas de l’adresse IP qui apparaît souvent sous la forme de 4 entiers... Mais cela n’est qu’une apparence. En effet l’adresse IP est en fait constituée d’un seul entier de 32 bits présenté souvent en 4 petits entiers de 1 octet à des fins à l’origine de distribution des adresses... L’entier le plus à droite (le 4e dans le sens de lecture) était censé indiquer l’adresse de l’ordinateur au sein du site d’entreprise, le 3e, le site de l’entreprise pour une entreprise multi-site, le second le siège de l’entreprise, et enfin le premier entier, le pays… Tout cela ayant été formalisé dans les années 1970 période de l’IBM 370, au cours de laquelle on était sûr qu’aucune entreprise au monde n’aurait eu plus de 255 ordinateurs sur un même site, ni plus de 255 sites, etc. On connait maintenant l’histoire, et afin de ne pas la répéter, la nouvelle adresse réseau dite IPV6 est matérialisée par une chaîne binaire n’ayant aucune découpe particulière.
Le viol de la première forme normale constitue une des plaies les plus importantes en matière de bases de données relationnelles et a des conséquences catastrophiques en matière de performances.
La modélisation des attributs dans une base relationnelle ne doit pas prendre en compte les traitements spécifiques au métier, mais doit tout simplement correspondre à la nature intrinsèque de l’information, ceci afin de permettre l’évolution des bases dans toutes les circonstances de leur utilisation présente ou future.

### 2FN – Deuxième forme normale
Une relation respecte la deuxième forme normale, si elle respecte la première forme normale et aussi le principe suivant :

Les attributs d’une relation sont divisés en deux groupes : le premier groupe est composé de l'identifiant (un ou plusieurs attributs). Le deuxième groupe est composé des autres attributs (éventuellement vide). La deuxième forme normale stipule que tout attribut du deuxième groupe ne peut pas dépendre d’un sous-ensemble (strict) d’attribut(s) du premier groupe. En d’autres termes : « Un attribut non identifiant ne dépend pas d’une partie de l'identifiant mais de tout l'identifiant. »
Corollaire : une relation ayant un identifiant formé d’un seul attribut est donc en deuxième forme normale.
Le non-respect de la 2FN entraîne une redondance des données qui encombrent alors inutilement la mémoire et l’espace disque.

### 3FN – Troisième forme normale
Respecte la troisième forme normale, la relation respectant la deuxième forme normale et respectant le principe suivant :

Les attributs d’une relation sont divisés en deux groupes : le premier groupe est composé de l'identifiant (un ou plusieurs attributs). Le deuxième groupe est composé des autres attributs (éventuellement vide). La troisième forme normale stipule que tout attribut du deuxième groupe ne peut pas dépendre d’un sous-ensemble (strict et excluant l’attribut considéré) d’autres attribut(s) du second groupe. En d’autres termes : « Un attribut non identifiant ne dépend pas d’un ou plusieurs attributs ne participant pas à l'identifiant ». Dit encore autrement : « Tous les attributs non identifiants doivent dépendre directement de l'identifiant, au sens où il n’y a aucun attribut non identifiant dépendant de l'identifiant par dépendances transitives par l’intermédiaire d’autres attributs non identifiants».
Corollaire : une relation déjà en deuxième forme normale ayant au plus un attribut n’appartenant pas à l'identifiant est donc en troisième forme normale.
Le respect de la 3FN ne garantit pas une absence de redondance des données d’où la FNBC.

### FNBC – Forme normale de Boyce-Codd
Respecte la forme normale de Boyce-Codd, la relation respectant la troisième forme normale et dont tous les attributs non identifiants (hormis les clefs candidates qui sont neutres et ne doivent pas être considérées) ne sont pas source de dépendance fonctionnelle (DF) pour une partie de l'identifiant.
Le non-respect de la 2FN, 3FN et la FNBC entraîne de la redondance, une même donnée étant répétée un nombre considérable de fois.

### 4FN - quatrième forme normale
Pour être en 4FN, il faut respecter la FNBC.
Pour toute relation de dimension n (avec n supérieur à 1) en forme normale de Boyce-Codd, les relations de dimension n − 1 construites sur sa collection doivent avoir un sens. Il ne doit pas être possible de reconstituer les occurrences de la relation de dimension n par jointure de deux relations de dimension n − 1. Cette normalisation conduit parfois à décomposer une relation complexe en deux relations plus simples.

### 5FN - cinquième forme normale
Pour toute relation de dimension n (avec n supérieur à 2) en quatrième forme normale, il ne doit pas être possible de retrouver l’ensemble de ses occurrences par jointure sur les occurrences des relations partielles prises deux à deux. Cette normalisation conduit parfois à décomposer une relation complexe en plusieurs relations plus simples.
Le non-respect de la 4FN et 5FN entraîne de la perte de données et les données manquent de précision.

### FNDC - forme normale domaine clef
Une relation est en FNDC si et seulement si toutes les contraintes sont la conséquence logique des contraintes de domaines et des contraintes de clefs qui s’appliquent à la relation.
Pour se souvenir de l’ordre et des caractéristiques des trois premières formes normales, il suffit de se rappeler le serment que tous les témoins doivent prêter devant la justice :
Je jure de dire la vérité, toute la vérité, rien d’autre que la vérité.
Ce qui donne : 1FN = La clef. 2FN = Toute la clef. 3FN = Rien que la clef.
La phrase originale étant : « The key, the whole key, nothing but the key » (Chris Date). Elle est empruntée à l’œuvre de Shakespeare.

## Exemple de normalisation
(Les attributs soulignés dénotent une clef primaire)
Selon les trois principaux types de formes normales :

Une entité des données est en première forme normale, si chaque attribut de l'entité contient une valeur atomique (non composée) ;
Exemple :

Dans ce cas les valeurs du fournisseur sont multivaluées et ne sont pas atomiques.
Pour que cette entité soit en première forme normale, il faut décomposer les attributs de la colonne fournisseur comme suit 
Solution :

Une entité de données est en deuxième forme normale si elle est en première forme normale et si chaque attribut qui n’appartient pas à l'identifiant (l’ensemble des attributs permettant d’identifier de manière unique un tuple de l’entité) ne dépend pas uniquement d’une partie de l'identifiant ;
Exemple :

Admettons que la clef de cette table soit composite (produit - fournisseur).
Dans le cas d’un changement d’adresse d’un fournisseur, il faudra faire preuve de beaucoup d’attention pour n’oublier aucun endroit où l’adresse est mentionnée. En effet, on constate que l'attribut adresse ne dépend que d’une partie de la clef : la colonne fournisseur, ce qui induit la possibilité d’une redondance au sein de la table. Il convient donc de scinder la table en deux:
Solution en seconde forme normale :

De cette manière, un changement d’adresse ne donne lieu qu’à une seule modification dans la table des fournisseurs.

Une entité de données est en troisième forme normale si elle est en deuxième forme normale et si ses attributs qui ne font pas partie de l'identifiant ne dépendent pas d’attributs ne faisant pas non plus partie de l'identifiant (les attributs sont donc complètement indépendants les uns des autres).
Exemple :

Le pays de l’adresse n’est pas dépendant de la clef de la table, à savoir le nom du fournisseur, mais est fonction de la ville de l’adresse.
De nouveau, il est préférable de scinder la table en deux:
Solution normalisée :

De cette manière, une modification de l’orthographe pour un pays (par exemple : ENGLAND en GREAT BRITAIN) ne donnera lieu qu’à une seule modification.
Dans la pratique, l’identification soignée de tous les objets élémentaires de l’application concernée (pays, ville, client, fournisseur, produit, commande, facture, etc) est la première étape avant de leur créer chacun leur table. Chaque table peut alors être soumise au test de respect/non de telle ou telle forme normale. En général, toute valeur de données agrégées et toute répétition d’une valeur de donnée, dans une colonne peuplée, sont potentiellement des violations de forme normale.

## Exemples de violation
(Les attributs soulignés dénotent une clef primaire)

### 1FN — première forme normale
tout attribut contient une valeur atomique

tous les attributs sont non répétitifs

tous les attributs sont constants dans le temps.

### 2FN — deuxième forme normale
tous les attributs non identifiants sont totalement dépendants fonctionnellement de la totalité de l'identifiant (et donc de la clef primaire au niveau tabulaire).

### 3FN — troisième forme normale
tout attribut n’appartenant pas à un identifiant ne dépend pas d’un attribut non identifiant

### FNBC — forme normale de Boyce-Codd
Si une entité ou une relation en troisième forme normale a un identifiant composé, aucune des propriétés élémentaires de cet identifiant ne doit être en dépendance fonctionnelle d’une autre propriété.

### FNDC — forme normale domaine clef
Une relation est en FNDC si et seulement si toutes les contraintes sont la conséquence logique des contraintes de domaines et des contraintes de clefs qui s’appliquent à la relation.
Soit la relation VEHICULE, avec les attributs suivants :

On remarque que le type VL (véhicule léger) ou PL (poids lourd) est déterminé par la valeur du PTAC. Ainsi, au-dessus de 3,5 tonnes le véhicule est un PL. En dessous c’est un VL… Il y a redondance des données de type qui peut être déduite de la lecture de la valeur du PTAC. En cas de changement de la réglementation (barre des 3,5 tonnes qui pourrait être amenée à changer) alors il faut mettre à jour plusieurs n-uplets.
- Pour résoudre cette anomalie de mise à jour, il faut décomposer la relation en deux comme suit :

### 1er véhicule, avec les attributs suivants
Le type de véhicule ne figure plus. Il sera déduit de la valeur du PTAC : au-dessus de 3,5 tonnes le véhicule est un PL. En dessous c’est un VL.

### 2e type véhicule, avec les attributs suivants
Une inéqui-jointure sera nécessaire à reconstituer la relation originale.

## Bibliographie
Georges Gardarin, Bases de données, Eyrolles, 2003, 788 p. (ISBN 978-2-212-11281-8, lire en ligne), pages 689 et suivantes
Laurent Audibert, Bases de données : de la modélisation au SQL, Ellipses, 2009, 254 p. (ISBN 978-2-7298-5120-0, lire en ligne)
Christian Soutou, Modélisation des bases de données. Eyrolles 2015

## Articles connexes
Relation multivaleur

## Notes et références
 Portail de l’informatique   Portail des bases de données
