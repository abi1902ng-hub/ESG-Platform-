"""
Seeds the database with:
  - 7 system roles
  - a baseline permission set per module (extended in later phases)
  - a demo organization + department
  - one demo user per role, so every dashboard can be reviewed immediately

Run with:  python -m app.utils.seed
"""
from app import create_app
from app.extensions import db
from app.models.user import User, Role, Permission, SYSTEM_ROLES
from app.models.organization import Organization, Department


ROLE_META = {
    "super_admin": ("Super Admin", "Full platform access across all organizations."),
    "org_admin": ("Organization Admin", "Full access within their organization."),
    "department_manager": ("Department Manager", "Manages a department's team, approvals, and goals."),
    "employee": ("Employee", "Logs personal activity, CSR participation, and challenges."),
    "auditor": ("Auditor", "Conducts audits and tracks compliance issues."),
    "csr_manager": ("CSR Manager", "Manages CSR activities, challenges, and rewards."),
    "viewer": ("Viewer", "Read-only access to ESG performance."),
}

# Baseline permission catalog. Later phases (environmental / social /
# governance / gamification) will register their own module-specific codes
# through the same Permission table without altering this seed's shape.
BASE_PERMISSIONS = [
    ("user.manage", "admin", "Create, update, deactivate users"),
    ("role.manage", "admin", "Manage roles and permissions"),
    ("department.manage", "admin", "Manage departments"),
    ("org.settings", "admin", "Manage organization settings"),
    ("report.view", "reports", "View generated reports"),
    ("report.export", "reports", "Export reports (PDF/Excel/CSV)"),
    ("audit.conduct", "governance", "Conduct internal audits"),
    ("compliance.manage", "governance", "Manage compliance issues"),
    ("csr.manage", "social", "Manage CSR activities and approvals"),
    ("challenge.manage", "gamification", "Manage challenges and rewards"),
    ("carbon.log", "environmental", "Log carbon-relevant transactions"),
]

ROLE_PERMISSIONS = {
    "super_admin": [code for code, _, _ in BASE_PERMISSIONS],
    "org_admin": [code for code, _, _ in BASE_PERMISSIONS],
    "department_manager": ["report.view", "csr.manage", "challenge.manage", "carbon.log"],
    "employee": ["carbon.log"],
    "auditor": ["audit.conduct", "compliance.manage", "report.view", "report.export"],
    "csr_manager": ["csr.manage", "challenge.manage", "report.view"],
    "viewer": ["report.view"],
}

DEMO_PASSWORD = "Ecosphere@123"


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        # --- roles -----------------------------------------------------
        roles = {}
        for name in SYSTEM_ROLES:
            role = Role.query.filter_by(name=name).first()
            if not role:
                display_name, description = ROLE_META[name]
                role = Role(name=name, display_name=display_name, description=description)
                db.session.add(role)
            roles[name] = role
        db.session.flush()

        # --- permissions -------------------------------------------------
        perms = {}
        for code, module, description in BASE_PERMISSIONS:
            perm = Permission.query.filter_by(code=code).first()
            if not perm:
                perm = Permission(code=code, module=module, description=description)
                db.session.add(perm)
            perms[code] = perm
        db.session.flush()

        for role_name, codes in ROLE_PERMISSIONS.items():
            role = roles[role_name]
            for code in codes:
                if perms[code] not in role.permissions:
                    role.permissions.append(perms[code])

        # --- demo organization + department -----------------------------
        org = Organization.query.filter_by(name="AstraVantage Demo Corp").first()
        if not org:
            org = Organization(
                name="AstraVantage Demo Corp",
                industry="Technology",
                country="India",
                timezone="Asia/Kolkata",
            )
            db.session.add(org)
            db.session.flush()

        dept = Department.query.filter_by(organization_id=org.id, code="OPS").first()
        if not dept:
            dept = Department(
                organization_id=org.id,
                name="Operations",
                code="OPS",
                description="Core operations department (demo seed).",
            )
            db.session.add(dept)
            db.session.flush()

        # --- one demo user per role ---------------------------------------
        for role_name in SYSTEM_ROLES:
            email = f"{role_name}@ecosphere.demo"
            user = User.query.filter_by(email=email).first()
            if user:
                continue
            display_name, _ = ROLE_META[role_name]
            first, *rest = display_name.split(" ")
            user = User(
                organization_id=org.id if role_name != "super_admin" else None,
                department_id=dept.id if role_name in ("department_manager", "employee") else None,
                role_id=roles[role_name].id,
                first_name=first,
                last_name=" ".join(rest) or "Demo",
                email=email,
                is_active=True,
                is_email_verified=True,
            )
            user.set_password(DEMO_PASSWORD)
            db.session.add(user)

        db.session.commit()
        print("Seed complete.")
        print(f"Demo password for all seeded users: {DEMO_PASSWORD}")
        for role_name in SYSTEM_ROLES:
            print(f"  {role_name:22s} -> {role_name}@ecosphere.demo")


if __name__ == "__main__":
    seed()
