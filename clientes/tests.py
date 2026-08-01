from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Cliente, Divida, Historico


class ClienteExclusaoTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='atendente', password='senha-teste-segura')
        self.client.force_login(self.usuario)

    def test_bloqueia_exclusao_quando_existe_divida_pendente(self):
        cliente = Cliente.objects.create(nome='Cliente com pendência')
        Divida.objects.create(
            cliente=cliente,
            valor=Decimal('20.00'),
            descricao='Corte',
            status=Divida.Status.PENDENTE,
        )

        response = self.client.post(reverse('excluir_cliente', args=[cliente.id]), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Cliente.objects.filter(id=cliente.id).exists())
        self.assertContains(response, 'dívida(s) pendente(s)')

    def test_permite_exclusao_quando_so_existem_dividas_pagas(self):
        cliente = Cliente.objects.create(nome='Cliente quitado')
        Divida.objects.create(
            cliente=cliente,
            valor=Decimal('30.00'),
            descricao='Barba',
            status=Divida.Status.PAGA,
        )

        response = self.client.post(reverse('excluir_cliente', args=[cliente.id]), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Cliente.objects.filter(id=cliente.id).exists())
        self.assertTrue(Historico.objects.filter(acao__icontains='Excluiu o cliente').exists())

    def test_get_nao_exclui_cliente(self):
        cliente = Cliente.objects.create(nome='Cliente protegido')

        response = self.client.get(reverse('excluir_cliente', args=[cliente.id]))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Cliente.objects.filter(id=cliente.id).exists())


class FuncionarioEdicaoTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin-teste',
            email='admin@example.invalid',
            password='senha-admin-segura',
        )
        self.funcionario = User.objects.create_user(
            username='funcionario-teste',
            email='funcionario@example.invalid',
            password='senha-funcionario-segura',
            first_name='Funcionário',
        )
        self.client.force_login(self.admin)

    def test_admin_pode_editar_dados_status_permissao_e_senha_de_outro_usuario(self):
        response = self.client.post(
            reverse('editar_funcionario', args=[self.funcionario.id]),
            {
                'username': 'funcionario-editado',
                'first_name': 'Nome Editado',
                'email': 'novo@example.invalid',
                'is_active': '',
                'is_superuser': 'on',
                'password1': 'NovaSenhaSegura123!',
                'password2': 'NovaSenhaSegura123!',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.funcionario.refresh_from_db()
        self.assertEqual(self.funcionario.username, 'funcionario-editado')
        self.assertEqual(self.funcionario.first_name, 'Nome Editado')
        self.assertEqual(self.funcionario.email, 'novo@example.invalid')
        self.assertFalse(self.funcionario.is_active)
        self.assertTrue(self.funcionario.is_superuser)
        self.assertTrue(self.funcionario.check_password('NovaSenhaSegura123!'))

    def test_admin_nao_pode_remover_proprio_status_de_administrador(self):
        response = self.client.post(
            reverse('editar_funcionario', args=[self.admin.id]),
            {
                'username': self.admin.username,
                'first_name': 'Administrador',
                'email': self.admin.email,
                'is_active': 'on',
                'is_superuser': '',
                'password1': '',
                'password2': '',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_superuser)
        self.assertContains(response, 'não pode remover seu próprio acesso de administrador')

    def test_admin_nao_pode_desativar_propria_conta(self):
        response = self.client.post(
            reverse('editar_funcionario', args=[self.admin.id]),
            {
                'username': self.admin.username,
                'first_name': 'Administrador',
                'email': self.admin.email,
                'is_active': '',
                'is_superuser': 'on',
                'password1': '',
                'password2': '',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)
        self.assertContains(response, 'não pode desativar sua própria conta')

    def test_usuario_comum_nao_acessa_edicao_de_funcionario(self):
        self.client.force_login(self.funcionario)

        response = self.client.get(reverse('editar_funcionario', args=[self.admin.id]))

        self.assertEqual(response.status_code, 302)


class NovaDividaBuscaClienteTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='atendente-busca', password='senha-teste-segura')
        self.cliente = Cliente.objects.create(nome='João da Silva', telefone='81 99999-1111')
        self.client.force_login(self.usuario)

    def test_formulario_exibe_busca_instantanea_de_cliente(self):
        response = self.client.get(reverse('nova_divida'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="cliente-search"')
        self.assertContains(response, 'João da Silva')
        self.assertContains(response, '81 99999-1111')

    def test_backend_continua_validando_cliente_ao_salvar_divida(self):
        response = self.client.post(
            reverse('nova_divida'),
            {
                'cliente': self.cliente.id,
                'valor': '35.00',
                'descricao': 'Corte + barba',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Divida.objects.filter(cliente=self.cliente, valor=Decimal('35.00')).exists())

    def test_cliente_inexistente_e_rejeitado_pelo_backend(self):
        response = self.client.post(
            reverse('nova_divida'),
            {
                'cliente': 999999,
                'valor': '35.00',
                'descricao': 'Corte + barba',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Divida.objects.exists())
        self.assertContains(response, 'Faça uma escolha válida')
