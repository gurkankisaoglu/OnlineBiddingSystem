# Generated by Django 3.0 on 2019-12-19 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ciftlikbank', '0014_person_verification_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='verification_number',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
