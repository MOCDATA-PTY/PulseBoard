# KPI Management System

## How to Run

```bash
cd "/home/ethan/Desktop/Gerlad Project"
python3 manage.py runserver
```

Open http://127.0.0.1:8000/

## Login Credentials

### Manager / Admin

| Username | Password | Role |
|----------|----------|------|
| ethan | password123 | Admin / Manager (manages all departments) |

### Department Users

| Username | Password | Name | Department |
|----------|----------|------|------------|
| fsa_user | test1234 | Sarah Mitchell | Food Safety Agency |
| iscm_user | test1234 | James Rivera | ISCM |
| eclick_user | test1234 | Mia Chen | Eclick |
| magnum_user | test1234 | Daniel Brooks | Magnum Opus |

## What Each Role Sees

**Manager (ethan):**
- Admin Center with all users and departments
- Can add new users and assign them to departments
- Can rate any employee on KPIs (Productivity, Quality, Teamwork, Communication, Initiative, Attendance)
- Can view KPI reports for any employee
- Can click into any department to see its members

**Department Users (fsa_user, iscm_user, eclick_user, magnum_user):**
- Branded dashboard matching their department's theme
- Their own profile and KPI scores
- "My Department" page listing all colleagues
- Can view profiles of colleagues in the same department only
- Cannot see other departments or users outside their department
