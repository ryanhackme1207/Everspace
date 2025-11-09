# Generated manually for adding is_finalized field to Room model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0014_gamesession'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='is_finalized',
            field=models.BooleanField(default=False, help_text='Whether room setup is complete'),
        ),
    ]
