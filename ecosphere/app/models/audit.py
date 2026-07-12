from datetime import datetime
from app.extensions import db


class ActivityLog(db.Model):
    """
    Immutable audit trail. Every meaningful action (login, CRUD, approval,
    export, etc.) writes a row here. Never updated or soft-deleted —
    a real audit log must stay tamper-evident.
    """

    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id"), nullable=True, index=True)

    action = db.Column(db.String(100), nullable=False, index=True)     # e.g. "login", "carbon.create"
    module = db.Column(db.String(50), index=True)                      # e.g. "auth", "environmental"
    entity_type = db.Column(db.String(80))                             # e.g. "CarbonTransaction"
    entity_id = db.Column(db.Integer)
    description = db.Column(db.String(500))

    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = db.relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<ActivityLog {self.action} by user={self.user_id}>"

    @staticmethod
    def log(action, user_id=None, organization_id=None, module=None,
            entity_type=None, entity_id=None, description=None,
            ip_address=None, user_agent=None):
        """Convenience factory + insert, does not commit (caller controls transaction)."""
        entry = ActivityLog(
            action=action,
            user_id=user_id,
            organization_id=organization_id,
            module=module,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.session.add(entry)
        return entry
