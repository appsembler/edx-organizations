from django.db import migrations
import uuid

def gen_uuid(apps, schema_editor):
    Organization = apps.get_model('organizations', 'Organization')
    for row in Organization.objects.all():
        row.edx_uuid = uuid.uuid4()
        row.save()

class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0006_organization_uuid'),
    ]

    operations = [
        # omit reverse_code=... if you don't want the migration to be reversible.
        migrations.RunPython(gen_uuid, reverse_code=migrations.RunPython.noop),
    ]
