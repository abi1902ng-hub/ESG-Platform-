from app.extensions import db
from app.models.base import BaseModel


class Organization(BaseModel):
    """A tenant of the platform. EcoSphere supports multiple organizations."""

    __tablename__ = "organizations"

    name = db.Column(db.String(150), nullable=False, unique=True)
    industry = db.Column(db.String(100))
    country = db.Column(db.String(100))
    logo_path = db.Column(db.String(255))
    timezone = db.Column(db.String(50), default="Asia/Kolkata")
    esg_reporting_year_start = db.Column(db.Integer, default=1)  # month, 1=Jan
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # relationships
    departments = db.relationship(
        "Department", backref="organization", lazy="dynamic",
        foreign_keys="Department.organization_id"
    )
    users = db.relationship(
        "User", backref="organization", lazy="dynamic",
        foreign_keys="User.organization_id"
    )

    def __repr__(self):
        return f"<Organization {self.name}>"


class Department(BaseModel):
    """Departments/business units within an organization."""

    __tablename__ = "departments"

    organization_id = db.Column(
        db.Integer, db.ForeignKey("organizations.id"), nullable=False, index=True
    )
    name = db.Column(db.String(150), nullable=False)
    code = db.Column(db.String(30))
    manager_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    manager = db.relationship("User", foreign_keys=[manager_id])

    __table_args__ = (
        db.UniqueConstraint("organization_id", "code", name="uq_dept_org_code"),
    )

    def __repr__(self):
        return f"<Department {self.name}>"
