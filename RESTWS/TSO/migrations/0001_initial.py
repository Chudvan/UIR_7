# Generated by Django 3.1.6 on 2021-02-04 12:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ErrorType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('errortype', models.CharField(choices=[('OK', 'OK'), ('SCANER', 'SCANER'), ('PAPER', 'PAPER'), ('CURRENCYDETECTOR', 'CURRENCYDETECTOR'), ('INK', 'INK'), ('POS', 'POS')], max_length=50, unique=True, verbose_name='Ограничения ТСО')),
            ],
        ),
        migrations.CreateModel(
            name='Petrol',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('petrolType', models.IntegerField(choices=[(1, 'OR92'), (2, 'OR95'), (3, 'OR98'), (4, 'DIESEL')], verbose_name='Вид НП')),
                ('price', models.FloatField(verbose_name='Цена')),
            ],
        ),
        migrations.CreateModel(
            name='Pump',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(unique=True, verbose_name='Номер ТРК')),
            ],
        ),
        migrations.CreateModel(
            name='Terminal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('terminalNumber', models.IntegerField(unique=True, verbose_name='Номер Терминала')),
            ],
        ),
        migrations.CreateModel(
            name='PumpState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('status', models.IntegerField(choices=[(1, 'FREE'), (2, 'BUSY'), (3, 'UNAVAILABLE')], verbose_name='Статус ТРК')),
                ('number', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='TSO.pump', verbose_name='Номер ТРК')),
            ],
        ),
        migrations.CreateModel(
            name='Error',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dateTime', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('errorType', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='TSO.errortype', verbose_name='Ограничения ТСО')),
                ('terminalNumber', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='TSO.terminal', verbose_name='Номер Терминала')),
            ],
        ),
    ]
