from django.db import migrations


def seed_departments(apps, schema_editor):
    Department = apps.get_model('accounts', 'Department')
    departments = [
        {'name': 'Food Safety Agency', 'description': 'Food safety and compliance department'},
        {'name': 'ISCM', 'description': 'Integrated supply chain management department'},
        {'name': 'Eclick', 'description': 'Eclick digital services department'},
        {'name': 'Magnum Opus', 'description': 'Magnum Opus operations department'},
    ]
    for dept in departments:
        Department.objects.get_or_create(name=dept['name'], defaults=dept)


def reverse_seed(apps, schema_editor):
    Department = apps.get_model('accounts', 'Department')
    Department.objects.filter(
        name__in=['Food Safety Agency', 'ISCM', 'Eclick', 'Magnum Opus']
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_departments, reverse_seed),
    ]
