# Pull Request Template

## Summary
Brief description of the changes in this pull request.

## Related Issue
Fixes #[issue_number]

## Purpose & Traceability
- [ ] Updates documentation first (if requirements changed)
- [ ] Matches folder/layering in `02-architecture.md`
- [ ] Every new endpoint exists in `04-api-spec.md` (or spec updated first)
- [ ] Tenant-owned tables/queries respect `tenant_id` scoping
- [ ] AI prompts in `ai_clients/prompts/`, not inlined
- [ ] New DB changes go through an Alembic migration
- [ ] Secrets read from environment variables, not hardcoded
- [ ] Tests cover the new logic (and tenant-isolation tests if applicable)

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring
- [ ] Test-related
- [ ] Other (please specify):

## Screenshots (if applicable)
Add screenshots or GIFs to help visualize the changes.

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published downsteam
- [ ] I have run `python scripts/check_drift.py` and it passes
- [ ] I have run the self-check in `docs/09-coding-standards.md` §8

## Acceptance Criteria
List the specific TC-* cases this PR satisfies:
- TC-EXAMPLE-01: Description
- TC-EXAMPLE-02: Description

## Additional Context
Add any other context about the PR here.