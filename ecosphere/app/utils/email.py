from flask import current_app, render_template
from flask_mail import Message
from app.extensions import mail


def send_otp_email(to_email: str, user_name: str, code: str, purpose: str):
    """
    Sends an OTP email. In development, if mail credentials are not
    configured, this silently no-ops after logging to console so the
    hackathon demo flow doesn't break without SMTP set up.
    """
    subject_map = {
        "email_verification": "Verify your EcoSphere account",
        "password_reset": "Reset your EcoSphere password",
    }
    subject = subject_map.get(purpose, "Your EcoSphere OTP Code")

    if not current_app.config.get("MAIL_USERNAME"):
        current_app.logger.info(f"[DEV OTP EMAIL] to={to_email} code={code} purpose={purpose}")
        return

    msg = Message(subject=subject, recipients=[to_email])
    msg.body = (
        f"Hi {user_name},\n\n"
        f"Your EcoSphere verification code is: {code}\n"
        f"This code expires in {current_app.config.get('OTP_EXPIRY_MINUTES', 10)} minutes.\n\n"
        f"If you did not request this, please ignore this email.\n\n"
        f"— EcoSphere Team"
    )
    mail.send(msg)
