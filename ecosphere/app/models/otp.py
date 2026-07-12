import random
from datetime import datetime, timedelta
from app.extensions import db


class OTPToken(db.Model):
    """
    One-time-password tokens used for:
      - email verification at signup
      - forgot-password flow
    Tokens are single-use and time-limited (see Config.OTP_EXPIRY_MINUTES).
    """

    __tablename__ = "otp_tokens"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    code = db.Column(db.String(10), nullable=False)
    purpose = db.Column(db.String(30), nullable=False)  # "email_verification" | "password_reset"
    is_used = db.Column(db.Boolean, default=False, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", foreign_keys=[user_id])

    @staticmethod
    def generate_code() -> str:
        return f"{random.randint(0, 999999):06d}"

    @classmethod
    def create_for_user(cls, user_id: int, purpose: str, expiry_minutes: int = 10):
        token = cls(
            user_id=user_id,
            code=cls.generate_code(),
            purpose=purpose,
            expires_at=datetime.utcnow() + timedelta(minutes=expiry_minutes),
        )
        db.session.add(token)
        return token

    def is_valid(self, code: str) -> bool:
        return (
            not self.is_used
            and self.code == code
            and self.expires_at > datetime.utcnow()
        )

    def mark_used(self):
        self.is_used = True
