Simulation homme ivre
=====================

Introduction
------------

Une usine de cadres de vélos souhaiterait voir son chiffre d’affaires 
augmenter sans pour autant accroitre sa production. Les produits finis étant
largement plus rentables, le gérant de l’entreprise s’est alors tourné vers la
solution de vendre ses propres vélos. Dans ses projets, il prévoit d’acquérir
une unité de montage. Il y aura alors une zone d’entreposage de kits de pièces
détachées (guidons, dérailleurs, roues, etc.), un poste d’assemblage, une zone
d’entreposage et d’expéditions des vélos.  
Voici un schéma des installations :

DESSIN

Nous disposons des renseignements initiaux suivants :
L’usine de cadres fonctionne de 8h à 11h et de 13h à 16h chaque jour de
la semaine, incluant les week-ends.

* Les cadres sont construits au rythme de 2 par minutes,
* Il faut 10 min pour que les cadres atteignent le poste d’assemblage,
* Le design de la chaîne initiale peut contenir 88 cadres,
* Il y a une livraison de kits à 7h et une 11h.

Nous allons créer une application de simulation pour répondres aux questions
suivantes :

* Quelles seront les tailles des zones d’entreposage,
* À quelle fréquence peut-on expédier (un camion contient 420 vélos) ?
* Est-ce que 88 places sur la chaîne est adéquat ?
* Quel est le rythme de production du poste s’assemblage pour
  avoir un procédé fluide ?

La programmation de l’outil
---------------------------
**Les horaires**

La description précédente permet d’isoler trois horaires différents
sachant qu’ils possèdent le point commun d’être journalier.

* Le premier est lié aux ouvertures de l’usine de cadres sur deux plages de
  3 heures : 8 à 11 et 13 à 16. Elle ne sera pas ouverte au début de la
  simulation, car cette dernière commence le lundi à 6 heures.
* Le second est lié à l’assemblage des kits avec les cadres. j'ai
  supposé que l’usine tournerait sans interruption, même s’il est rare que
  ce soit le cas dans les entreprises de petit format.
* Enfin, le dernier s’articule autour des deux livraisons de kits qui sont faites
  tous les jours à 7h et à 11h. Comme ce sont des événements ponctuels
  journaliers, l’état par défaut est inactif.

Pour ces horraires j'ai utilisé des objets `journee` contenant les horraires
des trois zones de productions


Le schéma initial laisse transparaître un graphe. Conséquemment,
Je suis partis des classes `Noeud` et `Arete` du fichier « flux.py » en
les héritant pour satisfaire nos exigences.

**Les noeuds du graphe**

L’arrivée des kits est un objet nommé `NoeudReceptionCamion`.
À travers notre problème , on comprend que lorsqu’un camion arrive, il 
décharge sa marchandise dans l’entrepôt s’il contient assez de place et repart
directement (fonction d’évacuation). Le noeud passe donc instantanément
de l’état actif à passif après avoir déchargé la marchandise. Dans le cas
où l’entrepôt serait plein, on ne décharge rien jusqu’à la prochaine
livraison. Si lors de la prochaine livraison, il est de même alors la
marchandise est considérée comme perdue (fonction d’envoi de matériel
d’un coup).  
temps de traitement lié au déchargement d’un camion n'est pas intégré car lorsqu’un produit sort du véhicule, il est déjà considéré
comme faisant partie de l’unité d’assemblage et donc de l’entrepôt.

L’usine des cadres est un objet nommé `NoeudUsineCadre`. Le
traitement (fonction de traitement) du matériel se produit lorsque l’usine
est en marche et qu’il y a encore du matériel produit par l’usine. Dans le
cas où l’usine a produit plus de matériel qu’il n’a pu être mis sur la chaîne
alors on n’en déverse pas à l’intérieur (fonction d’évacuation). Ce surplus
est considéré comme perdu.
L’usine produit deux cadres par minutes, sa période (`periode_usine_cadre`)
est donc égale à 30 secondes par cadres.

L’usine d’assemblage est un `Noeud` qui possède une période
(`periode_assemblage`) à déterminer à travers la simulation.


Enfin, la partie d’expédition des produits finis est un noeud
`NoeudEnvoiCamion`. Il est construit de telle manière à ce que
lorsque les arêtes entrantes atteignent un certain niveau (`taille lot`), on
évacue le matériel par camion. De plus, le temps de chargement des vélos
dans un camion égal à 1 heure.



**Les arêtes du graphe**

La chaîne est un `AreteTr`, qui correspond à un espace de stockage avec un
temps de transite. EN effet  il y a un temps de dix minutes entre l'usine de
cadre et la zone d'assemblage.
Cette chaîne contiendra un nombre maximum d’emplacements (`taille_chaine`) parametrable.
La chaine continue de transférer des cadre, meme si l'usine est
férmé dans le cas ou l'usine d'assemblage est toujours ouverte.

Les autres arêtes sont des objets `Arete` où leur capacité maximale est
contenue dans les variables `t_entrepot_kits` et `arete_Inf`. Elles
matérialisent les différents entrepôts.


Les différentes variables que l'on peut modifier sont centralisées dans 
la classe `Data`. Cela permet d'avoir toutes les variables au meme endroit 
pour tester nos hypothèses.


Cas d’études
------------
Il est donc obligatoire d’épuiser la totalité de ces kits pour éviter de 
surcharger l’entrepôt. En effet, si l’on produit moins de 720 vélos par jour
alors il restera des éléments dans l’entrepôt et quelle que soit sa taille, il
finira par être plein; tout en sachant que le but premier d’une entreprise
est de faire un maximum d’argent.  
Partons du postulat initial que l’usine d’assemblage tourne en tout temps
et sans interruption. Par conséquent, en 23 heures elle devra utiliser les
720 kits pour produire 720 vélos, car les livraisons se font une heure avant
l’ouverture de l’usine de cadres.  
On voudrait connaitre la vitesse de production de cette usine, la contenance
maximale de la chaine et de l’entrepôt des kits dans ces conditions.
L’usine d’assemblage ne recevrait donc qu’à 8h12 ses premiers cadres, car le
temps nécessaire pour écouler les kits est supérieur au temps d’écoulement des
cadres qui n’est que de 22h50 (115s~2 min). Nous avons donc :

    periode_usine_cadre = 30
    periode_assemblage = (23*3600-10*60-(23*3600)/720)/720
    t_entrepot_kits = arete_Inf
    taille_chaine = arete_Inf

Il suffit maintenant d’afficher les contenances en temps réel de chaîne et 
l’entrepôt des kits pour déterminer les maximums, ce qui donne :

    t_entrepot_kits = 473
    taille_chaine = 631

On explique ces résultats sur la chaine, entre 8h12 et 11h00, on ne peut
qu’utiliser
    (3 * 60 * 60−10 * 60−periode_assemblage)/periode_assemblage ~ 89 kits
Il est donc normal qu’à 11h il faille 360−89360=631 places.

De plus, de 8h12 à 13h00, on ne peut utiliser que
    (5 * 60 * 60−10 * 60−periode_assemblage) / periode_assemblage ~ 152 cadres 

De 13h à 16h, on ne peut utiliser que 
    (3 * 3600) / periode_assemblage ~ 95 cadres.
Donc, il est normal qu’il faille 360−152360−95=473 places.

On peut donc conclure que sous ses conditions, l'usine produit un vélo en 114
secondes, qu’il faudra **473 places sur la chaîne** et 
**631 places dans l’entrepôt** des kits.
Sous cette fréquence, on enverra un le premier camion partir
à 22h31 le jour même et un le lendemain à 13h00, il faut 114 * 420/60 = 798
minutes, soit 13h18 et une heure de chargement pour la première fois.
La zone d’entreposage de l’expédition devra contenir au minimum **452**
**emplacements**, car en 1h on a eu le temps de produire 52 vélos. 

Prenons la situation suivante : on souhaite que la chaîne ne fonctionne que
dans les horaires d’ouverture de l’usine et que l’usine d’assemblage
fonctionne tout le temps. Il va donc falloir calculer le nombre de places
maximum dans cette chaîne et dans l’entrepôt de kits. Il faudra aussi trouver
la fréquence d’assemblage afin de déterminer les horaires des camions. 

La chaîne transmet un cadre en 10 min, elle ne peut donc pas envoyer les 360
cadres, mais seulement (180−10) * 2 = 340 cadres en 3 heures. Elle doit donc
rester ouverte au minimum de 8h à 11h10 et de 13h à 16h10 et l’usine
d’assemblage peut seulement rester ouverte de 8h10 à 11h10 et de 13h10 à 16h10
sous condition que le temps d’assemblage soit nul. Ces conditions ne reflètent
pas la réalité, il est donc inutile de continuer ce raisonnement. 

Enfin, J'ai testé pour une chaîne de 88 emplacements et demandé à 
l'application de trouver la période approximative d’assemblage pour un vélo.
La période est d’environ **37.2 secondes** pour construire un vélo.
Le nombre maximum d’emplacements dans l’entrepôt des kits est de 
**449 emplacements**. Le premier camion partira à 14h49, l’entrepôt devra 
contenir **519 emplacements** pour anticiper le prochain camion.


Conclusion déterministe
-----------------------
J'ai approximé le temps d’assemblage d’un vélo par une personne à 20 min.
Comme vous avez pu le lire, les variables dépendent énormément de ce que le
gérant de l'entreprise souhaite. Au travers des cas limites, j'ai tenté
d’étudier le comportement de la vitesse de production afin de maximiser la
productivité. On remarque qu’elle est bornée par la vitesse d’arrivées des 
kits et la vitesse d’envoi des cadres sur la chaîne où 10 minutes séparent
l’usine de cadre et d’assemblage. En effet, il faut au minimum 20 secondes 
pour faire un vélo et au maximum 114 secondes pour que les cadres arrivent.

Ces résultats ne reflètent pas la réalité, car ils sont bien inférieurs à 20
minutes, mais notre programme ne prend pas en compte le nombre d’employés de
l’entreprise. Lorsqu’ils travailleront en parallèle, cela décroit assurément
le nombre de secondes nécessaire pour assembler un vélo en moyenne. 
On comprend donc qu’il faudra au minimum 11 employés pour atteindre les 114
secondes minimum (le modèle parallélisme est grossier).

On peut noter que le temps d’ouverture de chaque ensemble, les livraisons et
la contenance des entrepôts dépendent alors largement du choix de la cadence
de production. Une autre alternative, toujours dans le but de maximiser la
production aurait pu être de décupler le nombre de chaines ou d’arrivées
de kits. 



