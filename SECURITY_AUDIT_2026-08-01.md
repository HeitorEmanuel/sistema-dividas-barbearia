# Auditoria de segurança — 01/08/2026

## Escopo revisado

Revisão focada em dados sensíveis, autenticação, autorização, operações destrutivas e configuração de produção do sistema de dívidas da barbearia.

## Resultado resumido

- O repositório está público. Para um sistema usado com dados reais de clientes, recomenda-se fortemente torná-lo privado.
- Não foi encontrado `db.sqlite3` commitado no histórico inicial revisado.
- Não foi encontrado arquivo `.env` real commitado no histórico inicial revisado.
- `.gitignore` bloqueia banco SQLite, `.env`, backups ZIP, logs, mídia, ambientes virtuais e arquivos de IDE.
- `.env.example` contém apenas valores fictícios/placeholders.
- Senhas de usuários usam o sistema de hash do Django; não há armazenamento de senha em texto puro no código revisado.
- Telas principais exigem autenticação.
- Gerenciamento de funcionários e backup exigem superusuário.
- Ações destrutivas/pagamentos usam `POST` e CSRF.
- A exclusão de clientes adicionada nesta atualização usa `POST` e bloqueia clientes com dívidas pendentes.
- A edição de funcionários adicionada nesta atualização exige superusuário e impede que o administrador logado remova o próprio acesso administrativo ou desative a própria conta.
- A nova senha de funcionário passa pelos validadores de senha do Django.

## Endurecimento aplicado nesta atualização

### SECRET_KEY

Produção não possui mais chave secreta previsível como fallback. Quando `DEBUG=False`, a aplicação exige `SECRET_KEY` no ambiente e falha ao iniciar se ela estiver ausente.

### DEBUG

O valor padrão passou de `True` para `False`. Assim, a aplicação não entra acidentalmente em modo de depuração por falta de variável de ambiente.

### Cookies e HTTPS

Com `DEBUG=False`, continuam habilitados:

- `SESSION_COOKIE_SECURE=True`;
- `CSRF_COOKIE_SECURE=True`;
- `SECURE_SSL_REDIRECT=True` por padrão;
- HSTS configurável;
- `X_FRAME_OPTIONS='DENY'`;
- `SECURE_CONTENT_TYPE_NOSNIFF=True`;
- `SECURE_REFERRER_POLICY='same-origin'`.

## Checklist obrigatório no PythonAnywhere

Antes do reload da nova versão, confirmar no ambiente da aplicação:

```text
SECRET_KEY=<chave longa, aleatória e exclusiva>
DEBUG=False
ALLOWED_HOSTS=<seu-usuario>.pythonanywhere.com
CSRF_TRUSTED_ORIGINS=https://<seu-usuario>.pythonanywhere.com
SECURE_SSL_REDIRECT=True
```

Se usar PostgreSQL:

```text
DATABASE_URL=<string de conexão real configurada somente no servidor>
DB_SSL_REQUIRE=True
```

Nunca copiar esses valores reais para GitHub, mensagens, prints ou documentação pública.

## Recomendações adicionais

1. Tornar o repositório privado enquanto ele representar o sistema real da barbearia.
2. Usar uma `SECRET_KEY` nova e exclusiva no PythonAnywhere.
3. Confirmar que `DEBUG=False` está definido no servidor.
4. Fazer backup do banco antes de publicar alterações destrutivas.
5. Manter contas administrativas no mínimo necessário.
6. Desativar contas de ex-funcionários imediatamente.
7. Não compartilhar backups por WhatsApp/e-mail sem proteção, pois contêm dados pessoais e financeiros.
8. Revisar periodicamente o histórico do Git em busca de arquivos sensíveis adicionados por engano.

## Limites desta auditoria

Esta revisão cobre o código e o histórico Git acessíveis pelo conector. Ela não inspeciona diretamente as variáveis de ambiente, arquivos privados, banco de dados, logs ou configuração interna da conta PythonAnywhere. Portanto, a segurança final também depende da configuração real do servidor.
