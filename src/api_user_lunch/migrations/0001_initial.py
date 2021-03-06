# Generated by Django 2.2.7 on 2020-09-30 10:16

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('api_user', '0001_initial'),
        ('api_lunch', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserLunch',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('date', models.DateField(default=django.utils.timezone.now, null=True)),
                ('has_veggie', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('lunch', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api_lunch.Lunch')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api_user.Profile')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
