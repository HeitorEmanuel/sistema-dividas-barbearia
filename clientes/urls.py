from django.urls import path
from . import management_views, views

urlpatterns = [
    path('', views.lista_clientes, name='lista_clientes'),
    path('novo-cliente/', views.novo_cliente, name='novo_cliente'),
    path('cliente/<int:cliente_id>/editar/', views.editar_cliente, name='editar_cliente'),
    path('cliente/<int:cliente_id>/excluir/', management_views.excluir_cliente, name='excluir_cliente'),
    path('nova-divida/', views.nova_divida, name='nova_divida'),
    path('divida/<int:divida_id>/editar/', views.editar_divida, name='editar_divida'),
    path('cliente/<int:cliente_id>/', views.detalhe_cliente, name='detalhe_cliente'),
    path('divida/<int:divida_id>/pagar/', views.marcar_como_paga, name='marcar_como_paga'),
    path('cliente/<int:cliente_id>/pagar-todas/', views.pagar_todas_dividas, name='pagar_todas_dividas'),
    path('historico/', views.historico, name='historico'),
    path('relatorio/', views.relatorio, name='relatorio'),
    path('relatorio-pdf/', views.relatorio_pdf, name='relatorio_pdf'),
    path('funcionarios/', views.funcionarios, name='funcionarios'),
    path('funcionarios/novo/', views.novo_funcionario, name='novo_funcionario'),
    path('funcionarios/<int:usuario_id>/editar/', management_views.editar_funcionario, name='editar_funcionario'),
    path('funcionarios/<int:usuario_id>/trocar-senha/', views.trocar_senha_funcionario, name='trocar_senha_funcionario'),
    path('backup/', views.backup, name='backup'),
    path('backup/baixar/', views.baixar_backup, name='baixar_backup'),
]
