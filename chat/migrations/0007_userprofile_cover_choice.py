from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('chat', '0006_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='cover_choice',
            field=models.CharField(max_length=50, blank=True, default=''),
        ),
    ]
