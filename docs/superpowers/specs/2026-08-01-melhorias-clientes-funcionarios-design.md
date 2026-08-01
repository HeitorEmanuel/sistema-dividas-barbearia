# Design — melhorias de clientes, dívidas e funcionários

Data: 2026-08-01
Branch: `melhorias-clientes-funcionarios`

## Objetivo

Melhorar três fluxos do sistema de dívidas da barbearia sem alterar o funcionamento básico atual e sem adicionar dependências externas desnecessárias.

## Escopo aprovado

1. Melhorar a seleção de cliente ao adicionar uma dívida.
2. Permitir excluir clientes, mas somente quando não existirem dívidas pendentes.
3. Permitir edição completa de funcionários, incluindo dados cadastrais, status ativo/inativo e permissão de administrador.

## 1. Busca de cliente ao adicionar dívida

### Situação atual

O formulário `DividaForm` usa um campo `ModelChoiceField` renderizado como `<select>` comum, o que fica lento e pouco prático quando há muitos clientes.

### Solução

Substituir a experiência visual do campo por uma busca instantânea no próprio formulário, usando JavaScript simples e os dados já disponíveis no HTML.

A busca deve:

- filtrar por nome;
- filtrar por telefone;
- atualizar os resultados enquanto o usuário digita;
- permitir selecionar um cliente com toque/clique;
- manter um campo oculto com o `cliente_id` que será validado pelo Django;
- funcionar em desktop e celular;
- não exigir biblioteca externa.

### Validação

O backend continua responsável por validar se o cliente existe e se o ID recebido é válido. O JavaScript é apenas uma melhoria de interface.

## 2. Exclusão de cliente

### Regra aprovada

Um cliente só poderá ser excluído se não possuir nenhuma dívida com status `PENDENTE`.

Dívidas já pagas não bloqueiam a exclusão.

### Fluxo

- Adicionar um botão `Excluir cliente` na tela de detalhes do cliente.
- A ação deve exigir `POST` e CSRF.
- Antes de excluir, o backend verifica se há dívidas pendentes.
- Se houver, a exclusão é bloqueada e o usuário recebe uma mensagem clara.
- Se não houver, o cliente é excluído.
- Como o modelo atual usa `on_delete=CASCADE`, as dívidas antigas do cliente também serão removidas junto com ele. Isso deve ser comunicado na confirmação para evitar exclusões acidentais.
- Registrar a ação no histórico antes da exclusão.

## 3. Edição completa de funcionários

### Situação atual

A tela de funcionários permite apenas criar usuário e redefinir senha. Não existe edição dos demais dados.

### Solução

Criar uma tela de edição do funcionário com os seguintes campos:

- usuário (`username`);
- nome (`first_name`);
- e-mail (`email`);
- ativo/inativo (`is_active`);
- administrador (`is_superuser`);
- senha nova opcional.

A senha não será obrigatória ao editar. Se os campos de nova senha forem deixados vazios, a senha atual permanece igual.

### Regras de segurança

- A tela continua restrita a superusuários.
- Um administrador não poderá remover de si próprio o status de administrador pela tela de edição.
- Um administrador não poderá desativar a própria conta pela tela de edição.
- Toda alteração relevante deve ser registrada no histórico.

## Rotas previstas

Adicionar:

- `cliente/<int:cliente_id>/excluir/`
- `funcionarios/<int:usuario_id>/editar/`

A rota atual de troca de senha pode ser mantida por compatibilidade ou incorporada ao novo fluxo de edição. A implementação preferida é manter a rota antiga inicialmente e adicionar a nova edição completa, reduzindo risco de regressão.

## Arquivos principais envolvidos

- `clientes/forms.py`
- `clientes/views.py`
- `clientes/urls.py`
- `clientes/templates/clientes/formulario.html`
- `clientes/templates/clientes/detalhe_cliente.html`
- `clientes/templates/clientes/funcionarios.html`
- novo template de edição de funcionário, se necessário
- possíveis ajustes em CSS/JS já existentes

## Tratamento de erros

- Cliente inválido na nova dívida: mostrar erro normal do formulário.
- Exclusão com dívida pendente: bloquear e mostrar `messages.error` ou `messages.warning`.
- Tentativa de retirar o próprio acesso administrativo: bloquear e mostrar mensagem.
- Tentativa de desativar a própria conta: bloquear e mostrar mensagem.
- Username duplicado ou e-mail inválido: usar validações do Django.

## Testes esperados

### Busca de cliente

- localizar cliente pelo nome completo;
- localizar por parte do nome;
- localizar por telefone;
- selecionar cliente e salvar dívida;
- tentar enviar ID inválido e confirmar rejeição do backend;
- testar em tela pequena.

### Exclusão

- excluir cliente sem dívidas;
- excluir cliente apenas com dívidas pagas;
- bloquear cliente com ao menos uma dívida pendente;
- confirmar registro no histórico.

### Funcionários

- editar nome, usuário e e-mail;
- ativar/desativar outro funcionário;
- promover/rebaixar outro funcionário entre administrador e funcionário;
- alterar senha opcionalmente;
- salvar sem trocar senha;
- impedir o administrador logado de desativar a própria conta;
- impedir o administrador logado de remover o próprio status de administrador.

## Deploy no PythonAnywhere

Depois das alterações serem aprovadas e mescladas no `main`:

1. abrir o Bash Console do PythonAnywhere;
2. entrar na pasta do projeto;
3. executar `git pull`;
4. se não houver novas dependências nem migrations, nenhum comando adicional será necessário;
5. na aba Web, clicar em `Reload`.

A implementação deve evitar mudanças de banco sempre que possível para simplificar a publicação.
