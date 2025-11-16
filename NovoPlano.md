---

### **Blueprint Técnico: Sistema Inteligente de Geração de Fechamentos para Lotofácil**

**Objetivo Geral:** Criar uma aplicação desktop ou web local que assiste o usuário na criação de jogos de Lotofácil, utilizando análise de dados históricos e a aplicação de fechamentos matemáticos para otimizar o custo e aumentar as chances de premiação.

---

### **Módulo 1: Coleta e Gerenciamento de Dados Históricos**

*   **Objetivo Principal:** Obter, limpar e manter uma base de dados atualizada com todos os resultados históricos da Lotofácil. Este é o alicerce de toda a inteligência do sistema.

*   **Funcionalidades Detalhadas:**
    1.  **Web Scraping/Coleta de Dados:**
        *   Criar uma função que acessa uma fonte de dados confiável (como o site da Caixa) para baixar os resultados.
        *   O programa deve extrair as dezenas sorteadas e o número do concurso de cada resultado.
        *   Implementar um mecanismo de fallback: se a coleta online falhar, o sistema deve ser capaz de ler os dados de um arquivo local (CSV) que pode ser atualizado manualmente.
    2.  **Limpeza e Estruturação dos Dados:**
        *   Processar os dados coletados para garantir que estejam em um formato consistente (ex: todas as dezenas como números inteiros).
        *   Organizar os dados em uma tabela (DataFrame), onde cada linha representa um concurso e as colunas contêm o número do concurso e as dezenas sorteadas.
    3.  **Armazenamento Local:**
        *   Salvar o DataFrame limpo em um arquivo local, como `resultados_lotofacil.csv`.
        *   Criar uma função de "atualização" que verifica se há novos concursos disponíveis online e os adiciona ao arquivo local, sem precisar baixar todo o histórico novamente.

*   **Tecnologias/Bibliotecas Sugeridas (Python):**
    *   `requests`: Para fazer as requisições HTTP e buscar os dados da web.
    *   `BeautifulSoup4` ou `lxml`: Para extrair (parse) os dados do HTML da página de resultados.
    *   `pandas`: Essencial para manipular, limpar e armazenar os dados em formato de tabela (DataFrame) e exportar para CSV.

*   **Entradas (Inputs):** URL da página de resultados da Caixa.
*   **Saídas (Outputs):** Um arquivo `resultados_lotofacil.csv` limpo e estruturado.

---

### **Módulo 2: Painel de Análise e Inteligência Estatística**

*   **Objetivo Principal:** Analisar os dados históricos do Módulo 1 e apresentar ao usuário um painel visual com estatísticas e padrões que o ajudem a tomar decisões informadas.

*   **Funcionalidades Detalhadas:**
    1.  **Cálculos Estatísticos:** Criar funções separadas para calcular:
        *   **Frequência de Dezenas:** Contar quantas vezes cada dezena (de 1 a 25) foi sorteada.
        *   **Atraso de Dezenas:** Calcular há quantos concursos cada dezena não é sorteada.
        *   **Ciclos de Dezenas:** Identificar quais dezenas ainda não foram sorteadas dentro de um ciclo recente.
        *   **Padrões de Pares/Ímpares:** Calcular a distribuição de dezenas pares e ímpares para cada concurso e mostrar a frequência de cada padrão (ex: "8 ímpares e 7 pares" ocorreu em X% dos sorteios).
        *   **Padrões de Moldura/Miolo:** Classificar as dezenas (Moldura: 1,2,3,4,5,6,10,11,15,16,20,21,22,23,24,25; Miolo: 7,8,9,12,13,14,17,18,19) e analisar a frequência de suas combinações.
    2.  **Visualização de Dados:**
        *   Apresentar os dados acima em um painel interativo.
        *   Utilizar gráficos de barras para a frequência, tabelas para o atraso e gráficos de pizza para os padrões (par/ímpar, moldura/miolo).

*   **Tecnologias/Bibliotecas Sugeridas (Python):**
    *   `pandas`: Para realizar todos os cálculos de forma eficiente a partir do CSV.
    *   `streamlit`: Para criar a interface web e exibir os gráficos e tabelas de forma interativa.
    *   `plotly` ou `matplotlib`: Para gerar os gráficos que serão exibidos pelo Streamlit.

*   **Entradas (Inputs):** O arquivo `resultados_lotofacil.csv` do Módulo 1.
*   **Saídas (Outputs):** Uma interface visual (dashboard) com as análises estatísticas.

---

### **Módulo 3: Seletor de Estratégias de Fechamento**

*   **Objetivo Principal:** Permitir que o usuário escolha uma estratégia de fechamento com base no custo-benefício, informando com quantas dezenas deseja jogar.

*   **Funcionalidades Detalhadas:**
    1.  **Biblioteca de Fechamentos:**
        *   Criar uma estrutura de dados interna (um dicionário Python é ideal) que armazene as matrizes ou regras de todos os fechamentos disponíveis. A chave do dicionário seria a quantidade de dezenas (ex: 18), e o valor seria uma lista de estratégias possíveis para essa quantidade.
        *   Exemplo da estrutura: `fechamentos = {18: [{'garantia': 14, 'condicao': 15, 'jogos': 32, 'custo': 96.00}, ...]}`
    2.  **Interface de Seleção:**
        *   Apresentar um controle (slider ou dropdown) para o usuário selecionar a quantidade de dezenas que deseja usar em seu universo (ex: de 16 a 20).
    3.  **Exibição Dinâmica de Opções:**
        *   Com base na seleção do usuário, o sistema deve consultar a biblioteca de fechamentos e exibir dinamicamente uma tabela comparativa (como a descrita no nosso diálogo anterior) mostrando a garantia, condição, quantidade de jogos e custo de cada opção.
    4.  **Gerenciamento de Estado:**
        *   O sistema deve armazenar a estratégia de fechamento escolhida pelo usuário para ser usada nos próximos módulos.

*   **Tecnologias/Bibliotecas Sugeridas (Python):**
    *   `streamlit`: Para os componentes de interface (slider, botões, tabelas).
    *   Pura lógica Python para criar e consultar o dicionário de fechamentos.

*   **Entradas (Inputs):** A quantidade de dezenas do universo (ex: 18) escolhida pelo usuário.
*   **Saídas (Outputs):** A estratégia de fechamento completa (garantia, condição, número de jogos, etc.) salva em uma variável de estado.

---

### **Módulo 4: Seleção Assistida de Dezenas**

*   **Objetivo Principal:** Fornecer uma interface para o usuário selecionar as dezenas que comporão seu universo, utilizando as informações do Painel de Análise (Módulo 2).

*   **Funcionalidades Detalhadas:**
    1.  **Interface de Seleção Numérica:**
        *   Exibir um campo de seleção múltipla (`multiselect`) contendo todas as 25 dezenas da Lotofácil.
        *   O campo deve ser configurado dinamicamente para aceitar a quantidade exata de dezenas exigida pela estratégia escolhida no Módulo 3 (ex: se o usuário escolheu um fechamento de 18 dezenas, o campo só permitirá selecionar 18).
    2.  **Função de Sugestão (IA):**
        *   Criar um botão "Sugerir Dezenas".
        *   Ao ser clicado, ele executa um algoritmo que usa os dados do Módulo 2 para pré-selecionar as dezenas. O algoritmo pode ser simples (ex: "selecionar as 10 mais quentes + as 8 mais atrasadas") ou mais complexo.
    3.  **Validação:**
        *   O sistema deve impedir que o usuário avance para o próximo passo sem ter selecionado a quantidade correta de dezenas.

*   **Tecnologias/Bibliotecas Sugeridas (Python):**
    *   `streamlit`: Para o componente `st.multiselect` e validações na interface.
    *   `pandas`: A função de sugestão usará o DataFrame analisado para fazer sua recomendação.

*   **Entradas (Inputs):** A estratégia escolhida no Módulo 3 (para saber a quantidade de dezenas) e a interação do usuário com o painel e o campo de seleção.
*   **Saídas (Outputs):** Uma lista Python contendo as dezenas finais escolhidas pelo usuário.

---

### **Módulo 5: Motor de Geração de Fechamentos**

*   **Objetivo Principal:** Aplicar a matriz do fechamento escolhido sobre as dezenas selecionadas pelo usuário para gerar os jogos finais.

*   **Funcionalidades Detalhadas:**
    1.  **Lógica do Fechamento:**
        *   Esta é a função central. Ela receberá como entrada a lista de dezenas do usuário (Módulo 4) e a estratégia (Módulo 3).
        *   A função irá acessar a matriz matemática correspondente à estratégia na biblioteca de fechamentos. As matrizes são o "segredo" dos fechamentos e precisam ser pesquisadas ou adquiridas de fontes especializadas em "Wheeling Systems".
        *   O algoritmo irá mapear as dezenas do usuário para os índices da matriz, gerando assim as combinações de jogos que cumprem a garantia.
    2.  **Exibição dos Jogos:**
        *   Apresentar os jogos gerados em uma lista clara e formatada na interface.
    3.  **Funcionalidades de Exportação:**
        *   Adicionar botões para "Copiar para Área de Transferência" ou "Exportar para TXT", facilitando que o usuário utilize os jogos gerados.

*   **Tecnologias/Bibliotecas Sugeridas (Python):**
    *   Pura lógica Python para a implementação do algoritmo de mapeamento da matriz.
    *   `streamlit`: Para exibir os resultados e os botões de exportação.

*   **Entradas (Inputs):** A lista de dezenas selecionadas (Módulo 4) e a estratégia de fechamento (Módulo 3).
*   **Saídas (Outputs):** A lista final de jogos (listas de listas ou listas de tuplas), pronta para ser apostada.