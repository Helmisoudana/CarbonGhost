# Architecture — CarbonGhost Sentinel

Ce document explique les deux niveaux d'architecture utilisés dans le
projet :

1. **Microservices** — comment le système entier est découpé (niveau
   "vue d'ensemble")
2. **Hexagonale** — comment chaque service, individuellement, est
   organisé en interne (niveau "intérieur d'un service")

Les deux se combinent : CarbonGhost Sentinel est un **système
microservices**, où **chaque microservice** est construit en
**architecture hexagonale**.

---

## 1. Qu'est-ce qu'une architecture microservices ?

### Le principe

Au lieu d'écrire une seule grosse application qui fait tout (un
"monolithe"), on découpe le système en **plusieurs petits programmes
indépendants**, chacun responsable d'une seule chose, qui communiquent
entre eux par le réseau (HTTP, ou via un broker de messages comme
Kafka).

Chaque microservice :
- a son propre code, son propre dépôt logique (ici : son propre dossier)
- a sa propre base de données (personne d'autre n'y touche directement)
- peut être développé, testé, déployé et redémarré **indépendamment**
  des autres
- communique avec les autres uniquement via des interfaces définies à
  l'avance (API REST, événements Kafka)

### Monolithe vs microservices

| | Monolithe | Microservices |
|---|---|---|
| Structure | un seul programme, un seul déploiement | plusieurs programmes indépendants |
| Développement en équipe | tout le monde touche le même code → conflits fréquents | chacun travaille dans son service, peu de conflits |
| Panne | un bug peut faire planter toute l'application | un service qui plante n'arrête pas les autres |
| Scalabilité | on doit dupliquer toute l'application pour tenir la charge | on peut dupliquer uniquement le service qui en a besoin |
| Complexité | simple au début, difficile à faire grossir | plus complexe à mettre en place, mais tient mieux dans le temps |

### Pourquoi ce choix pour CarbonGhost Sentinel

Le projet a des responsabilités très différentes (authentification,
lecture de capteurs, calcul carbone, IA, assistant conversationnel,
gestion d'usine) et une équipe de 3 personnes qui doit avancer **en
parallèle**. Les microservices permettent :

- à Salma de coder `service-assistant` sans toucher au code de Helmi
- à `service-ia` de planter sans arrêter `service-user`
- de ne dupliquer, plus tard, que le service qui reçoit le plus de
  trafic (probablement `service-mesures`)

### Les microservices du projet

| Service | Responsabilité |
|---|---|
| `service-user` | authentification, gestion des comptes, JWT |
| `service-mesures` | réception des données capteurs (MQTT → Kafka) |
| `service-carbone` | calcul des événements carbone à partir des mesures |
| `service-ia` | détection d'anomalies, prédictions énergie |
| `service-assistant` | assistant conversationnel (LLM) |
| `service-factory` | gestion des machines et de l'usine |

### Comment les services communiquent

Deux modes, selon le besoin :

- **Synchrone (HTTP/REST)** — quand un service a besoin d'une réponse
  immédiate. Ex: le dashboard appelle `service-user` pour vérifier un
  login.
- **Asynchrone (Kafka)** — quand un service produit un événement que
  d'autres consomment sans réponse immédiate attendue. Ex:
  `service-mesures` publie une mesure, `service-carbone` la consomme
  quand il le peut, sans que `service-mesures` attende quoi que ce soit.

```
                     HTTP (synchrone)
   dashboard  ─────────────────────────▶  service-user
                                               │
                                               │ vérifie JWT
                                               ▼
   ESP32 ──MQTT──▶ edge-gateway ──▶ service-mesures
                                               │
                                    Kafka (asynchrone)
                                               ▼
                                       service-carbone
                                               │
                                    Kafka (asynchrone)
                                               ▼
                                          service-ia
```

### Comment on construit un projet microservices, étape par étape

1. **Définir les contrats avant le code** — les schémas de données
   échangées entre services (`shared/contracts/`). Sans ça, chaque
   service invente son propre format et rien ne s'assemble.
2. **Découper par responsabilité métier**, pas par couche technique. Un
   service = un domaine métier cohérent (ex: "tout ce qui concerne le
   carbone"), jamais "tout ce qui est base de données".
3. **Standardiser la structure interne** de chaque service (d'où le
   générateur) pour que n'importe qui puisse naviguer dans n'importe
   quel service.
4. **Démarrer par le service dont tous les autres dépendent**
   (`service-user`, pour l'authentification) avant les services métier.
5. **Faire communiquer les services** via API REST ou Kafka, jamais en
   important directement le code d'un autre service.
6. **Orchestrer le tout** avec Docker Compose, pour que le système
   entier démarre de façon identique chez tout le monde.
7. **Chaque service reste testable seul**, avec de fausses dépendances
   (repository en mémoire, etc.) — pas besoin que les 6 autres services
   tournent pour tester la logique d'un seul.

---

## 2. Qu'est-ce que l'architecture hexagonale ?

### Le problème qu'elle résout

Sans discipline, le code métier finit par appeler directement Postgres,
ou directement FastAPI, un peu partout. Résultat :

- impossible de tester la logique métier sans une vraie base de données
- changer d'outil technique (Postgres → MongoDB, REST → GraphQL) oblige
  à réécrire une partie du métier
- le code métier et le code technique sont mélangés, difficile à lire

### Le principe : ports et adaptateurs

L'idée centrale : **le métier ne doit jamais dépendre de la technique.**
C'est l'inverse qui doit être vrai : la technique dépend du métier.

On y arrive avec deux notions :

- **Un port** — une interface définie par le domaine. Elle dit "j'ai
  besoin de sauvegarder un utilisateur" sans jamais dire comment.
- **Un adaptateur** — l'implémentation concrète d'un port. Ex: un
  adaptateur Postgres qui implémente réellement la sauvegarde en SQL.

Le domaine ne connaît que les ports (des interfaces abstraites). Il ne
sait jamais si, derrière, il y a Postgres, une base en mémoire pour les
tests, ou autre chose.

### Schéma des 4 couches

```
        api/            (adaptateur d'ENTRÉE : reçoit une requête HTTP)
              │
              ▼
     application/        (use cases : orchestre la logique métier)
              │
              ▼
        domain/           (entités + ports : le métier pur, isolé)
              ▲
              │
   infrastructure/       (adaptateur de SORTIE : Postgres, Kafka, MQTT...)
```

Le mot "hexagonale" vient de la représentation habituelle du domaine
comme un hexagone central, entouré d'adaptateurs branchés sur chacune de
ses faces. Le nombre de côtés n'a pas d'importance réelle — seule compte
l'idée : le domaine au centre, isolé, entouré d'adaptateurs
interchangeables.

### Le rôle de chaque dossier

#### `domain/` — le cœur métier, zéro dépendance technique

- **`entities/`** — les objets métier (ex: `User`, `CarbonGhostEvent`).
  Données + règles, rien de plus. Aucun import de FastAPI, aucun import
  de Postgres.
- **`ports/repositories/`** — les interfaces (ex: `IUserRepository`
  avec une méthode `save(user)`). Le domaine décrit ce qu'il veut, pas
  comment c'est fait.
- **`exceptions/`** — les exceptions métier communes
  (`NotFoundException`, `ValidationException`, etc.), qui remontent
  jusqu'à `container.py` pour être transformées en réponse HTTP.

#### `application/` — l'orchestration

- **`use_cases/`** — une classe par action métier concrète (ex:
  `RegisterUserUseCase`). Un use case appelle les entités et les
  repositories via leurs interfaces (les ports), sans jamais savoir
  quelle implémentation technique tourne derrière.

#### `infrastructure/` — les adaptateurs de sortie

- **`persistence/postgres/`** — implémentation réelle des repositories
  avec de vraies requêtes SQL/ORM.
- **`mqtt/`** (si le service en a besoin) — client MQTT concret.

C'est la **seule** couche qui a le droit de dépendre d'un outil
technique précis.

#### `api/` — l'adaptateur d'entrée

- **`rest/<nom>_router.py`** — reçoit la requête HTTP, appelle le bon
  use case, retourne la réponse. Aucune logique métier ici — un router
  ne fait que traduire HTTP ↔ use case.

#### `main.py` et `container.py` — le câblage

- **`main.py`** — fixe, identique dans tous les services. Lance
  uvicorn sur l'app définie dans `container.py`.
- **`container.py`** — assemble tout : crée l'app FastAPI, branche les
  exception handlers, le endpoint `/health`, et inclut le router. C'est
  le seul endroit où toutes les couches se rencontrent.

### Comment on construit un service en hexagonal, étape par étape

1. **Générer le squelette** avec `generator/generate_service.py`.
2. **Définir l'entité** dans `domain/entities/` — juste les données et
   les règles metier de base (ex: un email doit contenir un `@`).
3. **Définir le port** dans `domain/ports/repositories/` — l'interface
   dont le use case aura besoin (ex: `save`, `find_by_email`).
4. **Écrire le use case** dans `application/use_cases/` — la vraie
   logique ("vérifier que l'email n'existe pas déjà, hasher le mot de
   passe, sauvegarder"), en appelant uniquement l'interface du port,
   jamais Postgres directement.
5. **Implémenter l'adaptateur** dans `infrastructure/persistence/` —
   le vrai code SQL qui réalise ce que le port promettait.
6. **Brancher le router** dans `api/rest/` — appelle le use case,
   retourne la réponse HTTP.
7. **Tester le use case seul**, avec un faux repository en mémoire —
   pas besoin de Postgres pour vérifier que la logique métier est
   correcte.

### Le bénéfice concret

Tester `RegisterUserUseCase` ne nécessite pas Postgres — on lui passe un
faux repository qui stocke juste en mémoire Python. Et le jour où vous
changez de base de données, seul `infrastructure/` bouge : `domain/` et
`application/` restent intacts, parce qu'ils ne connaissaient jamais
Postgres, seulement une interface.

---

## 3. Les deux niveaux, ensemble

```
                     SYSTÈME (microservices)
   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
   │ service- │   │ service- │   │ service- │   │ service- │
   │  user    │   │ mesures  │   │ carbone  │   │   ia     │  ...
   └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘
        │              │              │              │
   Chaque service, EN INTERNE, est construit en hexagonal :

        api/  →  application/  →  domain/  ←  infrastructure/
```

- **Le niveau microservices** répond à la question : *"comment
  découpe-t-on le système entier en petits programmes indépendants qui
  communiquent entre eux ?"*
- **Le niveau hexagonal** répond à la question : *"comment organise-t-on
  le code À L'INTÉRIEUR d'un seul de ces programmes pour que le métier
  reste propre et testable ?"*

Les deux se combinent, mais résolvent des problèmes différents et à des
échelles différentes.

---

## Résumé — les règles à retenir

- Un microservice = une responsabilité métier claire, sa propre base de
  données, jamais d'appel direct au code d'un autre service.
- `shared/contracts/` définit ce que les services peuvent échanger —
  on ne le modifie jamais seul, sans prévenir l'équipe.
- Dans un service, `domain/` ne dépend jamais de rien de technique.
- `infrastructure/` est la seule couche qui a le droit de connaître
  Postgres, Kafka, ou MQTT en détail.
- `main.py` et `container.py` ne se modifient jamais à la main — ils
  sont générés une fois pour toutes.
- Tout ce qui est logique métier se teste sans base de données réelle,
  via de faux repositories.
