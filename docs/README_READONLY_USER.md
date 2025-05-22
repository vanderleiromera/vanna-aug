# Configuração de Usuário Somente Leitura para Vanna AI Odoo

Este guia explica como criar um usuário PostgreSQL com permissões somente leitura para ser usado pela aplicação Vanna AI Odoo. Isso melhora a segurança da aplicação, garantindo que ela não possa modificar dados no banco de dados Odoo.

## Por que usar um usuário somente leitura?

Usar um usuário com permissões somente leitura oferece várias vantagens:

1. **Segurança**: Previne modificações acidentais ou maliciosas no banco de dados
2. **Isolamento**: Separa as permissões da aplicação de análise das permissões do sistema Odoo
3. **Auditoria**: Facilita o rastreamento de consultas feitas pela aplicação
4. **Conformidade**: Ajuda a atender requisitos de segurança e conformidade

## Opções de Configuração

Existem duas maneiras de configurar o usuário somente leitura:

### Opção 1: Usando o script automatizado (Recomendado)

1. Dê permissão de execução ao script:
   ```bash
   chmod +x setup_readonly_user.sh
   ```

2. Execute o script:
   ```bash
   ./setup_readonly_user.sh
   ```

3. Siga as instruções na tela para fornecer as informações necessárias:
   - Host do PostgreSQL (padrão: localhost)
   - Porta do PostgreSQL (padrão: 5432)
   - Nome do banco de dados Odoo
   - Usuário administrador do PostgreSQL (padrão: postgres)
   - Senha do usuário administrador
   - Nome do usuário somente leitura (padrão: vanna_readonly)
   - Senha para o usuário somente leitura

4. O script criará o usuário, configurará as permissões e testará a conexão.

### Opção 2: Executando o SQL manualmente

1. Edite o arquivo `create_readonly_user.sql` para definir:
   - Nome do usuário somente leitura
   - Senha do usuário
   - Nome do banco de dados Odoo

2. Execute o script SQL como superusuário ou um usuário com permissões de criação de usuários:
   ```bash
   psql -h localhost -U postgres -d odoo_db -f create_readonly_user.sql
   ```

## Atualizando a Configuração da Aplicação

Após criar o usuário somente leitura, você precisa atualizar o arquivo `.env` da aplicação:

1. Abra o arquivo `.env` no diretório raiz da aplicação
2. Atualize as seguintes linhas:
   ```
   ODOO_DB_USER=vanna_readonly
   ODOO_DB_PASSWORD=sua_senha_segura
   ```
3. Salve o arquivo e reinicie a aplicação:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

## Verificando a Configuração

Para verificar se a aplicação está usando o usuário somente leitura:

1. Acesse a aplicação Vanna AI Odoo
2. Faça uma consulta simples
3. Verifique nos logs da aplicação se a conexão está sendo feita com o usuário somente leitura

## Solução de Problemas

Se encontrar problemas ao usar o usuário somente leitura:

1. **Erro de conexão**: Verifique se o usuário tem permissão para se conectar ao banco de dados
2. **Erro de permissão**: Verifique se o usuário tem permissão SELECT em todas as tabelas
3. **Tabelas não visíveis**: Verifique se o usuário tem permissão USAGE no schema public

## Segurança Adicional

Para maior segurança, considere:

1. Usar uma senha forte e única para o usuário somente leitura
2. Limitar o acesso ao banco de dados por IP usando regras no pg_hba.conf
3. Configurar SSL para conexões com o banco de dados

## Limitações

O usuário somente leitura:

1. Não pode modificar dados (INSERT, UPDATE, DELETE)
2. Não pode criar ou modificar objetos do banco de dados (CREATE, ALTER, DROP)
3. Não pode executar funções com permissões elevadas

Estas limitações são intencionais e garantem a segurança do banco de dados Odoo.

Primeiro, conecte-se ao PostgreSQL como usuário com privilégios suficientes (geralmente o postgres ou o usuário do Odoo):

sql
```
   sudo -u postgres psql
```

Crie o novo usuário:

sql
```
   CREATE USER usuario_leitura WITH PASSWORD 'senha_segura';
```

Conceda permissões somente leitura ao banco de dados do Odoo:

sql
```
   GRANT CONNECT ON DATABASE nome_do_banco_odoo TO usuario_leitura;
```

Conecte-se ao banco de dados específico do Odoo:

sql
```
   \c nome_do_banco_odoo
```

Conceda permissões SELECT em todas as tabelas existentes:

sql
```
   GRANT SELECT ON ALL TABLES IN SCHEMA public TO usuario_leitura;

```
Configure as permissões padrão para tabelas futuras:

sql
```
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO usuario_leitura;

```
Saia do PostgreSQL:

sql
```
   \q
```
