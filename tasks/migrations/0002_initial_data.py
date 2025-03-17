from django.db import migrations

def add_initial_statuses(apps, schema_editor):
    Status = apps.get_model('tasks', 'Status')
    statuses = ['active', 'completed', 'archived']
    for status in statuses:
        Status.objects.get_or_create(type=status)

def reverse_add_initial_statuses(apps, schema_editor):
    Status = apps.get_model('tasks', 'Status')
    Status.objects.filter(type__in=['active', 'completed', 'archived']).delete()

def create_priorities(apps, schema_editor):
    Priority = apps.get_model('tasks', 'Priority')
    TYPE_WEIGHT_MAP = {
        'high': 4,
        'medium': 3,
        'low': 2,
        'default': 1
    }
    for type_name, weight in TYPE_WEIGHT_MAP.items():
        Priority.objects.update_or_create(
            type=type_name,
            defaults={'weight': weight}
        )

def reverse_priorities(apps, schema_editor):
    Priority = apps.get_model('tasks', 'Priority')
    TYPE_WEIGHT_MAP = {
        'high': 4,
        'medium': 3,
        'low': 2,
        'default': 1
    }
    Priority.objects.filter(type__in=TYPE_WEIGHT_MAP.keys()).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            add_initial_statuses,
            reverse_code=reverse_add_initial_statuses
        ),
        migrations.RunPython(
            create_priorities,
            reverse_code=reverse_priorities
        ),
    ]