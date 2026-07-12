from datetime import datetime
from flask_login import UserMixin
from app.extensions import db, bcrypt
from app.models.base import BaseModel


# ---------------------------------------------------------------------------
# RBAC core: Role <-> Permission (many-to-many via RolePermission),
# User -> Role (many-to-one). Seven fixed system roles are seeded by
# app/utils/seed.py, but permissions remain data-driven so new ones can be
# added per module without a schema change.
# ---------------------------------------------------------------------------

SYSTEM_ROLES = [
    "super_admin",
    "org_admin",
    "department_manager",
    "employee",
    "auditor",
    "csr_manager",
    "viewer",
]


class Permission(BaseModel):
    __tablename__ = "permissions"

    code = db.Column(db.String(100), unique=True, nullable=False)  # e.g. "carbon.create"
    module = db.Column(db.String(50), nullable=False, index=True)  # e.g. "environmental"
    description = db.Column(db.String(255))

    def __repr__(self):
        return f"<Permission {self.code}>"


class RolePermission(db.Model):
    """Join table: which permissions a role has."""

    __tablename__ = "role_permissions"

    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), primary_key=True)
    permission_id = db.Column(db.Integer, db.ForeignKey("permissions.id"), primary_key=True)


class Role(BaseModel):
    __tablename__ = "roles"

    name = db.Column(db.String(50), unique=True, nullable=False)  # matches SYSTEM_ROLES
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    is_system_role = db.Column(db.Boolean, default=True, nullable=False)

    permissions = db.relationship(
        "Permission", secondary="role_permissions", backref="roles", lazy="joined"
    )
    users = db.relationship("User", backref="role", lazy="dynamic", foreign_keys="User.role_id")

    def has_permission(self, code: str) -> bool:
        return any(p.code == code for p in self.permissions)

    def __repr__(self):
        return f"<Role {self.name}>"


class User(BaseModel, UserMixin):
    __tablename__ = "users"

    organization_id = db.Column(
        db.Integer, db.ForeignKey("organizations.id"), nullable=True, index=True
    )
    department_id = db.Column(
        db.Integer, db.ForeignKey("departments.id"), nullable=True, index=True
    )
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False, index=True)

    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    avatar_path = db.Column(db.String(255))
    designation = db.Column(db.String(100))

    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_email_verified = db.Column(db.Boolean, default=False, nullable=False)

    # Security
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)
    last_login_at = db.Column(db.DateTime, nullable=True)
    last_login_ip = db.Column(db.String(45))
    password_changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    must_change_password = db.Column(db.Boolean, default=False, nullable=False)

    # Gamification snapshot (denormalized for fast dashboard reads;
    # authoritative ledger lives in the gamification module tables built later)
    xp_points = db.Column(db.Integer, default=0, nullable=False)
    coins = db.Column(db.Integer, default=0, nullable=False)
    level = db.Column(db.Integer, default=1, nullable=False)

    department = db.relationship(
        "Department", backref="employees", foreign_keys=[department_id]
    )

    __table_args__ = (
        db.Index("ix_user_org_role", "organization_id", "role_id"),
    )

    # --- password helpers -------------------------------------------------
    def set_password(self, raw_password: str) -> None:
        self.password_hash = bcrypt.generate_password_hash(raw_password).decode("utf-8")
        self.password_changed_at = datetime.utcnow()

    def check_password(self, raw_password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, raw_password)

    # --- account lockout helpers -------------------------------------------
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_MINUTES = 15

    def register_failed_login(self):
        from datetime import timedelta
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= self.MAX_FAILED_ATTEMPTS:
            self.locked_until = datetime.utcnow() + timedelta(minutes=self.LOCKOUT_MINUTES)

    def register_successful_login(self, ip_address: str = None):
        self.failed_login_attempts = 0
        self.locked_until = None
        self.last_login_at = datetime.utcnow()
        if ip_address:
            self.last_login_ip = ip_address

    def is_locked(self) -> bool:
        return bool(self.locked_until and self.locked_until > datetime.utcnow())

    # --- convenience --------------------------------------------------------
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def has_permission(self, code: str) -> bool:
        return self.role.has_permission(code) if self.role else False

    def has_role(self, *role_names) -> bool:
        return self.role is not None and self.role.name in role_names

    def get_id(self):
        # Flask-Login requires a string
        return str(self.id)

    def __repr__(self):
        return f"<User {self.email}>"
