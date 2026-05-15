# ukhaan-inbox-be

Django + Graphene (GraphQL) backend for a Facebook Page inbox tool.

## Stack

- Django 4.2 + Graphene 3 (single GraphQL endpoint at `/graphql`, GraphiQL enabled)
- PostgreSQL 16
- Redis 7 (token store)
- Facebook Graph API v25.0 (OAuth + Pages)
- PyJWT for session tokens

No REST layer, no Django admin, no auth/sessions middleware. Identity is a custom `account.User` keyed by `facebook_id`.

## Requirements

- Python 3.9+
- Docker (for local Postgres + Redis)

## Setup

```bash
# 1. Start Postgres (5432) and Redis (6379)
docker compose up -d

# 2. Activate venv and install deps
source .venv/bin/activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.examples .env
# Fill in FACEBOOK_APP_ID, FACEBOOK_APP_SECRET, SECRET_KEY

# 4. Apply migrations
python manage.py migrate

# 5. Run the dev server
python manage.py runserver
```

GraphQL endpoint: <http://127.0.0.1:8000/graphql>

## Common commands

```bash
python manage.py makemigrations <app>
python manage.py migrate
python manage.py shell
python manage.py runserver
```

## Environment variables

See `.env.examples`. Required: `SECRET_KEY`, `FACEBOOK_APP_ID`, `FACEBOOK_APP_SECRET`, Postgres + Redis connection details.

`core/settings.py` loads `.env` via `python-dotenv` only if the file exists at the project root.

## Project structure

```
/<app>/
  graphql/
    mutations/   GraphQL mutations (one file per mutation, includes input types)
    resolvers.py GraphQL resolvers
    schema.py    App-level Query / Mutation classes
    types.py     DjangoObjectType definitions
  migrations/
  models.py
  apps.py

/core/
  graphql/
    decorators/  e.g. login_required
    schema.py    Root schema composed by multiple inheritance of each app's Query / Mutation
  provider/      Singleton infra clients (redis, ...)
  services/      External integrations / business logic (facebook, authentication, ...)
  settings.py    Namespaced config dicts (FACEBOOK, REDIS, JWT, ...)
```

### Adding an app to the GraphQL schema

1. Create `<app>/graphql/schema.py` with `Query` and/or `Mutation` `graphene.ObjectType` subclasses.
2. Add the app to `INSTALLED_APPS` in `core/settings.py`.
3. Add the new `Query` / `Mutation` to the inheritance list in `core/graphql/schema.py`.

Mutations live in `<app>/graphql/mutations/<name>.py` and are exposed as fields on the app's `Mutation` class (e.g. `authenticate = AuthenticateMutation.Field()`).

## Auth

There is no Django auth / `User` model from `django.contrib.auth`. The `authenticate(code)` mutation exchanges a Facebook OAuth code, upserts `account.User` keyed by `facebook_id`, syncs the user's `Page`s, and returns a JWT access token. The token's `jti` is stored in Redis (key prefix `auth:access:`) with the configured TTL; `Authentication.verify` rejects tokens whose `jti` is no longer in Redis. Protect resolvers with `core.graphql.decorators.login_required`.

## Tooling

No test runner, lint, or formatter is configured yet.
