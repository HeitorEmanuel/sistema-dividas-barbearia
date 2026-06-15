# Generated for report improvements.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('clientes', '0004_melhorias_cliente_divida'),
    ]

    operations = [
        migrations.AddField(
            model_name='divida',
            name='criado_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dividas_criadas', to=settings.AUTH_USER_MODEL, verbose_name='funcionário que criou'),
        ),
        migrations.AddField(
            model_name='divida',
            name='pago_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dividas_pagas', to=settings.AUTH_USER_MODEL, verbose_name='funcionário que recebeu'),
        ),
    ]
