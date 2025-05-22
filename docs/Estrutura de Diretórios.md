vanna-ai-odoo/
├── app/                    # Diretório principal da aplicação
│   ├── modules/            # Módulos Python
│   │   ├── vanna_odoo.py             # Implementação base da classe VannaOdoo
│   │   ├── vanna_odoo_numeric.py     # Extensão para processamento de valores numéricos
│   │   ├── vanna_odoo_extended.py    # Extensão com métodos adicionais
│   │   ├── sql_evaluator.py          # Avaliador de qualidade de SQL
│   │   ├── example_pairs.py          # Exemplos de pares pergunta-SQL
│   │   ├── anomaly_detection.py      # Detecção de anomalias nos dados
│   │   ├── visualization.py          # Funções de visualização de dados
│   │   └── odoo_priority_tables.py   # Lista de tabelas prioritárias do Odoo
│   ├── app.py              # Aplicação Streamlit
│   ├── train_all.py        # Script unificado para treinar o modelo
│   ├── tests/              # Testes unitários e de integração
│   ├── utils/              # Utilitários e ferramentas
│   └── legacy_tests/       # Testes legados (mantidos para referência)
├── data/                   # Diretório para dados persistentes (criado automaticamente)
│   └── chromadb/           # Dados do ChromaDB
├── .env.example            # Exemplo de arquivo de variáveis de ambiente
├── docker-compose.yml      # Configuração do Docker Compose
├── Dockerfile              # Dockerfile para construir a imagem
├── pyproject.toml          # Configuração do Poetry e dependências
├── poetry.lock             # Arquivo de lock do Poetry com dependências fixadas
├── requirements.txt        # Dependências Python (para compatibilidade)
├── run_local.sh            # Script para executar a aplicação localmente
├── run_train.sh            # Script para treinar o modelo
├── run_tests.sh            # Script para executar os testes
└── run_tests_with_options.sh # Script para executar os testes com opções
