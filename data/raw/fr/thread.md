# Thread (informatique)

Un thread ou fil (traduction normalisés par ISO/CEI 2382-7:2000) (autres appellations connues : processus léger, fil d'exécution, fil d'instruction, processus allégé, sous-processus, filet d'exécution, exétron, tâche[réf. nécessaire], voire unité d'exécution ou unité de traitement[réf. nécessaire]) est similaire à un processus car tous deux représentent l'exécution d'un ensemble d'instructions du langage machine d'un processeur.
Du point de vue de l'utilisateur, ces exécutions semblent se dérouler en parallèle. Toutefois, là où chaque processus possède sa propre mémoire virtuelle, les threads d'un même processus se partagent sa mémoire virtuelle. En revanche, tous les threads possèdent leur propre pile d'exécution.

## Utilisations
Les threads sont utilisés avec l'interface graphique (Graphical user interface) d'un programme. Les interactions de l'utilisateur avec le processus, par l'intermédiaire des périphériques d'entrée, sont gérées par un thread, technique similaire à celle utilisée pour les attentes asynchrones, tandis que les calculs lourds (en termes de temps de calcul) sont gérés par un ou plusieurs autres threads. Cette technique de conception de logiciel est avantageuse dans ce cas, car l'utilisateur peut continuer d'interagir avec le programme même lorsque celui-ci est en train d'exécuter une tâche. Une application pratique se retrouve dans les traitements de texte où la correction orthographique est exécutée tout en permettant à l'utilisateur de continuer à entrer son texte. L'utilisation des threads permet donc de rendre l'utilisation d'une application plus fluide, car il n'y a plus de blocage durant les phases de traitements intenses.
Les threads sont utilisés dans des programmes de calcul intensif (comme l'encodage d'une vidéo, les simulations mathématiques, etc.). L'utilisation de plusieurs threads permet de paralléliser le traitement, ce qui, sur les machines multiprocesseur, permet de l'effectuer plus rapidement.
Les threads sont aussi utilisés pour des attentes asynchrones dans les télécommunications.

## Threads et multitâche
Deux processus sont totalement indépendants et isolés l'un de l'autre. Ils ne peuvent interagir qu'à travers une API fournie par le système, telle qu'IPC. A l'inverse, les threads partagent une information sur l'état du processus, des zones de mémoires, ainsi que d'autres ressources. En fait, à part leur pile d’appel, des mécanismes comme le Thread Local Storage et quelques rares exceptions spécifiques à chaque implémentation, les threads partagent tout.
Puisqu'il n'y a pas de changement de mémoire virtuelle, la commutation de contexte (context switch) entre deux threads est moins coûteuse en temps que la commutation de contexte entre deux processus. On peut y voir un avantage de la programmation utilisant des threads multiples.

## Avantages et inconvénients
Dans certains cas, les programmes utilisant des threads sont plus rapides que des programmes séquentiels, en particulier sur les machines comportant plusieurs processeurs. Hormis le problème du coût de la commutation de contexte, le principal surcoût dû à l'utilisation de processus multiples provient de la communication entre processus séparés. En effet, le partage de ressources entre threads permet une communication plus efficace entre les différents threads d'un processus qu'entre deux processus distincts. Là où deux processus séparés doivent utiliser un mécanisme fourni par le système pour communiquer, les threads partagent une partie de l'état du processus, notamment sa mémoire. Dans le cas de données en lecture seule, il n'y a même pas besoin du moindre mécanisme de synchronisation pour que les threads utilisent les mêmes données.
La programmation utilisant des threads est toutefois plus rigoureuse que la programmation séquentielle, et l'accès à certaines ressources partagées doit être restreint par le programme lui-même, pour éviter que l'état d'un processus ne devienne temporairement incohérent, tandis qu'un autre thread va avoir besoin de consulter cette portion de l'état du processus. Il est donc obligatoire de mettre en place des mécanismes de synchronisation (à l'aide de sémaphores, par exemple), tout en conservant à l'esprit que l'utilisation de la synchronisation peut aboutir à des situations d'interblocage si elle est mal utilisée.
La complexité des programmes utilisant des threads est aussi nettement plus grande que celle des programmes déférant séquentiellement le travail à faire à plusieurs processus plus simples (la complexité est similaire dans le cas de plusieurs processus travaillant en parallèle). Cette complexité accrue, lorsqu'elle est mal gérée lors de la phase de conception ou de mise en œuvre d'un programme, peut conduire à de multiples problèmes tels que :

interblocages apparemment aléatoires :
si un algorithme est mal conçu et permet un interblocage, le changement de vitesse du processeur, par l'utilisation incomplète d'un quantum de temps alloué ou au contraire de la nécessité d'utiliser un quantum supplémentaire, peut provoquer la situation d'interblocage ;
de même, des périphériques plus ou moins rapides que ceux de la machine ayant servi à développer/tester le programme induisent des synchronisations temporellement différentes, et donc peuvent provoquer un interblocage non détecté auparavant ;
enfin, le changement de charge processeur de la machine (un programme lourd tournant en parallèle, par exemple) peut là aussi déclencher plus facilement des interblocages qui n'avaient pas été vus auparavant, avec l'illusion d'un phénomène aléatoire.
complexification inutile de certains algorithmes, qui ne bénéficient pas de la parallélisation du code mais qui sont pénalisés par des synchronisations d'accès aux ressources partagées :
sur-parallélisation du code alors qu'un traitement séquentiel serait plus adapté, la perte de temps liée à la commutation de contexte n'étant pas compensée par la parallélisation ;
Introduction de variables globales, forçant l'utilisation de synchronisation à outrance et donc des commutations de contexte inutiles.
sur-utilisation des mécanismes de synchronisation inadaptés là où ils ne sont pas nécessaires, induisant un surcoût de temps processeur inutile :
la mise en œuvre d'un pipeline FIFO entre deux threads seulement peut être effectuée facilement sans aucun mutex ;
utilisation d'une section critique au lieu d'un mutex lecteurs/rédacteur, par exemple lorsque beaucoup de threads lisent une donnée tandis que peu écrivent dedans ou qu'une donnée est plus souvent lue qu'écrite.

## Support des threads
### Systèmes d'exploitation
Les systèmes d'exploitation mettent généralement en œuvre les threads, souvent appelés threads système ou threads natifs (par opposition aux threads liés à un langage de programmation donné). Ils sont utilisés au travers d'une API propre au système d'exploitation, par exemple Windows API ou les Threads POSIX. En général, cette API n'est pas orientée objet, et peut être relativement complexe à bien mettre en œuvre car composée uniquement de fonctions primitives, ce qui demande souvent à avoir quelques notions sur le fonctionnement de l'ordonnanceur.
L'avantage des threads natifs est qu'ils permettent des performances maximales, car leur API permet de minimiser le temps passé dans le noyau et d'éliminer les couches logicielles inutiles. Leur principal inconvénient est, de par la nature primitive de l'API, une plus grande complexité de mise en œuvre.

### Langages de programmation
Certains langages de programmation, tels que Smalltalk et certaines implémentations de Java, intègrent un support pour les threads implémentés dans l'espace utilisateur (green threads (en)), indépendamment des capacités du système d'exploitation hôte.
La plupart des langages (Java sur la plupart des systèmes d'exploitation, C# .NET, C++, Ruby…) utilisent des extensions du langage ou des bibliothèques pour utiliser directement les services de multithreading du système d'exploitation, mais de façon portable. Enfin, des langages comme Haskell utilisent un système hybride à mi-chemin entre les deux approches. À noter que, pour des raisons de performances en fonction des besoins, la plupart des langages permettent d'utiliser au choix des threads natifs ou des green threads (notamment via l'utilisation de fibres). D'autres langages, comme Ada (langage), implémentent également un multitâche indépendant du système d'exploitation sans pour autant utiliser réellement le concept de thread.
Le C++, depuis la norme nommée C++11, possède aussi une bibliothèque standard de gestion des threads (inspirée de Boost) : le modèle de classe est std::thread. Celui-ci est simple d'utilisation, et permet de bien créer et exécuter ses threads. Auparavant, chaque framework devait implémenter sa propre surcouche de gestion des threads, en général câblée directement sur les threads natifs du système.

### Paradigmes de programmation
#### Programmation parallèle
En programmation parallèle, le principe de base est d'assurer la réentrance des entités logicielles utilisées par les threads, soit par conception (fonctions pures), soit par synchronisation (notamment par l'utilisation d'un mutex encadrant l'appel à la fonction).

#### Programmation procédurale
En programmation procédurale, on utilise le plus souvent directement les threads natifs du système d'exploitation. Leur utilisation est alors directement dépendante de l'API du système, avec ses avantages et inconvénients. Notamment, les fonctions utilisées par les threads doivent être réentrantes ou protégées par mutex.

#### Programmation orientée objet
En programmation orientée objet, l'utilisation des threads se fait en général par héritage depuis une classe mère (ou modèle de classe) générique, possédant une méthode virtuelle pure qui contiendra le code à exécuter en parallèle. Il faut et il suffit alors d'écrire la classe dérivée implémentant ce que l'on veut paralléliser, de l'instancier et d'appeler une méthode particulière (souvent nommée Run ou équivalent) pour démarrer le thread. Des méthodes d'arrêt ou d'attente de fin de tâche sont également présentes, simplifiant fortement la création de threads simples. Toutefois, des opérations plus complexes (barrière sur un nombre important de threads, réglages précis de priorité, etc.) peuvent être moins faciles qu'avec l'utilisation des threads natifs.
On parle de classe réentrante lorsque des instances distinctes d'une telle classe peuvent être chacune utilisées par des threads sans effet de bord, ce qui signifie en général une absence d'élément global ou statique dans l'implémentation de la classe. On parle aussi de classe thread-safe lorsque plusieurs threads peuvent utiliser une seule et même instance de cette classe sans engendrer de problèmes de concurrence. Une classe thread-safe est forcément réentrante, mais la réciproque est fausse.

#### Programmation fonctionnelle
Par nature, comme tout élément en programmation fonctionnelle est réentrant - et souvent thread-safe - à quelques rares exceptions près, la mise en œuvre des threads est fortement simplifiée par ce paradigme. En général, la parallélisation du code ne dépend que des contrats et des séquences d'appel : 
  
    
      
        f
        (
        g
        (
        x
        )
        )
      
    
    {\displaystyle f(g(x))}
  
 requiert bien entendu de calculer 
  
    
      
        y
        =
        g
        (
        x
        )
      
    
    {\displaystyle y=g(x)}
  
 avant 
  
    
      
        f
        (
        y
        )
      
    
    {\displaystyle f(y)}
  
, ce qui empêche de paralléliser les deux fonctions. Mais ces contraintes ne sont pas spécifiques à la programmation fonctionnelle, elles sont inhérentes à l'algorithme implémenté.

## Patrons de conception (design patterns) classiques avec les threads
Beaucoup de patrons de conception (patterns) peuvent bénéficier des threads, comme Decorator, Factory Method, Command ou encore Proxy. De manière générale, toute passation d'information à une entité logicielle d'un pattern peut faire l'objet de l'utilisation de threads.
Parmi les autres exemples classiques, on trouve :

les modèles maître-esclave et client-serveur :
un thread « maître » centralise le travail à faire et le distribue aux threads « esclaves », collectant ensuite leurs résultats ;
un pool de threads (le pool étant statique ou dynamique) permet d'interroger plusieurs serveurs sans bloquer le client ;
le Pair à pair (Peer-to-peer) est un modèle similaire au maître-esclave, mais où le thread maître n'est pas figé (chaque thread est le maître de tous les autres, tout en étant esclave lui-même).
un pipeline (« tube ») :
la tâche est découpée en diverses étapes successives et/ou opérations unitaires. Chaque thread réalise une des étapes et passe son résultat au suivant ;
plusieurs pipelines peuvent coexister afin d'accélérer encore le traitement ;
des traitements comme la compilation, le streaming, le traitement multimédia (décodage de vidéos par exemple) bénéficient fortement d'une implémentation utilisant des threads.

## Confusion possible
Il ne faut pas confondre la technologie Hyper-Threading de certains processeurs Intel avec les threads. Cette technologie permet en effet aussi bien l'exécution simultanée de processus distincts que de threads. Toute machine comportant des processeurs multiples (SMP) ou des processeurs intégrant l’Hyper-Threading permet aussi bien l'exécution plus rapide de programmes utilisant des threads que de multiples processus.

## Voir aussi
### Articles connexes
Fibre (informatique)

### Liens externes
(fr) Les threads
(en) Easythread bibliothèque C++ avec un exemple de fonctionnement simple des threads

## Références
 Portail de l’informatique   Portail de la programmation informatique
