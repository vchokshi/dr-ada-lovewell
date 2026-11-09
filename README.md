# Dr. Ada Lovewell

Ada is a scripted presenter of published, trainee-safe lessons. This is a separate application, migrated
out of ViharBot under [vchokshi/viharbot#293](https://github.com/vchokshi/viharbot/issues/293). It does not
import ViharBot or Archie code (a test enforces this).

## What is here

- `src/dr_ada_lovewell/archie_contract/` — a **vendored snapshot** of the delivery-package contract defined
  by [Professor Archibald](https://github.com/vchokshi/professor-archibald): `AdaPackage`,
  `PublishedStore` and `AdaGateway` (`PACKAGE_SCHEMA = "1.0"`), plus the few modules they need. Archie owns
  the schema. Ada can only read published packages; the gateway fails closed on a missing, unpublished,
  revoked or tampered package.
- `src/dr_ada_lovewell/identity/`, `skills/` — Ada's identity, prompt and skill definitions, moved as data.
  Nothing here loads them yet.
- `tests/test_archie_contract.py` — contract tests against `tests/fixtures/archie_published/`, a real
  package produced by Archie's own workflow.

## Tests

```
python -m venv .venv && . .venv/bin/activate
pip install -e ".[test]"
pytest
```

## Keeping the contract current

When Archie changes the package schema it bumps `PACKAGE_SCHEMA`. To update here: copy
`learning/{ada,audit,fsutil,lesson,basis,models}.py` and `curriculum/models.py` from
`professor-archibald/src/professor_archibald/` into `archie_contract/`, then regenerate the fixture by
running Archie's workflow to a published package (see `tests/test_archie_workflow_e2e.py` there) and
copying its `published/` store to `tests/fixtures/archie_published/`.

## Status

Identity and skills are carried over as data only. There is no learner-facing application yet.
