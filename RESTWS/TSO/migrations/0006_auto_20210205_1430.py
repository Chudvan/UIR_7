# Generated by Django 3.1.6 on 2021-02-05 11:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('TSO', '0005_auto_20210205_1348'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telephone', models.CharField(max_length=20, verbose_name='Телефон')),
                ('email', models.CharField(max_length=50, verbose_name='email')),
            ],
        ),
        migrations.CreateModel(
            name='OrderOther',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='PayType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payType', models.CharField(choices=[('CASH', 'CASH'), ('CARD', 'CARD'), ('PCARD', 'PCARD')], max_length=30, unique=True, verbose_name='Тип оплаты')),
            ],
        ),
        migrations.CreateModel(
            name='OrderPetrol',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('volume', models.FloatField(verbose_name='Объём')),
                ('amount', models.FloatField(verbose_name='Заплачено')),
                ('change', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='TSO.orderother', verbose_name='Перевод сдачи')),
                ('customerDetails', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='TSO.customerdetail', verbose_name='Персональные данные')),
                ('orderId', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='TSO.order', verbose_name='Номер заказа')),
                ('payType', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='TSO.paytype', verbose_name='Тип оплаты')),
                ('petrol', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='TSO.petrol', verbose_name='НП')),
                ('pump', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='TSO.pumpstate', verbose_name='Состояние ТРК')),
            ],
        ),
        migrations.AddConstraint(
            model_name='customerdetail',
            constraint=models.UniqueConstraint(fields=('telephone', 'email'), name='uniqueCustomer'),
        ),
    ]