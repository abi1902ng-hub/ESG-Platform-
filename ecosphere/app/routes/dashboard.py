from flask import Blueprint, render_template
from flask_login import login_required, current_user

dashboard_bp = Blueprint("dashboard", __name__, template_folder="../templates/dashboard")


# Role -> dashboard template mapping. Each role sees a different landing
# view; the underlying data widgets are wired up in later phases
# (environmental/social/governance/gamification modules).
ROLE_TEMPLATES = {
    "super_admin": "dashboard/super_admin.html",
    "org_admin": "dashboard/org_admin.html",
    "department_manager": "dashboard/manager.html",
    "employee": "dashboard/employee.html",
    "auditor": "dashboard/auditor.html",
    "csr_manager": "dashboard/csr_manager.html",
    "viewer": "dashboard/viewer.html",
}


@dashboard_bp.route("/")
@login_required
def index():
    role_name = current_user.role.name if current_user.role else "viewer"
    template = ROLE_TEMPLATES.get(role_name, "dashboard/viewer.html")
    return render_template(template, role_name=role_name)
