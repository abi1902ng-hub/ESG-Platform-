# EcoSphere — ESG Management Platform

Enterprise-grade ESG (Environmental, Social, Governance) management platform built for the Odoo Hackathon. Pure Python backend (Flask + SQLAlchemy + PostgreSQL), Bootstrap/Jinja frontend, Chart.js for analytics.

## Status: Phase 2 Complete

Phase 1 delivered the platform foundation. Phase 2 adds the three core ESG modules with full CRUD:

- ✅ **Environmental**: emission factor reference data (scope 1/2/3), carbon transaction ledger with quantity → CO2e calculation, submit/approve/reject workflow, running totals
- ✅ **Social / CSR**: CSR activity planning (category, budget, target beneficiaries), employee sign-up/participation with hours + feedback logging, per-activity participant rollups
- ✅ **Governance**: audit scheduling and tracking (type, scope, auditor, score, findings), compliance issue tracking linked to audits (severity, assignment, due dates, resolution)
- ✅ All Phase 2 tables follow the same `BaseModel` (audit fields + soft delete) as Phase 1
- ✅ New permission codes (`carbon.approve`, `factor.manage`, etc.) wired into the existing RBAC system, scoped per role in the seed script
- ✅ Every module writes to the immutable `ActivityLog` on create/update/delete/approve/reject
- ✅ Sidebar now links to live Environmental / Social / Governance / Compliance pages
- ✅ Seed script extended with demo emission factors, a carbon transaction, a CSR activity, an audit, and a compliance issue

**Not yet built** (Phases 3–4, by design): Real dashboard widgets (Chart.js) wired to the new module data, gamification engine (XP/badges/challenges/leaderboard), notification system, report generation (PDF/Excel/CSV), AI features.

## Setup

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # then edit .env with real DB/mail credentials

# Create PostgreSQL database first:
#   createdb ecosphere_db

python -m app.utils.seed           # creates roles, permissions, demo org, 7 demo users, and Phase 2 sample data
python run.py                      # visit http://localhost:5000
```

## Demo Logins

All seeded users share the password `Ecosphere@123`.

| Role | Email |
|---|---|
| Super Admin | super_admin@ecosphere.demo |
| Org Admin | org_admin@ecosphere.demo |
| Department Manager | department_manager@ecosphere.demo |
| Employee | employee@ecosphere.demo |
| Auditor | auditor@ecosphere.demo |
| CSR Manager | csr_manager@ecosphere.demo |
| Viewer | viewer@ecosphere.demo |

## Project Structure

```
ecosphere/
├── run.py                     # entrypoint
├── config.py                  # env-driven config (dev/prod/test)
├── requirements.txt
├── .env.example
├── app/
│   ├── __init__.py            # app factory
│   ├── extensions.py          # shared Flask extension instances
│   ├── models/
│   │   ├── base.py            # AuditMixin + SoftDeleteMixin + BaseModel
│   │   ├── user.py            # User, Role, Permission, RolePermission
│   │   ├── organization.py    # Organization, Department
│   │   ├── audit.py           # ActivityLog (immutable audit trail)
│   │   ├── otp.py             # OTPToken (email verification / reset)
│   │   ├── environmental.py   # EmissionFactor, CarbonTransaction (Phase 2)
│   │   ├── social.py          # CSRActivity, CSRParticipation (Phase 2)
│   │   └── governance.py      # Audit, ComplianceIssue (Phase 2)
│   ├── routes/
│   │   ├── main.py            # landing page
│   │   ├── auth.py            # login/logout/OTP/password/profile/activity log
│   │   ├── dashboard.py       # role-routed dashboard
│   │   ├── environmental.py   # carbon ledger + emission factor CRUD (Phase 2)
│   │   ├── social.py          # CSR activity + participation CRUD (Phase 2)
│   │   └── governance.py      # audit + compliance issue CRUD (Phase 2)
│   ├── utils/
│   │   ├── rbac.py            # @role_required / @permission_required decorators
│   │   ├── forms.py           # WTForms with password-policy validation (auth)
│   │   ├── esg_forms.py       # WTForms for environmental/social/governance (Phase 2)
│   │   ├── email.py           # OTP email sender
│   │   └── seed.py            # seeds roles/permissions/demo data
│   ├── templates/
│   │   ├── base.html / layout_app.html
│   │   ├── landing.html
│   │   ├── partials/          # sidebar, topbar, flash messages
│   │   ├── auth/               # login, forgot/reset password, OTP, profile, etc.
│   │   ├── dashboard/          # 7 role-specific dashboards
│   │   ├── environmental/      # transactions, factors (Phase 2)
│   │   ├── social/              # activities, activity detail (Phase 2)
│   │   ├── governance/          # audits, compliance issues (Phase 2)
│   │   └── errors/             # 403 / 404 / 500
│   └── static/
│       ├── css/theme.css       # design tokens (light/dark), app shell
│       ├── css/landing.css     # landing page styles
│       └── js/                 # theme toggle, animated stat counters
```

## Security Implemented

- Bcrypt password hashing
- CSRF protection (Flask-WTF) on every form
- Rate limiting on login (10/min) and forgot-password (5/min)
- Account lockout after 5 failed attempts (15 min)
- Session timeout + secure/httponly cookies
- Security headers (X-Content-Type-Options, X-Frame-Options, Referrer-Policy)
- Immutable activity/audit logging
- Password policy enforced via regex (8+ chars, upper/lower/digit/symbol)
- Permission checks and org-scoped queries on every Phase 2 CRUD route

## Next Phases

- **Phase 3**: Real dashboard widgets (Chart.js) fed by the environmental/social/governance data, gamification engine (XP/badges/challenges/leaderboard), notification system
- **Phase 4**: Report generation (PDF/Excel/CSV with embedded charts), AI features (score prediction, anomaly detection, recommendation engine)

