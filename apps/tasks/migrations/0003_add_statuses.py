from django.db import migrations

def add_initial_statuses(apps, schema_editor):
    Status = apps.get_model('tasks', 'Status')
    statuses = ['active', 'completed', 'archived']

    for status in statuses:
        Status.objects.get_or_create(type=status)

class Migration(migrations.Migration):
    dependencies = [('tasks', '0002_add_priorities')]
    operations = [migrations.RunPython(add_initial_statuses)]
