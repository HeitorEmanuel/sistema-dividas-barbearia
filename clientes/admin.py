from django.contrib import admin
from .models import Cliente, Divida, Historico

admin.site.site_header = 'Riko Barbearia'
admin.site.site_title = 'Riko Barbearia'
admin.site.index_title = 'Painel administrativo'


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'criado_em')
    search_fields = ('nome', 'telefone')
    list_filter = ('criado_em',)


@admin.register(Divida)
class DividaAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'valor', 'status', 'criado_por', 'data_criacao', 'pago_por', 'data_pagamento')
    list_filter = ('status', 'data_criacao', 'data_pagamento')
    search_fields = ('cliente__nome', 'descricao')
    autocomplete_fields = ('cliente', 'criado_por', 'pago_por')


@admin.register(Historico)
class HistoricoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'acao', 'data')
    search_fields = ('usuario', 'acao')
    list_filter = ('data',)
    readonly_fields = ('usuario', 'acao', 'data')
