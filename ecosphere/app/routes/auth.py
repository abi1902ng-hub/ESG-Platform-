from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user

from app.extensions import db, limiter
from app.models.user import User
from app.models.otp import OTPToken
from app.models.audit import ActivityLog
from app.utils.forms import (
    LoginForm, ForgotPasswordForm, VerifyOTPForm, ResetPasswordForm,
    ChangePasswordForm, ProfileForm,
)
from app.utils.email import send_otp_email

auth_bp = Blueprint("auth", __name__, template_folder="../templates/auth")


def _client_ip():
    return request.headers.get("X-Forwarded-For", request.remote_addr)


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip(), is_deleted=False).first()

        if user and user.is_locked():
            flash("Account temporarily locked due to too many failed attempts. Try again later.", "danger")
            return render_template("auth/login.html", form=form)

        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash("Your account has been deactivated. Contact your administrator.", "danger")
                return render_template("auth/login.html", form=form)

            user.register_successful_login(ip_address=_client_ip())
            ActivityLog.log(
                action="login", user_id=user.id, organization_id=user.organization_id,
                module="auth", description="User logged in",
                ip_address=_client_ip(), user_agent=str(request.user_agent),
            )
            db.session.commit()

            login_user(user, remember=form.remember_me.data)
            session.permanent = True
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard.index"))

        if user:
            user.register_failed_login()
            db.session.commit()

        flash("Invalid email or password.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    ActivityLog.log(
        action="logout", user_id=current_user.id, organization_id=current_user.organization_id,
        module="auth", description="User logged out",
        ip_address=_client_ip(), user_agent=str(request.user_agent),
    )
    db.session.commit()
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip(), is_deleted=False).first()
        if user:
            token = OTPToken.create_for_user(user.id, purpose="password_reset")
            db.session.commit()
            send_otp_email(user.email, user.first_name, token.code, "password_reset")
            session["reset_user_id"] = user.id
        # Always show the same message to avoid leaking which emails exist
        flash("If that email exists, an OTP has been sent.", "info")
        return redirect(url_for("auth.verify_otp"))
    return render_template("auth/forgot_password.html", form=form)


@auth_bp.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    user_id = session.get("reset_user_id")
    if not user_id:
        return redirect(url_for("auth.forgot_password"))

    form = VerifyOTPForm()
    if form.validate_on_submit():
        token = (
            OTPToken.query.filter_by(user_id=user_id, purpose="password_reset", is_used=False)
            .order_by(OTPToken.created_at.desc())
            .first()
        )
        if token and token.is_valid(form.code.data):
            token.mark_used()
            db.session.commit()
            session["otp_verified"] = True
            return redirect(url_for("auth.reset_password"))
        flash("Invalid or expired OTP.", "danger")

    return render_template("auth/verify_otp.html", form=form)


@auth_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    user_id = session.get("reset_user_id")
    if not user_id or not session.get("otp_verified"):
        return redirect(url_for("auth.forgot_password"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = db.session.get(User, user_id)
        user.set_password(form.password.data)
        user.must_change_password = False
        db.session.commit()

        session.pop("reset_user_id", None)
        session.pop("otp_verified", None)

        flash("Password reset successfully. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", form=form)


@auth_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("Current password is incorrect.", "danger")
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash("Password changed successfully.", "success")
            return redirect(url_for("dashboard.index"))
    return render_template("auth/change_password.html", form=form)


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.phone = form.phone.data
        current_user.designation = form.designation.data
        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("auth.profile"))
    return render_template("auth/profile.html", form=form)


@auth_bp.route("/activity-log")
@login_required
def activity_log():
    page = request.args.get("page", 1, type=int)
    logs = (
        ActivityLog.query.filter_by(user_id=current_user.id)
        .order_by(ActivityLog.created_at.desc())
        .paginate(page=page, per_page=20)
    )
    return render_template("auth/activity_log.html", logs=logs)
