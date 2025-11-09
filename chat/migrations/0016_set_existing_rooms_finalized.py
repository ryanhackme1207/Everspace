# Generated manually to set existing rooms as finalized

from django.db import migrations


def set_existing_rooms_finalized(apps, schema_editor):
    """Mark all existing rooms as finalized"""
    Room = apps.get_model('chat', 'Room')
    Room.objects.all().update(is_finalized=True)


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0015_room_is_finalized'),
    ]

    operations = [
        migrations.RunPython(set_existing_rooms_finalized, migrations.RunPython.noop),
    ]
