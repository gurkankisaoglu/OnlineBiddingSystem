# Generated by Django 3.0 on 2019-12-17 20:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ciftlikbank', '0002_auto_20191217_1905'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=100)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ciftlikbank.Person')),
            ],
        ),
        migrations.CreateModel(
            name='SellItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=30)),
                ('itemtype', models.CharField(max_length=30)),
                ('description', models.CharField(max_length=30)),
                ('auction_type', models.CharField(max_length=30)),
                ('image', models.ImageField(upload_to='')),
                ('state', models.CharField(choices=[('onhold', 'ONHOLD'), ('active', 'ACTIVE'), ('sold', 'SOLD')], default='onhold', max_length=6)),
                ('auction_started', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('current_bidder', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='current_bidder', to='ciftlikbank.Person')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owner', to='ciftlikbank.Person')),
            ],
        ),
        migrations.CreateModel(
            name='BidRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('bidder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ciftlikbank.Person')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ciftlikbank.SellItem')),
            ],
        ),
    ]