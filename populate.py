#!/usr/bin/env python
"""
populate_moc_real_team.py
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

fake = Faker('en_ZA')

def create_user(username, first_name, last_name, password="moc2026"):
    if User.objects.filter(username=username).exists():
        print(f"Skipped (already exists): {username} ({first_name} {last_name})")
        return User.objects.get(username=username)

    user = User.objects.create_user(
        username=username,
        email=f"{username}@moc-pty.com",
        password=password,
        first_name=first_name,
        last_name=last_name,
    )
    print(f"Added user: {first_name} {last_name} ({username})")
    return user

def get_dept(name):
    try:
        return Department.objects.get(name=name)
    except Department.DoesNotExist:
        return None

def create_profile(user, dept, job_title, reports_to=None, order=10):
    if not dept:
        print(f"  Skipping profile for {user.get_full_name()} — department not found")
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
        print(f"  └─ Added profile: {job_title} (order {order})")
    else:
        print(f"  └─ Profile already exists: {job_title}")
    return profile

def populate_real_team():
    print("=== Adding ONLY real MOC Leadership (from moc-pty.com/about-us) ===\n")

    exec_dept   = get_dept("Executive Leadership") or get_dept("Executive")
    ops_dept    = get_dept("Engineering & Technology") or get_dept("Operations")
    mkt_dept    = get_dept("Marketing & Communications") or get_dept("Marketing")

    fallback_dept = exec_dept

    if not fallback_dept:
        print("ERROR: No Executive/Leadership department found. Create one first.")
        return

    ceo = create_user("a.visagie", "Armand", "Visagie")
    ceo_prof = create_profile(ceo, exec_dept or fallback_dept, "Chief Executive Officer", order=5)

    waldo = create_user("w.gaybba", "Waldo", "Gaybba")
    create_profile(waldo, exec_dept or fallback_dept, "Head of Business Development", reports_to=ceo_prof, order=20)

    anthony = create_user("a.penzes", "Anthony", "Penzes")
    create_profile(anthony, ops_dept or fallback_dept, "Head of Operations", reports_to=ceo_prof, order=25)

    jane = create_user("j.greyling", "Jané", "Greyling")
    create_profile(jane, mkt_dept or fallback_dept, "Head of Marketing", reports_to=ceo_prof, order=30)

    print("\nDone!")
    print(f"Users: {User.objects.count()}")
    print(f"Profiles: {UserProfile.objects.count()}")

if __name__ == "__main__":
    try:
        populate_real_team()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)