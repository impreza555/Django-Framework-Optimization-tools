# Generated by Django 3.2.9 on 2022-01-03 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authapp', '0004_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='langs',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='язык'),
        ),
    ]
