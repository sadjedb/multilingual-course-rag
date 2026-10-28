# Structured Query Language

SQL (sigle pour Structured Query Language, « langage de requêtes structurées ») est un langage informatique normalisé servant à exploiter des bases de données relationnelles. La partie langage de manipulation des données de SQL permet de rechercher, d'ajouter, de modifier ou de supprimer des données dans les bases de données relationnelles.
Outre le langage de manipulation des données :

le langage de définition des données permet de créer et de modifier l'organisation des données dans la base de données,
le langage de contrôle de transaction permet de commencer et de terminer des transactions,
le langage de contrôle des données permet d'autoriser ou d'interdire l'accès à certaines données (base, table, enregistrement) à certaines personnes.
Créé en 1974, normalisé depuis 1986, le langage est reconnu par la grande majorité des systèmes de gestion de bases de données relationnelles (SGBDR) du marché.
SQL fait partie de la même famille que les langages ALPHA (dont il est le descendant), SQUARE, QUEL (intégré à Ingres) ou QBE (Zloof). Il a été appelé SEQUEL à sa naissance, mais ce nom a été changé en SQL parce que SEQUEL était une marque déposée de l'avionneur Hawker Siddeley.

## Historique
En juin 1970, Edgar Frank Codd publia l'article A Relational Model of Data for Large Shared Data Banks (« Un référentiel de données relationnel pour de grandes banques de données partagées ») dans la revue Communications of the ACM (Association for Computing Machinery). Ce référentiel relationnel fondé sur la logique des prédicats du premier ordre a été rapidement reconnu comme un modèle théorique intéressant, pour l'interrogation des bases de données, et a inspiré le développement du langage Structured English QUEry Language (SEQUEL) (« langage d'interrogation structuré en anglais »), renommé ultérieurement SQL pour cause de conflit de marque déposée.
Développée chez IBM en 1970 par Donald Chamberlin et Raymond Boyce, cette première version a été conçue pour manipuler et éditer des données stockées dans la base de données relationnelle à l'aide du système de gestion de base de données IBM System R. Le nom SEQUEL, qui était déposé commercialement par l'avionneur Hawker Siddeley pour un système d'acquisition de données, a été abandonné et contracté en SQL en 1975. SQL était censé alors devenir un élément clé du futur projet FS.
En 1979, Relational Software, Inc. (actuellement Oracle Corporation) présenta la première version commercialement disponible de SQL, rapidement imité par d'autres fournisseurs.
SQL a été adopté comme recommandation par l'Institut de normalisation américaine (ANSI) en 1986, puis comme norme internationale par l'ISO en 1987 sous le nom de ISO/CEI 9075 - Technologies de l'information - Langages de base de données - SQL.
La norme internationale SQL est passée par un certain nombre de révisions :

Comme toute norme internationale publiée par l'ISO, ISO/CEI 9075 est disponible à l'achat sur le site de cette organisation, ou via un représentant national de l'ISO (AFNOR en France, ANSI aux États-Unis, etc.).

## Utilisation
Le langage SQL s'utilise principalement de trois manières :

un programme écrit dans un langage de programmation donné utilise l'interface de programmation du SGBD pour lui transmettre des instructions en langage SQL. Ces programmes utilisent des composants logiciels tels que ODBC ou JDBC. Cette technique est utilisée par l'invite de commande qui permet à un administrateur d'effectuer des opérations sur les bases de données, opérations qu'il décrit en SQL ;
technique dite embedded SQL : des instructions en langage SQL sont incorporées dans le code source d'un programme écrit dans un autre langage ;
technique des procédures stockées : des fonctions écrites dans un langage procédural propre à chaque SGBD (PL/SQL pour Oracle, SQL/PSM pour MySQL ...) sont enregistrées dans la base de données en vue d'être exécutées par le SGBD. Cette technique est aussi utilisée pour les triggers - procédures déclenchées automatiquement sur modification du contenu de la base de données.

## Syntaxe générale
Les instructions SQL s'écrivent d'une manière qui ressemble à celle de phrases ordinaires en anglais. Cette ressemblance voulue vise à faciliter l'apprentissage et la lecture.
C'est un langage déclaratif c'est-à-dire qu'il permet de décrire le résultat escompté, sans décrire la manière de l'obtenir. Les SGBD sont équipés d'optimiseurs de requêtes - des mécanismes qui déterminent automatiquement la manière optimale d'effectuer les opérations, notamment par une estimation de la complexité algorithmique. Celle-ci est fondée sur des statistiques récoltées à partir des données contenues dans la base de données (nombre d'enregistrements, nombre de valeurs distinctes dans une colonne, etc.).
Les instructions SQL couvrent quatre domaines : 

Langage de définition de données ;
Langage de manipulation de données ;
Langage de contrôle de données ;
Langage de contrôle des transactions.

### Langage de manipulation de données
Les instructions de manipulation du contenu de la base de données commencent par les mots clés SELECT, UPDATE, INSERT ou DELETE qui correspondent respectivement aux opérations de recherche de contenu, modification, ajout et suppression.
Divers autres mots-clés tels que FROM, JOIN et GROUP BY permettent d'indiquer les opérations d'algèbre relationnelle à effectuer en vue d'obtenir le contenu à manipuler.

### Langage de définition de données
Les instructions de manipulation des métadonnées - description de la structure, l'organisation et les caractéristiques de la base de données - commencent avec les mots-clés CREATE, ALTER, DROP, RENAME, COMMENT ou TRUNCATE (opérations d'ajouter, modifier, supprimer, renommer, commenter ou vider une métadonnée). Ces mots clés sont immédiatement suivis du type de métadonnée à manipuler : TABLE, VIEW, INDEX... Exemple : ALTER TABLE.

### Langage de contrôle de données et langage de contrôle des transactions
Les mots clés GRANT et REVOKE permettent d'autoriser des opérations à certaines personnes, d'ajouter ou de supprimer des autorisations. Tandis que les mots clés COMMIT et ROLLBACK permettent de confirmer ou annuler l'exécution de transactions.
La syntaxe de SQL fait l'objet de la norme ISO 9075. Cette norme laisse la possibilité aux producteurs de SGBD d'y ajouter des instructions spécifiques et non normalisées.
La norme a évolué au cours des années en vue de s'adapter aux demandes. Ainsi, les éditeurs de SGBD ont souvent ajouté des possibilités à leurs produits, avant que celles-ci fassent objet de normes. Cela provoque des variations dans la compréhension et l'interprétation qui est faite d'un code source en SQL par les différents logiciels de SGBD.
Ces différences font qu'un code source écrit sans précautions pour un SGBD donné ne fonctionnera pas forcément avec un autre SGBD.

### Exemples de code
Recherche

procédure stockée

Supprimer totalement une base de données et tout ce qu'elle contient :

## Manipulation de données
Le Langage de manipulation de données LMD (Data Manipulation Language, DML, en anglais) est un sous-ensemble du SQL utilisé pour ajouter, modifier et supprimer des données :

INSERT insère des n-uplets (informellement appelés lignes et appelés tuples en anglais) dans une table existante. Par exemple :

UPDATE Modifie un ensemble de n-uplets existant dans une table. Par exemple :

DELETE Supprime un ensemble de n-uplets existant dans une table. Par exemple :

MERGE Combine les données de plusieurs tables. C'est la combinaison de INSERT et UPDATE. Il peut être nommé UPSERT, INSERT OR REPLACE INTO, ou encore INSERT ON DUPLICATE KEY UPDATE dans certains moteurs de base de données.

## NULL et la logique ternaire
Le mot-clef NULL fut introduit dans SQL pour exprimer les informations manquantes dans le modèle relationnel. L'introduction de NULL, avec TRUE et FALSE est le fondement de la logique ternaire. NULL n'a pas de valeur en SQL (et n'est membre d'aucun type de données), c'est un mot-clé réservé, indiquant qu'une information est manquante. Par conséquent, la comparaison avec NULL, même avec NULL lui-même, ne peut ni être VRAI ni être FAUX, elle est obligatoirement inconnue et ne possède aucune valeur booléenne. En effet, NULL ne peut pas être considéré égal à NULL, puisque les deux informations manquantes, que ces deux NULL distincts représentent, peuvent s'avérer différentes. On dit généralement que NULL est un « marqueur ».

## Langages apparentés
Créé par extension de SQL, Transact-SQL est un langage de programmation des SGBD SQL Adaptive Server Anywhere (ASA), SQL Adaptive Server Enterprise (ASE), Sybase IQ de Sybase ainsi que SQL Server de Microsoft.
PL/SQL est un langage de programmation du SGBD Oracle Database de Oracle Corporation. PL/pgSQL est un langage de programmation du SGBD PostgreSQL. Ce sont des langages de programmation procédurale dans lesquels peuvent être ajoutées des instructions en langage SQL. Le code source écrit dans ce type de langage est compilé par le SGBD, puis enregistré dans la base de données et exécuté au besoin.
OQL est un langage similaire à SQL, pour demander des opérations aux bases de données orientées objet et obtenir les résultats sous forme d'objets. Le langage est normalisé par le Object Data Management Group - un consortium d'industriels informatiques qui a cessé toute activité en 2001.

## Dialectes inspirés par SQL
De nombreux dialectes ont été créés en s'inspirant de SQL. Par exemple :

par Salesforce, le SOQL reprenant une partie de la syntaxe SQL mais gérant les jointures différemment (à partir des tables de relation) ;
par Apache Hive, le HiveQL ou HQL qui reprend le SQL et vise à s'en rapprocher le plus possible ;
Snowflake (DataWareHouse Cloud ou DataLake Cloud) présente le Snowflake SQL, qui est un sous-ensemble de SQL-99.

## Langages concurrents
Parmi les autres langages de requêtes, citons les ancêtres de SQL comme QUEL (Query English Language) ou encore le langage QBE (Query By Example). Cependant le langage QBE, très différent de SQL, est encore en vigueur dans les SGBDR de type « fichier » que sont Paradox (Ansa Software/Borland/Corel) ou Microsoft Access (base de données) de Microsoft.

## Alternatives
Le langage Tutorial D est présenté comme étant plus cohérent et plus simple d'emploi par ses inventeurs. Il permet, de surcroît, pour alléger le libellé des requêtes, l'emploi d'une clause WITH inspirée du langage Pascal.
La technique du WITH a été en partie reprise dans la norme SQL:1999 pour réaliser des « Common Table Expression » (CTE ou expressions de table communes en français), c'est-à-dire des vues non instanciées utilisables par la requête dans laquelle elles figurent, et ce afin de factoriser des expressions ou encore de permettre l'écriture de requêtes récursives de manière à résoudre élégamment des parcours d'arbres ou de graphes.
Parmi les autres candidats, on compte :

BS12, qui lui aussi s'est attaqué à ce problème de l'enchâssement et de la perte de lisibilité qu'il entraîne.

## Systèmes de gestion de base de données avec SQL
Tous ces systèmes présentent certaines particularités. Il est d'ailleurs toujours intéressant de se référer au manuel de référence du SGBDR, lors de requêtes particulières ou complexes, ainsi que pour leur optimisation.

## Enseignement
L'apprentissage des requêtes de base en SQL fait partie du programme d'informatique tronc commun des classes préparatoires scientifiques MP, PC, PSI et PT.

## Notes et références
## Voir aussi
## Bibliographie
### En français
SQL Synthèse de cours et exercices - 4e édition (2 chapitres supplémentaires sur l'indexation et l'administration) - Frédéric Brouard, Christian Soutou, Rudi Bruchez - Pearson Education, 2012
Bases de données - de la modélisation au SQL - Laurent Audibert - Ellipses, 2009
SQL Synthèse de cours et exercices - 2e édition - Frédéric Brouard, Christian Soutou, Rudi Bruchez - Pearson Education, 2008
SQL par l'exemple - Antony Molinaro - O'Reilly, 2007
SQL en concentré - Kevin Kline - O'Reilly, 2005
SQL pour les nuls - Allen G. Taylor - First Interactive, 2001
SQL développement - Frédéric Brouard - Campus Press, 2001
SQL2 - SQL3, Applications à Oracle (3e édition) - Pierre Delmal - De Boeck Université, 2001
SQL avancé (2e édition) - Joe Celko - Vuibert, 2000

### En anglais
The Art of SQL - Stéphane Faroult - O'Reilly, 2006
Advanced SQL:1999 - Jim Melton - Morgan Kaufmann, 2003
SQL bible - A. Kriegel, B. M. Trukhnov - John Wiley, 2003
SQL:1999, Understanding Relational Language Components - Jim Melton, Alan R. Simon - Morgan Kauffman, 2002
SQL in a nutshell - Kevin Kline, Daniel Kline - O'Reilly, 2001
SQL 3, Implementing the SQL Foundation Standard - Paul Fortier - McGraw-Hill, 1999
SQL-99 complete really - Peter Gulutzan, Trudy Pelzer - R&D Books, 1999
The Complete Reference SQL - J. R. Groff, P. N. Weinberg - Osborne, 1999
A guide to the SQL standard - Chris J. Date, Hugh Darwen - Addison Wesley - USA, 1997
Understanding the new SQL - Jim Melton, Alan R. Simon - Morgan Kaufmann, 1993

### Articles connexes
NoSQL
Base de données relationnelle
Formes normales
Pro*C
Système de gestion de base de données
Pick (système d'exploitation)
Query by Example
SAS (langage)
W3Schools : site d'apprentissage de divers langages de programmation dont SQL

 Portail de la programmation informatique   Portail des bases de données   Portail des données
