# GitHub Project Setup for PropVista CRM

## Overview
This document outlines the setup of a GitHub Project (beta) for tracking PropVista CRM development using the sprint-based workflow defined in `docs/15-development-plan.md`.

## Project Structure
- **Project Name**: PropVista CRM Development
- **Project Type**: Project (beta) - GitHub's new project experience
- **Visibility**: Public (matching repository visibility)

## Columns (Based on Sprint Phases)
1. **Backlog** - All upcoming tasks
2. **Sprint 0: Environment & Foundation** - Active sprint tasks
3. **Sprint 1: Data Layer, Auth & Tenancy**
4. **Sprint 2: Property Management (Non-AI)**
5. **Sprint 3: Public Property Listing & Details**
6. **Sprint 4: Contact/Lead Capture & Basic CRM Pipeline**
7. **Sprint 5: AI Search**
8. **Sprint 6: AI Chatbot**
9. **Sprint 7: AI Recommendation**
10. **Sprint 8: Remaining Admin Modules (Part 1)**
11. **Sprint 9: Remaining Admin Modules (Part 2)**
12. **Sprint 10: Tenant Onboarding & Hardening**
13. **Sprint 11: Pilot Prep**
14. **Done** - Completed tasks

## Milestones (One per Sprint)
- Sprint 0: Environment & Foundation
- Sprint 1: Data Layer, Auth & Tenancy
- Sprint 2: Property Management (Non-AI)
- Sprint 3: Public Property Listing & Details
- Sprint 4: Contact/Lead Capture & Basic CRM Pipeline
- Sprint 5: AI Search
- Sprint 6: AI Chatbot
- Sprint 7: AI Recommendation
- Sprint 8: Remaining Admin Modules (Part 1)
- Sprint 9: Remaining Admin Modules (Part 2)
- Sprint 10: Tenant Onboarding & Hardening
- Sprint 11: Pilot Prep

## Labels
- `task` - Development tasks
- `bug` - Bug reports
- `enhancement` - Feature requests
- `documentation` - Documentation updates
- `test` - Test-related work
- `refactor` - Code refactoring
- `sprint-0` through `sprint-11` - Sprint assignment
- `phase-1` through `phase-3` - Development phase
- `backend`, `frontend`, `ai` - Component area
- `priority-high`, `priority-medium`, `priority-low` - Priority levels
- `blocked` - Blocked by external dependencies
- `ready-for-review` - Ready for PR review

## Automation
1. **Issue Templates**: Already created in `.github/ISSUE_TEMPLATE/`
2. **PR Template**: To be created
3. **Workflow**: GitHub Actions for CI (will be set up in Sprint 0)

## Next Steps
Once GitHub authentication is resolved, execute:
1. Create GitHub Project (beta) with the columns above
2. Create milestones for each sprint
3. Apply labels to repository
4. Populate backlog with tasks from `docs/15-development-plan.md` and `docs/BACKLOG.md`
5. Set up project automation (if desired)