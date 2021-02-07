# Generated by Django 3.1.6 on 2021-02-07 11:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('TSO', '0014_auto_20210207_0044'),
    ]

    operations = [
        migrations.CreateModel(
            name='Scan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dateTime', models.DateTimeField(db_index=True)),
                ('barCode', models.CharField(max_length=30, verbose_name='Штрих-код')),
                ('terminalNumber', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='TSO.terminal', verbose_name='Номер Терминала')),
            ],
        ),
    ]
