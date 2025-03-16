from django.db import migrations

def create_priorities(apps, schema_editor):
    Priority = apps.get_model('tasks', 'Priority')

    for type_name in Priority.TYPE_WEIGHT_MAP:
        Priority.objects.get_or_create(type=type_name)


class Migration(migrations.Migration):
    dependencies = [('tasks', '0001_initial')]
    operations = [migrations.RunPython(create_priorities)]
