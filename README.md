#DASHBOARD RH
Este é um dashboard interativo de Recursos Humanos, construído com Streamlit, para análise e visualização de dados de funcionários. O objetivo é fornecer uma visão rápida e detalhada sobre a força de trabalho da empresa, com gráficos, filtros e a possibilidade de exportar os dados filtrados.

Funcionalidades Principais
Filtros Dinâmicos: Filtre os dados por área, cargo e nível para explorar subconjuntos específicos de informações.

Visualizações Interativas: Veja a distribuição de idade, sexo e salário por meio de gráficos que se atualizam em tempo real conforme você usa os filtros.

KPIs (Indicadores-chave de Desempenho): Acompanhe métricas essenciais como o número total de funcionários, salário médio, tempo médio de contratação e rotatividade (turnover).

Tabela de Dados: Visualize a tabela completa dos dados filtrados.

Exportação de Dados: Baixe a tabela filtrada em formato CSV ou Excel com um clique.

Como Executar o Projeto
Siga os passos abaixo para rodar a aplicação em sua máquina.

Pré-requisitos
Certifique-se de que você tem o Python instalado. As bibliotecas necessárias estão listadas no arquivo requirements.txt.

1. Clonar o repositório
Bash

git clone <URL_DO_SEU_REPOSITORIO>
cd <NOME_DO_SEU_REPOSITORIO>
2. Criar e ativar o ambiente virtual
É uma boa prática usar um ambiente virtual para isolar as dependências do projeto.

Windows

Bash

python -m venv venv
.\venv\Scripts\activate
macOS/Linux

Bash

python3 -m venv venv
source venv/bin/activate
3. Instalar as dependências
Com o ambiente virtual ativado, instale todas as bibliotecas necessárias usando o arquivo requirements.txt.

Bash

pip install -r requirements.txt
4. Rodar a aplicação
Certifique-se de que o arquivo de dados (BaseFuncionarios.xlsx) está na mesma pasta que o arquivo app.py.

Bash

streamlit run app.py
O Streamlit irá iniciar um servidor local e abrir o dashboard no seu navegador padrão.
