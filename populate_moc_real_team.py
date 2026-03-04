#!/usr/bin/env python
"""
Populate Magnum Opus Consultants - 'Magnum Opus' department
"""

import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
    import django
    django.setup()

from django.contrib.auth.models import User
from faker import Faker
from accounts.models import Department, UserProfile

fake = Faker()  # default locale

DEFAULT_PASSWORD = "moc2026"

def create_user(username, first_name, last_name, password=DEFAULT_PASSWORD):
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "email": f"{username}@moc-pty.com",
            "first_name": first_name,
            "last_name": last_name,
        }
    )
    if created:
        user.set_password(password)
        user.save()
        print(f"Added user: {first_name} {last_name} ({username})")
    else:
        print(f"Skipped (exists): {first_name} {last_name} ({username})")
    return user

def get_department():
    try:
        return Department.objects.get(name="Magnum Opus")
    except Department.DoesNotExist:
        print("ERROR: Department 'Magnum Opus' not found. Create it in admin first.")
        return None

def create_profile(user, dept, job_title, reports_to=None, order=10):
    if not dept:
        return None
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            "department": dept,
            "job_title": job_title,
            "phone_number": fake.phone_number()[:20],
            "hierarchy_order": order,
            "reports_to": reports_to,
        }
    )
    if created:
        print(f"  └─ Added profile: {job_title}")
    else:
        print(f"  └─ Profile exists: {job_title}")
    return profile

def populate():
    print("=== Populating Magnum Opus Consultants Leadership ===\n")

    dept = get_department()
    if not dept:
        return

    # CEO
    ceo = create_user("a.visagie", "Armand", "Visagie")
    ceo_prof = create_profile(ceo, dept, "Chief Executive Officer", order=5)

    # Business Development
    waldo = create_user("w.gaybba", "Waldo", "Gaybba")
    create_profile(waldo, dept, "Head of Business Development", reports_to=ceo_prof, order=20)

    # Operations
    anthony = create_user("a.penzes", "Anthony", "Penzes")
    create_profile(anthony, dept, "Head of Operations", reports_to=ceo_prof, order=25)

    # Marketing
    jane = create_user("j.greyling", "Jané", "Greyling")
    create_profile(jane, dept, "Head of Marketing", reports_to=ceo_prof, order=30)

    print("\nDone populating MOC leadership.")
    print(f"Total users: {User.objects.count()}")
    print(f"Total profiles: {UserProfile.objects.count()}")

if __name__ == "__main__":
    try:
        populate()
    except Exception as e:
        print(f"Error: {e}")