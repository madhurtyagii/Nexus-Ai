# Nexus AI - Database Documentation

Nexus AI uses SQLAlchemy as its ORM, providing flexibility to work with various relational databases (PostgreSQL, SQLite, MySQL).

## Schema Overview

The database is built around four primary entities: **Users**, **Projects**, **Tasks**, and **Agents**.

### 👤 Users
Stores user accounts and authentication state.
- `id`: Primary key.
- `email`: Unique login identifier.
- `hashed_password`: Securely hashed password.
- `is_active`: User status.

### 🚀 Projects
Manages complex objective-driven workflows.
- `id`: Primary key.
- `name`, `description`: Project metadata.
- `status`: Current state (planning, in_progress, completed).
- `progress`: Percentage completion derived from tasks.
- `project_plan`: JSON structure defining phases and agent assignments.

### 📝 Tasks & Subtasks
The core units of execution.
- **Tasks**: Represent a single high-level request.
- **Subtasks**: Individual steps within a task or project phase, assigned to specific agents.
- **Fields**: `id`, `user_id`, `project_id`, `user_prompt`, `status`, `output`, `complexity_score`.

### 🤖 Agents & Messages
- **Agents**: Stores agent definitions and specialized prompts.
- **AgentMessages**: A log of inter-agent communication during complex project execution.

## Relationships

- A **User** has many **Projects** and **Tasks**.
- A **Project** has many **Tasks** (linked via `project_id`).
- A **Task** can have many **Subtasks**.
- **AgentMessages** are linked to a specific **Task** tracking the collaboration trail.

## Migrations

Nexus AI uses **Alembic** for database migrations.

### Commands
- **Generate Migration**: `alembic revision --autogenerate -m "description"`
- **Apply Migration**: `alembic upgrade head`
- **Rollback**: `alembic downgrade -1`

## Vector Database (Semantic Memory)
While relational data is in SQLAlchemy, **Nexus AI** also uses a Vector Database (ChromaDB/Qdrant) for semantic memory. 
- **Purpose**: Fast similarity search for past tasks and user preferences.
- **Format**: Text embeddings generated via OpenAI's `text-embedding-3-small`.

## Performance
- **Indexing**: Frequent filters (User/Project ID, Status) are indexed.
- **Caching**: Redis is used to cache task results and session data to reduce DB load.
