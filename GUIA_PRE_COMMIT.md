# Guia de Uso do Pre-commit

Este guia explica como configurar e usar o pre-commit para garantir a qualidade do código no projeto Vanna AI.

## O que é o Pre-commit?

Pre-commit é uma ferramenta que executa verificações automáticas antes de cada commit, garantindo que o código siga os padrões definidos no projeto.

## Instalação

```bash
# Instalar o pre-commit
pip install pre-commit

# Configurar o pre-commit no repositório
cd /caminho/para/vanna-ai-aug
pre-commit install
```

## Como Funciona

Depois de instalado, o pre-commit executa automaticamente todas as verificações configuradas no arquivo `.pre-commit-config.yaml` antes de cada commit.

### Verificações Configuradas

1. **trailing-whitespace**: Remove espaços em branco no final das linhas
2. **end-of-file-fixer**: Garante que os arquivos terminem com uma nova linha
3. **check-yaml**: Verifica a sintaxe de arquivos YAML
4. **check-added-large-files**: Impede a adição de arquivos grandes ao repositório
5. **check-ast**: Verifica a sintaxe de arquivos Python
6. **check-json**: Verifica a sintaxe de arquivos JSON
7. **check-merge-conflict**: Detecta conflitos de merge não resolvidos
8. **detect-private-key**: Detecta chaves privadas no código
9. **black**: Formata automaticamente o código Python
10. **flake8**: Verifica o estilo e a qualidade do código
11. **isort**: Ordena automaticamente os imports
12. **mypy**: Verifica tipos estáticos

## Configuração Atual

Para facilitar a adoção do pre-commit em um projeto existente, configuramos os hooks para ignorar temporariamente alguns problemas comuns:

### Flake8

Configuramos o flake8 para ignorar:
- Importações não utilizadas (F401)
- Importações fora do topo do arquivo (E402)
- Redefinição de variáveis não utilizadas (F811)
- Docstrings ausentes ou incorretas (D100-D417)
- Espaços em branco ausentes (E226, E231, E241)
- Exceções genéricas (E722)
- Variáveis não utilizadas (F841)
- Strings f sem placeholders (F541)
- E outros problemas comuns

### Mypy

Desabilitamos temporariamente o mypy no arquivo `.pre-commit-config.yaml`:
```yaml
# Temporariamente desabilitado até resolvermos os problemas de tipo
# -   repo: https://github.com/pre-commit/mirrors-mypy
#     rev: v1.3.0
#     hooks:
#     -   id: mypy
#         additional_dependencies: [types-requests, types-PyYAML]
#         args: ["--config-file=mypy.ini"]
```

Quando reativarmos o mypy, ele será configurado para ser extremamente permissivo:
- Ignorar erros de importação (ignore_missing_imports = True)
- Ignorar todos os arquivos na pasta app/ (exclude = app/)
- Desativar todas as verificações rigorosas (disallow_untyped_defs = False, etc.)
- Pular a verificação de imports (follow_imports = skip)
- Permitir qualquer tipo de 'Any' (disallow_any_* = False)

## Uso Diário

### Commit Normal

```bash
git add arquivo.py
git commit -m "Mensagem do commit"
```

O pre-commit será executado automaticamente antes do commit. Se alguma verificação falhar, o commit será abortado e você verá uma mensagem explicando o problema.

### Executar Manualmente

```bash
# Verificar todos os arquivos
pre-commit run --all-files

# Verificar arquivos específicos
pre-commit run --files app/modules/vanna_odoo.py
```

### Ignorar Verificações Temporariamente

```bash
# Ignorar todas as verificações
git commit -m "Commit urgente" --no-verify

# Ignorar uma verificação específica
SKIP=flake8 git commit -m "Ignorar flake8 neste commit"
```

### Atualizar os Hooks

```bash
pre-commit autoupdate
```

## Resolução de Problemas Comuns

### 1. Formatação de Código (Black)

Se o black falhar, ele já terá formatado o arquivo para você. Basta adicionar o arquivo novamente e tentar o commit:

```bash
git add arquivo.py
git commit -m "Mensagem do commit"
```

### 2. Ordenação de Imports (isort)

Se o isort falhar, ele já terá ordenado os imports para você. Basta adicionar o arquivo novamente e tentar o commit:

```bash
git add arquivo.py
git commit -m "Mensagem do commit"
```

### 3. Verificação de Estilo (flake8)

Se o flake8 falhar, você precisará corrigir manualmente os problemas de estilo. O flake8 mostrará uma lista de problemas com o número da linha e uma descrição:

```
app/modules/vanna_odoo.py:123:45: E231 missing whitespace after ':'
```

### 4. Verificação de Tipos (mypy)

Se o mypy falhar, você precisará corrigir manualmente os problemas de tipo. O mypy mostrará uma lista de problemas com o número da linha e uma descrição:

```
app/modules/vanna_odoo.py:123: error: Incompatible types in assignment
```

## Benefícios

- **Consistência**: Garante que todo o código siga os mesmos padrões
- **Qualidade**: Identifica problemas antes que eles entrem no repositório
- **Automação**: Automatiza verificações que seriam tediosas de fazer manualmente
- **Colaboração**: Facilita a colaboração entre desenvolvedores, pois todos seguem os mesmos padrões

## Dúvidas Frequentes

### O pre-commit está muito lento. O que fazer?

O pre-commit pode ser lento na primeira execução, pois precisa criar ambientes virtuais para cada hook. Nas execuções seguintes, ele será mais rápido.

### Posso desabilitar temporariamente o pre-commit?

Sim, você pode usar a opção `--no-verify` no comando `git commit` para ignorar todas as verificações temporariamente.

### Como adicionar novas verificações?

Edite o arquivo `.pre-commit-config.yaml` e adicione novos hooks. Depois, execute `pre-commit install` para atualizar a configuração.

### O que fazer se um hook estiver causando problemas?

Você pode desabilitar temporariamente um hook específico usando a variável de ambiente `SKIP`:

```bash
SKIP=flake8 git commit -m "Ignorar flake8 neste commit"
```

## Plano de Melhoria Gradual

Para melhorar gradualmente a qualidade do código, recomendamos:

1. **Fase 1**: Usar a configuração atual para permitir commits sem bloquear o desenvolvimento
2. **Fase 2**: Corrigir problemas em arquivos novos ou modificados
3. **Fase 3**: Instalar stubs de tipo para bibliotecas externas:
   ```bash
   pip install types-python-dateutil pandas-stubs types-psycopg2
   ```
4. **Fase 4**: Reativar o mypy no arquivo `.pre-commit-config.yaml` (descomentando as linhas)
5. **Fase 5**: Gradualmente remover exceções no `.flake8` e `mypy.ini`
6. **Fase 6**: Implementar verificações mais rigorosas

### Problemas Comuns e Soluções

#### Importações fora do topo do arquivo (E402)

Este erro ocorre quando você importa módulos depois de outras instruções no arquivo. Para corrigir:

```python
# Antes
import os
import sys

# Algum código aqui...

import pandas as pd  # E402: Importação não está no topo do arquivo

# Depois
import os
import sys
import pandas as pd

# Algum código aqui...
```

#### Redefinição de variáveis não utilizadas (F811)

Este erro ocorre quando você redefine uma variável importada mas não a utiliza. Para corrigir:

```python
# Antes
import vanna  # Importação original
# ... código ...
vanna = mock_vanna()  # F811: Redefinição de 'vanna' importado mas não utilizado

# Depois
import vanna as vanna_original  # Renomeie a importação
# ... código ...
vanna = mock_vanna()  # Agora não há conflito
```

## Conclusão

O pre-commit é uma ferramenta poderosa para garantir a qualidade do código e a consistência do repositório. Com o arquivo `.pre-commit-config.yaml` já configurado no projeto, você só precisa instalar o pre-commit e configurá-lo no repositório para começar a aproveitar seus benefícios.
