from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from datetime import datetime, time
from io import BytesIO
import os
import zipfile

from django.conf import settings
from django.contrib.staticfiles import finders
from django.db.models import Count, Q, Sum
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .forms import ClienteForm, DividaForm, FuncionarioForm, FuncionarioSenhaForm, RelatorioPeriodoForm
from .models import Cliente, Divida, Historico


def formatar_moeda(valor):
    valor = valor or 0
    return f'R$ {valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def registrar_historico(usuario, acao):
    Historico.objects.create(
        usuario=usuario.username if usuario.is_authenticated else 'Sistema',
        acao=acao,
    )


def usuario_admin(user):
    return user.is_authenticated and user.is_superuser


@login_required
def lista_clientes(request):
    busca = request.GET.get('busca', '').strip()
    filtro = request.GET.get('filtro', 'todos')
    ordenacao = request.GET.get('ordenacao', 'nome')

    clientes = Cliente.objects.annotate(
        total_pendente=Sum(
            'dividas__valor',
            filter=Q(dividas__status=Divida.Status.PENDENTE),
        ),
        qtd_pendentes=Count(
            'dividas',
            filter=Q(dividas__status=Divida.Status.PENDENTE),
        ),
    )

    if busca:
        clientes = clientes.filter(
            Q(nome__icontains=busca) |
            Q(telefone__icontains=busca)
        )

    if filtro == 'pendentes':
        clientes = clientes.filter(qtd_pendentes__gt=0)
    elif filtro == 'em_dia':
        clientes = clientes.filter(qtd_pendentes=0)

    if ordenacao == 'maior_divida':
        clientes = clientes.order_by('-total_pendente', 'nome')
    elif ordenacao == 'mais_pendencias':
        clientes = clientes.order_by('-qtd_pendentes', 'nome')
    else:
        clientes = clientes.order_by('nome')

    clientes = list(clientes)
    for cliente in clientes:
        cliente.total_pendente_formatado = formatar_moeda(cliente.total_pendente or 0)

    totais = Cliente.objects.aggregate(
        total_clientes=Count('id'),
        total_a_receber=Sum(
            'dividas__valor',
            filter=Q(dividas__status=Divida.Status.PENDENTE),
        ),
        total_dividas_pendentes=Count(
            'dividas',
            filter=Q(dividas__status=Divida.Status.PENDENTE),
        ),
    )

    ultimas_acoes = Historico.objects.order_by('-data')[:5]

    return render(request, 'clientes/lista_clientes.html', {
        'clientes': clientes,
        'busca': busca,
        'filtro': filtro,
        'ordenacao': ordenacao,
        'total_clientes': totais['total_clientes'] or 0,
        'total_a_receber': totais['total_a_receber'] or 0,
        'total_a_receber_formatado': formatar_moeda(totais['total_a_receber'] or 0),
        'total_dividas_pendentes': totais['total_dividas_pendentes'] or 0,
        'ultimas_acoes': ultimas_acoes,
    })

@login_required
def novo_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            registrar_historico(request.user, f'Cadastrou o cliente {cliente.nome}')
            messages.success(request, 'Cliente cadastrado com sucesso.')
            return redirect('lista_clientes')
    else:
        form = ClienteForm()

    return render(request, 'clientes/formulario.html', {
        'form': form,
        'titulo': 'Novo cliente',
        'subtitulo': 'Cadastre apenas o essencial para agilizar o atendimento.',
        'botao': 'Salvar cliente',
    })


@login_required
def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)

    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            cliente = form.save()
            registrar_historico(request.user, f'Editou o cadastro do cliente {cliente.nome}')
            messages.success(request, 'Cliente atualizado com sucesso.')
            return redirect('detalhe_cliente', cliente_id=cliente.id)
    else:
        form = ClienteForm(instance=cliente)

    return render(request, 'clientes/formulario.html', {
        'form': form,
        'titulo': f'Editar cliente: {cliente.nome}',
        'subtitulo': 'Atualize somente as informações necessárias.',
        'botao': 'Salvar alterações',
        'voltar_url': 'detalhe_cliente',
        'voltar_id': cliente.id,
    })



@login_required
def nova_divida(request):
    cliente_id = request.GET.get('cliente')
    initial = {}
    if cliente_id:
        initial['cliente'] = get_object_or_404(Cliente, id=cliente_id)

    if request.method == 'POST':
        form = DividaForm(request.POST)
        if form.is_valid():
            divida = form.save(commit=False)
            divida.criado_por = request.user
            divida.save()
            registrar_historico(
                request.user,
                f'Adicionou dívida de {formatar_moeda(divida.valor)} para {divida.cliente.nome}'
            )
            messages.success(request, 'Dívida adicionada com sucesso.')
            return redirect('detalhe_cliente', cliente_id=divida.cliente.id)
    else:
        form = DividaForm(initial=initial)

    return render(request, 'clientes/formulario.html', {
        'form': form,
        'titulo': 'Nova dívida',
        'subtitulo': 'Informe o cliente, o valor e o motivo da dívida.',
        'botao': 'Salvar dívida',
        'voltar_url': 'lista_clientes',
    })


@login_required
def editar_divida(request, divida_id):
    divida = get_object_or_404(Divida, id=divida_id)

    if request.method == 'POST':
        form = DividaForm(request.POST, instance=divida)
        if form.is_valid():
            divida = form.save()
            registrar_historico(
                request.user,
                f'Editou a dívida de {formatar_moeda(divida.valor)} de {divida.cliente.nome}'
            )
            messages.success(request, 'Dívida atualizada com sucesso.')
            return redirect('detalhe_cliente', cliente_id=divida.cliente.id)
    else:
        form = DividaForm(instance=divida)

    return render(request, 'clientes/formulario.html', {
        'form': form,
        'titulo': f'Editar dívida de {divida.cliente.nome}',
        'subtitulo': 'Corrija valor, descrição ou cliente quando necessário.',
        'botao': 'Salvar alterações',
        'voltar_url': 'detalhe_cliente',
        'voltar_id': divida.cliente.id,
    })



@login_required
def detalhe_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    dividas = cliente.dividas.all()
    total_pendente = dividas.filter(status=Divida.Status.PENDENTE).aggregate(
        total=Sum('valor')
    )['total'] or 0
    qtd_pendentes = dividas.filter(status=Divida.Status.PENDENTE).count()

    return render(request, 'clientes/detalhe_cliente.html', {
        'cliente': cliente,
        'dividas': dividas,
        'total_pendente': total_pendente,
        'total_pendente_formatado': formatar_moeda(total_pendente),
        'qtd_pendentes': qtd_pendentes,
    })


@login_required
def marcar_como_paga(request, divida_id):
    divida = get_object_or_404(Divida, id=divida_id)

    if request.method != 'POST':
        return redirect('detalhe_cliente', cliente_id=divida.cliente.id)

    if divida.status == Divida.Status.PENDENTE:
        divida.marcar_como_paga(request.user)
        registrar_historico(
            request.user,
            f'Marcou como paga a dívida de {formatar_moeda(divida.valor)} de {divida.cliente.nome}'
        )
        messages.success(request, 'Dívida marcada como paga.')

    return redirect('detalhe_cliente', cliente_id=divida.cliente.id)


@login_required
def pagar_todas_dividas(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)

    if request.method != 'POST':
        return redirect('detalhe_cliente', cliente_id=cliente.id)

    dividas_pendentes = cliente.dividas.filter(status=Divida.Status.PENDENTE)
    quantidade = dividas_pendentes.count()

    for divida in dividas_pendentes:
        divida.marcar_como_paga(request.user)

    if quantidade:
        registrar_historico(
            request.user,
            f'Marcou todas as dívidas pendentes de {cliente.nome} como pagas. Total: {quantidade}'
        )
        messages.success(request, f'{quantidade} dívida(s) marcada(s) como paga(s).')
    else:
        messages.info(request, 'Esse cliente não possui dívidas pendentes.')

    return redirect('detalhe_cliente', cliente_id=cliente.id)


@login_required
def historico(request):
    historicos = Historico.objects.all().order_by('-data')[:100]
    return render(request, 'clientes/historico.html', {'historicos': historicos})



@login_required
def relatorio(request):
    hoje = timezone.localdate()
    inicio_mes = hoje.replace(day=1)

    form = RelatorioPeriodoForm(request.GET or None, initial={
        'data_inicio': inicio_mes,
        'data_fim': hoje,
    })

    data_inicio = inicio_mes
    data_fim = hoje

    if form.is_valid():
        data_inicio = form.cleaned_data['data_inicio']
        data_fim = form.cleaned_data['data_fim']

        if data_inicio > data_fim:
            data_inicio, data_fim = data_fim, data_inicio

    inicio_dt = timezone.make_aware(datetime.combine(data_inicio, time.min))
    fim_dt = timezone.make_aware(datetime.combine(data_fim, time.max))

    dividas = Divida.objects.select_related(
        'cliente', 'criado_por', 'pago_por'
    ).filter(
        Q(data_criacao__range=(inicio_dt, fim_dt)) |
        Q(data_pagamento__range=(inicio_dt, fim_dt))
    ).order_by('-data_criacao')

    total_criado = dividas.filter(data_criacao__range=(inicio_dt, fim_dt)).aggregate(total=Sum('valor'))['total'] or 0
    total_pago = dividas.filter(status=Divida.Status.PAGA, data_pagamento__range=(inicio_dt, fim_dt)).aggregate(total=Sum('valor'))['total'] or 0
    total_pendente_periodo = dividas.filter(status=Divida.Status.PENDENTE).aggregate(total=Sum('valor'))['total'] or 0

    return render(request, 'clientes/relatorio.html', {
        'form': form,
        'dividas': dividas,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'total_criado_formatado': formatar_moeda(total_criado),
        'total_pago_formatado': formatar_moeda(total_pago),
        'total_pendente_periodo_formatado': formatar_moeda(total_pendente_periodo),
        'quantidade': dividas.count(),
    })


@login_required
def relatorio_pdf(request):
    hoje = timezone.localdate()
    inicio_mes = hoje.replace(day=1)

    form = RelatorioPeriodoForm(request.GET or None, initial={
        'data_inicio': inicio_mes,
        'data_fim': hoje,
    })

    data_inicio = inicio_mes
    data_fim = hoje

    if form.is_valid():
        data_inicio = form.cleaned_data['data_inicio']
        data_fim = form.cleaned_data['data_fim']
        if data_inicio > data_fim:
            data_inicio, data_fim = data_fim, data_inicio

    inicio_dt = timezone.make_aware(datetime.combine(data_inicio, time.min))
    fim_dt = timezone.make_aware(datetime.combine(data_fim, time.max))

    dividas = Divida.objects.select_related(
        'cliente', 'criado_por', 'pago_por'
    ).filter(
        Q(data_criacao__range=(inicio_dt, fim_dt)) |
        Q(data_pagamento__range=(inicio_dt, fim_dt))
    ).order_by('status', 'cliente__nome', '-data_criacao')

    pendentes = dividas.filter(status=Divida.Status.PENDENTE)
    pagas = dividas.filter(status=Divida.Status.PAGA)

    total_criado = dividas.filter(data_criacao__range=(inicio_dt, fim_dt)).aggregate(total=Sum('valor'))['total'] or 0
    total_pago = pagas.filter(data_pagamento__range=(inicio_dt, fim_dt)).aggregate(total=Sum('valor'))['total'] or 0
    total_pendente_periodo = pendentes.aggregate(total=Sum('valor'))['total'] or 0
    agora = timezone.localtime(timezone.now())
    periodo_txt = f'{data_inicio.strftime("%d/%m/%Y")} até {data_fim.strftime("%d/%m/%Y")}'

    response = HttpResponse(content_type='application/pdf')
    nome_arquivo = f'relatorio-riko-{data_inicio:%Y-%m-%d}-a-{data_fim:%Y-%m-%d}.pdf'
    response['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'

    doc = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        rightMargin=1.1 * cm,
        leftMargin=1.1 * cm,
        topMargin=1.0 * cm,
        bottomMargin=1.2 * cm,
        title='Relatório de Dívidas - Riko Barbearia',
        author='Riko Barbearia',
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='PdfTitulo',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#2a201b'),
        alignment=0,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name='PdfSubtitulo',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#6b625b'),
    ))
    styles.add(ParagraphStyle(
        name='PdfSecao',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#2a201b'),
        spaceBefore=10,
        spaceAfter=7,
    ))
    styles.add(ParagraphStyle(
        name='PdfPequeno',
        parent=styles['Normal'],
        fontSize=7.2,
        leading=9,
        textColor=colors.HexColor('#2a201b'),
    ))
    styles.add(ParagraphStyle(
        name='PdfMuted',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#6b625b'),
    ))

    def nome_usuario(usuario):
        if not usuario:
            return '-'
        nome = usuario.get_full_name().strip()
        return nome or usuario.get_username()

    def data_local(valor):
        if not valor:
            return '-'
        return timezone.localtime(valor).strftime('%d/%m/%Y %H:%M')

    def desenhar_rodape(canvas, doc_obj):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor('#d8c6b1'))
        canvas.setLineWidth(0.4)
        canvas.line(doc_obj.leftMargin, 0.8 * cm, landscape(A4)[0] - doc_obj.rightMargin, 0.8 * cm)
        canvas.setFont('Helvetica', 7)
        canvas.setFillColor(colors.HexColor('#6b625b'))
        canvas.drawString(doc_obj.leftMargin, 0.45 * cm, 'Riko Barbearia • Controle interno de fiados')
        canvas.drawRightString(landscape(A4)[0] - doc_obj.rightMargin, 0.45 * cm, f'Página {doc_obj.page}')
        canvas.restoreState()

    elementos = []

    logo_path = finders.find('clientes/img/logo-riko.jpeg')
    cabecalho_esquerda = []
    if logo_path:
        cabecalho_esquerda.append(Image(logo_path, width=2.0 * cm, height=2.0 * cm))
    else:
        cabecalho_esquerda.append(Paragraph('Riko', styles['PdfTitulo']))

    cabecalho_direita = [
        Paragraph('Riko Barbearia', styles['PdfTitulo']),
        Paragraph('Relatório financeiro de fiados', styles['PdfSubtitulo']),
        Paragraph(f'Período: <b>{periodo_txt}</b>', styles['PdfSubtitulo']),
        Paragraph(f'Gerado por: <b>{request.user.get_username()}</b> • Emitido em: {agora.strftime("%d/%m/%Y às %H:%M")}', styles['PdfSubtitulo']),
    ]

    header = Table([[cabecalho_esquerda, cabecalho_direita]], colWidths=[2.5 * cm, 23.8 * cm])
    header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, -1), 1.2, colors.HexColor('#2a201b')),
    ]))
    elementos.append(header)
    elementos.append(Spacer(1, 0.45 * cm))

    resumo = Table([
        ['Registros', 'Total criado', 'Total recebido', 'Saldo pendente'],
        [str(dividas.count()), formatar_moeda(total_criado), formatar_moeda(total_pago), formatar_moeda(total_pendente_periodo)],
    ], colWidths=[5.2 * cm, 7.0 * cm, 7.0 * cm, 7.0 * cm])
    resumo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2a201b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#fff8ee')),
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.HexColor('#2a201b')),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 13),
        ('BOX', (0, 0), (-1, -1), 0.7, colors.HexColor('#d8c6b1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#d8c6b1')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
    ]))
    elementos.append(resumo)
    elementos.append(Spacer(1, 0.45 * cm))

    def tabela_dividas(titulo, queryset, tipo):
        elementos.append(Paragraph(titulo, styles['PdfSecao']))

        if not queryset.exists():
            vazio = Table([[Paragraph('Nenhum registro encontrado nesta seção.', styles['PdfMuted'])]], colWidths=[26.2 * cm])
            vazio.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fbf7f0')),
                ('BOX', (0, 0), (-1, -1), 0.4, colors.HexColor('#d8c6b1')),
                ('PADDING', (0, 0), (-1, -1), 8),
            ]))
            elementos.append(vazio)
            return

        if tipo == 'pendentes':
            dados = [['Cliente', 'Descrição', 'Valor', 'Criada em', 'Criada por']]
            for divida in queryset:
                dados.append([
                    Paragraph(divida.cliente.nome, styles['PdfPequeno']),
                    Paragraph(divida.descricao, styles['PdfPequeno']),
                    formatar_moeda(divida.valor),
                    data_local(divida.data_criacao),
                    nome_usuario(divida.criado_por),
                ])
            colunas = [4.5 * cm, 8.5 * cm, 3.0 * cm, 4.5 * cm, 5.7 * cm]
        else:
            dados = [['Cliente', 'Descrição', 'Valor', 'Criada em', 'Criada por', 'Paga em', 'Recebida por']]
            for divida in queryset:
                dados.append([
                    Paragraph(divida.cliente.nome, styles['PdfPequeno']),
                    Paragraph(divida.descricao, styles['PdfPequeno']),
                    formatar_moeda(divida.valor),
                    data_local(divida.data_criacao),
                    nome_usuario(divida.criado_por),
                    data_local(divida.data_pagamento),
                    nome_usuario(divida.pago_por),
                ])
            colunas = [3.7 * cm, 6.2 * cm, 2.5 * cm, 3.8 * cm, 3.4 * cm, 3.8 * cm, 2.8 * cm]

        tabela = Table(dados, colWidths=colunas, repeatRows=1)
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2a201b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 7.4),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff8ee')]),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#d8c6b1')),
            ('PADDING', (0, 0), (-1, -1), 4.2),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
        ]))
        elementos.append(tabela)

    tabela_dividas('Dívidas pendentes', pendentes, 'pendentes')
    elementos.append(Spacer(1, 0.25 * cm))
    tabela_dividas('Dívidas pagas / recebidas', pagas, 'pagas')

    doc.build(elementos, onFirstPage=desenhar_rodape, onLaterPages=desenhar_rodape)
    return response


@login_required
@user_passes_test(usuario_admin)
def funcionarios(request):
    usuarios = User.objects.order_by('-is_superuser', 'username')
    return render(request, 'clientes/funcionarios.html', {'usuarios': usuarios})


@login_required
@user_passes_test(usuario_admin)
def novo_funcionario(request):
    if request.method == 'POST':
        form = FuncionarioForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            registrar_historico(request.user, f'Cadastrou o funcionário {usuario.username}')
            messages.success(request, 'Funcionário cadastrado com sucesso.')
            return redirect('funcionarios')
    else:
        form = FuncionarioForm()

    return render(request, 'clientes/formulario.html', {
        'form': form,
        'titulo': 'Novo funcionário',
        'subtitulo': 'Crie o acesso de um membro da barbearia.',
        'botao': 'Salvar funcionário',
        'voltar_url': 'funcionarios',
    })


@login_required
@user_passes_test(usuario_admin)
def trocar_senha_funcionario(request, usuario_id):
    funcionario = get_object_or_404(User, id=usuario_id)

    if request.method == 'POST':
        form = FuncionarioSenhaForm(funcionario, request.POST)
        if form.is_valid():
            form.save()
            registrar_historico(request.user, f'Redefiniu a senha do usuário {funcionario.username}')
            messages.success(request, f'Senha de {funcionario.username} alterada com sucesso.')
            return redirect('funcionarios')
    else:
        form = FuncionarioSenhaForm(funcionario)

    return render(request, 'clientes/formulario.html', {
        'form': form,
        'titulo': f'Trocar senha de {funcionario.username}',
        'subtitulo': 'Use esta opção quando um funcionário esquecer a senha.',
        'botao': 'Alterar senha',
        'voltar_url': 'funcionarios',
    })



@login_required
@user_passes_test(usuario_admin)
def backup(request):
    return render(request, 'clientes/backup.html')


@login_required
@user_passes_test(usuario_admin)
def baixar_backup(request):
    db_path = settings.DATABASES['default'].get('NAME')

    if not db_path or not os.path.exists(db_path):
        messages.error(request, 'Banco de dados local não encontrado para backup.')
        return redirect('backup')

    agora = timezone.localtime(timezone.now())
    nome_zip = f'backup-riko-barbearia-{agora:%Y-%m-%d-%H-%M}.zip'

    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.write(db_path, arcname='db.sqlite3')
        zip_file.writestr(
            'LEIA-ME.txt',
            'Backup do sistema Dívidas da Barbearia\n'
            f'Gerado em: {agora:%d/%m/%Y %H:%M}\n\n'
            'Para restaurar localmente, substitua o arquivo db.sqlite3 do projeto por este arquivo.\n'
            'Guarde este backup em local seguro, pois ele contém dados dos clientes e das dívidas.\n'
        )

    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{nome_zip}"'

    registrar_historico(request.user, 'Gerou um backup do banco de dados')
    return response
