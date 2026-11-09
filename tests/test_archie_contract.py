"""Contract tests: Ada reads the package format Archie publishes (PACKAGE_SCHEMA 1.0).

`tests/fixtures/archie_published/` is a real package produced by Archie's own workflow (see README for
how to regenerate it). Offline; no model, no network.
"""

from __future__ import annotations

import ast
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from dr_ada_lovewell.archie_contract.learning import ada
from dr_ada_lovewell.archie_contract.learning.ada import AdaGateway, NotAvailable, PublishedStore
from dr_ada_lovewell.archie_contract.learning.audit import AuditLog

FIXTURE = Path(__file__).parent / "fixtures" / "archie_published"
LESSON = "viharbot-pr7-ccccccc"
SRC = Path(__file__).resolve().parents[1] / "src"


@pytest.fixture
def gateway(tmp_path):
    root = tmp_path / "published"
    shutil.copytree(FIXTURE, root)
    return AdaGateway(PublishedStore(root), AuditLog(tmp_path / "audit")), root


def test_ada_reads_and_verifies_a_package_archie_published(gateway):
    gw, _ = gateway
    package = gw.get(LESSON)
    assert package.verify()
    assert package.content.title and package.provenance.approved_by == "reviewer-one"


def test_a_tampered_package_fails_closed(gateway):
    gw, root = gateway
    path = root / LESSON / "v1" / "package.json"
    data = json.loads(path.read_text())
    data["content"]["title"] = "Tampered title"
    path.write_text(json.dumps(data))
    with pytest.raises(NotAvailable):
        gw.get(LESSON)


def test_a_revoked_package_is_not_available(gateway):
    gw, root = gateway
    PublishedStore(root).revoke(LESSON, 1)
    with pytest.raises(NotAvailable):
        gw.get(LESSON)


@pytest.mark.parametrize("lesson_id", ["missing-lesson", "../etc/passwd", "UPPER", ""])
def test_unknown_or_malformed_ids_are_not_available(gateway, lesson_id):
    gw, _ = gateway
    with pytest.raises(NotAvailable):
        gw.get(lesson_id)


def test_the_gateway_holds_only_the_published_store_and_audit_log(gateway):
    gw, _ = gateway
    assert {type(v).__name__ for v in vars(gw).values()} == {"PublishedStore", "AuditLog"}


def test_the_ada_module_imports_nothing_that_reaches_instructor_material():
    tree = ast.parse(Path(ada.__file__).read_text())
    imported = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
    forbidden = {"instructor_access", "assignment", "github", "evidence", "publication", "workflow",
                 "synthesis", "authn", "ingest"}
    assert not (imported & forbidden), imported & forbidden
    code = ("import sys, dr_ada_lovewell.archie_contract.learning.ada\n"
            f"bad=[m for m in sys.modules if m.rsplit('.',1)[-1] in {sorted(forbidden)!r} "
            "and m.startswith('dr_ada_lovewell')]\nassert not bad, bad\n")
    done = subprocess.run([sys.executable, "-c", code], env={"PYTHONPATH": str(SRC), "PATH": ""},
                          capture_output=True, text=True)
    assert done.returncode == 0, done.stderr


def test_ada_does_not_import_viharbot_or_archie():
    for p in SRC.rglob("*.py"):
        text = p.read_text()
        for banned in ("import viharbot", "from viharbot", "import professor_archibald",
                       "from professor_archibald"):
            assert banned not in text, (p, banned)
