from django.db import migrations


def replace_department_word(apps, schema_editor):
    Department = apps.get_model('accounts', 'Department')
    for dept in Department.objects.all():
        if dept.description and 'department' in dept.description.lower():
            dept.description = dept.description.replace(' department', ' company').replace('Department', 'Company')
            dept.save()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_alter_department_options_kpifile_kpi_score_and_more'),
    ]

    operations = [
        migrations.RunPython(replace_department_word, migrations.RunPython.noop),
    ]
