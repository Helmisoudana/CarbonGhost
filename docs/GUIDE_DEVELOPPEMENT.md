# Guide de développement — CarbonGhost Sentinel

Ce document ne répète pas "c'est quoi l'architecture hexagonale" (voir
`docs/ARCHITECTURE.md` pour ça). Il répond à une question différente et
plus pratique : **par où je commence, et dans quel ordre, quand je dois
coder une fonctionnalité dans un service ?**

La méthode s'applique à n'importe quel service du projet —
`service-user`, `service-carbone`, `service-assistant`, peu importe.

---

## Le raisonnement en 7 questions

Avant d'écrire une seule ligne de code, posez-vous ces questions dans
cet ordre. Chaque question correspond à un dossier précis.

### 1. Quel est le besoin métier, en une phrase ?

Pas de code, pas de technique. Juste la phrase.

> "Un utilisateur doit pouvoir s'inscrire avec un email et un mot de
> passe."

Si vous n'arrivez pas à l'écrire en une phrase simple, le besoin n'est
pas encore assez clair pour commencer à coder.

### 2. Quelles données sont concernées ?

→ Ça définit ce qui va dans `domain/entities/`.

Exemple : un `User` a un `id`, un `email`, un `password_hash`, une
`date de création`.

**Piège à éviter** : ne mettez pas de champs techniques ici (pas de
`created_at` généré par Postgres, pas de logique HTTP). Une entité,
c'est juste la donnée + les règles qui lui sont propres (ex: "un email
doit contenir un `@`").

### 3. Quelles actions veut-on pouvoir faire ?

→ Ça définit les classes dans `application/use_cases/`.

Une action = un use case = une classe. Exemples :
- `RegisterUserUseCase`
- `LoginUserUseCase`
- `PublishCarbonEventUseCase`

**Règle** : si une phrase d'action contient "et", posez-vous la question
si ce n'est pas deux use cases déguisés en un seul. "Enregistrer un
utilisateur ET lui envoyer un email" → souvent deux responsabilités
différentes.

### 4. De quoi ce use case a-t-il besoin, qu'il ne peut pas faire lui-même ?

→ Ça définit les interfaces dans `domain/ports/repositories/`.

Le use case ne sait pas parler à Postgres. Il a juste besoin de
"quelque chose qui sait sauvegarder un user" et "quelque chose qui sait
retrouver un user par email". Vous écrivez ça comme une interface
abstraite :

```python
# domain/ports/repositories/i_user_repository.py
from abc import ABC, abstractmethod
from domain.entities.user import User

class IUserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> None: ...

    @abstractmethod
    def find_by_email(self, email: str) -> User | None: ...
```

À ce stade, **aucune ligne de SQL n'existe encore**, et c'est normal.

### 5. Comment ce besoin est-il réellement satisfait, techniquement ?

→ Ça définit l'implémentation dans `infrastructure/`.

C'est ici, et seulement ici, que Postgres (ou Kafka, ou MQTT) apparaît
dans le code :

```python
# infrastructure/persistence/postgres/postgres_user_repository.py
from domain.ports.repositories.i_user_repository import IUserRepository
from domain.entities.user import User

class PostgresUserRepository(IUserRepository):
    def __init__(self, db_connection):
        self.db = db_connection

    def save(self, user: User) -> None:
        # vraie requête SQL ici
        ...

    def find_by_email(self, email: str) -> User | None:
        # vraie requête SQL ici
        ...
```

### 6. Comment le monde extérieur déclenche cette action ?

→ Ça définit le router dans `api/rest/`.

Le router ne fait que traduire une requête HTTP en appel de use case,
puis retourne une réponse. Rien d'autre :

```python
# api/rest/user_router.py
from fastapi import APIRouter
from application.use_cases.register_user_use_case import RegisterUserUseCase

router = APIRouter(prefix="/user", tags=["user"])

@router.post("/register")
def register(payload: RegisterUserRequest):
    use_case = RegisterUserUseCase(repository=...)
    user = use_case.execute(payload.email, payload.password)
    return {"id": user.id, "email": user.email}
```

**Piège à éviter** : ne mettez jamais de `if` métier dans un router
(genre "si l'email existe déjà, retourner une erreur"). Cette
vérification vit dans le use case, pas dans le router.

### 7. Qu'est-ce qui peut mal tourner ?

→ Ça définit quelles exceptions lever, parmi celles de
`domain/exceptions/base_exceptions.py`.

| Situation | Exception à lever | Code HTTP retourné automatiquement |
|---|---|---|
| L'email existe déjà | `ConflictException` | 409 |
| Le mot de passe est trop court | `ValidationException` | 422 |
| L'utilisateur n'existe pas | `NotFoundException` | 404 |
| Le token est invalide | `UnauthorizedException` | 401 |

Vous n'avez **jamais** besoin d'écrire de `try/except` dans le router —
`container.py` intercepte déjà ces exceptions et les transforme en
réponse HTTP.

```python
# dans le use case
if self.repository.find_by_email(email) is not None:
    raise ConflictException("Un compte existe déjà avec cet email")
```

---

## Exemple complet, filé du début à la fin

Besoin : *"Un utilisateur doit pouvoir s'inscrire avec un email et un
mot de passe."*

```
1. Entité         → domain/entities/user.py
2. Port            → domain/ports/repositories/i_user_repository.py
3. Use case        → application/use_cases/register_user_use_case.py
4. Implémentation  → infrastructure/persistence/postgres/postgres_user_repository.py
5. Router           → api/rest/user_router.py
```

```python
# 1. domain/entities/user.py
from dataclasses import dataclass

@dataclass
class User:
    id: str
    email: str
    password_hash: str
```

```python
# 2. domain/ports/repositories/i_user_repository.py
from abc import ABC, abstractmethod
from domain.entities.user import User

class IUserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> None: ...
    @abstractmethod
    def find_by_email(self, email: str) -> User | None: ...
```

```python
# 3. application/use_cases/register_user_use_case.py
import uuid
import bcrypt
from domain.entities.user import User
from domain.ports.repositories.i_user_repository import IUserRepository
from domain.exceptions.base_exceptions import ConflictException, ValidationException

class RegisterUserUseCase:
    def __init__(self, repository: IUserRepository):
        self.repository = repository

    def execute(self, email: str, password: str) -> User:
        if len(password) < 8:
            raise ValidationException("Le mot de passe doit faire au moins 8 caractères")

        if self.repository.find_by_email(email) is not None:
            raise ConflictException("Un compte existe déjà avec cet email")

        user = User(
            id=str(uuid.uuid4()),
            email=email,
            password_hash=bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode(),
        )
        self.repository.save(user)
        return user
```

```python
# 4. infrastructure/persistence/postgres/postgres_user_repository.py
from domain.ports.repositories.i_user_repository import IUserRepository
from domain.entities.user import User

class PostgresUserRepository(IUserRepository):
    def __init__(self, db_connection):
        self.db = db_connection

    def save(self, user: User) -> None:
        self.db.execute(
            "INSERT INTO users (id, email, password_hash) VALUES (%s, %s, %s)",
            (user.id, user.email, user.password_hash),
        )

    def find_by_email(self, email: str) -> User | None:
        row = self.db.fetch_one("SELECT * FROM users WHERE email = %s", (email,))
        return User(**row) if row else None
```

```python
# 5. api/rest/user_router.py
from fastapi import APIRouter
from pydantic import BaseModel
from application.use_cases.register_user_use_case import RegisterUserUseCase
from infrastructure.persistence.postgres.postgres_user_repository import PostgresUserRepository

router = APIRouter(prefix="/user", tags=["user"])

class RegisterRequest(BaseModel):
    email: str
    password: str

@router.post("/register")
def register(payload: RegisterRequest):
    repository = PostgresUserRepository(db_connection=...)
    use_case = RegisterUserUseCase(repository)
    user = use_case.execute(payload.email, payload.password)
    return {"id": user.id, "email": user.email}
```

Remarquez : à aucun moment `register_user_use_case.py` ne mentionne
Postgres, SQL, ou FastAPI. Il ne connaît que `IUserRepository`, une
interface. C'est ce qui rend ce fichier testable sans base de données
réelle (voir plus bas).

---

## Comment tester ce que vous venez d'écrire

Un faux repository en mémoire, sans Postgres ni Docker :

```python
# tests/test_register_user.py
from domain.ports.repositories.i_user_repository import IUserRepository
from application.use_cases.register_user_use_case import RegisterUserUseCase
from domain.exceptions.base_exceptions import ConflictException
import pytest

class FakeUserRepository(IUserRepository):
    def __init__(self):
        self.users = {}

    def save(self, user):
        self.users[user.email] = user

    def find_by_email(self, email):
        return self.users.get(email)

def test_register_success():
    use_case = RegisterUserUseCase(FakeUserRepository())
    user = use_case.execute("test@test.com", "motdepasse123")
    assert user.email == "test@test.com"

def test_register_duplicate_raises():
    repo = FakeUserRepository()
    use_case = RegisterUserUseCase(repo)
    use_case.execute("test@test.com", "motdepasse123")

    with pytest.raises(ConflictException):
        use_case.execute("test@test.com", "autremdp123")
```

```bash
pytest
```

Rapide (quelques millisecondes), pas besoin de Docker pour vérifier que
la logique métier est correcte.

---

## Cas particulier : un service qui consomme Kafka au lieu de HTTP

Le raisonnement des 7 questions reste identique. Seule la question 6
change : au lieu d'un router HTTP, le déclencheur est un message Kafka.

```python
# infrastructure/kafka/consumer.py
from application.use_cases.compute_carbon_event_use_case import ComputeCarbonEventUseCase

for message in consumer:
    mesure = SensorMeasurment(**message.value)
    use_case = ComputeCarbonEventUseCase(repository=...)
    use_case.execute(mesure)   # même use case, même logique testable
```

Le use case, lui, ne change pas de nature : il reste appelable et
testable de la même façon, qu'il soit déclenché par HTTP ou par Kafka.

---

## Checklist avant de commit

```
□ L'entité ne contient aucun import FastAPI/Postgres/Kafka
□ Le use case ne connaît que des interfaces (ports), jamais Postgres directement
□ Toute erreur métier lève une exception de domain/exceptions/base_exceptions.py
□ Le router ne contient aucun if métier, juste un appel au use case
□ Un test existe pour le cas de succès ET au moins un cas d'erreur
□ pytest passe sans erreur
□ docker-compose up -d --build <service> démarre sans crash
□ curl .../health répond "ok"
```

---

## Résumé — l'ordre à toujours suivre

```
1. Une phrase claire du besoin métier
2. domain/entities/        → la donnée
3. domain/ports/            → ce dont on a besoin, en abstrait
4. application/use_cases/   → la logique, orchestrée
5. infrastructure/          → l'implémentation technique réelle
6. api/rest/ (ou kafka/)    → le déclencheur externe
7. domain/exceptions/       → ce qui peut mal tourner
8. tests/                   → preuve que ça marche, sans Docker
```

Cet ordre n'est pas arbitraire : il va toujours du **métier** vers la
**technique**, jamais l'inverse. C'est la règle numéro un de
l'architecture hexagonale, appliquée concrètement à chaque
fonctionnalité que vous développez.
