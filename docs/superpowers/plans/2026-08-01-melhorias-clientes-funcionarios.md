# Melhorias de clientes, dívidas e funcionários — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Melhorar a busca de clientes ao criar dívidas, permitir exclusão segura de clientes e edição completa de funcionários, junto com uma auditoria de segurança e dados sensíveis.

**Architecture:** Manter o backend Django como fonte de verdade e usar JavaScript simples apenas para melhorar a experiência de seleção de clientes. Todas as ações destrutivas ou administrativas permanecem protegidas por login, superusuário quando aplicável, POST e CSRF.

**Tech Stack:** Django, templates Django, Bootstrap, JavaScript simples, SQLite/PostgreSQL conforme ambiente, PythonAnywhere.

## Global Constraints

- Não adicionar dependências externas para a busca de clientes.
- Não alterar o banco se não for necessário.
- Não expor dados sensíveis no GitHub, HTML público, logs ou mensagens de erro.
- Preservar compatibilidade com PythonAnywhere.
- Implementar tudo na branch `melhorias-clientes-funcionarios`.

---

### Task 1: Testes de comportamento e segurança

**Files:**
- Create: `clientes/tests.py`

**Interfaces:**
- Consumes: views, forms, models e rotas atuais.
- Produces: testes de regressão para exclusão de cliente, edição de funcionário e proteção administrativa.

- [ ] Escrever testes que falham para: bloquear exclusão com dívida pendente; permitir exclusão sem dívida pendente; impedir autodesativação e autorrebaixamento; permitir edição de outro funcionário; validar criação de dívida com cliente válido.
- [ ] Executar `python manage.py test clientes` e confirmar falhas esperadas antes da implementação.

### Task 2: Busca instantânea de clientes em nova dívida

**Files:**
- Modify: `clientes/forms.py`
- Modify: `clientes/views.py`
- Modify: `clientes/templates/clientes/formulario.html`

**Interfaces:**
- Produces: campo de busca visual por nome/telefone e campo real `cliente` validado pelo Django.

- [ ] Ajustar `DividaForm` para oferecer metadados seguros dos clientes ao template sem remover a validação server-side.
- [ ] No fluxo `nova_divida`, disponibilizar clientes ordenados para a interface de busca.
- [ ] No template, renderizar busca instantânea por nome/telefone com seleção por clique/toque e manter o `select` real sincronizado/oculto.
- [ ] Garantir escape de conteúdo no template e evitar `|safe` com dados de cliente.
- [ ] Executar testes.

### Task 3: Exclusão segura de cliente

**Files:**
- Modify: `clientes/views.py`
- Modify: `clientes/urls.py`
- Modify: `clientes/templates/clientes/detalhe_cliente.html`

**Interfaces:**
- Produces: rota `cliente/<int:cliente_id>/excluir/` aceita somente POST autenticado.

- [ ] Criar view `excluir_cliente` que rejeita GET, verifica dívidas pendentes, registra histórico antes da exclusão e retorna mensagem apropriada.
- [ ] Adicionar rota.
- [ ] Adicionar botão/formulário POST com CSRF e confirmação explícita informando que dívidas pagas também serão removidas por CASCADE.
- [ ] Executar testes.

### Task 4: Edição completa de funcionários

**Files:**
- Modify: `clientes/forms.py`
- Modify: `clientes/views.py`
- Modify: `clientes/urls.py`
- Modify: `clientes/templates/clientes/funcionarios.html`
- Reuse/Modify: `clientes/templates/clientes/formulario.html`

**Interfaces:**
- Produces: `FuncionarioEdicaoForm` e rota `funcionarios/<int:usuario_id>/editar/`.

- [ ] Criar formulário de edição para `username`, `first_name`, `email`, `is_active`, `is_superuser` e senha opcional com confirmação.
- [ ] Criar view restrita a superusuário.
- [ ] Impedir que o usuário logado remova de si mesmo `is_superuser` ou `is_active`.
- [ ] Registrar alterações administrativas relevantes no histórico sem registrar senha.
- [ ] Atualizar lista de funcionários com botão Editar e indicadores de ativo/inativo/admin.
- [ ] Executar testes.

### Task 5: Auditoria de segurança e dados sensíveis

**Files:**
- Review: `.gitignore`
- Review: `.env.example`
- Review: `*/settings.py`
- Review: templates, views, forms e histórico.
- Modify only if findings require it.

**Interfaces:**
- Produces: checklist objetivo de exposição de segredos/PII e correções necessárias.

- [ ] Verificar se `.env`, `db.sqlite3`, backups, logs, chaves e credenciais estão ignorados.
- [ ] Verificar `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, cookies seguros e HTTPS por ambiente.
- [ ] Buscar por padrões `SECRET_KEY`, `password`, `senha`, `token`, `api_key`, `DATABASE_URL`, e-mails/telefones de dados reais.
- [ ] Confirmar que histórico não grava senhas, tokens ou credenciais.
- [ ] Confirmar que templates autenticados não expõem dados além do necessário.
- [ ] Corrigir qualquer achado concreto e executar os testes novamente.

### Task 6: Verificação final

**Files:**
- Review all changed files.

- [ ] Executar `python manage.py test clientes`.
- [ ] Executar `python manage.py check --deploy` com observação de que alguns avisos dependem das variáveis do ambiente de produção.
- [ ] Comparar branch com `main` e revisar diff por segurança, escopo e regressões.
- [ ] Somente após verificação, preparar PR/diff para revisão antes de merge em `main`.
