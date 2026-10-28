# Interblocage

Un interblocage (ou étreinte fatale, deadlock en anglais) est un phénomène qui peut survenir en programmation concurrente. L'interblocage se produit lorsque des processus concurrents s'attendent mutuellement. Un processus peut aussi s'attendre lui-même. Les processus bloqués dans cet état le sont définitivement, il s'agit donc d'une situation catastrophique. Les mécanismes conduisant aux phénomènes d'interblocage ont été étudiés principalement par Edward G. Coffman Jr. (en).

## Conditions nécessaires
Une situation de blocage sur une ressource peut survenir si et seulement si toutes les conditions suivantes sont réunies simultanément dans un système:

Exclusion mutuelle : Au moins une ressource doit être conservée dans un mode non partageable. Sinon, les processus ne seraient pas empêchés d'utiliser la ressource si nécessaire. Un seul processus peut utiliser la ressource à un instant donné.
Hold and wait ou resource holding : un processus détient actuellement au moins une ressource et demande des ressources supplémentaires qui sont détenues par d'autres processus.
Non préemption : une ressource ne peut être libérée que volontairement par le processus qui la détient.
Attente circulaire : chaque processus doit attendre une ressource qui est détenue par un autre processus, qui à son tour attend que le premier processus libère la ressource. En général, il existe un  ensemble de processus en attente, P = {P1, P2,…, PN}, tel que P1 attend une ressource détenue par P2, P2 attend une ressource détenue par P3.
Ces quatre conditions sont connues sous le nom de «conditions de Coffman» d'après leur première description dans un article de 1971 par Edward G. Coffman Jr. (en).
Bien que ces conditions soient suffisantes pour produire un blocage sur les systèmes de ressources à instance unique, elles indiquent uniquement la possibilité d'un blocage sur les systèmes ayant plusieurs instances de ressources.

## Exemples
Un exemple concret d'interblocage peut se produire lorsque deux processus légers (thread en anglais) essayent d'acquérir deux mutex dans un ordre différent. Par exemple avec deux mutex (M1 et M2), deux processus légers (P1 et P2) et la séquence d'opération suivante : 

P1 acquiert M1.
P2 acquiert M2.
P1 attend pour acquérir M2 (qui est détenu par P2).
P2 attend pour acquérir M1 (qui est détenu par P1).
Dans cette situation, les deux processus légers sont définitivement bloqués.

## Évitement
Les interblocages peuvent être évités si certaines informations sont connues à l'avance lors des allocations de ressources. Pour chaque allocation de ressources, le système regarde s'il va entrer dans un état « non sûr », c'est-à-dire un état qui pourrait engendrer un interblocage. Le système ne répond favorablement qu'aux requêtes qui mènent à des états « sûrs ». Pour être capable de décider si l'état suivant sera sûr ou non sûr, le système a besoin de connaître à tout moment le nombre et le type de ressources existantes, disponibles et demandées. Un algorithme classique permettant la détection des interblocages à l'avance est l'algorithme du banquier. Celui-ci nécessite de connaître à l'avance les limites d'utilisation des ressources. Toutefois, pour beaucoup de systèmes, il est impossible de connaître à l'avance les demandes de chaque processus. Cela implique que l'évitement des interblocages est souvent impossible.
Les algorithmes Attente/Mort (Wait/Die) et Blessé/Attente (Wound/Wait) sont deux autres méthodes d'évitement qui utilisent une technique de rupture de la symétrie. Dans ces deux algorithmes on prend en compte l'âge des processus et l'on distingue un processus âgé (A) et un processus jeune (J).
L'âge d'un processus peut être déterminé par horodatage (timestamp en anglais) lors de sa création. Les dates les plus petites appartiennent à des processus plus âgés, les plus grandes à des processus plus jeunes.

Il est important de se rendre compte qu'un processus peut être dans un état non sûr sans pour autant forcément conduire à un interblocage. La notion d'état sûr et non sûr fait uniquement référence à la possibilité que le système entre dans un interblocage ou non. Par exemple, si un processus fait une requête sur une ressource A qui aboutit à un état non sûr, mais libère une ressource B pour éviter une attente circulaire, alors l'état est non sûr mais le système n'est pas en interblocage.

## Prévention
Une méthode consiste à toujours acquérir les mutex dans le même ordre. En effet, si plusieurs processus légers nécessitent d'acquérir plusieurs verrous pour effectuer leur travail, s'ils acquièrent les verrous dans un ordre différent, il est possible qu'ils se bloquent lors de la séquence d'acquisition (comme dans l'exemple précédent).
Il convient aussi de s'intéresser aux priorités des processus. En effet, si par exemple un processus de haute priorité utilise un verrou en commun avec un processus de basse priorité (voir aussi inversion de priorité), il est possible d'obtenir des situations de blocage. Une solution à ce genre de problème consiste à n'utiliser des verrous qu'entre des processus de même priorité.

## Notes et références
## Bibliographie
Programmation concurrente et temps réel avec ADA 95, Luigi Zaffalon, Pierre Breguet, Presses polytechniques et universitaires romandes, Lausanne, 1999.
Confirmation of Deadlock Potentials Detected by Runtime Analysis, Saddek Bensalem, Jean-Claude Fernandez, Klaus Havelund, Laurent Mounier, Portland (Maine), 2006.

 Portail de l’informatique
