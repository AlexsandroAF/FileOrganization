# Organizador Automático de Pastas

Aplicativo para monitorar e organizar arquivos automaticamente em pastas específicas.

## Funcionalidades

- Monitoramento em tempo real de pastas selecionadas
- Organização automática de arquivos por tipo
- Estatísticas de uso de espaço
- Visualização de logs do sistema
- Execução em segundo plano na bandeja do sistema
- Interface gráfica intuitiva

## Requisitos

- Python 3.6 ou superior
- PyQt5
- Watchdog
- Pillow (opcional, para geração de ícones)

## Instalação

### Método 1: Uso com Python

1. Clone o repositório:
```
git clone git@github.com:AlexsandroAF/FileOrganization.git
cd organizador-pastas
```

2. Instale as dependências:
```
pip install -r requirements.txt
```

3. Execute:
```
python main.py
```

### Método 2: Executável compilado

1. Baixe o arquivo executável mais recente da seção Releases
2. Execute o arquivo `organizador-pastas.exe`

### Para desenvolvedores - Compilação

```
pyinstaller --onefile --windowed --add-data "assets/icons/tray_icon.png;assets/icons" main.py
```

## Uso básico

1. Inicie o aplicativo
2. Clique em "Adicionar Pasta" para selecionar diretórios a serem monitorados
3. O aplicativo criará automaticamente subpastas para diferentes tipos de arquivos
4. Os arquivos adicionados às pastas monitoradas serão organizados automaticamente
5. Use a aba "Estatísticas" para visualizar o espaço ocupado
6. Use a aba "Logs" para verificar as operações realizadas

Ao minimizar, o aplicativo continuará em execução na bandeja do sistema (canto inferior direito).

## Solução de problemas

- **Ícone ausente na bandeja:** O aplicativo cria um ícone padrão se não encontrar o arquivo em assets/icons
- **Erros de permissão:** Certifique-se de que o aplicativo tem permissão para ler/escrever nas pastas selecionadas
- **Aplicativo não inicia:** Verifique se todas as dependências estão instaladas corretamente

## Estrutura do projeto

```
organizador-pastas/
├── assets/
│   └── icons/              # Ícones do sistema
├── core/
│   ├── file_organizer.py   # Lógica de organização de arquivos
│   ├── folder_watcher.py   # Monitor de pastas em tempo real
│   └── logger.py           # Sistema de logs
├── db/
│   └── database.py         # Interface com banco de dados SQLite
├── ui/
│   ├── main_window.py      # Interface principal
│   └── tray_icon.py        # Funcionalidade da bandeja do sistema
├── config/
│   ├── file_types.py       # Configuração de tipos de arquivo
│   └── settings.py         # Configurações gerais
├── main.py                 # Ponto de entrada do aplicativo
└── requirements.txt        # Dependências do projeto
```

## Licença

Este projeto está licenciado sob a Licença MIT.
