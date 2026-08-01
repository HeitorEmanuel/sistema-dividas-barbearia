from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FuncionarioEdicaoForm
from .models import Cliente, Divida, Historico


def usuario_admin(user):
    return user.is_authenticated and user.is_superuser


def registrar_historico(usuario, acao):
    Historico.objects.create(
        usuario=usuario.username if usuario.is_authenticated else 'Sistema',
        acao=acao,
    )


@login_required
def excluir_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)

    if request.method != 'POST':
        return redirect('detalhe_cliente', cliente_id=cliente.id)

    qtd_pendentes = cliente.dividas.filter(status=Divida.Status.PENDENTE).count()
    if qtd_pendentes:
        messages.warning(
            request,
            f'Não foi possível excluir {cliente.nome}: existem {qtd_pendentes} dívida(s) pendente(s).'
        )
        return redirect('detalhe_cliente', cliente_id=cliente.id)

    nome_cliente = cliente.nome
    total_dividas = cliente.dividas.count()
    registrar_historico(
        request.user,
        f'Excluiu o cliente {nome_cliente} e {total_dividas} dívida(s) já quitada(s) vinculada(s) ao cadastro.'
    )
    cliente.delete()
    messages.success(request, f'Cliente {nome_cliente} excluído com sucesso.')
    return redirect('lista_clientes')


@login_required
@user_passes_test(usuario_admin)
def editar_funcionario(request, usuario_id):
    funcionario = get_object_or_404(User, id=usuario_id)

    if request.method == 'POST':
        form = FuncionarioEdicaoForm(request.POST, instance=funcionario, actor=request.user)
        if form.is_valid():
            antes = {
                'username': funcionario.username,
                'first_name': funcionario.first_name,
                'email': funcionario.email,
                'is_active': funcionario.is_active,
                'is_superuser': funcionario.is_superuser,
            }
            senha_alterada = bool(form.cleaned_data.get('password1'))
            funcionario = form.save()

            alteracoes = []
            campos = [
                ('username', 'usuário'),
                ('first_name', 'nome'),
                ('email', 'e-mail'),
                ('is_active', 'status ativo'),
                ('is_superuser', 'perfil administrador'),
            ]
            for campo, rotulo in campos:
                if antes[campo] != getattr(funcionario, campo):
                    alteracoes.append(rotulo)
            if senha_alterada:
                alteracoes.append('senha')

            resumo = ', '.join(alteracoes) if alteracoes else 'nenhuma alteração de dados'
            registrar_historico(
                request.user,
                f'Editou o funcionário {funcionario.username}: {resumo}'
            )
            messages.success(request, f'Funcionário {funcionario.username} atualizado com sucesso.')
            return redirect('funcionarios')
    else:
        form = FuncionarioEdicaoForm(instance=funcionario, actor=request.user)

    return render(request, 'clientes/formulario.html', {
        'form': form,
        'titulo': f'Editar funcionário: {funcionario.username}',
        'subtitulo': 'Altere dados, acesso e permissões. A nova senha é opcional.',
        'botao': 'Salvar alterações',
        'voltar_url': 'funcionarios',
    })
