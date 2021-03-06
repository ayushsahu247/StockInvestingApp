# Generated by Django 3.2.5 on 2021-08-17 07:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Investor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.DecimalField(decimal_places=2, default=100000, max_digits=10)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=50)),
                ('companyName', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=1000)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('investor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='investApp.investor')),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='investApp.stock')),
            ],
        ),
        migrations.CreateModel(
            name='Investment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('n_shares', models.IntegerField()),
                ('avg_price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('investor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='investApp.investor')),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='investApp.stock')),
            ],
        ),
    ]
