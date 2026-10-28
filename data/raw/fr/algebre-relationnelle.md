# Algèbre relationnelle

En informatique, plus précisément en théorie des bases de données relationnelles, l'algèbre relationnelle est un langage de requêtes, inventé en 1970 par Edgar Frank Codd, directeur de recherche du centre IBM de San José.
Il s'agit de la théorie sous-jacente aux langages de requête des SGBD, comme SQL. Le théorème de Codd dit que l'algèbre relationnelle est équivalente au calcul relationnel, c'est-à-dire la logique du premier ordre, mais sans les symboles de fonction.
Elle est aussi équivalente à Datalog¬ (Datalog avec la négation) non récursif. Datalog est un langage de requête et de règles pour les bases de données déductives (en).
Selon Abiteboul et al., l'algèbre relationnelle est conceptuellement un langage "procédural" : en effet, les requêtes sont des suites d'opérations qui construisent la réponse.
Cela s'oppose aux langages conceptuellement "déclaratifs" comme le calcul relationnel et Datalog.

## Modèle relationnel
Dans le modèle relationnel, les données sont stockées dans des tables, aussi appelées relations. Voici un exemple de relation :

Plus précisément, une relation (au sens du modèle de Codd) est constituée :

d'un schéma, c'est-à-dire l'ensemble des noms des champs (ici Clé, Nom, Email), et des types correspondants (dans l'exemple respectivement, un nombre entier, puis deux chaînes de caractères).
d'une extension, c'est-à-dire le contenu de la table, qui est un ensemble de n-uplets (dont l'ordre n'a pas d'importance). Chacun des n-uplets s'appelle un enregistrement.

## Définition
Le langage procédural de l'algèbre relationnel contient les opérations ensemblistes de la théorie des ensembles sur les relations ainsi que des opérations pour fusionner/projeter des relations.

### Opérateurs ensemblistes
Les opérateurs ensemblistes sont l'union, l'intersection, la différence et le produit cartésien.

#### Union
L'union de deux relations sur le même schéma est la relation sur ce schéma contenant exactement l'union des enregistrements de ces deux relations. Formellement, l'union des relations 
  
    
      
        R
      
    
    {\displaystyle R}
  
 et 
  
    
      
        S
      
    
    {\displaystyle S}
  
 est  
  
    
      
        R
        ∪
        S
        =
        {
        t
        :
        t
        ∈
        R
         
        o
        u
         
        t
        ∈
        S
        }
        
      
    
    {\displaystyle R\cup S=\{t:t\in R\ ou\ t\in S\}\,}
  
.

#### Intersection
L'intersection de deux relations sur le même schéma est la relation sur ce schéma contenant exactement les enregistrements qui apparaissent dans les deux relations. Formellement, l'intersection des relations 
  
    
      
        R
      
    
    {\displaystyle R}
  
 et 
  
    
      
        S
      
    
    {\displaystyle S}
  
 est  
  
    
      
        R
        ∩
        S
        =
        {
        t
        :
        t
        ∈
        R
         
        e
        t
         
        t
        ∈
        S
        }
        
      
    
    {\displaystyle R\cap S=\{t:t\in R\ et\ t\in S\}\,}
  
.

#### Différence
La différence de deux relations sur le même schéma est la relation sur ce schéma contenant exactement les enregistrements qui apparaissent dans la première relation mais pas dans la deuxième. Formellement, la différence des relations 
  
    
      
        R
      
    
    {\displaystyle R}
  
 et 
  
    
      
        S
      
    
    {\displaystyle S}
  
 est 
  
    
      
        R
        −
        S
        =
        {
        t
        :
        t
        ∈
        R
         
        e
        t
         
        t
        ∉
        S
        }
        
      
    
    {\displaystyle R-S=\{t:t\in R\ et\ t\not \in S\}\,}
  
. Par exemple, on peut calculer les personnes inscrits en football mais qui ne sont pas inscrits en cours de piano :

#### Produit cartésien
Avec le produit cartésien de deux relations, on recopie chaque tuple de la première relation pour chacun des tuples de la deuxième. Formellement, le produit cartésien des relations 
  
    
      
        R
      
    
    {\displaystyle R}
  
 et 
  
    
      
        S
      
    
    {\displaystyle S}
  
 est 
  
    
      
        R
        ×
        S
        =
        {
        (
        r
        ,
        s
        )
        :
        r
        ∈
        R
         
        e
        t
         
        s
        ∈
        S
        }
      
    
    {\displaystyle R\times S=\{(r,s):r\in R\ et\ s\in S\}}
  
.

### Opérateurs relationnels
#### Sélection
La sélection (ou restriction[réf. nécessaire]) consiste à ne retenir que les enregistrements vérifiant une condition donnée. Dans l'exemple plus bas, on ne garde que les touristes dont la ville est Paris.

Données : Une relation 
  
    
      
        R
        
      
    
    {\displaystyle R\,}
  
 et une formule 
  
    
      
        F
        
      
    
    {\displaystyle F\,}
  
 formée d'une combinaison de comparaisons et de connecteurs logiques.
Résultat : 
  
    
      
        
          σ
          
            F
          
        
        (
        R
        )
        =
        {
        r
        ∈
        R
        :
        r
        
      
    
    {\displaystyle \sigma _{F}(R)=\{r\in R:r\,}
  
 satisfait la condition donnée par 
  
    
      
        F
        }
        
      
    
    {\displaystyle F\}\,}
  
, dans l'exemple 
  
    
      
        
          σ
          
            V
            i
            l
            l
            e
            
              =
              ′
            
            P
            a
            r
            i
            
              s
              ′
            
          
        
        (
        
      
    
    {\displaystyle \sigma _{Ville='Paris'}(\,}
  
Touristes
  
    
      
        )
        
      
    
    {\displaystyle )\,}
  

Équivalent SQL : WHERE

#### Projection
La projection permet de ne garder que certains attributs. Dans l'exemple ci-dessous, on ne garde que les attributs NomT et Ville de la relation Touristes.

Données : Une relation 
  
    
      
        R
        
      
    
    {\displaystyle R\,}
  
 et un ensemble d'attributs 
  
    
      
        A
        
      
    
    {\displaystyle A\,}
  
 de 
  
    
      
        R
        
      
    
    {\displaystyle R\,}
  

Résultat : 
  
    
      
        
          π
          
            A
          
        
        (
        R
        )
        
      
    
    {\displaystyle \pi _{A}(R)\,}
  
, qui est la Relation 
  
    
      
        R
        
      
    
    {\displaystyle R\,}
  
 où on ne considère que les attributs de 
  
    
      
        A
        
      
    
    {\displaystyle A\,}
  
, par exemple  
  
    
      
        
          π
          
            N
            o
            m
            T
            ,
            V
            i
            l
            l
            e
          
        
        (
        
      
    
    {\displaystyle \pi _{NomT,Ville}(\,}
  
Touristes
  
    
      
        )
        
      
    
    {\displaystyle )\,}
  

Équivalent SQL : SELECT

#### Renommage
Le renommage consiste à renommer un attribut d'une table.

Données : Une relation 
  
    
      
        R
        
      
    
    {\displaystyle R\,}
  
 et un attribut 
  
    
      
        b
        
      
    
    {\displaystyle b\,}
  
 de 
  
    
      
        R
        
      
    
    {\displaystyle R\,}
  

Résultat : 
  
    
      
        
          ρ
          
            a
            
              /
            
            b
          
        
        (
        R
        )
        
      
    
    {\displaystyle \rho _{a/b}(R)\,}
  
, qui est la Relation 
  
    
      
        R
        
      
    
    {\displaystyle R\,}
  
 avec 
  
    
      
        b
        
      
    
    {\displaystyle b\,}
  
 renommé 
  
    
      
        a
        
      
    
    {\displaystyle a\,}
  

Équivalent SQL : AS

#### Jointure
La jointure de deux relations consiste à regrouper les deux tables, comme un produit cartésien, mais en identifiant les attributs communs. La jointure peut s'exprimer à l'aide d'un produit cartésien, d'une sélection et d'une projection (cf. Définition 14.35 dans ).

Données : deux relations 
  
    
      
        R
        
      
    
    {\displaystyle R\,}
  
 et 
  
    
      
        S
      
    
    {\displaystyle S}
  

Résultat : 
  
    
      
        R
        ⋈
        S
        =
        {
        (
        a
        ,
        b
        ,
        c
        )
        :
        (
        a
        ,
        b
        )
        ∈
        R
         
        e
        t
         
        (
        b
        ,
        c
        )
        ∈
        S
        }
        
      
    
    {\displaystyle R\bowtie S=\{(a,b,c):(a,b)\in R\ et\ (b,c)\in S\}\,}
  

Équivalent SQL : JOIN

#### Division
La division prend en entrée deux relations 
  
    
      
        R
        (
        
          x
          
            1
          
        
        ,
        .
        .
        .
        ,
        
          x
          
            m
          
        
        ,
        
          y
          
            1
          
        
        ,
        .
        .
        .
        ,
        
          y
          
            p
          
        
        )
        
      
    
    {\displaystyle R(x_{1},...,x_{m},y_{1},...,y_{p})\,}
  
 et 
  
    
      
        S
        (
        
          y
          
            1
          
        
        ,
        .
        .
        .
        ,
        
          y
          
            p
          
        
        )
        
      
    
    {\displaystyle S(y_{1},...,y_{p})\,}
  
.
Ainsi, tout n-uplet 
  
    
      
        r
        ∈
        R
        
      
    
    {\displaystyle r\in R\,}
  
 se décompose en deux n-uplets 
  
    
      
        r
        =
        (
        t
        ,
        s
        )
        
      
    
    {\displaystyle r=(t,s)\,}
  
, avec 
  
    
      
        t
        =
        (
        
          t
          
            1
          
        
        ,
        .
        .
        .
        ,
        
          t
          
            m
          
        
        )
        
      
    
    {\displaystyle t=(t_{1},...,t_{m})\,}
  
 de schéma 
  
    
      
        X
        =
        {
        
          x
          
            1
          
        
        ,
        .
        .
        .
        ,
        
          x
          
            m
          
        
        }
        
      
    
    {\displaystyle X=\{x_{1},...,x_{m}\}\,}
  
 et 
  
    
      
        s
        =
        (
        
          s
          
            1
          
        
        ,
        .
        .
        .
        ,
        
          s
          
            p
          
        
        )
        
      
    
    {\displaystyle s=(s_{1},...,s_{p})\,}
  
 de schéma 
  
    
      
        y
        =
        {
        
          y
          
            1
          
        
        ,
        .
        .
        .
        ,
        
          y
          
            p
          
        
        }
        
      
    
    {\displaystyle y=\{y_{1},...,y_{p}\}\,}
  
. et retourne la table de schéma 
  
    
      
        X
        
      
    
    {\displaystyle X\,}
  
 tel que 
  
    
      
        R
        
          /
        
        S
        =
        {
        t
        :
        ∀
        s
        ∈
        S
        ,
         
        (
        t
        ,
        s
        )
        ∈
        R
        }
        
      
    
    {\displaystyle R/S=\{t:\forall s\in S,\ (t,s)\in R\}\,}
  
. La division revient à donner “tous les x tels que pour tout y...”

## Théorèmes de Codd
L'algèbre SPC (sélection, projection et produit cartésien) correspond au calcul conjonctif (calcul relationnel sans disjonction et sans négation) : c'est une des versions du théorème de Codd (section 14.4.1 dans ). L'algèbre SPCU- (l'algèbre SPC avec en plus l'union et la différence) correspond au calcul relationnel en entier : c'est une autre version du théorème de Codd (section 14.4.2 dans ).

## Optimisation
Voici des règles de réécriture pour transformer une expression de l'algèbre relationnelle en une autre expression équivalente.

## Implémentation
Cependant, les bases de données relationnelles ne fonctionnent pas tout à fait selon les règles ensemblistes de l'algèbre relationnelle. En effet, si l'on ne définit pas de clé primaire, il est possible d'insérer plusieurs lignes identiques dans une table, ce qui d'un point de vue ensembliste n'a pas de sens : un élément fait partie ou ne fait pas partie d'un ensemble. Si l'on veut appliquer strictement les règles des ensembles, il faut vérifier à chaque ajout dans une table que les lignes introduites ne sont pas déjà présentes.

### Objets précis du modèle
Il s'agit ici de déterminer des Domaines (i.e., type atomique) :

Numérique : entier ou réel (SQL : Int, Float, etc.) ;
Chaîne de caractères (SQL : Char(20), VarChar(32), etc.) ;
Date (SQL : DATE, TIME, YEAR, etc.) ;
Type énuméré.

## Notes et références
## Voir aussi
Système de gestion de base de données
Algèbre
Théorie des ensembles
Base de données
Base de données relationnelle

### Liens externes
RAT, Software Rational Algebra Translator to SQL
(fr) Laurent Audibert, « Bases de données relationnelles », sur developpez.com
 Portail des bases de données   Portail des mathématiques
