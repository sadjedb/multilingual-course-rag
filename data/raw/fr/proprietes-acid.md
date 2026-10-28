# Propriétés ACID

En informatique, les propriétés ACID (atomicité, cohérence, isolation et durabilité) sont un ensemble de propriétés qui garantissent qu'une transaction informatique est exécutée de façon fiable.
Dans le domaine des bases de données, une opération sur les données est appelée une transaction ou transaction informatique. Par exemple, un transfert de fonds d'un compte de banque à un autre, même s'il implique plusieurs actions comme le débit d'un compte et le crédit d'un autre, est une seule transaction.
Jim Gray a défini les propriétés qui garantissent des transactions fiables à la fin des années 1970 et a développé des technologies pour les mettre en œuvre automatiquement.
En 1983, Andreas Reuter et Theo Härder ont créé l'acronyme ACID pour désigner ces propriétés.
Il faut noter qu'il existe des modèles de bases de données qui s'écartent des propriétés ACID, pour répondre à d'autres priorités comme la gestion de données massives et distribuées pour les usages du big data notamment par les géants d'Internet : ce sont les bases NoSQL.

## Propriétés
Les caractéristiques de ces quatre propriétés telles que définies par Reuter et Härder sont les suivantes :

### Atomicité
Les transactions sont souvent composées de plusieurs instructions. L'atomicité garantit que chaque transaction est traitée comme une seule « unité », qui réussit complètement ou échoue complètement : si l'une des déclarations constituant une transaction échoue, la transaction entière échoue et la base de données reste inchangée. Un système atomique doit garantir l'atomicité dans toutes les situations, y compris les pannes de courant, les erreurs et les crashs. Une garantie d'atomicité empêche que les mises à jour de la base de données ne se produisent que partiellement, ce qui peut causer des problèmes plus importants que le rejet pur et simple de toute la série. En conséquence, la transaction ne peut pas être observée comme étant en cours par un autre client de la base de données. À un moment donné, elle n'a pas encore eu lieu, et au moment suivant, elle s'est déjà produite en totalité (ou rien ne s'est produit si la transaction a été annulée en cours).

### Cohérence
La cohérence garantit qu'une transaction ne peut faire passer la base de données que d'un état cohérent à un autre, en préservant les invariants de la base de données : toute donnée écrite dans la base de données doit être valide selon toutes les règles définies, y compris les contraintes, les rollbacks, les déclencheurs et toute combinaison de ceux-ci. Cela empêche la corruption de la base de données par une transaction illégale. L'intégrité référentielle garantit la relation clé primaire-clé étrangère.

### Isolation
Les transactions sont souvent exécutées simultanément (par exemple, plusieurs transactions lisant et écrivant dans une table en même temps). L'isolation garantit que l'exécution simultanée des transactions laisse la base de données dans le même état que celui qui aurait été obtenu si les transactions avaient été exécutées séquentiellement. L'isolation est le principal objectif du contrôle de la concurrence ; selon le niveau d'isolation utilisé, les effets d'une transaction incomplète peuvent ne pas être visibles pour les autres transactions.

### Durabilité
La durabilité garantit qu'une fois qu'une transaction a été validée, elle le restera même en cas de défaillance du système (par exemple, une panne de courant ou un crash). Cela signifie généralement que les transactions terminées (ou leurs effets) sont enregistrées dans une mémoire non volatile.

## Illustration des propriétés
Les sections suivantes expliquent les propriétés ACID en décrivant un exemple d'échec inacceptable pour chacune des propriétés.
Dans ces exemples, une base de données contient une table avec deux colonnes A et B. Une contrainte d'intégrité stipule que la somme de A et B doit toujours être 100. L'énoncé SQL suivant décrit cette contrainte :

### Échec d'atomicité
Supposons qu'une transaction tente de soustraire 10 à A et d'ajouter 10 à B. C'est une transaction valide étant donné que la somme de A et B est 100 après la transaction. Si, après avoir soustrait 10 à A, la transaction est interrompue par un problème quelconque sans pouvoir ajouter 10 à B, alors la propriété d'atomicité serait violée si la base de données restait dans cet état. Pour que la propriété d'atomicité soit respectée, il faut que la transaction se complète ou qu'elle ne se fasse pas du tout. Dans le cas présent, il faut que A soit remis dans son état initial pour que l'atomicité soit respectée.

### Échec de cohérence
La cohérence est le respect de toutes les règles spécifiées dans les contraintes d'intégrité. Dans notre exemple, la seule règle est que la somme de A et B doit être 100. Il pourrait y avoir d'autres règles, par exemple, une règle pourrait spécifier que la valeur de A doit être plus grande que 5.
Supposons qu'une transaction T1 tente de soustraire 10 de A sans modifier B. Comme la cohérence a été vérifiée après la transaction qui a précédé la transaction T1, nous savons que la somme de A et B est égale à 100 avant la transaction T1. Si la transaction T1 s'exécute jusqu'au bout, elle retranchera 10 de A et l'atomicité sera respectée. Par contre, une validation de cohérence montrera que la somme de A et B est égale à 90 et non à 100. Comme la cohérence n'est pas respectée, la transaction sera annulée et la valeur de A sera augmentée de 10 pour reprendre la valeur qu'elle avait avant la transaction T1.

### Échec d'isolation
Supposons les deux transactions suivantes : T1 transfère 10 de A à B, T2 transfère 5 de B à A. Si les transactions s'exécutent en séquence, nous avons les actions suivantes :

première partie de la transaction T1 : A est réduit de 10 ;
seconde partie de la transaction T1 : B est augmenté de 10 ;
première partie de la transaction T2 : B est réduit de 5 ;
seconde partie de la transaction T2 : A est augmenté de 5.
Si les quatre opérations sont exécutées dans l'ordre ci-dessus, l'isolation est assurée. Si la transaction T1 est interrompue après sa première action, le système effacera l'effet partiel de T1 avant le début de T2 et T2 s'exécutera sur des données valides.
Par contre, si les transactions tentent de s'exécuter simultanément et que la transaction T2 commence avant la fin de T1, on peut obtenir la suite d'actions suivante :

première partie de la transaction T1 : A est réduit de 10 ;
première partie de la transaction T2 : B est réduit de 5 ;
seconde partie de la transaction T2 : A est augmenté de 5 ;
seconde partie de la transaction T1 : B est augmenté de 10.
Si la transaction T1 est interrompue avant sa deuxième partie, mais après la complétion de la transaction T2, le rétablissement de A à sa valeur d'avant la transaction T1 annulera l'augmentation valide de A faite par la transaction T2 et laissera la base de données dans un état corrompu parce que A sera revenu à sa valeur initiale, mais B aura été réduit de 5. Ce serait un échec d'isolation. La propriété d'isolation n'interdit pas la séquence d'actions précédente. Par contre, le système doit être muni de contrôles et de rollbacks qui assurent que, dans tous les cas, le résultat de l'exécution simultanée des transactions donne le même résultat que leur exécution en séquence.

### Échec de durabilité
Supposons qu'une transaction transfère 10 de A à B. Supposons qu'une confirmation de la transaction est envoyée à l'utilisateur après l'instruction d'écriture sur disque des nouvelles valeurs de A et B, mais avant que le contenu du tampon du disque soit transféré au disque. Supposons aussi qu'une panne d'électricité se produise entre la confirmation et le transfert du tampon au disque et supposons aussi que le système n'a aucune façon de recréer les valeurs de A et B. Nous avons alors un échec de durabilité parce que l'utilisateur a reçu une confirmation, mais que l'effet de la transaction est perdu.

## Références
## Source
(en) Cet article est partiellement ou en totalité issu de l’article de Wikipédia en anglais intitulé « ACID » (voir la liste des auteurs).

 Portail de l’informatique   Portail des bases de données
