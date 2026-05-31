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

O sistema desenvolvido é uma plataforma multi-agentes que coleta, processa e disponibiliza dados sobre pesquisadores bolsistas do CNPq. O sistema realiza scraping automatizado do site do CNPq e do Currículo Lattes, organiza os dados em um dataset estruturado, e os disponibiliza através de um dashboard interativo com suporte a consultas em linguagem natural via LangChain Pandas Agent com GPT-4o.

### 1.1 Objetivos do Sistema

- Coletar automaticamente dados de pesquisadores do site do CNPq
- Enriquecer os dados com informações do Currículo Lattes
- Gerar um dataset estruturado com informações completas dos bolsistas
- Disponibilizar um dashboard interativo para visualização dos dados
- Permitir exportação dos dados em formato CSV e PDF
- Oferecer interface de consulta em linguagem natural com precisão total
- Registrar log de todas as operações realizadas
- Validar a integridade dos dados automaticamente
- Detectar e tratar novos e removidos pesquisadores automaticamente

### 1.2 Tecnologias Utilizadas

| Tecnologia | Finalidade | Justificativa |
|---|---|---|
| Python 3.x | Linguagem principal | Ecossistema rico com bibliotecas maduras para scraping e IA |
| Streamlit | Dashboard web | Cria interfaces web sem necessidade de HTML/JS |
| BeautifulSoup4 | Web scraping CNPq | Parser HTML robusto para sites estáticos |
| Selenium | Web scraping Lattes | Automação de navegador para sites com JavaScript e CAPTCHA |
| Pandas | Manipulação de dados | Padrão para análise de dados em Python |
| Plotly | Gráficos interativos | Visualizações ricas e interativas |
| LangChain + GPT-4o | Linguagem natural | Agente que executa código pandas para respostas precisas |
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
| RF10 | Consultar Linguagem Natural | O sistema deve responder qualquer pergunta em português sobre os dados com precisão total |
| RF11 | Registrar Log | O sistema deve registrar todas as ações realizadas com data e hora |
| RF12 | Validar Integridade | O sistema deve validar automaticamente a integridade do dataset |
| RF13 | Detectar Mudanças | O sistema deve detectar novos e removidos pesquisadores no CNPq |
| RF14 | Gerenciar Ativos | O sistema deve marcar pesquisadores removidos como inativos sem excluí-los |

### 2.2 Requisitos Não Funcionais

| ID | Categoria | Descrição |
|---|---|---|
| RNF01 | Desempenho | Cache de 1 hora para evitar requisições repetidas ao CNPq |
| RNF02 | Disponibilidade | Sistema disponível online via Streamlit Cloud |
| RNF03 | Segurança | Chaves de API armazenadas em variáveis de ambiente seguras |
| RNF04 | Usabilidade | Interface intuitiva sem necessidade de treinamento |
| RNF05 | Manutenção | Código organizado em módulos por responsabilidade |
| RNF06 | Resiliência | Reinício automático do driver Selenium em caso de falha de sessão |
| RNF07 | Confiabilidade | Validações automáticas de integridade do dataset a cada carregamento |
| RNF08 | Precisão | Respostas de linguagem natural via execução real de código pandas |
| RNF09 | Disponibilidade | Fallback automático CNPq → GitHub → arquivo local |
| RNF10 | Rastreabilidade | Pesquisadores removidos mantidos no dataset com campo ativo=N |

---

## 3. Design do Sistema

### 3.1 Por que Arquitetura Multi-Agentes?

A escolha pela arquitetura multi-agentes se justifica pela necessidade de separar responsabilidades complexas e distintas: coleta de dados de dois sites diferentes, enriquecimento de dados, visualização, consulta em linguagem natural, logging, validação e gerenciamento de ciclo de vida dos pesquisadores. Um sistema monolítico dificultaria a manutenção, o teste individual de cada componente e a substituição de partes sem afetar o todo.

### 3.2 Agentes do Sistema

| Agente | Responsabilidade | Ferramentas (Tools) |
|---|---|---|
| Orchestrator Agent | Coordena todos os agentes e define o fluxo de execução | Gerenciamento de estado, logging |
| Scraping Agent | Coleta dados do site do CNPq automaticamente | requests, BeautifulSoup4, pandas |
| Enrichment Agent | Busca dados complementares no Currículo Lattes | Selenium, ChromeDriver |
| Data Agent | Processa, limpa e organiza os dados coletados | pandas, gender-guesser, regex |
| Data Loader Agent | Carrega dados com fallback e detecta mudanças | requests, pandas, BeautifulSoup4 |
| Dashboard Agent | Exibe visualizações e permite exportação | Streamlit, Plotly, FPDF2 |
| Query Agent | Responde perguntas em linguagem natural via execução de código | LangChain, GPT-4o, pandas |
| Logger Agent | Registra todas as operações do sistema | logging, arquivo .log |
| Validation Agent | Valida integridade do dataset automaticamente | pandas, assertions |

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
Data Loader Agent verifica CNPq
       ↓
Detecta novos/removidos → atualiza campo ativo
       ↓
Validation Agent valida integridade
       ↓
Dashboard Agent exibe apenas pesquisadores com ativo=S
       ↓
Usuário faz pergunta → Query Agent acionado
       ↓
LangChain cria agente pandas com GPT-4o
       ↓
GPT-4o gera código pandas para responder
       ↓
Código executado nos dados reais → resposta precisa
       ↓
Logger Agent registra todas as operações
```

### 3.4 Query Agent — Arquitetura LangChain Pandas

O Query Agent utiliza o padrão **Text-to-Pandas** via LangChain:

```
Usuário pergunta em português
       ↓
GPT-4o gera código pandas para responder
       ↓
LangChain executa o código no DataFrame real
       ↓
Resultado calculado nos dados reais
       ↓
GPT-4o formata a resposta em português
```

Isso garante que **qualquer pergunta** sobre os dados seja respondida corretamente, incluindo cruzamentos de múltiplos campos.

### 3.5 Handoffs

| De | Para | Condição |
|---|---|---|
| Orchestrator | Data Loader Agent | Ao iniciar o dashboard |
| Data Loader Agent | Validation Agent | Após carregar os dados |
| Data Loader Agent | Dashboard Agent | Após validar os dados |
| Dashboard Agent | Logger Agent | A cada ação do usuário |
| Dashboard Agent | Query Agent | Quando usuário digita uma pergunta |
| Query Agent | LangChain | Para gerar código pandas |
| LangChain | GPT-4o | Para raciocinar sobre a pergunta |
| GPT-4o | LangChain | Código pandas gerado |
| LangChain | Dashboard Agent | Resultado calculado |

### 3.6 Guardrails

- **Validação de linhas:** apenas linhas com 6 ou mais colunas são processadas
- **Filtro de cabeçalhos:** linhas com texto NOME são ignoradas
- **Deduplicação:** pesquisadores duplicados são removidos pelo nome
- **Timeout:** requisições ao CNPq têm limite de 15 segundos
- **Cache:** dados armazenados por 1 hora para evitar sobrecarga
- **Reinício automático:** driver Selenium reinicia em caso de sessão perdida
- **Campo ativo:** pesquisadores removidos marcados como ativo=N, nunca excluídos
- **Fallback triplo:** CNPq → GitHub → arquivo local
- **Colunas reduzidas:** Query Agent recebe apenas colunas essenciais para evitar erro 413
- **handle_parsing_errors:** LangChain trata erros de parsing automaticamente
- **max_iterations:** limite de 5 iterações por consulta para evitar loops infinitos

---

## 4. Implementação

### 4.1 Estrutura de Arquivos

```
projeto-cnpq/
├── agents/
│   └── logger_agent.py              # Logger Agent
├── tools/
│   ├── cnpq_scraper.py              # Scraping Agent
│   ├── lattes_scraper.py            # Enrichment Agent
│   ├── data_loader.py               # Data Loader Agent
│   ├── extrair_ano.py               # Data Agent
│   ├── corrigir_area.py             # Data Agent
│   ├── corrigir_area2.py            # Data Agent
│   └── corrigir_sexo.py             # Data Agent
├── data/
│   └── dataset.csv                  # Dataset final com 480 pesquisadores
├── dashboard/
│   └── app.py                       # Dashboard + Query + Logger + Validation
├── logs/
│   └── operacoes.log                # Log de todas as operações
├── docs/
│   ├── documentacao_projeto_cnpq.md
│   └── documentacao_projeto_cnpq_v4.docx
├── .env                             # Variáveis de ambiente (não versionado)
├── .gitignore
└── requirements.txt
```

### 4.2 Dataset Final (480 pesquisadores, 16 colunas)

| Campo | Descrição | Fonte |
|---|---|---|
| nome | Nome completo do pesquisador | CNPq |
| sexo | Masculino/Feminino | gender-guesser + dicionário manual |
| instituicao | Instituição de vínculo | CNPq |
| uf | Estado (UF) | Mapeamento por sigla da instituição |
| nivel_bolsa | Nível da bolsa CNPq (PQ-1A, PQ-1B, etc.) | CNPq |
| area_atuacao | Área de atuação detalhada | Lattes |
| ano_conclusao_doutorado | Ano de conclusão do doutorado | Extraído via regex |
| url_lattes | Link do Currículo Lattes | Lattes |
| google_scholar | Link do Google Scholar | N/A |
| vigencia_inicio | Início da vigência da bolsa | CNPq |
| vigencia_termino | Término da vigência da bolsa | CNPq |
| situacao | Situação atual da bolsa | CNPq |
| formacao_academica | Formação acadêmica completa | Lattes |
| pos_doutorado | Pós-doutorado(s) realizados | Lattes |
| url | Link de busca no CNPq | Gerado automaticamente |
| ativo | S=ativo no CNPq / N=removido | Gerenciado automaticamente |

### 4.3 Query Agent — LangChain Pandas Agent com GPT-4o

O Query Agent foi completamente reescrito para usar o padrão Text-to-Pandas:

```python
from langchain_openai import ChatOpenAI
from langchain_experimental.agents import create_pandas_dataframe_agent

llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Envia apenas colunas essenciais para reduzir tokens
df_query = df_filtrado[["nome", "sexo", "instituicao", "uf",
                          "nivel_bolsa", "situacao",
                          "ano_conclusao_doutorado"]].copy()

agent = create_pandas_dataframe_agent(
    llm, df_query,
    allow_dangerous_code=True,
    max_iterations=5,
    agent_executor_kwargs={"handle_parsing_errors": True}
)
```

**Por que apenas colunas essenciais?** O dataset completo com todas as colunas (especialmente formacao_academica com textos longos) ultrapassava o limite de tokens da API (44.585 tokens solicitados vs limite de 30.000).

### 4.4 Log de Operações

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

---

## 5. Architecture Decision Records (ADRs)

### ADR-001: Adoção de Arquitetura Multi-Agentes

| Campo | Descrição |
|---|---|
| **Contexto** | O sistema precisa realizar tarefas complexas: scraping, enriquecimento, visualização, linguagem natural, logging, validação e gerenciamento de ciclo de vida |
| **Decisão** | Adotar arquitetura multi-agentes com responsabilidades bem definidas |
| **Justificativa** | Permite separar responsabilidades, facilitar teste individual e substituição de partes sem afetar o todo |
| **Alternativas** | Sistema monolítico (difícil de manter), microserviços (desnecessário) |
| **Consequências** | Maior organização, facilidade de manutenção e extensibilidade |

### ADR-002: Escolha da Linguagem de Programação

| Campo | Descrição |
|---|---|
| **Contexto** | Necessidade de scraping, processamento, interface web e integração com APIs de IA |
| **Decisão** | Python 3.x |
| **Justificativa** | Ecossistema rico com bibliotecas maduras para todas as necessidades |
| **Alternativas** | Node.js (menor suporte a data science), Java (mais verboso) |
| **Consequências** | Desenvolvimento rápido e código legível |

### ADR-003: Ferramenta de Scraping do CNPq

| Campo | Descrição |
|---|---|
| **Contexto** | Necessidade de coletar dados da tabela do CNPq |
| **Decisão** | requests + BeautifulSoup4 |
| **Justificativa** | Site do CNPq retorna HTML estático, não requerendo JavaScript |
| **Alternativas** | Selenium (mais pesado), Scrapy (mais complexo) |
| **Consequências** | Scraping rápido e eficiente |

### ADR-004: Ferramenta de Scraping do Lattes

| Campo | Descrição |
|---|---|
| **Contexto** | O Lattes requer interação com formulários, cliques e CAPTCHA |
| **Decisão** | Selenium com ChromeDriver |
| **Tentativas anteriores** | requests direto (bloqueado pelo CAPTCHA), XML do Lattes (timeout) |
| **Mudança de abordagem** | Primeira versão identificou âncoras HTML incorretamente. DevTools corrigiu. |
| **Consequências** | Processo mais lento com CAPTCHA manual, mas funcional com reinício automático |

### ADR-005: Framework de Dashboard

| Campo | Descrição |
|---|---|
| **Contexto** | Necessidade de interface web interativa sem expertise em frontend |
| **Decisão** | Streamlit |
| **Justificativa** | Dashboards interativos apenas com Python. Deploy gratuito. |
| **Alternativas** | Dash (mais complexo), Flask (requer frontend) |
| **Consequências** | Desenvolvimento rápido com menos flexibilidade de customização |

### ADR-006: Estratégia de Hospedagem

| Campo | Descrição |
|---|---|
| **Contexto** | Necessidade de disponibilizar o dashboard online |
| **Decisão** | GitHub + Streamlit Community Cloud |
| **Primeira tentativa** | Execução local — bloqueada por firewall na porta 8501 |
| **Mudança de abordagem** | Deploy no Streamlit Community Cloud |
| **Consequências** | Sistema acessível de qualquer dispositivo |

### ADR-007: Fonte dos Dados no Dashboard

| Campo | Descrição |
|---|---|
| **Contexto** | Streamlit Cloud não acessa o CNPq diretamente (timeout) |
| **Decisão** | Fallback triplo: CNPq → GitHub → arquivo local |
| **Primeira tentativa** | Scraping em tempo real — bloqueado por timeout |
| **Mudança de abordagem** | Dataset no GitHub com verificação do CNPq para detectar mudanças |
| **Consequências** | Sistema resiliente com dados sempre disponíveis |

### ADR-008: Estratégia de Inferência de Sexo

| Campo | Descrição |
|---|---|
| **Contexto** | Dataset não contém o campo sexo |
| **Decisão** | gender-guesser + dicionário manual de nomes brasileiros |
| **Primeira tentativa** | Apenas gender-guesser — 96 indefinidos |
| **Mudança de abordagem** | Dicionário manual corrigiu 95. Erickson corrigido manualmente. |
| **Consequências** | 100% dos pesquisadores com sexo definido |

### ADR-009: Gerenciamento do Ciclo de Vida dos Pesquisadores

| Campo | Descrição |
|---|---|
| **Contexto** | Pesquisadores podem ser adicionados ou removidos do CNPq ao longo do tempo |
| **Decisão** | Campo ativo (S/N) — pesquisadores removidos nunca são excluídos |
| **Justificativa** | Preserva histórico. Pesquisador removido pode retornar. Dashboard exibe apenas ativo=S. |
| **Alternativas** | Exclusão física (perde histórico), tabela separada (desnecessário) |
| **Consequências** | Dados históricos preservados, dashboard sempre atualizado |

### ADR-010: Separação do Data Loader em Módulo Independente

| Campo | Descrição |
|---|---|
| **Contexto** | Função carregar_dados() dentro do app.py misturava responsabilidades |
| **Decisão** | Criar tools/data_loader.py com a lógica isolada |
| **Justificativa** | Princípio de Single Responsibility. Código mais limpo e testável. |
| **Implementação** | Cache do Streamlit mantido no app.py via wrapper |
| **Consequências** | Código organizado e fácil de manter |

### ADR-011: Evolução da Estratégia do Query Agent

| Campo | Descrição |
|---|---|
| **Contexto** | Necessidade de interface de linguagem natural precisa para qualquer pergunta sobre os dados |
| **Decisão Final** | LangChain Pandas Agent com GPT-4o (Text-to-Pandas) |
| **Tentativa 1** | Groq + Llama 3.1 com prompt simples — modelo se perdia em cálculos e inventava dados |
| **Tentativa 2** | Dados pré-calculados no Python — funcionou para perguntas simples mas falhou em cruzamentos de 3+ campos |
| **Tentativa 3** | Groq + Llama 3.1 com LangChain Pandas Agent — erro 413 (limite de 6.000 tokens ultrapassado) |
| **Tentativa 4** | OpenAI GPT-4o com LangChain Pandas Agent — erro 429 (44.585 tokens solicitados, limite 30.000) |
| **Solução Final** | GPT-4o com apenas colunas essenciais do DataFrame (reduz tokens para menos de 30.000) |
| **Justificativa** | Text-to-Pandas garante precisão total — o modelo gera código pandas que é executado nos dados reais, eliminando alucinações |
| **Consequências** | Qualquer pergunta respondida com precisão total, incluindo cruzamentos de múltiplos campos |

---

## 6. Testes e Inconsistências

### 6.1 Testes Realizados

| Teste | Resultado Esperado | Resultado Obtido |
|---|---|---|
| Scraping do CNPq | 480 pesquisadores | 480 coletados |
| Geração do CSV | 16 colunas | CSV gerado corretamente |
| Inferência de sexo | 100% classificados | 100% após correção manual |
| Mapeamento de UF | Sem NaN | 480 com UF |
| Scraping do Lattes | Dados de formação e área | 480 enriquecidos |
| Campo ativo | S para todos | 480 com ativo=S |
| Fallback CNPq indisponível | Usa GitHub com aviso | Funcionando |
| Detecção de novos/removidos | Atualiza campo ativo | Funcionando |
| Filtros do dashboard | 5 critérios | Funcionando |
| Exportação CSV e PDF | Download | Funcionando |
| LN - pergunta simples | Resposta precisa | Funcionando |
| LN - cruzamento 2 campos | Sexo por UF | Funcionando |
| LN - cruzamento 3 campos | Sexo + UF + nível | Funcionando com GPT-4o |
| LN - fora do escopo | Recusar resposta | Funcionando |
| LN - nível com prefixo PQ | Interpretar PQ-1A | Funcionando |
| Log de operações | Registrar ações | Funcionando |
| Validações de integridade | Alertar problemas | Funcionando |
| Deploy Streamlit Cloud | Dashboard online | Funcionando |

### 6.2 Inconsistências Identificadas e Corrigidas

| Inconsistência | Quantidade | Solução |
|---|---|---|
| Pesquisadores com sexo Indefinido | 96 | Dicionário manual de nomes brasileiros |
| Sexo indefinido restante (Erickson) | 1 | Correção manual |
| Área de atuação incorreta | 10 | Reprocessamento com Selenium |
| Áreas ainda incorretas | 10 | Definidas como Ciência da Computação |
| Pesquisador com URL inválida (Lucchesi) | 1 | Correção manual |
| Instituições sem mapeamento de UF | 13 | Adicionadas ao dicionário |
| Modelo errando cálculos numéricos | Vários | Migração para Text-to-Pandas |
| Erro 413 Groq (6.000 tokens) | 1 | Migração para GPT-4o |
| Erro 429 GPT-4o (44.585 tokens) | 1 | Redução para colunas essenciais |
| AgentType não encontrado no LangChain | 1 | Removido import desnecessário |
| gender-guesser ausente do requirements | 1 | Adicionado ao requirements.txt |
| Import data_loader com NameError | 1 | Corrigido com sys.path.insert e alias |

### 6.3 Evolução do Query Agent — Erros e Soluções

| Versão | Abordagem | Problema | Solução |
|---|---|---|---|
| v1 | Groq + prompt simples | Alucinações, erros de cálculo | Dados pré-calculados |
| v2 | Groq + dados pré-calculados | Falha em cruzamentos de 3+ campos | LangChain Pandas Agent |
| v3 | Groq + LangChain | Erro 413 (6.000 tokens) | Migração para GPT-4o |
| v4 | GPT-4o + LangChain completo | Erro 429 (44.585 tokens) | Redução de colunas |
| v5 (final) | GPT-4o + colunas essenciais | Nenhum | Funcionando perfeitamente |

---

## 7. Implantação

### 7.1 Processo de Deploy

1. Desenvolvimento e testes locais com Python
2. Versionamento no GitHub (repositório: elengreice/projeto-cnpq)
3. Configuração das variáveis de ambiente no Streamlit Cloud (GROQ_API_KEY, OPENAI_API_KEY)
4. Deploy automático via Streamlit Community Cloud
5. Validação do sistema em produção

### 7.2 Variáveis de Ambiente

| Variável | Uso |
|---|---|
| GROQ_API_KEY | API Groq (usada anteriormente, mantida como backup) |
| OPENAI_API_KEY | API OpenAI GPT-4o para o Query Agent |

### 7.3 Atualização dos Dados

1. Executar: `python tools/cnpq_scraper.py`
2. Executar: `python tools/lattes_scraper.py`
3. Executar: `python tools/extrair_ano.py`
4. Commit e push: `git add . && git commit -m "atualiza dados" && git push`
5. Dashboard carrega automaticamente os dados atualizados

---

## 8. Model Context Protocol (MCP)

O MCP define como o modelo de linguagem interage com o contexto dos dados.

### 8.1 Arquitetura Text-to-Pandas

O Query Agent usa o padrão Text-to-Pandas via LangChain:

1. **Usuário** faz uma pergunta em linguagem natural
2. **LangChain** envia o schema do DataFrame + a pergunta para o GPT-4o
3. **GPT-4o** raciocina e gera código pandas para responder
4. **LangChain** executa o código no DataFrame real
5. **GPT-4o** formata o resultado em português
6. **Dashboard** exibe a resposta ao usuário

### 8.2 Contexto Fornecido ao Modelo

- Schema do DataFrame (colunas e tipos)
- Amostra dos dados para referência
- 10 regras obrigatórias de comportamento
- Instruções sobre prefixo PQ- nos níveis de bolsa
- Restrição ao escopo dos dados do CNPq

### 8.3 Vantagem sobre Abordagem Anterior

| Abordagem anterior | Abordagem atual |
|---|---|
| Dados pré-calculados enviados ao modelo | Código pandas gerado e executado |
| Limitado a cruzamentos previstos | Qualquer cruzamento possível |
| Risco de alucinação | Resultado calculado nos dados reais |
| Falha em perguntas complexas | Funciona para qualquer pergunta |

---

## 9. Qualidade e Resiliência

### 9.1 Resiliência do Sistema

| Componente | Mecanismo de Resiliência |
|---|---|
| Carregamento de dados | Fallback triplo: CNPq → GitHub → local |
| Enrichment Agent | Reinício automático, 3 tentativas por pesquisador |
| Dataset | Campo ativo preserva histórico de removidos |
| Query Agent | Text-to-Pandas elimina alucinações |
| Dashboard | Validações automáticas alertam sobre problemas |
| LangChain | handle_parsing_errors trata erros de parsing |

### 9.2 Exemplo Real do Log

```
2026-05-30 19:06:47 | INFO | DASHBOARD INICIADO | CNPq disponivel. Total: 480
2026-05-30 19:06:47 | INFO | VALIDACAO DO DATASET | Dataset valido com 480 pesquisadores
2026-05-30 19:06:55 | INFO | FILTRO APLICADO | UF: ['BA']
2026-05-30 19:07:10 | INFO | CONSULTA LINGUAGEM NATURAL | Pergunta: Quantos pesquisadores do sexo feminino tem na Bahia com nivel PQ-2?
2026-05-30 19:07:12 | INFO | RESPOSTA GERADA | Pergunta respondida com sucesso
```

---

## 10. Conclusão

O sistema multi-agentes desenvolvido atende a todos os requisitos propostos. A evolução mais significativa foi o Query Agent, que passou por 5 versões até chegar à solução final com LangChain Pandas Agent + GPT-4o, capaz de responder qualquer pergunta sobre os dados com precisão total.

### 10.1 Principais Desafios e Soluções

| Desafio | Solução Adotada |
|---|---|
| Firewall bloqueando Streamlit local | Deploy no Streamlit Community Cloud |
| CNPq bloqueando acesso do Streamlit Cloud | Fallback triplo com dataset no GitHub |
| CAPTCHA no Currículo Lattes | Selenium com resolução manual |
| Sessão do Selenium sendo perdida | Reinício automático com retomada de progresso |
| Cartão brasileiro rejeitado na OpenAI | Uso temporário da chave de colega |
| Modelo Groq descontinuado | Atualização para llama-3.1-8b-instant |
| 96 pesquisadores com sexo indefinido | Dicionário manual de nomes brasileiros |
| Área de atuação incorreta | Correção de 10 registros |
| Alucinações no Query Agent | Migração para Text-to-Pandas |
| Erro 413 Groq (limite de tokens) | Migração para GPT-4o |
| Erro 429 GPT-4o (muitos tokens) | Redução para colunas essenciais |
| Pesquisadores novos/removidos no CNPq | Campo ativo com detecção automática |
| Código misturando responsabilidades | Refatoração com data_loader.py separado |
| Google Scholar não disponível | Campo N/A com justificativa documentada |

### 10.2 Limitações Conhecidas

- **Google Scholar:** não obtido automaticamente sem risco de dados incorretos
- **Enrichment de novos:** novos pesquisadores entram sem dados do Lattes
- **Atualização de dados:** requer execução manual dos scrapers localmente
- **Selenium:** não pode rodar no Streamlit Cloud

### 10.3 Possíveis Melhorias Futuras

- Automação completa da atualização de dados via agendamento
- Integração com a API oficial do Lattes quando disponível
- Busca automatizada do Google Scholar via ScraperAPI
- Script automatizado para enriquecer novos pesquisadores com dados do Lattes
- Notificações automáticas quando o dataset ficar desatualizado
