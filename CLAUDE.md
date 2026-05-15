# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Stack

Django 4.2 + Graphene (GraphQL) backend for a Facebook Page inbox tool. PostgreSQL 16 + Redis 7. Single GraphQL endpoint at `/graphql` (GraphiQL enabled). No REST layer, no Django admin, no auth/sessions middleware — `MIDDLEWARE = []` in `core/settings.py`.

## Common commands

Local infra (Postgres on 5432, Redis on 6379):

```bash
docker compose up -d
```

Python env + dependencies (the `.venv` is checked in):

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Django:

```bash
python manage.py migrate
python manage.py makemigrations <app>
python manage.py runserver           # http://127.0.0.1:8000/graphql
python manage.py shell
```

Before running anything, copy `.env.examples` → `.env` and fill in `FACEBOOK_APP_ID` / `FACEBOOK_APP_SECRET` / `SECRET_KEY`. `core/settings.py` reads env via `python-dotenv`, so envs are only loaded if `.env` exists at the project root.

No test runner, lint, or formatter is configured yet.

## Folder structure

- /{apps}
- - /graphql
- - - /mutations - Graphql mutation files, all mutations include input types
- - resolvers.py - Graphql resolvers
- - schema.py - Graphql schema for this app, include (mutations, resolvers)
- - types.py - Graphql types, models to graphql type
- - /migrations - Generated migrations
- - models.py - Data models of app
- - apps.py - App configuration
- /core - Core app
- - /grahpql - Root graphql
- - - /decorators - Decorators
- - - schema.py - Root schema, includes all apps schema
- - /providers - Integration providers
- - /services - Root services

## Architecture

### GraphQL schema composition

The root schema in `core/graphql/schema.py` is built by **multiple inheritance** from each Django app's `Query` / `Mutation` classes:

```python
class Query(AccountQuery, graphene.ObjectType): pass
class Mutation(AccountMutation, graphene.ObjectType): pass
```

To add a new app's GraphQL surface: create `<app>/graphql/schema.py` with `Query` and/or `Mutation` `graphene.ObjectType` subclasses, then add them to the inheritance list in `core/graphql/schema.py`. Mutations live in `<app>/graphql/mutations/<name>.py` and are exposed as fields on the app's `Mutation` class (e.g. `authenticate = AuthenticateMutation.Field()`). Types live in `<app>/graphql/types.py`.

`GRAPHENE['SCHEMA']` in `core/settings.py` points to the composed schema.

### Layering

- `<app>/models.py` — Django ORM models. Note `db_table` is set explicitly (`ukhaan_users`, `ukhaan_pages`, `ukhaan_user_pages`) — table names are not the default `<app>_<model>`.
- `<app>/graphql/` — GraphQL surface only (types, queries, mutations). Resolvers stay thin and call into `core/services/`.
- `core/services/` — external integrations / business logic (e.g. `facebook.py` wraps Graph API v25.0 OAuth + `/me` + `/me/accounts`). Mutations instantiate these directly.
- `core/provider/` — singleton clients for infrastructure (e.g. `redis.py` exports a configured `RedisClient`).
- `core/settings.py` — exposes external config as namespaced dicts (`FACEBOOK`, `REDIS`) read via `settings.FACEBOOK.get(...)` rather than module-level constants.

### Auth model

There is no Django auth / `User` model from `django.contrib.auth` — `django.contrib.auth` and `django.contrib.sessions` are intentionally not in `INSTALLED_APPS`. Identity is a custom `account.User` keyed by `facebook_id`, created/updated on the `authenticate(code)` mutation via Facebook OAuth code exchange. `Page` ↔ `User` is many-to-many through `UserPages`, with the page's Facebook `access_token` stored on the `Page` row. Any session / token layer for the API itself is not yet implemented (PyJWT is in requirements but unused).
