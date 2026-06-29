"""PostgreSQL connection helper and CRUD for all Nunneri tables."""
from __future__ import annotations

import os
import time

import psycopg
from psycopg.rows import dict_row

from models import Membership, NodeConfig, Org, Project, RbacRole, Run, RunNode, Team, Thread, User

DATABASE_URL: str = os.environ.get(
    "DATABASE_URL",
    "postgresql://nunneri:nunneri@localhost:5432/nunneri",
)


async def get_conn() -> psycopg.AsyncConnection:
    return await psycopg.AsyncConnection.connect(DATABASE_URL, row_factory=dict_row)


# ---------------------------------------------------------------------------
# Schema init
# ---------------------------------------------------------------------------

async def init_db() -> None:
    async with await get_conn() as conn:
        # Core run tables
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS nunneri_threads (
                id            TEXT PRIMARY KEY,
                project_id    TEXT,
                agent         TEXT,
                model         TEXT,
                last_message  TEXT,
                runs          INTEGER DEFAULT 0,
                created_at    DOUBLE PRECISION
            )
        """)
        await conn.execute(
            "ALTER TABLE nunneri_threads ADD COLUMN IF NOT EXISTS project_id TEXT"
        )
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS nunneri_runs (
                id            TEXT PRIMARY KEY,
                thread_id     TEXT,
                project_id    TEXT,
                agent         TEXT,
                kind          TEXT,
                model         TEXT,
                project_path  TEXT,
                message       TEXT,
                system_prompt TEXT,
                output        TEXT,
                status        TEXT,
                duration_s    REAL,
                started_at    DOUBLE PRECISION
            )
        """)
        await conn.execute(
            "ALTER TABLE nunneri_runs ADD COLUMN IF NOT EXISTS project_id TEXT"
        )
        await conn.execute(
            "ALTER TABLE nunneri_runs ADD COLUMN IF NOT EXISTS error_detail TEXT"
        )
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS nunneri_run_nodes (
                id          TEXT PRIMARY KEY,
                run_id      TEXT,
                node_id     TEXT,
                label       TEXT,
                phase       INTEGER,
                node_type   TEXT,
                status      TEXT,
                output      TEXT,
                entered_at  DOUBLE PRECISION,
                exited_at   DOUBLE PRECISION
            )
        """)

        # Multi-tenant tables
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS nunneri_users (
                id         TEXT PRIMARY KEY,
                sub        TEXT UNIQUE NOT NULL,
                email      TEXT NOT NULL,
                name       TEXT,
                picture    TEXT,
                created_at DOUBLE PRECISION
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS nunneri_orgs (
                id         TEXT PRIMARY KEY,
                name       TEXT NOT NULL,
                slug       TEXT UNIQUE NOT NULL,
                created_at DOUBLE PRECISION
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS nunneri_teams (
                id         TEXT PRIMARY KEY,
                org_id     TEXT NOT NULL,
                name       TEXT NOT NULL,
                slug       TEXT NOT NULL,
                created_at DOUBLE PRECISION,
                UNIQUE (org_id, slug)
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS nunneri_projects (
                id          TEXT PRIMARY KEY,
                team_id     TEXT NOT NULL,
                org_id      TEXT NOT NULL,
                name        TEXT NOT NULL,
                slug        TEXT NOT NULL,
                description TEXT,
                created_at  DOUBLE PRECISION,
                UNIQUE (team_id, slug)
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS nunneri_memberships (
                id          TEXT PRIMARY KEY,
                scope_type  TEXT NOT NULL,
                scope_id    TEXT NOT NULL,
                user_id     TEXT NOT NULL,
                role        TEXT NOT NULL DEFAULT 'member',
                created_at  DOUBLE PRECISION,
                UNIQUE (scope_type, scope_id, user_id)
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS nunneri_node_configs (
                id                    TEXT PRIMARY KEY,
                agent_name            TEXT NOT NULL,
                node_id               TEXT NOT NULL,
                label                 TEXT,
                system_prompt         TEXT,
                routing_rules_json    TEXT DEFAULT '[]',
                classification_labels_json TEXT DEFAULT '[]',
                notes                 TEXT,
                updated_at            DOUBLE PRECISION,
                UNIQUE (agent_name, node_id)
            )
        """)

        # Close any runs that were left in "running" state (server crashed / SSE dropped).
        # Anything older than 1 hour is considered abandoned.
        await conn.execute("""
            UPDATE nunneri_runs
            SET status = 'error',
                duration_s = EXTRACT(EPOCH FROM NOW()) - started_at
            WHERE status = 'running'
              AND started_at < EXTRACT(EPOCH FROM NOW()) - 3600
        """)
        await conn.execute("""
            UPDATE nunneri_run_nodes SET status = 'error',
                exited_at = EXTRACT(EPOCH FROM NOW())
            WHERE run_id IN (
                SELECT id FROM nunneri_runs WHERE status = 'error'
                  AND started_at < EXTRACT(EPOCH FROM NOW()) - 3600
            )
            AND exited_at IS NULL
        """)

        # Indexes
        for stmt in [
            "CREATE INDEX IF NOT EXISTS idx_run_nodes_run_id ON nunneri_run_nodes(run_id)",
            "CREATE INDEX IF NOT EXISTS idx_runs_thread_id ON nunneri_runs(thread_id)",
            "CREATE INDEX IF NOT EXISTS idx_runs_started_at ON nunneri_runs(started_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_runs_project_id ON nunneri_runs(project_id)",
            "CREATE INDEX IF NOT EXISTS idx_threads_project_id ON nunneri_threads(project_id)",
            "CREATE INDEX IF NOT EXISTS idx_memberships_scope ON nunneri_memberships(scope_type, scope_id)",
            "CREATE INDEX IF NOT EXISTS idx_memberships_user ON nunneri_memberships(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_teams_org ON nunneri_teams(org_id)",
            "CREATE INDEX IF NOT EXISTS idx_projects_team ON nunneri_projects(team_id)",
            "CREATE INDEX IF NOT EXISTS idx_node_configs_agent ON nunneri_node_configs(agent_name)",
        ]:
            await conn.execute(stmt)


# ---------------------------------------------------------------------------
# Thread helpers
# ---------------------------------------------------------------------------

async def insert_thread(t: Thread) -> None:
    async with await get_conn() as conn:
        await conn.execute(
            "INSERT INTO nunneri_threads "
            "(id, project_id, agent, model, last_message, runs, created_at) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING",
            (t.id, t.project_id, t.agent, t.model, t.last_message, t.runs, t.created_at),
        )


async def update_thread(
    tid: str, agent: str, model: str, last_message: str
) -> None:
    async with await get_conn() as conn:
        await conn.execute(
            "UPDATE nunneri_threads "
            "SET agent=%s, model=%s, last_message=%s, runs=runs+1 "
            "WHERE id=%s",
            (agent, model, last_message[:200], tid),
        )


async def list_threads(project_id: str | None = None) -> list[Thread]:
    async with await get_conn() as conn:
        if project_id:
            rows = await conn.execute(
                "SELECT * FROM nunneri_threads WHERE project_id=%s ORDER BY created_at DESC",
                (project_id,),
            )
        else:
            rows = await conn.execute(
                "SELECT * FROM nunneri_threads ORDER BY created_at DESC"
            )
        return [Thread(**r) for r in await rows.fetchall()]


async def delete_thread(tid: str) -> None:
    async with await get_conn() as conn:
        await conn.execute("DELETE FROM nunneri_threads WHERE id=%s", (tid,))


# ---------------------------------------------------------------------------
# Run helpers
# ---------------------------------------------------------------------------

async def insert_run(r: Run) -> None:
    async with await get_conn() as conn:
        await conn.execute(
            "INSERT INTO nunneri_runs "
            "(id, thread_id, project_id, agent, kind, model, project_path, message, "
            " system_prompt, output, status, duration_s, started_at) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (r.id, r.thread_id, r.project_id, r.agent, r.kind, r.model, r.project_path,
             r.message, r.system_prompt, r.output, r.status, r.duration_s, r.started_at),
        )


async def finish_run(
    run_id: str,
    output: str,
    duration_s: float,
    status: str = "done",
    error_detail: str | None = None,
) -> None:
    async with await get_conn() as conn:
        await conn.execute(
            "UPDATE nunneri_runs SET output=%s, status=%s, duration_s=%s, error_detail=%s WHERE id=%s",
            (output, status, duration_s, error_detail, run_id),
        )


async def cancel_run(run_id: str, reason: str = "Cancelled by user") -> Run | None:
    async with await get_conn() as conn:
        rows = await conn.execute("SELECT * FROM nunneri_runs WHERE id=%s", (run_id,))
        row = await rows.fetchone()
        if not row:
            return None
        duration_s = max(0.0, time.time() - float(row.get("started_at") or time.time()))
        await conn.execute(
            """
            UPDATE nunneri_runs
            SET status='cancelled',
                duration_s=%s,
                error_detail=%s
            WHERE id=%s AND status IN ('running', 'waiting_approval')
            """,
            (duration_s, reason, run_id),
        )
        await conn.execute(
            """
            UPDATE nunneri_run_nodes
            SET status='cancelled',
                exited_at=EXTRACT(EPOCH FROM NOW())
            WHERE run_id=%s
              AND status IN ('pending', 'active', 'waiting_approval')
            """,
            (run_id,),
        )
        rows = await conn.execute("SELECT * FROM nunneri_runs WHERE id=%s", (run_id,))
        updated = await rows.fetchone()
        run = Run(**{k: v for k, v in updated.items() if k != "nodes"})
        run.nodes = await list_run_nodes(run_id, conn=conn)
        return run


async def list_runs(
    thread_id: str | None = None,
    project_id: str | None = None,
    limit: int = 50,
) -> list[Run]:
    async with await get_conn() as conn:
        if thread_id:
            rows = await conn.execute(
                "SELECT * FROM nunneri_runs WHERE thread_id=%s "
                "ORDER BY started_at DESC LIMIT %s",
                (thread_id, limit),
            )
        elif project_id:
            rows = await conn.execute(
                "SELECT * FROM nunneri_runs WHERE project_id=%s "
                "ORDER BY started_at DESC LIMIT %s",
                (project_id, limit),
            )
        else:
            rows = await conn.execute(
                "SELECT * FROM nunneri_runs ORDER BY started_at DESC LIMIT %s",
                (limit,),
            )
        return [Run(**{k: v for k, v in r.items() if k != "nodes"})
                for r in await rows.fetchall()]


async def get_run(run_id: str) -> Run | None:
    async with await get_conn() as conn:
        rows = await conn.execute("SELECT * FROM nunneri_runs WHERE id=%s", (run_id,))
        row = await rows.fetchone()
        if not row:
            return None
        run = Run(**{k: v for k, v in row.items() if k != "nodes"})
        run.nodes = await list_run_nodes(run_id, conn=conn)
        return run


async def latest_waiting_run(thread_id: str, gate_id: str | None = None) -> Run | None:
    async with await get_conn() as conn:
        if gate_id:
            rows = await conn.execute(
                """
                SELECT r.*
                FROM nunneri_runs r
                JOIN nunneri_run_nodes n ON n.run_id = r.id
                WHERE r.thread_id=%s
                  AND r.status='waiting_approval'
                  AND n.node_id=%s
                  AND n.status='waiting_approval'
                ORDER BY r.started_at DESC
                LIMIT 1
                """,
                (thread_id, gate_id),
            )
        else:
            rows = await conn.execute(
                """
                SELECT *
                FROM nunneri_runs
                WHERE thread_id=%s AND status='waiting_approval'
                ORDER BY started_at DESC
                LIMIT 1
                """,
                (thread_id,),
            )
        row = await rows.fetchone()
        if not row:
            return None
        run = Run(**{k: v for k, v in row.items() if k != "nodes"})
        run.nodes = await list_run_nodes(run.id, conn=conn)
        return run


# ---------------------------------------------------------------------------
# RunNode helpers
# ---------------------------------------------------------------------------

async def upsert_run_node(n: RunNode) -> None:
    async with await get_conn() as conn:
        await conn.execute(
            "INSERT INTO nunneri_run_nodes "
            "(id, run_id, node_id, label, phase, node_type, status, output, "
            " entered_at, exited_at) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
            "ON CONFLICT (id) DO UPDATE SET "
            "status=EXCLUDED.status, output=EXCLUDED.output, exited_at=EXCLUDED.exited_at",
            (n.id, n.run_id, n.node_id, n.label, n.phase, n.node_type,
             n.status, n.output, n.entered_at, n.exited_at),
        )


async def list_run_nodes(
    run_id: str,
    conn: psycopg.AsyncConnection | None = None,
) -> list[RunNode]:
    async def _fetch(c: psycopg.AsyncConnection) -> list[RunNode]:
        rows = await c.execute(
            "SELECT * FROM nunneri_run_nodes WHERE run_id=%s ORDER BY entered_at",
            (run_id,),
        )
        return [RunNode(**r) for r in await rows.fetchall()]

    if conn:
        return await _fetch(conn)
    async with await get_conn() as c:
        return await _fetch(c)


# ---------------------------------------------------------------------------
# User helpers
# ---------------------------------------------------------------------------

async def upsert_user(u: User) -> User:
    async with await get_conn() as conn:
        await conn.execute(
            "INSERT INTO nunneri_users (id, sub, email, name, picture, created_at) "
            "VALUES (%s,%s,%s,%s,%s,%s) "
            "ON CONFLICT (sub) DO UPDATE SET "
            "email=EXCLUDED.email, name=EXCLUDED.name, picture=EXCLUDED.picture",
            (u.id, u.sub, u.email, u.name, u.picture, u.created_at),
        )
        # Return the canonical row (may have existing id from prior upsert)
        rows = await conn.execute(
            "SELECT * FROM nunneri_users WHERE sub=%s", (u.sub,)
        )
        row = await rows.fetchone()
        return User(**row)


async def get_user_by_sub(sub: str) -> User | None:
    async with await get_conn() as conn:
        rows = await conn.execute(
            "SELECT * FROM nunneri_users WHERE sub=%s", (sub,)
        )
        row = await rows.fetchone()
        return User(**row) if row else None


async def get_user(user_id: str) -> User | None:
    async with await get_conn() as conn:
        rows = await conn.execute(
            "SELECT * FROM nunneri_users WHERE id=%s", (user_id,)
        )
        row = await rows.fetchone()
        return User(**row) if row else None


# ---------------------------------------------------------------------------
# Org helpers
# ---------------------------------------------------------------------------

async def insert_org(org: Org) -> Org:
    async with await get_conn() as conn:
        await conn.execute(
            "INSERT INTO nunneri_orgs (id, name, slug, created_at) "
            "VALUES (%s,%s,%s,%s)",
            (org.id, org.name, org.slug, org.created_at),
        )
    return org


async def list_orgs(user_id: str) -> list[Org]:
    async with await get_conn() as conn:
        rows = await conn.execute(
            "SELECT o.* FROM nunneri_orgs o "
            "JOIN nunneri_memberships m ON m.scope_id=o.id AND m.scope_type='org' "
            "WHERE m.user_id=%s ORDER BY o.created_at",
            (user_id,),
        )
        return [Org(**r) for r in await rows.fetchall()]


async def get_org(org_id: str) -> Org | None:
    async with await get_conn() as conn:
        rows = await conn.execute("SELECT * FROM nunneri_orgs WHERE id=%s", (org_id,))
        row = await rows.fetchone()
        return Org(**row) if row else None


async def delete_org(org_id: str) -> None:
    async with await get_conn() as conn:
        await conn.execute("DELETE FROM nunneri_orgs WHERE id=%s", (org_id,))


# ---------------------------------------------------------------------------
# Team helpers
# ---------------------------------------------------------------------------

async def insert_team(team: Team) -> Team:
    async with await get_conn() as conn:
        await conn.execute(
            "INSERT INTO nunneri_teams (id, org_id, name, slug, created_at) "
            "VALUES (%s,%s,%s,%s,%s)",
            (team.id, team.org_id, team.name, team.slug, team.created_at),
        )
    return team


async def list_teams(org_id: str, user_id: str | None = None) -> list[Team]:
    async with await get_conn() as conn:
        if user_id:
            rows = await conn.execute(
                "SELECT t.* FROM nunneri_teams t "
                "JOIN nunneri_memberships m ON m.scope_id=t.id AND m.scope_type='team' "
                "WHERE t.org_id=%s AND m.user_id=%s ORDER BY t.created_at",
                (org_id, user_id),
            )
        else:
            rows = await conn.execute(
                "SELECT * FROM nunneri_teams WHERE org_id=%s ORDER BY created_at",
                (org_id,),
            )
        return [Team(**r) for r in await rows.fetchall()]


async def get_team(team_id: str) -> Team | None:
    async with await get_conn() as conn:
        rows = await conn.execute("SELECT * FROM nunneri_teams WHERE id=%s", (team_id,))
        row = await rows.fetchone()
        return Team(**row) if row else None


async def delete_team(team_id: str) -> None:
    async with await get_conn() as conn:
        await conn.execute("DELETE FROM nunneri_teams WHERE id=%s", (team_id,))


# ---------------------------------------------------------------------------
# Project helpers
# ---------------------------------------------------------------------------

async def insert_project(p: Project) -> Project:
    async with await get_conn() as conn:
        await conn.execute(
            "INSERT INTO nunneri_projects "
            "(id, team_id, org_id, name, slug, description, created_at) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (p.id, p.team_id, p.org_id, p.name, p.slug, p.description, p.created_at),
        )
    return p


async def list_projects(team_id: str, user_id: str | None = None) -> list[Project]:
    async with await get_conn() as conn:
        if user_id:
            rows = await conn.execute(
                "SELECT p.* FROM nunneri_projects p "
                "JOIN nunneri_memberships m ON m.scope_id=p.id AND m.scope_type='project' "
                "WHERE p.team_id=%s AND m.user_id=%s ORDER BY p.created_at",
                (team_id, user_id),
            )
        else:
            rows = await conn.execute(
                "SELECT * FROM nunneri_projects WHERE team_id=%s ORDER BY created_at",
                (team_id,),
            )
        return [Project(**r) for r in await rows.fetchall()]


async def get_project(project_id: str) -> Project | None:
    async with await get_conn() as conn:
        rows = await conn.execute(
            "SELECT * FROM nunneri_projects WHERE id=%s", (project_id,)
        )
        row = await rows.fetchone()
        return Project(**row) if row else None


async def delete_project(project_id: str) -> None:
    async with await get_conn() as conn:
        await conn.execute("DELETE FROM nunneri_projects WHERE id=%s", (project_id,))


# ---------------------------------------------------------------------------
# Membership helpers
# ---------------------------------------------------------------------------

async def upsert_membership(m: Membership) -> Membership:
    async with await get_conn() as conn:
        await conn.execute(
            "INSERT INTO nunneri_memberships "
            "(id, scope_type, scope_id, user_id, role, created_at) "
            "VALUES (%s,%s,%s,%s,%s,%s) "
            "ON CONFLICT (scope_type, scope_id, user_id) DO UPDATE SET role=EXCLUDED.role",
            (m.id, m.scope_type, m.scope_id, m.user_id, m.role, m.created_at),
        )
    return m


async def delete_membership(scope_type: str, scope_id: str, user_id: str) -> None:
    async with await get_conn() as conn:
        await conn.execute(
            "DELETE FROM nunneri_memberships "
            "WHERE scope_type=%s AND scope_id=%s AND user_id=%s",
            (scope_type, scope_id, user_id),
        )


async def get_role(
    scope_type: str, scope_id: str, user_id: str
) -> RbacRole | None:
    async with await get_conn() as conn:
        rows = await conn.execute(
            "SELECT role FROM nunneri_memberships "
            "WHERE scope_type=%s AND scope_id=%s AND user_id=%s",
            (scope_type, scope_id, user_id),
        )
        row = await rows.fetchone()
        return row["role"] if row else None


async def list_members(scope_type: str, scope_id: str) -> list[dict]:
    async with await get_conn() as conn:
        rows = await conn.execute(
            "SELECT u.id, u.email, u.name, u.picture, m.role "
            "FROM nunneri_memberships m "
            "JOIN nunneri_users u ON u.id = m.user_id "
            "WHERE m.scope_type=%s AND m.scope_id=%s ORDER BY u.email",
            (scope_type, scope_id),
        )
        return list(await rows.fetchall())


# ---------------------------------------------------------------------------
# NodeConfig helpers
# ---------------------------------------------------------------------------

def _row_to_node_config(row: dict) -> NodeConfig:
    import json as _json
    return NodeConfig(
        id=row["id"],
        agent_name=row["agent_name"],
        node_id=row["node_id"],
        label=row.get("label"),
        system_prompt=row.get("system_prompt"),
        routing_rules=_json.loads(row.get("routing_rules_json") or "[]"),
        classification_labels=_json.loads(row.get("classification_labels_json") or "[]"),
        notes=row.get("notes"),
        updated_at=row.get("updated_at") or 0.0,
    )


async def upsert_node_config(nc: NodeConfig) -> NodeConfig:
    import json as _json
    async with await get_conn() as conn:
        await conn.execute(
            "INSERT INTO nunneri_node_configs "
            "(id, agent_name, node_id, label, system_prompt, "
            " routing_rules_json, classification_labels_json, notes, updated_at) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) "
            "ON CONFLICT (agent_name, node_id) DO UPDATE SET "
            "label=EXCLUDED.label, system_prompt=EXCLUDED.system_prompt, "
            "routing_rules_json=EXCLUDED.routing_rules_json, "
            "classification_labels_json=EXCLUDED.classification_labels_json, "
            "notes=EXCLUDED.notes, updated_at=EXCLUDED.updated_at",
            (
                nc.id, nc.agent_name, nc.node_id, nc.label, nc.system_prompt,
                _json.dumps([r.model_dump() for r in nc.routing_rules]),
                _json.dumps(nc.classification_labels),
                nc.notes, nc.updated_at,
            ),
        )
        rows = await conn.execute(
            "SELECT * FROM nunneri_node_configs WHERE agent_name=%s AND node_id=%s",
            (nc.agent_name, nc.node_id),
        )
        return _row_to_node_config(await rows.fetchone())


async def get_node_config(agent_name: str, node_id: str) -> NodeConfig | None:
    async with await get_conn() as conn:
        rows = await conn.execute(
            "SELECT * FROM nunneri_node_configs WHERE agent_name=%s AND node_id=%s",
            (agent_name, node_id),
        )
        row = await rows.fetchone()
        return _row_to_node_config(row) if row else None


async def list_node_configs(agent_name: str) -> list[NodeConfig]:
    async with await get_conn() as conn:
        rows = await conn.execute(
            "SELECT * FROM nunneri_node_configs WHERE agent_name=%s ORDER BY node_id",
            (agent_name,),
        )
        return [_row_to_node_config(r) for r in await rows.fetchall()]


async def delete_node_config(agent_name: str, node_id: str) -> None:
    async with await get_conn() as conn:
        await conn.execute(
            "DELETE FROM nunneri_node_configs WHERE agent_name=%s AND node_id=%s",
            (agent_name, node_id),
        )
