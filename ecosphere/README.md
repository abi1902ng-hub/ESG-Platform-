# EcoSphere — ESG Management Platform

Enterprise-grade ESG (Environmental, Social, Governance) management platform built for the Odoo Hackathon. Pure Python backend (Flask + SQLAlchemy + PostgreSQL), Bootstrap/Jinja frontend, Chart.js for analytics.

## Status: Phase 1 Complete

This phase delivers the **foundation** the rest of the platform builds on:

- ✅ Full RBAC with 7 system roles (Super Admin, Org Admin, Department Manager, Employee, Auditor, CSR Manager, Viewer)
- ✅ Complete authentication: login, logout, forgot password + email OTP, change password, profile, activity log, session timeout, account lockout, rate limiting, CSRF protection, password hashing (bcrypt)
- ✅ Multi-tenant data model: Organization → Department → User, with audit fields (created_by/updated_by/timestamps) and soft delete on every table
- ✅ Role-differentiated dashboards (7 distinct views)
- ✅ Professional SaaS landing page: hero, animated stats, features, ESG pillars, testimonials, pricing, FAQ, dark/light mode
- ✅ Enterprise UI shell: sidebar, topbar, notifications dropdown, theme toggle — all role-aware
- ✅ Immutable ActivityLog audit trail
- ✅ Seed script with one demo user per role

**Not yet built** (Phases 2–4, by design): Environmental module (carbon engine), Social module (CSR), Governance module (audits/compliance), Gamification (XP/badges/challenges), Reports (PDF/Excel export), AI features, master data CRUD screens. The schema and permission system are already structured so these slot in without refactoring auth/RBAC.

## Setup

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # then edit .env with real DB/mail credentials

# Create PostgreSQL database first:
#   createdb ecosphere_db

python -m app.utils.seed           # creates roles, permissions, demo org, and 7 demo users
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
│   │   └── otp.py             # OTPToken (email verification / reset)
│   ├── routes/
│   │   ├── main.py            # landing page
│   │   ├── auth.py            # login/logout/OTP/password/profile/activity log
│   │   └── dashboard.py       # role-routed dashboard
│   ├── utils/
│   │   ├── rbac.py            # @role_required / @permission_required decorators
│   │   ├── forms.py           # WTForms with password-policy validation
│   │   ├── email.py           # OTP email sender
│   │   └── seed.py            # seeds roles/permissions/demo data
│   ├── templates/
│   │   ├── base.html / layout_app.html
│   │   ├── landing.html
│   │   ├── partials/          # sidebar, topbar, flash messages
│   │   ├── auth/               # login, forgot/reset password, OTP, profile, etc.
│   │   ├── dashboard/          # 7 role-specific dashboards
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

## Next Phases

- **Phase 2**: Environmental (carbon engine + emission factors), Social (CSR), Governance (audits/compliance) modules with full CRUD
- **Phase 3**: Real dashboard widgets (Chart.js), gamification engine (XP/badges/challenges/leaderboard), notification system
- **Phase 4**: Report generation (PDF/Excel/CSV with embedded charts), AI features (score prediction, anomaly detection, recommendation engine)
