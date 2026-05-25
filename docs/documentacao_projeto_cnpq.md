# Sistema Multi-Agentes para Análise de Pesquisadores CNPq

**Disciplina:** Agentic AI  
**Professor:** Dr. Eduardo Almeida  
**Aluna:** Elen Greice  
**Ano:** 2026

---

## Sumário

1. [Visão Geral do Sistema](#1-visão-geral-do-sistema)
2. [Requisitos do Sistema](#2-requisitos-do-sistema)
3. [Design do Sistema](#3-design-do-sistema)
4. [Implementação](#4-implementação)
5. [Architecture Decision Records (ADRs)](#5-architecture-decision-records-adrs)
6. [Testes e Inconsistências](#6-testes-e-inconsistências)
7. [Implantação](#7-implantação)
8. [Model Context Protocol (MCP)](#8-model-context-protocol-mcp)
9. [Qualidade e Resiliência](#9-qualidade-e-resiliência)
10. [Conclusão](#10-conclusão)

---

## 1. Visão Geral do Sistema

O sistema desenvolvido é uma plataforma multi-agentes que coleta, processa e disponibiliza dados sobre pesquisadores bolsistas do CNPq. O sistema realiza scraping automatizado do site do CNPq e do Currículo Lattes, organiza os dados em um dataset estruturado, e os disponibiliza através de um dashboard interativo com suporte a consultas em linguagem natural.

### 1.1 Objetivos do Sistema

- Coletar automaticamente dados de pesquisadores do site do CNPq
- Enriquecer os dados com informações do Currículo Lattes
- Gerar um dataset estruturado com informações completas dos bolsistas
- Disponibilizar um dashboard interativo para visualização dos dados
- Permitir exportação dos dados em formato CSV e PDF
- Oferecer interface de consulta em linguagem natural
- Registrar log de todas as operações realizadas
- Validar a integridade dos dados automaticamente

### 1.2 Tecnologias Utilizadas

| Tecnologia | Finalidade | Justificativa |
|---|---|---|
| Python 3.x | Linguagem principal | Ecossistema rico com bibliotecas maduras para scraping e IA |
| Streamlit | Dashboard web | Cria interfaces web sem necessidade de HTML/JS |
| BeautifulSoup4 | Web scraping CNPq | Parser HTML robusto para sites estáticos |
| Selenium | Web scraping Lattes | Automação de navegador para sites com JavaScript e CAPTCHA |
| Pandas | Manipulação de dados | Padrão para análise de dados em Python |
| Plotly | Gráficos interativos | Visualizações ricas e interativas |
| Groq API + Llama 3.1 | Linguagem natural | API gratuita com modelo de alta qualidade |
| FPDF2 | Geração de PDF | Simples e eficiente para relatórios |
| gender-guesser | Inferência de sexo | Detecta sexo pelo primeiro nome automaticamente |
| GitHub + Streamlit Cloud | Implantação | Hospedagem gratuita e deploy automatizado |

---

## 2. Requisitos do Sistema

### 2.1 Requisitos Funcionais

| ID | Requisito | Descrição |
|---|---|---|
| RF01 | Coletar Dados | O sistema deve coletar dados automaticamente do site do CNPq |
| RF02 | Enriquecer Dataset | O sistema deve buscar dados complementares no Currículo Lattes |
| RF03 | Inferir Sexo | O sistema deve inferir o sexo do pesquisador pelo primeiro nome |
| RF04 | Mapear UF | O sistema deve identificar o estado (UF) pela sigla da instituição |
| RF05 | Gerar Dataset | Os dados devem ser organizados em formato CSV estruturado |
| RF06 | Visualizar Dashboard | O sistema deve exibir gráficos e tabelas com os dados coletados |
| RF07 | Filtrar Dados | O dashboard deve permitir filtragem por nível, instituição, UF, sexo e situação |
| RF08 | Exportar CSV | O sistema deve permitir download dos dados filtrados em CSV |
| RF09 | Exportar PDF | O sistema deve permitir download dos dados filtrados em PDF |
| RF10 | Consultar Linguagem Natural | O sistema deve responder perguntas em português sobre os dados |
| RF11 | Registrar Log | O sistema deve registrar todas as ações realizadas |
| RF12 | Validar Integridade | O sistema deve validar automaticamente a integridade do dataset |

### 2.2 Requisitos Não Funcionais

| ID | Categoria | Descrição |
|---|---|---|
| RNF01 | Desempenho | Cache de 1 hora para evitar requisições repetidas ao CNPq |
| RNF02 | Disponibilidade | Sistema disponível online via Streamlit Cloud |
| RNF03 | Segurança | Chave de API armazenada em variável de ambiente segura |
| RNF04 | Usabilidade | Interface intuitiva sem necessidade de treinamento |
| RNF05 | Manutenção | Código organizado em módulos por responsabilidade |
| RNF06 | Resiliência | Reinício automático do driver Selenium em caso de falha de sessão |
| RNF07 | Confiabilidade | Validações automáticas de integridade do dataset a cada carregamento |
| RNF08 | Precisão | Respostas de linguagem natural baseadas em dados pré-calculados |

---

## 3. Design do Sistema

### 3.1 Por que Arquitetura Multi-Agentes?

A escolha pela arquitetura multi-agentes se justifica pela necessidade de separar responsabilidades complexas e distintas: coleta de dados de dois sites diferentes, enriquecimento de dados, visualização e consulta em linguagem natural. Cada responsabilidade opera de forma relativamente independente, mas precisa de coordenação. Um sistema monolítico dificultaria a manutenção, o teste individual de cada componente e a substituição de partes sem afetar o todo.

### 3.2 Agentes do Sistema

| Agente | Responsabilidade | Ferramentas (Tools) |
|---|---|---|
| Orchestrator Agent | Coordena todos os agentes e define o fluxo de execução | Gerenciamento de estado, logging |
| Scraping Agent | Coleta dados do site do CNPq automaticamente | requests, BeautifulSoup4, pandas |
| Enrichment Agent | Busca dados complementares no Currículo Lattes | Selenium, ChromeDriver |
| Data Agent | Processa, limpa e organiza os dados coletados | pandas, gender-guesser, regex |
| Dashboard Agent | Exibe visualizações e permite exportação | Streamlit, Plotly, FPDF2 |
| Query Agent | Responde perguntas em linguagem natural | Groq API, Llama 3.1 8B Instant |
| Logger Agent | Registra todas as operações do sistema | logging, arquivo .log |
| Validation Agent | Valida integridade do dataset | pandas, assertions |

### 3.3 Fluxo do Sistema (Flow)

Fluxo de coleta de dados (executado localmente):
```
Scraping Agent acessa site CNPq
       ↓
Extrai 480 pesquisadores
       ↓
Validation Agent valida os dados coletados
       ↓
Data Agent infere sexo, UF e área de atuação
       ↓
Enrichment Agent acessa Currículo Lattes via Selenium
       ↓
Data Agent extrai ano de conclusão do doutorado via regex
       ↓
Dataset final salvo em CSV e enviado para GitHub
```

Fluxo do dashboard (executado online):
```
Dashboard Agent carrega dados do CSV (GitHub)
       ↓
Validation Agent valida integridade do dataset
       ↓
Logger Agent registra inicialização
       ↓
Usuário aplica filtros → Dashboard Agent filtra em tempo real
       ↓
Logger Agent registra filtros aplicados
       ↓
Usuário faz pergunta → Query Agent acionado
       ↓
Query Agent usa dados pré-calculados + API Groq
       ↓
Logger Agent registra consulta e resposta
```

### 3.4 Comunicação entre Agentes (Orchestration)

O modelo de orquestração adotado é o **Centralized Orchestration**, onde o Orchestrator Agent coordena todos os outros agentes. A escolha por orquestração centralizada se justifica pela natureza sequencial do pipeline de dados e pela facilidade de rastreamento e logging das operações.

### 3.5 Handoffs

| De | Para | Condição |
|---|---|---|
| Orchestrator | Scraping Agent | Ao iniciar a coleta de dados |
| Scraping Agent | Validation Agent | Após coletar os dados do CNPq |
| Validation Agent | Data Agent | Após validar a integridade |
| Data Agent | Enrichment Agent | Após organizar os dados iniciais |
| Enrichment Agent | Data Agent | Após coletar dados do Lattes |
| Data Agent | Dashboard Agent | Após finalizar o dataset completo |
| Dashboard Agent | Validation Agent | Ao carregar o dashboard |
| Dashboard Agent | Logger Agent | A cada ação do usuário |
| Dashboard Agent | Query Agent | Quando usuário digita uma pergunta |
| Query Agent | Dashboard Agent | Após receber resposta da API Groq |

### 3.6 Guardrails

- **Validação de linhas:** apenas linhas com 6 ou mais colunas são processadas
- **Filtro de cabeçalhos:** linhas com texto "NOME" são ignoradas
- **Deduplicação:** pesquisadores duplicados são removidos pelo nome
- **Timeout:** requisições ao CNPq têm limite de 30 segundos
- **Cache:** dados armazenados por 1 hora para evitar sobrecarga no servidor
- **Reinício automático:** driver Selenium reinicia em caso de sessão perdida
- **Retomada de progresso:** Enrichment Agent retoma do ponto onde parou
- **Segurança:** chave de API em variável de ambiente, nunca no código
- **Validações automáticas:** dataset validado a cada carregamento do dashboard
- **Regras do Query Agent:** 14 regras obrigatórias para respostas precisas e confiáveis
- **Dados pré-calculados:** estatísticas calculadas no Python antes de enviar ao modelo

### 3.7 Reasoning e Planning

- **Scraping Agent:** decide quais linhas são dados válidos com base em regras de validação
- **Data Agent:** planeja limpeza dos dados, identificando duplicatas e inferindo campos ausentes
- **Enrichment Agent:** identifica as âncoras HTML corretas para cada seção do Lattes
- **Query Agent:** usa dados pré-calculados para formular respostas precisas em português
- **Validation Agent:** verifica proativamente a integridade antes de qualquer processamento
- **Orchestrator:** planeja a sequência de execução dos agentes baseado no estado atual

---

## 4. Implementação

### 4.1 Estrutura de Arquivos

```
projeto-cnpq/
├── agents/
│   └── logger_agent.py          # Logger Agent
├── tools/
│   ├── cnpq_scraper.py          # Scraping Agent
│   ├── lattes_scraper.py        # Enrichment Agent
│   ├── extrair_ano.py           # Data Agent - extrai ano de conclusão
│   ├── corrigir_area.py         # Data Agent - corrige áreas de atuação
│   ├── corrigir_area2.py        # Data Agent - correção complementar
│   └── corrigir_sexo.py         # Data Agent - corrige sexo indefinido
├── data/
│   └── dataset.csv              # Dataset final com 480 pesquisadores
├── dashboard/
│   └── app.py                   # Dashboard + Query + Logger + Validation
├── logs/
│   └── operacoes.log            # Log de todas as operações
├── docs/
│   ├── documentacao_projeto_cnpq.md
│   └── documentacao_projeto_cnpq_v2.docx
├── .env                         # Variáveis de ambiente (não versionado)
├── .gitignore
└── requirements.txt
```

### 4.2 Dataset Final

O dataset contém 480 pesquisadores com os seguintes campos:

| Campo | Descrição | Fonte |
|---|---|---|
| nome | Nome completo do pesquisador | CNPq |
| sexo | Masculino/Feminino | Inferido pelo primeiro nome (gender-guesser + dicionário manual) |
| instituicao | Instituição de vínculo | CNPq |
| uf | Estado (UF) | Mapeamento por sigla da instituição |
| nivel_bolsa | Nível da bolsa CNPq | CNPq |
| area_atuacao | Área de atuação detalhada | Lattes (AreasAtuacao) |
| ano_conclusao_doutorado | Ano de conclusão do doutorado | Extraído da formação via regex |
| url_lattes | Link do Currículo Lattes | Lattes |
| google_scholar | Link do Google Scholar | N/A |
| vigencia_inicio | Início da vigência da bolsa | CNPq |
| vigencia_termino | Término da vigência da bolsa | CNPq |
| situacao | Situação atual da bolsa | CNPq |
| formacao_academica | Formação acadêmica completa | Lattes |
| pos_doutorado | Pós-doutorado(s) realizados | Lattes |

### 4.3 Log de Operações

O sistema registra automaticamente as seguintes operações:

| Operação | Quando ocorre |
|---|---|
| DASHBOARD INICIADO | Ao carregar o dashboard |
| VALIDACAO DO DATASET | Após carregar os dados |
| FILTRO APLICADO | Quando usuário seleciona filtros |
| EXPORTACAO CSV | Quando usuário baixa CSV |
| EXPORTACAO PDF | Quando usuário baixa PDF |
| CONSULTA LINGUAGEM NATURAL | Quando usuário faz uma pergunta |
| RESPOSTA GERADA | Após resposta bem-sucedida |
| ERRO NA CONSULTA | Em caso de falha na API |
| ATUALIZACAO DE DADOS | Quando usuário clica em Atualizar |

### 4.4 Validações Automáticas de Integridade

O sistema valida automaticamente:

- Dataset não está vazio
- Dataset tem mais de 100 registros
- Colunas obrigatórias existem (nome, sexo, instituicao, uf, nivel_bolsa, situacao)
- Não há UFs nulas
- Não há sexos indefinidos

Em caso de problema crítico, exibe alerta vermelho no dashboard e registra no log. Em caso de aviso, exibe alerta amarelo.

### 4.5 Query Agent — Estratégia de Dados Pré-Calculados

Para garantir respostas precisas, o sistema pré-calcula estatísticas no Python antes de enviar ao modelo:

- UF com mais/menos pesquisadores (com valores exatos)
- Top 3 e bottom 3 UFs
- UF com mais/menos pesquisadoras femininas
- UFs sem pesquisadoras femininas
- Distribuição completa de sexo por UF

Isso evita que o modelo interprete dados brutos e cometa erros de cálculo.

### 4.6 Regras do Query Agent

O Query Agent segue 14 regras obrigatórias:

1. Responder APENAS com base nos dados fornecidos
2. Se não puder responder: "Não tenho essa informação nos dados disponíveis"
3. Citar números EXATOS dos dados fornecidos
4. Responder SEMPRE em português
5. Não responder perguntas fora do escopo do CNPq
6. Explicar ambiguidades antes de responder
7. NUNCA fazer suposições sobre dados ausentes
8. Citar nomes exatamente como constam nos dados
9. Informar que Google Scholar não está disponível
10. Ser direto e conciso (máximo 5 linhas)
11. Para rankings, citar apenas top 3 com números exatos
12. NUNCA usar linguagem de incerteza
13. Citar números exatos quando disponíveis
14. Para sexo por UF, usar APENAS os dados da tabela pré-calculada

---

## 5. Architecture Decision Records (ADRs)

### ADR-001: Adoção de Arquitetura Multi-Agentes

| Campo | Descrição |
|---|---|
| **Contexto** | O sistema precisa realizar tarefas complexas e distintas: scraping de dois sites, processamento de dados, visualização e consulta em linguagem natural |
| **Decisão** | Adotar arquitetura multi-agentes com responsabilidades bem definidas |
| **Justificativa** | Permite separar responsabilidades complexas, facilita teste individual de cada componente e substituição de partes sem afetar o todo. Sistema monolítico dificultaria manutenção e rastreamento de erros. |
| **Alternativas** | Sistema monolítico (mais simples, mas difícil de manter), microserviços (mais complexo e desnecessário) |
| **Consequências** | Maior organização do código, facilidade de manutenção e extensibilidade |

### ADR-002: Escolha da Linguagem de Programação

| Campo | Descrição |
|---|---|
| **Contexto** | Necessidade de scraping, processamento de dados, interface web e integração com APIs de IA |
| **Decisão** | Python 3.x |
| **Justificativa** | Ecossistema rico com bibliotecas maduras para todas as necessidades. Curva de aprendizado acessível. |
| **Alternativas** | Node.js (menor suporte a data science), Java (mais verboso) |
| **Consequências** | Desenvolvimento rápido e código legível |

### ADR-003: Ferramenta de Scraping do CNPq

| Campo | Descrição |
|---|---|
| **Contexto** | Necessidade de coletar dados da tabela de pesquisadores do site do CNPq |
| **Decisão** | requests + BeautifulSoup4 |
| **Justificativa** | O site do CNPq retorna HTML estático, não requerendo JavaScript. Selenium seria desnecessário e mais lento. |
| **Alternativas** | Selenium (mais pesado), Scrapy (mais complexo para um único site) |
| **Consequências** | Scraping rápido e eficiente |

### ADR-004: Ferramenta de Scraping do Lattes

| Campo | Descrição |
|---|---|
| **Contexto** | O Lattes requer interação com formulários, cliques e CAPTCHA |
| **Decisão** | Selenium com ChromeDriver |
| **Justificativa** | Única alternativa viável após tentativas bloqueadas |
| **Tentativas anteriores** | requests direto (bloqueado pelo CAPTCHA), XML do Lattes via URL (timeout) |
| **Mudança de abordagem** | Primeira versão identificou âncoras HTML incorretamente. Inspecionamento via DevTools corrigiu o problema. |
| **Consequências** | Processo mais lento, mas funcional com reinício automático de sessão |

### ADR-005: Framework de Dashboard

| Campo | Descrição |
|---|---|
| **Contexto** | Necessidade de interface web interativa sem expertise em frontend |
| **Decisão** | Streamlit |
| **Justificativa** | Permite dashboards interativos apenas com Python. Deploy gratuito no Streamlit Cloud. |
| **Alternativas** | Dash/Plotly (mais complexo), Flask (requer frontend separado) |
| **Consequências** | Desenvolvimento rápido, com menos flexibilidade de customização |

### ADR-006: Modelo de Linguagem

| Campo | Descrição |
|---|---|
| **Contexto** | Necessidade de interface de linguagem natural em português |
| **Decisão** | Groq API com Llama 3.1 8B Instant |
| **Justificativa** | API gratuita com bom desempenho em português |
| **Primeira tentativa** | OpenAI GPT-4o — cartões brasileiros rejeitados na plataforma |
| **Mudança de abordagem** | Groq API. Modelo llama3-8b-8192 foi descontinuado, atualizado para llama-3.1-8b-instant |
| **Consequências** | Sem custo operacional, qualidade adequada para o caso de uso |

### ADR-007: Estratégia de Hospedagem

| Campo | Descrição |
|---|---|
| **Contexto** | Necessidade de disponibilizar o dashboard online |
| **Decisão** | GitHub + Streamlit Community Cloud |
| **Justificativa** | Hospedagem gratuita com deploy automático |
| **Primeira tentativa** | Execução local — bloqueada por firewall na porta 8501 |
| **Mudança de abordagem** | Deploy no Streamlit Community Cloud |
| **Consequências** | Sistema acessível de qualquer dispositivo |

### ADR-008: Fonte dos Dados no Dashboard

| Campo | Descrição |
|---|---|
| **Contexto** | Streamlit Cloud não consegue acessar o CNPq diretamente (timeout) |
| **Decisão** | CSV hospedado no GitHub via URL raw |
| **Primeira tentativa** | Scraping em tempo real — bloqueado por timeout no Streamlit Cloud |
| **Mudança de abordagem** | Dataset estático no GitHub, recarregado via botão "Atualizar dados" |
| **Consequências** | Dados podem ficar desatualizados, mas processo de atualização é simples |

### ADR-009: Estratégia de Inferência de Sexo

| Campo | Descrição |
|---|---|
| **Contexto** | O dataset não contém o campo sexo — necessário inferir |
| **Decisão** | Biblioteca gender-guesser + dicionário manual de nomes brasileiros |
| **Justificativa** | gender-guesser funciona bem para nomes internacionais, mas falha em muitos nomes brasileiros. O dicionário manual complementa os casos indefinidos. |
| **Primeira tentativa** | Apenas gender-guesser — resultou em 96 pesquisadores com sexo "Indefinido" |
| **Mudança de abordagem** | Criado dicionário manual com 95 nomes brasileiros. Apenas 1 caso corrigido manualmente (Erickson). |
| **Consequências** | 100% dos pesquisadores com sexo definido |

### ADR-010: Estratégia de Respostas do Query Agent

| Campo | Descrição |
|---|---|
| **Contexto** | Modelo de linguagem cometia erros ao interpretar dados brutos |
| **Decisão** | Pré-calcular estatísticas no Python e enviar resultados prontos ao modelo |
| **Justificativa** | Modelos de linguagem são ruins em cálculos numéricos. Pré-calcular no Python garante precisão. |
| **Primeira tentativa** | Enviar dados brutos — modelo se perdia em cálculos e dava respostas erradas |
| **Mudança de abordagem** | Python calcula, modelo apenas formata a resposta em português |
| **Consequências** | Respostas precisas e confiáveis para perguntas numéricas |

---

## 6. Testes e Inconsistências

### 6.1 Testes Realizados

| Teste | Resultado Esperado | Resultado Obtido |
|---|---|---|
| Scraping do CNPq | Coletar todos os pesquisadores | 480 pesquisadores coletados |
| Geração do CSV | Arquivo salvo com 15 colunas | CSV gerado corretamente |
| Inferência de sexo | Classificar todos os pesquisadores | 100% classificados após correção manual |
| Mapeamento de UF | Identificar estado pela instituição | 480 pesquisadores com UF identificada |
| Scraping do Lattes | Extrair formação, área e URL | 480 pesquisadores enriquecidos |
| Extração do ano de doutorado | Extrair ano via regex | Funcionando para todos |
| Correção de áreas | Corrigir registros com dados errados | 10 registros corrigidos |
| Filtros do dashboard | Filtrar por múltiplos critérios | Funcionando corretamente |
| Exportação CSV | Download do arquivo | Funcionando |
| Exportação PDF | Download do arquivo | Funcionando |
| Linguagem natural — pergunta simples | Resposta precisa | Funcionando |
| Linguagem natural — cruzamento de dados | Resposta com dados de sexo por UF | Funcionando após pré-cálculo |
| Linguagem natural — pergunta fora do escopo | Recusar resposta | Funcionando |
| Linguagem natural — dado ausente | "Não tenho essa informação" | Funcionando |
| Log de operações | Registrar todas as ações | Funcionando |
| Validações de integridade | Alertar sobre problemas | Funcionando |
| Deploy Streamlit Cloud | Dashboard acessível online | Funcionando |

### 6.2 Inconsistências Identificadas e Corrigidas

| Inconsistência | Quantidade | Solução |
|---|---|---|
| Pesquisadores com sexo "Indefinido" | 96 | Dicionário manual de nomes brasileiros |
| Pesquisador com sexo indefinido restante | 1 (Erickson) | Correção manual |
| Área de atuação incorreta (atuação profissional capturada) | 10 | Reprocessamento com Selenium |
| Áreas ainda incorretas após reprocessamento | 10 | Definidas como "Ciência da Computação" |
| Pesquisador com URL inválida | 1 (Cláudio Lucchesi) | Correção manual com dados do Lattes |
| Instituições sem mapeamento de UF | 13 | Adicionadas ao dicionário de mapeamento |
| Modelo de linguagem respondendo errado | Vários casos | Pré-cálculo de estatísticas no Python |
| Erro 413 (contexto muito grande) | 1 | Redução do contexto enviado ao modelo |

### 6.3 Comportamento do Sistema em Mudanças no CNPq

O sistema foi projetado para detectar mudanças no site do CNPq:

| Mudança | Impacto | Solução |
|---|---|---|
| Novos/removidos pesquisadores | Nenhum | Automático |
| Nova UF/instituição | UF fica NaN — alerta no dashboard | Atualizar dicionário de mapeamento |
| Colunas renomeadas | Alerta crítico no dashboard | Atualizar scraper |
| Layout HTML mudado | Scraper quebra — alerta crítico | Inspecionar HTML e corrigir |

---

## 7. Implantação

### 7.1 Processo de Deploy

1. Desenvolvimento e testes locais com Python
2. Versionamento no GitHub (repositório: `elengreice/projeto-cnpq`)
3. Configuração das variáveis de ambiente no Streamlit Cloud (`GROQ_API_KEY`)
4. Deploy automático via Streamlit Community Cloud
5. Validação do sistema em produção

### 7.2 Atualização dos Dados

1. Executar: `python tools/cnpq_scraper.py`
2. Executar: `python tools/lattes_scraper.py`
3. Executar: `python tools/extrair_ano.py`
4. Commit e push: `git add . && git commit -m "atualiza dados" && git push`
5. Dashboard carrega automaticamente os dados atualizados

### 7.3 Acesso ao Sistema

- **Repositório GitHub:** https://github.com/elengreice/projeto-cnpq
- **Dashboard online:** disponível via Streamlit Community Cloud

---

## 8. Model Context Protocol (MCP)

O MCP define como o modelo de linguagem interage com o contexto dos dados.

### 8.1 Contexto Fornecido ao Modelo

- Total de pesquisadores no dataset filtrado
- Top 5 instituições com mais pesquisadores
- Distribuição por nível, situação, UF e sexo
- Estatísticas pré-calculadas de sexo por UF
- Rankings pré-calculados de UFs (mais/menos pesquisadores)
- Exemplos das primeiras 10 linhas do dataset

### 8.2 Protocolo de Comunicação

- **System message:** contexto dos dados + 14 regras obrigatórias
- **User message:** pergunta do usuário em linguagem natural
- **Assistant message:** resposta gerada em português

---

## 9. Qualidade e Resiliência

### 9.1 Validações Automáticas

O sistema executa automaticamente as seguintes validações ao carregar o dashboard:

```python
# Dataset não vazio
if len(df) == 0: → alerta crítico

# Quantidade mínima de registros
if len(df) < 100: → alerta de atenção

# Colunas obrigatórias presentes
for col in colunas_obrigatorias: → alerta crítico se ausente

# UFs sem mapeamento
if df["uf"].isna().sum() > 0: → alerta de atenção

# Sexos indefinidos
if (df["sexo"] == "Indefinido").sum() > 0: → alerta de atenção
```

### 9.2 Resiliência do Enrichment Agent

- Reinício automático do ChromeDriver em caso de sessão perdida
- Até 3 tentativas por pesquisador antes de desistir
- Retomada automática do ponto onde parou em caso de interrupção
- Salvamento do progresso a cada 5 pesquisadores

### 9.3 Log de Operações

Todas as operações são registradas com data, hora e detalhes:

```
2026-05-25 13:22:47 | INFO | DASHBOARD INICIADO | Total: 480
2026-05-25 13:39:38 | INFO | FILTRO APLICADO | UF: ['CE']
2026-05-25 13:40:40 | INFO | EXPORTACAO CSV | Total exportados: 480
2026-05-25 13:44:55 | INFO | CONSULTA LINGUAGEM NATURAL | Pergunta: ...
2026-05-25 13:44:56 | INFO | RESPOSTA GERADA | Sucesso
```

---

## 10. Conclusão

O sistema multi-agentes desenvolvido atende a todos os requisitos propostos no trabalho. Foi construído com tecnologias modernas e gratuitas, com foco em funcionalidade, resiliência, precisão e boas práticas de engenharia de software.

### 10.1 Principais Desafios e Soluções

| Desafio | Solução Adotada |
|---|---|
| Firewall bloqueando Streamlit local | Deploy no Streamlit Community Cloud |
| CNPq bloqueando acesso do Streamlit Cloud | Dataset estático no GitHub |
| CAPTCHA no Currículo Lattes | Selenium com resolução manual pelo usuário |
| Sessão do Selenium sendo perdida | Reinício automático com retomada de progresso |
| Cartão brasileiro rejeitado na OpenAI | Migração para Groq API (gratuita) |
| Modelo Groq descontinuado | Atualização para llama-3.1-8b-instant |
| 96 pesquisadores com sexo indefinido | Dicionário manual de nomes brasileiros |
| Área de atuação capturada incorretamente | Correção de 10 registros |
| Modelo errando cálculos numéricos | Pré-cálculo de estatísticas no Python |
| Erro 413 (contexto muito grande) | Redução e otimização do contexto |
| Google Scholar não disponível automaticamente | Campo documentado como N/A com justificativa |

### 10.2 Limitações Conhecidas

- **Google Scholar:** não obtido automaticamente sem risco de dados incorretos
- **Atualização de dados:** requer execução manual dos scrapers localmente
- **Dados do Lattes:** dependentes da disponibilidade do site e do CAPTCHA

### 10.3 Possíveis Melhorias Futuras

- Automação completa da atualização de dados via agendamento
- Integração com a API oficial do Lattes quando disponível
- Busca automatizada do Google Scholar
- Notificações automáticas quando o dataset ficar desatualizado
