# EcoSphere — ESG Management Platform

Enterprise-grade ESG (Environmental, Social, Governance) management platform built for the Odoo Hackathon. Pure Python backend (Flask + SQLAlchemy + PostgreSQL), Bootstrap/Jinja frontend, Chart.js for analytics.

## Status: Phase 4 Complete

Phase 3 added real dashboard widgets (Chart.js) wired to Phase 2 data, the gamification engine
(XP/badges/challenges/leaderboard), and the notification system. Phase 4 adds:

- ✅ **Report generation**: PDF (reportlab, with native embedded charts), Excel (openpyxl, with
  native embedded charts across a Summary sheet, one data sheet per table, and a Charts sheet),
  and CSV exports for four report types — Full ESG Summary, Environmental/Carbon, Social/CSR, and
  Governance/Compliance. Every generated file is tracked in `generated_reports` (who generated it,
  when, for which org/department/date range) and served through a permission-checked download
  route rather than static hosting.
- ✅ **AI features** (`app/utils/ai_service.py`), built on transparent statistics rather than an
  opaque model so every output is explainable to an auditor:
  - *Score prediction*: OLS trend fit over the carbon ledger's monthly history, forecasting each
    ESG pillar (and overall score) 3 months out, with an R² fit-quality figure.
  - *Anomaly detection*: per-category z-score outlier detection over the carbon transaction ledger
    (an unusual entry is judged against others in its own emission-factor category).
  - *Recommendation engine*: a small rule engine over the same KPI/score data the dashboards
    already compute, so every recommendation cites the concrete number that triggered it.
- ✅ New `/reports` and `/ai` sections in the sidebar, gated by the existing `report.view` /
  `report.export` permissions (no new RBAC codes needed — Phase 2's seed already provisioned them).

**Not yet built**: none — all four phases are complete.

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
│   │   ├── governance.py      # Audit, ComplianceIssue (Phase 2)
│   │   ├── gamification.py    # XPTransaction, Badge, UserBadge, Challenge, ChallengeParticipant (Phase 3)
│   │   ├── notification.py    # Notification (Phase 3)
│   │   └── report.py          # GeneratedReport — export history/metadata (Phase 4)
│   ├── routes/
│   │   ├── main.py            # landing page
│   │   ├── auth.py            # login/logout/OTP/password/profile/activity log
│   │   ├── dashboard.py       # role-routed dashboard
│   │   ├── environmental.py   # carbon ledger + emission factor CRUD (Phase 2)
│   │   ├── social.py          # CSR activity + participation CRUD (Phase 2)
│   │   ├── governance.py      # audit + compliance issue CRUD (Phase 2)
│   │   ├── gamification.py    # challenges + leaderboard (Phase 3)
│   │   ├── notifications.py   # in-app notifications (Phase 3)
│   │   ├── reports.py         # generate/list/download/delete PDF/Excel/CSV reports (Phase 4)
│   │   └── ai_insights.py     # score prediction, anomaly detection, recommendations (Phase 4)
│   ├── utils/
│   │   ├── rbac.py            # @role_required / @permission_required decorators
│   │   ├── forms.py           # WTForms with password-policy validation (auth)
│   │   ├── esg_forms.py       # WTForms for environmental/social/governance (Phase 2)
│   │   ├── gamification_forms.py / gamification_service.py  # XP/badges/challenges engine (Phase 3)
│   │   ├── dashboard_data.py  # shared chart/KPI aggregation queries (Phase 3)
│   │   ├── report_forms.py / report_service.py  # report data assembly + PDF/Excel/CSV renderers (Phase 4)
│   │   ├── ai_service.py      # score prediction / anomaly detection / recommendations (Phase 4)
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
│   │   ├── gamification/        # challenges, leaderboard, badges (Phase 3)
│   │   ├── notifications/       # notification list (Phase 3)
│   │   ├── reports/             # report history + generate modal (Phase 4)
│   │   ├── ai/                  # AI insights dashboard (Phase 4)
│   │   └── errors/             # 403 / 404 / 500
│   └── static/
│       ├── css/theme.css       # design tokens (light/dark), app shell
│       ├── css/landing.css     # landing page styles
│       └── js/                 # theme toggle, animated stat counters, chart theme, notifications
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
- Generated reports served through a permission-checked download route (never static-hosted)


## Reports & AI Insights (Phase 4)

- `/reports` — pick a report type (Full ESG Summary, Environmental, Social/CSR, Governance),
  a format (PDF/Excel/CSV), an optional department, and a date range, then generate. History of
  every past export is listed with download/delete actions. Gated by the `report.view` (browse/
  download) and `report.export` (generate/delete) permissions already provisioned in Phase 2's
  seed script — no migration needed.
- `/ai` — forecast chart for the next 3 months per ESG pillar, a trend-direction summary, a
  carbon-transaction anomaly table (z-score outliers by category), and a prioritized list of
  rule-based recommendations, each naming the metric that triggered it.

