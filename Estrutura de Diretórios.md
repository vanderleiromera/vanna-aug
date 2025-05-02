vanna-ai-odoo/
├── app/                    # Diretório principal da aplicação
│   ├── modules/            # Módulos Python
│   │   └── vanna_odoo.py   # Implementação da classe VannaOdoo
│   ├── app.py              # Aplicação Streamlit
│   ├── train_vanna.py      # Script para treinar o modelo
│   ├── test_connection.py  # Script para testar a conexão com o banco de dados
│   ├── debug_chromadb.py   # Script para depurar problemas do ChromaDB
│   └── check_persistence.py # Script para verificar persistência do ChromaDB
├── data/                   # Diretório para dados persistentes (criado automaticamente)
│   └── chromadb/           # Dados do ChromaDB
├── .env.example            # Exemplo de arquivo de variáveis de ambiente
├── docker-compose.yml      # Configuração do Docker Compose
├── Dockerfile              # Dockerfile para construir a imagem
├── requirements.txt        # Dependências Python
└── run_local.sh            # Script para executar a aplicação localmente