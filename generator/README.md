# generator/

Ce dossier contient `generate_service.py`, le script qui crée le squelette
d'un nouveau microservice pour CarbonGhost Sentinel. Il garantit que tous
les services ont **exactement la même structure**, pour que n'importe qui
dans l'équipe puisse naviguer dans n'importe quel service sans se
reperdre.

## Utilisation

Toujours lancer le script **depuis la racine du repo**, pas depuis
`generator/` :

```bash
python generator/generate_service.py <nom> --port <port> [--with-mqtt]
```

Exemples :

```bash
python generator/generate_service.py user      --port 8001
python generator/generate_service.py mesures   --port 8003 --with-mqtt
python generator/generate_service.py carbone   --port 8002
python generator/generate_service.py ia        --port 8004
python generator/generate_service.py assistant --port 8005
python generator/generate_service.py factory   --port 8006
```

`--with-mqtt` ajoute un client MQTT vide (`infrastructure/mqtt/`), utile
uniquement pour les services qui reçoivent des données de l'edge-gateway
(ex: `service-mesures`).

Le script refuse d'écraser un service déjà existant — s'il trouve déjà
`services/service-<nom>/`, il s'arrête sans rien modifier.

## Ce que le script génère

```
services/service-<nom>/
├── domain/
│   ├── entities/
│   ├── exceptions/
│   │   └── base_exceptions.py
│   └── ports/
│       └── repositories/
├── application/
│   └── use_cases/
├── infrastructure/
│   └── persistence/
│       └── postgres/
├── api/
│   └── rest/
│       └── <nom>_router.py
├── main.py
├── container.py
├── requirements.txt
├── Dockerfile
└── .env.example
```

### `domain/`

Le cœur métier. Aucune dépendance à FastAPI, Postgres, Kafka ou quoi que
ce soit de technique — uniquement des objets Python purs.

- **`entities/`** — les objets métier (ex: `User`, `CarbonGhostEvent`).
  Ce sont des données + des règles, rien d'autre.
- **`ports/repositories/`** — des interfaces (ex: `IUserRepository`).
  Elles décrivent *ce qu'on veut faire* ("sauvegarder un user") sans dire
  *comment* on le fait. C'est ce qui permet de changer de base de données
  plus tard sans toucher au reste du code.
- **`exceptions/base_exceptions.py`** — généré à l'identique dans chaque
  service. Contient les exceptions communes (`NotFoundException`,
  `ValidationException`, `ConflictException`, `UnauthorizedException`)
  que `container.py` sait automatiquement transformer en réponse HTTP.

### `application/`

- **`use_cases/`** — la logique métier concrète, une classe par action
  (ex: `RegisterUserUseCase`). Un use case orchestre : il appelle les
  entités et les repositories (via leurs interfaces), sans jamais savoir
  s'il tourne avec Postgres, une base en mémoire pour les tests, ou autre
  chose.

### `infrastructure/`

L'implémentation technique concrète des ports définis dans `domain/`.

- **`persistence/postgres/`** — l'implémentation réelle des repositories
  avec Postgres (requêtes SQL ou ORM).
- **`mqtt/`** (si `--with-mqtt`) — le client MQTT concret.

### `api/`

- **`rest/<nom>_router.py`** — les routes HTTP. Un router ne fait que
  recevoir la requête, appeler le bon use case, et retourner la réponse.
  Aucune logique métier ne doit vivre ici.

### `main.py` — fixe, ne jamais modifier

Identique dans tous les services. Se contente de lancer `uvicorn` sur
l'app définie dans `container.py`. Si vous avez besoin de changer un
comportement de démarrage, ce n'est pas ici que ça se passe.

### `container.py` — le seul fichier d'assemblage

Regroupe tout ce qui est commun à un service : création de l'app
FastAPI, middlewares (CORS), exception handlers (basés sur
`domain/exceptions/base_exceptions.py`), endpoint `/health`, et
inclusion du router. C'est le fichier que le générateur personnalise
avec le nom du service.

## Petite explication de l'architecture hexagonale

L'idée centrale : **le métier ne doit jamais dépendre de la technique**.

Dans une architecture classique, le code métier appelle souvent
directement Postgres, ou directement FastAPI. Résultat : impossible de
tester la logique sans une vraie base de données, et un changement
d'outil technique (Postgres → MongoDB, par exemple) oblige à réécrire le
métier.

L'architecture hexagonale inverse la dépendance avec le principe des
**ports et adaptateurs** :

- Le **domaine** (`domain/`) définit des **ports** — des interfaces, des
  contrats. Il dit "j'ai besoin de sauvegarder un user" sans jamais dire
  comment.
- L'**infrastructure** (`infrastructure/`) fournit des **adaptateurs** —
  les implémentations concrètes de ces ports (Postgres, MQTT, etc.).
- L'**API** (`api/`) est elle-même un adaptateur, côté entrée : elle
  traduit une requête HTTP en appel de use case.

```
        api/ (adaptateur d'entrée : HTTP)
              │
              ▼
     application/ (use cases : orchestration)
              │
              ▼
        domain/ (entités + ports : le métier pur)
              ▲
              │
   infrastructure/ (adaptateur de sortie : Postgres, MQTT...)
```

Le mot "hexagonale" vient de la représentation habituelle du domaine
comme un hexagone au centre, avec des adaptateurs branchés tout autour
sur chacune de ses faces — HTTP d'un côté, base de données de l'autre,
message broker encore ailleurs. Le nombre de côtés n'a pas d'importance
réelle, seule compte l'idée : le domaine au centre, isolé, entouré
d'adaptateurs interchangeables.

**Bénéfice concret pour vous trois** : tester `RegisterUserUseCase` ne
nécessite pas Postgres — on lui donne un faux repository en mémoire. Et
le jour où vous changez de base de données, seul `infrastructure/`
bouge : `domain/` et `application/` restent intacts.
