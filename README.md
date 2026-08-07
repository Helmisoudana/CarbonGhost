# CarbonGhost Sentinel

## Le problème

Dans une usine, une machine peut consommer plus d'énergie que ce que sa
production réelle justifie, sans que personne ne le remarque. Quelques
exemples concrets :

- un moteur qui continue de tourner à vide entre deux cycles de
  production
- un réglage mal calibré qui fait consommer plus que nécessaire pour le
  même résultat
- une pièce mécanique qui s'use progressivement et force le moteur à
  compenser, sans qu'aucune alarme classique ne se déclenche
- une anomalie ponctuelle (pic de courant, vibration anormale) qui
  passe inaperçue au milieu du bruit normal de l'usine

Ce surplus de consommation a deux conséquences : un coût financier
direct, et une empreinte carbone qui aurait pu être évitée. Le problème
n'est pas l'absence de données — les machines modernes génèrent déjà
beaucoup de mesures — c'est l'absence d'un système qui **relie ces
mesures à une explication concrète et actionnable**. Un opérateur voit
des chiffres bruts, pas une cause, pas une recommandation.

## L'idée de la solution

CarbonGhost Sentinel transforme des mesures capteur brutes en une
chaîne de sens complète :

```
mesure brute → écart détecté → équivalent CO2 → cause probable → action recommandée
```

Le nom du projet vient de cette idée : traquer le "fantôme carbone" —
la part de consommation invisible, qui ne se voit ni sur une facture
globale ni sur un tableau de bord classique, mais qui existe bel et
bien, machine par machine, minute par minute.

Le système ne se contente pas de mesurer : il **compare** ce qui est
réellement consommé à ce qui aurait dû l'être pour la production
observée, **traduit** cet écart en CO2 évitable, **explique** la cause
la plus probable grâce à l'IA, et **propose** une action concrète à
l'opérateur — au lieu de le laisser seul face à un graphique.

## Les couches du projet

Le système est pensé comme une chaîne, où chaque couche transforme la
donnée un peu plus, jusqu'à devenir une information utilisable par un
humain.

### 1. La couche capteurs — le firmware ESP32

C'est le point de contact physique avec la machine. Un microcontrôleur
ESP32 est fixé sur ou près de la machine et mesure en continu des
grandeurs physiques : courant électrique, température, vibration,
pression. C'est la couche qui répond à la question *"qu'est-ce qui se
passe réellement, physiquement, sur cette machine, là maintenant ?"*

### 2. La couche passerelle — l'edge-gateway

Les ESP32 ne parlent pas directement à internet ou au backend — ils
publient leurs mesures en local via MQTT, un protocole léger conçu pour
des appareils avec peu de ressources. L'edge-gateway (sur un Raspberry
Pi) reçoit ces messages MQTT et fait le pont vers le reste du système.
C'est la couche qui répond à *"comment une mesure capteur, sur le
terrain, arrive jusqu'au reste du système ?"*

### 3. La couche ingestion — service-mesures

Premier service backend à recevoir la donnée. Il la valide, la structure
selon un format commun, et la republie dans le système via Kafka, pour
que d'autres services puissent la consommer sans dépendre directement de
la source. C'est la couche qui répond à *"comment rendre une mesure
disponible pour tout le système, de façon fiable ?"*

### 4. La couche calcul — service-carbone

Le cœur métier du projet. Ce service compare l'énergie réellement
consommée à l'énergie attendue pour le niveau de production observé, et
calcule l'écart en équivalent CO2 évitable. C'est la couche qui répond
à *"combien ce gaspillage représente-t-il réellement, en carbone ?"*

### 5. La couche intelligence — service-ia

Une fois l'écart détecté, cette couche va plus loin : elle cherche la
cause la plus probable (dérive progressive, anomalie ponctuelle, panne
naissante) à partir de modèles entraînés sur l'historique des machines,
et produit des prédictions sur l'évolution de la consommation. C'est la
couche qui répond à *"pourquoi ce gaspillage arrive-t-il ?"*

### 6. La couche interface humaine — service-assistant et dashboard

Un opérateur n'a pas le temps de lire des courbes brutes. Le dashboard
présente l'information de façon visuelle et priorisée ; l'assistant
conversationnel permet de poser des questions en langage naturel
("pourquoi la machine 3 a consommé plus hier ?") et d'obtenir une
réponse construite à partir des données réelles du système. C'est la
couche qui répond à *"comment un humain comprend et agit sur cette
information, sans expertise technique préalable ?"*

### 7. La couche gestion — service-factory

Garde la connaissance du contexte industriel : quelles machines
existent, où elles sont situées, à quelle ligne de production elles
appartiennent. Les autres services s'appuient sur cette couche pour
donner du sens aux identifiants de machine qu'ils manipulent. C'est la
couche qui répond à *"de quelle machine, concrètement, parle-t-on ?"*

### 8. La couche identité — service-user

Transverse à tout le reste : gère qui a le droit de voir quoi, et de
faire quoi, dans le système. Un opérateur, un responsable qualité, et un
administrateur n'ont pas les mêmes besoins d'accès. C'est la couche qui
répond à *"qui est autorisé à agir ici ?"*

## Ce qui rend l'ensemble cohérent

Chaque couche ne fait qu'une seule chose, et transmet un résultat plus
riche à la suivante. Une mesure de courant électrique brute, en sortant
d'un ESP32, ne veut presque rien dire seule. En traversant chaque
couche, elle devient progressivement : une donnée fiable et structurée,
un écart mesuré, un équivalent carbone, une cause probable, puis une
recommandation compréhensible par un opérateur qui n'a jamais vu une
ligne de code.

C'est cette transformation progressive, couche par couche, qui est le
véritable objet du projet — pas la donnée capteur en elle-même, mais le
sens qu'on parvient à en extraire.
