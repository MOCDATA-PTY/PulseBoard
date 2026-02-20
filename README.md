# PulseBoard

A multi-department management platform built with Django. Manage users, departments, KPIs, and org charts with per-department branding.

## How to Run (Development)

```bash
cd "/home/ethan/Desktop/Gerlad Project"
python3 manage.py runserver
```

Open http://127.0.0.1:8000/

## Production Server

- **URL:** http://pulseboard.moc-pty.com
- **Server:** 167.88.43.168
- **Stack:** Gunicorn (port 9200) + Nginx (port 80)
- **Database:** MySQL (`pulseboard`)
- **Project path:** `/var/www/PulseBoard`

## Login Credentials

| Name | Username | Password | Role |
|------|----------|----------|------|
| Gerald MOC | Gerald | PulseBoard2026 | Manager |
| Anthony MOC | Anthony | PulseBoard2026 | Manager |
| Ethan MOC | Ethan | PulseBoard2026 | Manager |

All managers have full Admin Center access.

## Features

- **Admin Center** — Manage users, departments, and KPIs
- **Department Branding** — Each department has customizable colors (primary, hover, accent) and a logo
- **KPI Management** — Upload and track KPI files per employee
- **Org Charts** — Visual hierarchy for each department with drag-and-drop reordering
- **User Profiles** — Profile pictures, job titles, and department assignments
- **Role-Based Access** — Managers see the Admin Center; employees see their department dashboard

## Deployment

```bash
# On the server
cd /var/www/PulseBoard
git pull origin main
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart pulseboard
```
