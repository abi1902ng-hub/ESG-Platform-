"""
Shared mixins for every model in the platform:
- UUID-free integer PKs (simpler for a hackathon build, indexed by default)
- created_at / updated_at / created_by / updated_by audit fields
- soft delete (is_deleted flag instead of physical delete)
"""
from datetime import datetime
from app.extensions import db


class AuditMixin:
    """Adds created/updated timestamps and actor tracking to any model."""

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    @db.declared_attr
    def created_by(cls):
        return db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    @db.declared_attr
    def updated_by(cls):
        return db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)


class SoftDeleteMixin:
    """Adds a soft-delete flag so records are never physically removed."""

    is_deleted = db.Column(db.Boolean, default=False, nullable=False, index=True)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None


class BaseModel(db.Model, AuditMixin, SoftDeleteMixin):
    """Abstract base: every business table should inherit this."""

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
