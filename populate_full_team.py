#!/usr/bin/env python
"""
populate_full_team.py
Wipes existing users and populates the full Magnum Opus Consultants team
from LinkedIn data.

Managers get password 'moc2026' and is_staff=True.
Employees get unusable passwords (no login).
"""

import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
    import django
    django.setup()

from django.contrib.auth.models import User
from accounts.models import Department, UserProfile


# ── Team data ────────────────────────────────────────────────────────
MANAGERS = [
    # (username, first_name, last_name, job_title, hierarchy_order)
    ("armand",   "Armand",   "Visagie",      "Chief Executive Officer",       5),
    ("waldo",    "Waldo",    "Gaybba",       "Business Development Manager", 20),
    ("anthony",  "Anthony",  "Penzes",       "Operations Manager",           20),
    ("jane",     "Jané",     "de Villiers",  "Strategic Marketing Manager",  20),
    ("ethan",    "Ethan",    "Sevenster",    "Data Analyst",                 20),
]

EMPLOYEES = [
    # (username, first_name, last_name, job_title)
    ("eben",       "Eben",       "Fourie",      "IT Support Manager"),
    ("aveshni",    "Aveshni",    "Govender",    "Financial Operator"),
    ("melissa",    "Melissa",    "van Niekerk", "UX/UI Designer"),
    ("daniel",     "Daniel",     "Wohlfahrt",   "Data Solution Specialist"),
    ("johannes",   "Johannes",   "Ntshegang",   "AI Automation Engineer"),
    ("zamangema",  "Zamangema",  "Kunene",      "Legal Claims & Compliance Officer"),
    ("charles",    "Charles",    "Ndlovu",      "Senior Finance Intern"),
]

MANAGER_PASSWORD = "moc2026"
DEPARTMENT_NAME = "Magnum Opus"


def run():
    # ── Get the department ───────────────────────────────────────────
    try:
        dept = Department.objects.get(name=DEPARTMENT_NAME)
    except Department.DoesNotExist:
        print(f"ERROR: Department '{DEPARTMENT_NAME}' not found. Run migrations first.")
        sys.exit(1)

    # ── Wipe all existing users (and cascaded profiles) ──────────────
    existing = User.objects.all()
    count = existing.count()
    existing.delete()
    print(f"Deleted {count} existing user(s).\n")

    # ── Create managers ──────────────────────────────────────────────
    print("=== Creating Managers (with password) ===")
    ceo_profile = None

    for username, first, last, title, order in MANAGERS:
        user = User.objects.create_user(
            username=username,
            email=f"{username}@moc-pty.com",
            password=MANAGER_PASSWORD,
            first_name=first,
            last_name=last,
        )
        user.is_staff = True
        # Make the CEO a superuser so Django admin remains accessible
        if order == 5:
            user.is_superuser = True
        user.save()

        profile = user.profile
        profile.department = dept
        profile.job_title = title
        profile.hierarchy_order = order
        if ceo_profile and order != 5:
            profile.reports_to = ceo_profile
        profile.save()

        if order == 5:
            ceo_profile = profile

        print(f"  + {first} {last} ({username}) — {title}")

    # ── Create employees (no password) ───────────────────────────────
    print("\n=== Creating Employees (no password) ===")

    for username, first, last, title in EMPLOYEES:
        user = User.objects.create_user(
            username=username,
            email=f"{username}@moc-pty.com",
            password=None,
            first_name=first,
            last_name=last,
        )
        user.set_unusable_password()
        user.is_staff = False
        user.save()

        profile = user.profile
        profile.department = dept
        profile.job_title = title
        profile.hierarchy_order = 100
        if ceo_profile:
            profile.reports_to = ceo_profile
        profile.save()

        print(f"  + {first} {last} ({username}) — {title}")

    # ── Summary ──────────────────────────────────────────────────────
    total = User.objects.count()
    managers = User.objects.filter(is_staff=True).count()
    employees = total - managers
    print(f"\nDone! {total} users total — {managers} managers, {employees} employees.")


if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
