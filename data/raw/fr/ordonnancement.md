# Ordonnancement (informatique)

En informatique, l'ordonnancement est le fait d'ordonner des tâches à exécuter selon certaines contraintes. Ces tâches peuvent être l'exécution d'opération sur les entrées-sorties ou le traitement de processus. Les contraintes peuvent être temporelles ou dimensionnelles.
Dans les systèmes d'exploitation, l'ordonnanceur est le composant du noyau du système d'exploitation choisissant l'ordre d'exécution des processus sur les processeurs d'un ordinateur. En anglais, l'ordonnanceur est appelé scheduler.
Un processus a besoin de la ressource processeur pour exécuter des calculs ; il l'abandonne quand se produit une interruption, etc. De nombreux processeurs anciens ne peuvent effectuer qu'un traitement à la fois. Pour les autres, un ordonnanceur reste nécessaire pour déterminer quel processus sera exécuté sur quel processeur (c'est la notion d'affinité, très importante pour ne pas dégrader les performances). Au-delà des classiques processeurs multicœur, la notion d'hyperthreading rend la question de l'ordonnancement encore un peu plus complexe.
À un instant donné, il y a souvent davantage de processus à exécuter que de processeurs. Un des rôles du système d'exploitation, et plus précisément de l'ordonnanceur du noyau, est de permettre à tous ces processus de s'exécuter à un moment ou un autre et d'utiliser au mieux le processeur pour l'utilisateur. Pour que chaque tâche s'exécute sans se préoccuper des autres et/ou aussi pour exécuter les tâches selon les contraintes imposées au système (exemple : contraintes temporelles dans le cas d'un système d'exploitation temps réel) , l'ordonnanceur du noyau du système effectue des commutations de contexte de celui-ci.

## Commutation de contexte et élection
À intervalles réguliers, le système appelle une procédure d'ordonnancement qui élit le prochain processus à exécuter. Si le nouveau processus est différent de l'ancien, un changement de contexte (opération consistant à sauvegarder le contexte d'exécution de l'ancienne tâche comme les registres du processeur) a lieu. Cette structure de données est généralement appelée PCB. Le système d'exploitation restaure l'ancien PCB de la tâche élue, qui s'exécute alors en reprenant là où elle s'était arrêtée précédemment.

### Exemple
Si 
  
    
      
        n
      
    
    {\displaystyle n}
  
 tâches doivent être exécutées de manière simultanée et qu'il est physiquement impossible pour l'ordinateur de traiter plus d'une tâche simultanément, le noyau commute rapidement le contexte d'exécution des 
  
    
      
        n
      
    
    {\displaystyle n}
  
 tâches, de manière que :

une seule tâche soit exécutée à la fois ;
globalement toutes les tâches soient exécutées.
Par exemple, avec trois tâches cela peut se décomposer par :

Sauvegarde par le noyau des contextes d'exécution de chacune des tâches,
commutation de contexte et élection de la nouvelle tâche n°1
Chargement par le noyau du contexte de la tâche 1.
Exécution des instructions de la tâche 1 pendant x millisecondes
Sauvegarde du contexte de la tâche 1
commutation de contexte et élection de la nouvelle tâche n°2
Chargement par le noyau du contexte de la tâche 2.
Exécution des instructions de la tâche 2 pendant x millisecondes
Sauvegarde du contexte de la tâche 2
commutation de contexte et élection de la nouvelle tâche n°3
Chargement par le noyau du contexte de la tâche 3.
Exécution des instructions de la tâche 3 pendant x millisecondes
Sauvegarde du contexte de la tâche 3
commutation de contexte et élection de la nouvelle tâche n°1
Chargement par le noyau du contexte de la tâche 1.
Exécution des instructions de la tâche 1 pendant x millisecondes
Sauvegarde du contexte de la tâche 1
…
(3 tâches ordonnancées avec l'algorithme Round-robin (Chacun son tour)).

## Types d'algorithmes
Du choix de l'algorithme d'ordonnancement dépend le comportement du système. Il existe deux grande classes d'ordonnancement.

### Ordonnancement en temps partagé
Il est présent sur la plupart des ordinateurs  « classiques ». Par exemple l'ordonnancement « decay » ; qui est celui par défaut sous Unix. Il consiste en un système de priorités adaptatives, par exemple il privilégie les tâches interactives pour que leur temps de réponse soit bon. Une sous-classe de l'ordonnancement en temps partagé sont les ordonnanceurs dits « proportional share », eux sont plus destinés aux stations de calcul et permettent une gestion rigoureuse des ressources. On peut citer notamment « lottery » et « stride ».

### Ordonnancement en temps réel
Il assure qu'une certaine tâche sera terminée dans un délai donné. Cela est indispensable dans les systèmes embarqués.

#### Optimalité
Un ordonnanceur temps réel est dit optimal pour un système de tâches s'il trouve une solution d'ordonnancement du système lorsque cette solution existe. S'il ne trouve pas de solution à ce système, alors aucun autre ordonnanceur ne peut en trouver une.

## Algorithmes d'ordonnancement
Round-robin (ou méthode du tourniquet)
Rate-monotonic scheduling (RMS)
Earliest deadline first scheduling (EDF)
FIFO
Shortest job first (SJF, ou SJN -Shortest Job Next-)
Completely Fair Scheduler (CFS)
LIFO

## Stratégies d'ordonnancement
Ordonnancement sans réquisition
Ordonnancement avec réquisition

## Voir aussi
### Articles liés
Théorie de l'ordonnancement
Ordonnancement de travaux informatiques

### Bibliographie
Andrew Tanenbaum, Systèmes d'exploitation, 3e édition, Pearson Education, 2008,  (ISBN 978-2-7440-7299-4)
Joseph Y-T. Leung, Handbook of Scheduling: Algorithms, Models, and Performance Analysis, Chapman & Hall/CRC Computer & Information Science Series, 2004.
J. Stankovic et al., Deadline Scheduling for Real-Time Systems, Kluwer Aacademic, Boston, 1998,  (ISBN 0-7923-8269-2)

 Portail de l’informatique
