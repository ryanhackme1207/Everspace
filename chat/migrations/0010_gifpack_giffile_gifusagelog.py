# Generated migration for GIF system

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0009_gift_gifttransaction'),  # After the gift migration
    ]

    operations = [
        migrations.CreateModel(
            name='GifPack',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('icon', models.CharField(max_length=50)),
                ('order', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='GifFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('gif_file', models.FileField(upload_to='gifs/')),
                ('thumbnail', models.ImageField(blank=True, null=True, upload_to='gif_thumbnails/')),
                ('tags', models.CharField(blank=True, max_length=500)),
                ('category', models.CharField(blank=True, max_length=50)),
                ('source', models.CharField(blank=True, max_length=200)),
                ('file_size', models.IntegerField(default=0)),
                ('width', models.IntegerField(default=0)),
                ('height', models.IntegerField(default=0)),
                ('duration', models.FloatField(default=0)),
                ('is_animated', models.BooleanField(default=True)),
                ('order', models.IntegerField(default=0)),
                ('views', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('pack', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gifs', to='chat.gifpack')),
            ],
            options={
                'ordering': ['pack', 'order', '-views'],
            },
        ),
        migrations.CreateModel(
            name='GifUsageLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_text', models.TextField(blank=True)),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('gif', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usage_logs', to='chat.giffile')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chat.room')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'ordering': ['-sent_at'],
            },
        ),
        migrations.AddIndex(
            model_name='giffile',
            index=models.Index(fields=['pack', 'created_at'], name='chat_giffile_pack_created_idx'),
        ),
        migrations.AddIndex(
            model_name='giffile',
            index=models.Index(fields=['tags'], name='chat_giffile_tags_idx'),
        ),
        migrations.AddIndex(
            model_name='gifusagelog',
            index=models.Index(fields=['user', 'sent_at'], name='chat_gifusage_user_sent_idx'),
        ),
        migrations.AddIndex(
            model_name='gifusagelog',
            index=models.Index(fields=['gif', 'sent_at'], name='chat_gifusage_gif_sent_idx'),
        ),
    ]
