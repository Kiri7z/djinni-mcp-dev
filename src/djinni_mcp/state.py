"""Small local profile/history store using SQLite and existing validation."""

import json
import os
import sqlite3
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator
from platformdirs import user_data_path

from .source import job_id, now

ProfileKey = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]{0,63}$")]
ProfileValue = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]
Facts = Annotated[dict[ProfileKey, ProfileValue], Field(max_length=30)]
QuestionnairePatch = Annotated[dict[ProfileKey, ProfileValue | None], Field(max_length=30)]
JobId = Annotated[str, Field(pattern=r"^[1-9][0-9]{0,11}$")]


class Profile(BaseModel):
    version: int = 0
    updated_at: str | None = None
    fields: dict[str, str] = Field(default_factory=dict)


class HistoryItem(BaseModel):
    job_id: str
    title: str | None = None
    summary: str | None = None
    draft: str | None = None
    source_updated_label: str | None = None
    profile_version: int | None = None
    first_recommended_at: str | None = None
    last_recommended_at: str | None = None
    excluded: bool = False
    exclusion_reason: str | None = None


class History(BaseModel):
    items: list[HistoryItem]


class Recommendation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    job_id: JobId
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]
    summary: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=4000)]
    draft: Annotated[str, Field(max_length=4000)] | None = None
    source_updated_label: Annotated[str, Field(max_length=200)] | None = None


class SearchSave(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request_id: Annotated[str, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$")]
    profile_version: Annotated[int, Field(ge=0)]
    recommendations: Annotated[list[Recommendation], Field(min_length=1, max_length=50)]
    report_markdown: Annotated[str, Field(min_length=1, max_length=100000)]

    @model_validator(mode="after")
    def unique_jobs(self):
        if len({r.job_id for r in self.recommendations}) != len(self.recommendations):
            raise ValueError("recommendations must contain unique job IDs")
        return self


class SaveReceipt(BaseModel):
    request_id: str
    saved_at: str
    report_path: str
    recommendation_count: int
    replayed: bool


class StateError(Exception):
    """A local-state failure with a safe user-facing message."""


SCHEMA = (
    "CREATE TABLE profile (id INTEGER PRIMARY KEY CHECK(id=1), questionnaire TEXT NOT NULL, "
    "resume_facts TEXT NOT NULL, version INTEGER NOT NULL, updated_at TEXT NOT NULL)",
    "CREATE TABLE history (job_id TEXT PRIMARY KEY, title TEXT, summary TEXT, draft TEXT, "
    "source_updated_label TEXT, profile_version INTEGER, first_recommended_at TEXT, "
    "last_recommended_at TEXT, excluded INTEGER NOT NULL DEFAULT 0, exclusion_reason TEXT)",
    "CREATE TABLE searches (request_id TEXT PRIMARY KEY, saved_at TEXT NOT NULL, payload TEXT NOT NULL)",
)


class LocalStore:
    def __init__(self, data_dir: Path | str | None = None):
        self.root = Path(data_dir or os.environ.get("DJINNI_MCP_DATA_DIR")
                         or user_data_path("djinni-mcp", appauthor=False)).expanduser().resolve()
        self.path = self.root / "state.sqlite3"

    @contextmanager
    def _db(self, *, write=False):
        db = None
        try:
            if write:
                self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
                if not self.path.exists():
                    self.path.touch(mode=0o600)
                db = sqlite3.connect(self.path, timeout=5)
                db.execute("BEGIN IMMEDIATE")
            else:
                db = sqlite3.connect(self.path.as_uri() + "?mode=ro", uri=True, timeout=5)
            db.row_factory = sqlite3.Row
            version = db.execute("PRAGMA user_version").fetchone()[0]
            if version == 0 and write:
                for statement in SCHEMA:
                    db.execute(statement)
                db.execute("PRAGMA user_version=1")
            elif version != 1:
                raise StateError("storage_version: unsupported local database version")
            yield db
            if write:
                db.commit()
        except (sqlite3.Error, OSError, ValueError, TypeError):
            raise StateError("storage_error: could not read or save local state") from None
        finally:
            if db is not None:
                db.close()

    @staticmethod
    def _profile(db):
        row = db.execute("SELECT * FROM profile WHERE id=1").fetchone()
        if row is None:
            return {}, {}, Profile()
        questionnaire, resume = json.loads(row["questionnaire"]), json.loads(row["resume_facts"])
        return questionnaire, resume, Profile(
            version=row["version"], updated_at=row["updated_at"], fields={**resume, **questionnaire})

    def get_profile(self) -> Profile:
        if not self.path.exists():
            return Profile()
        with self._db() as db:
            return self._profile(db)[2]

    def update_profile(self, questionnaire=None, resume_facts=None) -> Profile:
        if questionnaire is None and resume_facts is None:
            raise StateError("invalid_update: supply questionnaire fields or explicitly refreshed resume facts")
        with self._db(write=True) as db:
            old_q, old_cv, previous = self._profile(db)
            updated_q = old_q.copy()
            for key, value in (questionnaire or {}).items():
                if value is None:
                    updated_q.pop(key, None)
                else:
                    updated_q[key] = value
            updated_cv = old_cv if resume_facts is None else resume_facts
            if len(updated_q) > 30 or len(updated_cv) > 30:
                raise StateError("profile_too_large: keep each profile section within 30 concise fields")
            if updated_q == old_q and updated_cv == old_cv:
                return previous
            timestamp = now()
            db.execute("INSERT INTO profile VALUES (1, ?, ?, ?, ?) ON CONFLICT(id) DO UPDATE SET "
                       "questionnaire=excluded.questionnaire, resume_facts=excluded.resume_facts, "
                       "version=excluded.version, updated_at=excluded.updated_at",
                       (json.dumps(updated_q), json.dumps(updated_cv), previous.version + 1, timestamp))
            return Profile(version=previous.version + 1, updated_at=timestamp, fields={**updated_cv, **updated_q})

    def get_history(self, job_ids: list[str]) -> History:
        identities = list(dict.fromkeys(job_ids))
        rows = {}
        if identities and self.path.exists():
            with self._db() as db:
                marks = ",".join("?" for _ in identities)
                rows = {r["job_id"]: dict(r) for r in db.execute(
                    f"SELECT * FROM history WHERE job_id IN ({marks})", identities)}
        try:
            return History(items=[HistoryItem(**rows.get(i, {"job_id": i})) for i in identities])
        except ValueError:
            raise StateError("storage_error: invalid local history data") from None

    def set_job_excluded(self, job: str, excluded=True, reason="") -> HistoryItem:
        identity = job_id(job)
        with self._db(write=True) as db:
            db.execute("INSERT INTO history (job_id, excluded, exclusion_reason) VALUES (?, ?, ?) "
                       "ON CONFLICT(job_id) DO UPDATE SET excluded=excluded.excluded, "
                       "exclusion_reason=excluded.exclusion_reason",
                       (identity, int(excluded), reason if excluded else None))
        return self.get_history([identity]).items[0]

    def _write_report(self, request: SearchSave) -> Path:
        folder = self.root / "reports"
        folder.mkdir(exist_ok=True, mode=0o700)
        destination = folder / (request.request_id + ".md")
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=folder, delete=False) as file:
                temporary = Path(file.name)
                file.write(request.report_markdown)
            temporary.replace(destination)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        return destination

    def save_search(self, request: SearchSave) -> SaveReceipt:
        payload = json.dumps(request.model_dump(), ensure_ascii=False, sort_keys=True)
        with self._db(write=True) as db:
            previous = db.execute("SELECT * FROM searches WHERE request_id=?", (request.request_id,)).fetchone()
            if previous is not None:
                if previous["payload"] != payload:
                    raise StateError("request_conflict: this request_id was already used for different output")
                timestamp, replayed = previous["saved_at"], True
            else:
                if self._profile(db)[2].version != request.profile_version:
                    raise StateError("profile_changed: reload the saved profile before recording this batch")
                timestamp, replayed = now(), False
                for rec in request.recommendations:
                    row = db.execute("SELECT excluded FROM history WHERE job_id=?", (rec.job_id,)).fetchone()
                    if row is not None and row["excluded"]:
                        raise StateError("excluded_job: remove explicitly excluded jobs from the output")
                    db.execute("INSERT INTO history (job_id, title, summary, draft, source_updated_label, "
                               "profile_version, first_recommended_at, last_recommended_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
                               "ON CONFLICT(job_id) DO UPDATE SET title=excluded.title, summary=excluded.summary, "
                               "draft=excluded.draft, source_updated_label=excluded.source_updated_label, "
                               "profile_version=excluded.profile_version, "
                               "first_recommended_at=COALESCE(history.first_recommended_at, excluded.first_recommended_at), "
                               "last_recommended_at=excluded.last_recommended_at",
                               (rec.job_id, rec.title, rec.summary, rec.draft, rec.source_updated_label,
                                request.profile_version, timestamp, timestamp))
                db.execute("INSERT INTO searches VALUES (?, ?, ?)", (request.request_id, timestamp, payload))
        try:
            report = self._write_report(request)
        except OSError:
            raise StateError("report_write_failed: database saved; retry save_search with the same request_id and data to restore Markdown") from None
        return SaveReceipt(request_id=request.request_id, saved_at=timestamp, report_path=str(report),
                           recommendation_count=len(request.recommendations), replayed=replayed)
