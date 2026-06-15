# Generated manually during project cleanup.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0003_historico'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='criado_em',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='criado em'),
        ),
        migrations.AddField(
            model_name='cliente',
            name='atualizado_em',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='atualizado em'),
        ),
        migrations.AddField(
            model_name='divida',
            name='data_pagamento',
            field=models.DateTimeField(blank=True, null=True, verbose_name='data de pagamento'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='nome',
            field=models.CharField(max_length=100, verbose_name='nome'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='observacao',
            field=models.TextField(blank=True, verbose_name='observação'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='telefone',
            field=models.CharField(blank=True, max_length=20, verbose_name='telefone'),
        ),
        migrations.AlterField(
            model_name='divida',
            name='cliente',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='dividas', to='clientes.cliente', verbose_name='cliente'),
        ),
        migrations.AlterField(
            model_name='divida',
            name='data_criacao',
            field=models.DateTimeField(auto_now_add=True, verbose_name='data de criação'),
        ),
        migrations.AlterField(
            model_name='divida',
            name='descricao',
            field=models.CharField(max_length=200, verbose_name='descrição'),
        ),
        migrations.AlterField(
            model_name='divida',
            name='status',
            field=models.CharField(choices=[('pendente', 'Pendente'), ('paga', 'Paga')], default='pendente', max_length=20, verbose_name='status'),
        ),
        migrations.AlterField(
            model_name='divida',
            name='valor',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='valor'),
        ),
        migrations.AlterField(
            model_name='historico',
            name='acao',
            field=models.CharField(max_length=255, verbose_name='ação'),
        ),
        migrations.AlterField(
            model_name='historico',
            name='data',
            field=models.DateTimeField(auto_now_add=True, verbose_name='data'),
        ),
        migrations.AlterField(
            model_name='historico',
            name='usuario',
            field=models.CharField(max_length=100, verbose_name='usuário'),
        ),
        migrations.AlterModelOptions(
            name='cliente',
            options={'ordering': ['nome'], 'verbose_name': 'Cliente', 'verbose_name_plural': 'Clientes'},
        ),
        migrations.AlterModelOptions(
            name='divida',
            options={'ordering': ['status', '-data_criacao'], 'verbose_name': 'Dívida', 'verbose_name_plural': 'Dívidas'},
        ),
        migrations.AlterModelOptions(
            name='historico',
            options={'ordering': ['-data'], 'verbose_name': 'Histórico', 'verbose_name_plural': 'Histórico'},
        ),
    ]
