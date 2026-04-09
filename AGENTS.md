# AGENTS.md

## Purpose
This repository contains a PoC travel recommendation system built around a structured retrieval layer and a lightweight agent experience.

## Architecture
- `app/graphql/`: GraphQL retrieval layer on top of the destination dataset.
- `app/agent/`: rules-first and hybrid LLM orchestration for parsing, retrieval, and response generation.
- `app/static/`: chat UI, technical view, and architecture visualization.
- `app/ingestion/`: CSV-to-database loading flow.
- `app/db/`: SQLAlchemy models and database session setup.

## Working Agreements
- Keep the GraphQL schema and resolvers stable unless a task explicitly requires retrieval changes.
- Prefer deterministic and readable logic over abstract frameworks.
- Treat the dataset as structured source-of-truth data and keep LLM usage focused on interpretation and explanation.
- Maintain the current UX split between demo-friendly output and technical inspectability.
- Keep multilingual UI strings aligned across English, Dutch, and French when changing visible text.

## Common Commands
- Run the app: `uvicorn app.main:app --reload`
- Run tests: `.venv/bin/python -m unittest discover -s tests -v`
- Reload the dataset: `.venv/bin/python -m app.ingestion.load_data`
