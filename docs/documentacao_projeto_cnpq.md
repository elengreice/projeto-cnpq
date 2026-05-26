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
| RF11 | Registrar Log | O sistema deve registrar todas as ações realizadas com data e hora |
| RF12 | Validar Integridade | O sistema deve validar automaticamente a integridade do dataset |
| RF13 | Detectar Mudanças | O sistema deve detectar novos e removidos pesquisadores no CNPq |
| RF14 | Gerenciar Ativos | O sistema deve marcar pesquisadores removidos como inativos sem excluí-los |

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
| RNF09 | Disponibilidade | Fallback automático CNPq → GitHub → arquivo local |
| RNF10 | Rastreabilidade | Pesquisadores removidos mantidos no dataset com campo ativo=N |

---

## 3. Design do Sistema

### 3.1 Por que Arquitetura Multi-Agentes?

A escolha pela arquitetura multi-agentes se justifica pela necessidade de separar responsabilidades complexas e distintas: coleta de dados de dois sites diferentes, enriquecimento de dados, visualização, consulta em linguagem natural, logging, validação e gerenciamento de ciclo de vida dos pesquisadores. Cada responsabilidade opera de forma relativamente independente, mas precisa de coordenação. Um sistema monolítico dificultaria a manutenção, o teste individual de cada componente e a substituição de partes sem afetar o todo.

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
| Validation Agent | Valida integridade do dataset automaticamente | pandas, assertions |
| Data Loader Agent | Carrega dados com fallback e detecta mudanças | requests, pandas, BeautifulSoup4 |

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
Se CNPq disponível: compara com dataset, detecta novos/removidos
       ↓
Novos → adiciona com ativo=S e campos básicos
Removidos → marca ativo=N (mantém dados)
Voltaram → reativa com ativo=S
       ↓
Se CNPq indisponível → carrega do GitHub
Se GitHub indisponível → carrega do arquivo local
       ↓
Validation Agent valida integridade
       ↓
Dashboard Agent exibe apenas pesquisadores com ativo=S
       ↓
Logger Agent registra todas as operações
```

### 3.4 Comunicação entre Agentes (Orchestration)

O modelo de orquestração adotado é o **Centralized Orchestration**. A escolha se justifica pela natureza sequencial do pipeline de dados e pela facilidade de rastreamento e logging das operações.

### 3.5 Handoffs

| De | Para | Condição |
|---|---|---|
| Orchestrator | Data Loader Agent | Ao iniciar o dashboard |
| Data Loader Agent | Scraping Agent | Para verificar CNPq |
| Data Loader Agent | Validation Agent | Após carregar os dados |
| Data Loader Agent | Dashboard Agent | Após validar os dados |
| Scraping Agent | Data Agent | Novos pesquisadores detectados |
| Dashboard Agent | Logger Agent | A cada ação do usuário |
| Dashboard Agent | Query Agent | Quando usuário digita uma pergunta |
| Query Agent | Dashboard Agent | Após receber resposta da API Groq |

### 3.6 Guardrails

- **Validação de linhas:** apenas linhas com 6 ou mais colunas são processadas
- **Filtro de cabeçalhos:** linhas com texto "NOME" são ignoradas
- **Deduplicação:** pesquisadores duplicados são removidos pelo nome
- **Timeout:** requisições ao CNPq têm limite de 15 segundos
- **Cache:** dados armazenados por 1 hora para evitar sobrecarga no servidor
- **Reinício automático:** driver Selenium reinicia em caso de sessão perdida
- **Retomada de progresso:** Enrichment Agent retoma do ponto onde parou
- **Segurança:** chave de API em variável de ambiente, nunca no código
- **Validações automáticas:** dataset validado a cada carregamento
- **Campo ativo:** pesquisadores removidos marcados como ativo=N, nunca excluídos
- **Fallback triplo:** CNPq → GitHub → arquivo local
- **14 regras do Query Agent:** respostas precisas e confiáveis
- **Dados pré-calculados:** estatísticas calculadas no Python antes de enviar ao modelo

### 3.7 Reasoning e Planning

- **Scraping Agent:** decide quais linhas são dados válidos com base em regras de validação
- **Data Agent:** planeja limpeza dos dados, identificando duplicatas e inferindo campos ausentes
- **Enrichment Agent:** identifica as âncoras HTML corretas para cada seção do Lattes
- **Data Loader Agent:** decide qual fonte usar (CNPq, GitHub ou local) e como tratar mudanças
- **Query Agent:** usa dados pré-calculados para formular respostas precisas em português
- **Validation Agent:** verifica proativamente a integridade antes de qualquer processamento

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
│   ├── data_loader.py               # Data Loader Agent (fallback + detecção de mudanças)
│   ├── extrair_ano.py               # Data Agent - extrai ano de conclusão
│   ├── corrigir_area.py             # Data Agent - corrige áreas de atuação
│   ├── corrigir_area2.py            # Data Agent - correção complementar
│   └── corrigir_sexo.py             # Data Agent - corrige sexo indefinido
├── data/
│   └── dataset.csv                  # Dataset final com 480 pesquisadores
├── dashboard/
│   └── app.py                       # Dashboard + Query + Logger + Validation
├── logs/
│   └── operacoes.log                # Log de todas as operações
├── docs/
│   ├── documentacao_projeto_cnpq.md
│   └── documentacao_projeto_cnpq_v3.docx
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
| nivel_bolsa | Nível da bolsa CNPq | CNPq |
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
| **ativo** | **S=ativo no CNPq / N=removido** | **Gerenciado automaticamente** |

### 4.3 Data Loader Agent (tools/data_loader.py)

O Data Loader Agent é responsável por carregar os dados com fallback triplo e detectar mudanças no CNPq. Foi criado como módulo separado seguindo o princípio de Single Responsibility — a lógica de carregamento fica isolada do dashboard.

**Fluxo de decisão:**

```
1. Tenta carregar dataset completo do GitHub (com todos os campos)
2. Se falhar → tenta arquivo local
3. Verifica CNPq com timeout de 15 segundos
4. Se CNPq disponível:
   - Compara nomes com dataset
   - Novos → adiciona com ativo=S e campos básicos (sexo e UF inferidos)
   - Removidos → marca ativo=N (dados preservados)
   - Voltaram → reativa com ativo=S
5. Se CNPq indisponível → usa dataset do GitHub com aviso
```

**No dashboard, apenas pesquisadores com ativo=S são exibidos:**
```python
df = df[df["ativo"] == "S"].copy()
```

### 4.4 Refatoração do Código

O código foi refatorado para separar responsabilidades:

| Antes | Depois |
|---|---|
| `carregar_dados()` dentro do `app.py` | `carregar_dados()` em `tools/data_loader.py` |
| `app.py` continha lógica de negócio | `app.py` apenas chama funções externas |
| Código mais difícil de manter | Código limpo e organizado |

O cache do Streamlit foi mantido no `app.py` usando um wrapper:
```python
from tools.data_loader import carregar_dados as carregar_dados_cnpq

@st.cache_data(ttl=3600)
def carregar_dados():
    return carregar_dados_cnpq()
```

### 4.5 Fallback Triplo de Dados

| Tentativa | Fonte | Condição |
|---|---|---|
| 1ª | Site do CNPq (tempo real) | CNPq disponível |
| 2ª | Dataset no GitHub | CNPq indisponível |
| 3ª | Arquivo local `data/dataset.csv` | GitHub indisponível |
| Erro | Exibe mensagem e para | Tudo indisponível |

### 4.6 Log de Operações

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

### 4.7 Validações Automáticas de Integridade

- Dataset não está vazio → alerta CRÍTICO
- Dataset tem mais de 100 registros → alerta de ATENÇÃO
- Colunas obrigatórias existem → alerta CRÍTICO se ausente
- Não há UFs nulas → alerta de ATENÇÃO
- Não há sexos indefinidos → alerta de ATENÇÃO

### 4.8 Query Agent — 14 Regras Obrigatórias

1. Responder APENAS com dados fornecidos
2. Se não puder responder: "Não tenho essa informação nos dados disponíveis"
3. Citar números EXATOS
4. Responder SEMPRE em português
5. Não responder perguntas fora do escopo
6. Explicar ambiguidades antes de responder
7. NUNCA fazer suposições
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
| **Contexto** | O sistema precisa realizar tarefas complexas e distintas: scraping de dois sites, processamento, visualização, linguagem natural, logging, validação e gerenciamento de ciclo de vida |
| **Decisão** | Adotar arquitetura multi-agentes com responsabilidades bem definidas |
| **Justificativa** | Permite separar responsabilidades, facilita teste individual e substituição de partes sem afetar o todo |
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

### ADR-006: Modelo de Linguagem

| Campo | Descrição |
|---|---|
| **Contexto** | Necessidade de linguagem natural em português |
| **Decisão** | Groq API com Llama 3.1 8B Instant |
| **Primeira tentativa** | OpenAI GPT-4o — cartões brasileiros rejeitados |
| **Mudança de abordagem** | Groq API. Modelo llama3-8b-8192 descontinuado → llama-3.1-8b-instant |
| **Consequências** | Sem custo operacional, qualidade adequada |

### ADR-007: Estratégia de Hospedagem

| Campo | Descrição |
|---|---|
| **Contexto** | Necessidade de disponibilizar o dashboard online |
| **Decisão** | GitHub + Streamlit Community Cloud |
| **Primeira tentativa** | Execução local — bloqueada por firewall na porta 8501 |
| **Mudança de abordagem** | Deploy no Streamlit Community Cloud |
| **Consequências** | Sistema acessível de qualquer dispositivo |

### ADR-008: Fonte dos Dados no Dashboard

| Campo | Descrição |
|---|---|
| **Contexto** | Streamlit Cloud não acessa o CNPq diretamente (timeout) |
| **Decisão** | Fallback triplo: CNPq → GitHub → arquivo local |
| **Primeira tentativa** | Scraping em tempo real — bloqueado por timeout |
| **Mudança de abordagem** | Dataset no GitHub com verificação do CNPq para detectar mudanças |
| **Consequências** | Sistema resiliente com dados sempre disponíveis |

### ADR-009: Estratégia de Inferência de Sexo

| Campo | Descrição |
|---|---|
| **Contexto** | Dataset não contém o campo sexo |
| **Decisão** | gender-guesser + dicionário manual de nomes brasileiros |
| **Primeira tentativa** | Apenas gender-guesser — 96 indefinidos |
| **Mudança de abordagem** | Dicionário manual corrigiu 95. Erickson corrigido manualmente. |
| **Consequências** | 100% dos pesquisadores com sexo definido |

### ADR-010: Estratégia de Respostas do Query Agent

| Campo | Descrição |
|---|---|
| **Contexto** | Modelo cometia erros ao interpretar dados brutos |
| **Decisão** | Pré-calcular estatísticas no Python e enviar resultados prontos |
| **Primeira tentativa** | Dados brutos — modelo errava cálculos (ex: somou feminino+masculino) |
| **Segundo problema** | Erro 413 (37.798 tokens, limite 6.000) — contexto reduzido |
| **Consequências** | Respostas precisas e confiáveis |

### ADR-011: Gerenciamento do Ciclo de Vida dos Pesquisadores

| Campo | Descrição |
|---|---|
| **Contexto** | Pesquisadores podem ser adicionados ou removidos do CNPq ao longo do tempo |
| **Decisão** | Campo `ativo` (S/N) no dataset — pesquisadores removidos nunca são excluídos |
| **Justificativa** | Preserva histórico de dados. Pesquisador removido pode retornar. Dashboard exibe apenas ativo=S. Novos entram automaticamente com campos básicos inferidos. |
| **Alternativas** | Exclusão física (perde histórico), tabela separada (complexidade desnecessária) |
| **Consequências** | Dados históricos preservados, dashboard sempre atualizado |

### ADR-012: Separação do Data Loader em Módulo Independente

| Campo | Descrição |
|---|---|
| **Contexto** | Função `carregar_dados()` dentro do `app.py` misturava responsabilidades |
| **Decisão** | Criar `tools/data_loader.py` com a lógica de carregamento isolada |
| **Justificativa** | Princípio de Single Responsibility. Código mais limpo, testável e reutilizável. |
| **Implementação** | Cache do Streamlit mantido no `app.py` via wrapper que chama o módulo externo |
| **Consequências** | Código organizado, fácil de manter e estender |

---

## 6. Testes e Inconsistências

### 6.1 Testes Realizados

| Teste | Resultado Esperado | Resultado Obtido |
|---|---|---|
| Scraping do CNPq | Coletar todos os pesquisadores | 480 pesquisadores coletados |
| Geração do CSV | Arquivo com 16 colunas | CSV gerado corretamente |
| Inferência de sexo | 100% classificados | 100% após correção manual |
| Mapeamento de UF | Sem NaN | 480 pesquisadores com UF |
| Scraping do Lattes | Dados de formação e área | 480 pesquisadores enriquecidos |
| Extração do ano de doutorado | Ano via regex | Funcionando para todos |
| Campo ativo | S para todos os 480 | Funcionando corretamente |
| Fallback CNPq indisponível | Usa GitHub com aviso | Funcionando |
| Fallback GitHub indisponível | Usa arquivo local | Funcionando |
| Detecção de novos pesquisadores | Adiciona com ativo=S | Funcionando |
| Detecção de removidos | Marca ativo=N | Funcionando |
| Reativação de pesquisadores | Marca ativo=S | Funcionando |
| Filtros do dashboard | Filtrar por 5 critérios | Funcionando |
| Exportação CSV e PDF | Download dos arquivos | Funcionando |
| Linguagem natural - simples | Resposta precisa | Funcionando |
| Linguagem natural - cruzamento | Sexo por UF correto | Funcionando após pré-cálculo |
| Linguagem natural - fora do escopo | Recusar resposta | Funcionando |
| Log de operações | Registrar todas as ações | Funcionando |
| Validações de integridade | Alertar sobre problemas | Funcionando |
| Refatoração data_loader | Módulo separado funcional | Funcionando |
| Deploy Streamlit Cloud | Dashboard online | Funcionando |

### 6.2 Inconsistências Identificadas e Corrigidas

| Inconsistência | Quantidade | Solução |
|---|---|---|
| Pesquisadores com sexo "Indefinido" | 96 | Dicionário manual de nomes brasileiros |
| Sexo indefinido restante (Erickson) | 1 | Correção manual |
| Área de atuação incorreta | 10 | Reprocessamento com Selenium |
| Áreas ainda incorretas | 10 | Definidas como "Ciência da Computação" |
| Pesquisador com URL inválida (Lucchesi) | 1 | Correção manual |
| Instituições sem mapeamento de UF | 13 | Adicionadas ao dicionário |
| Modelo errando cálculos numéricos | Vários | Pré-cálculo no Python |
| Erro 413 - contexto muito grande | 1 | Redução do contexto |
| gender-guesser não estava no requirements.txt | 1 | Adicionado ao requirements.txt |
| Import do data_loader com NameError | 1 | Corrigido com sys.path.insert |

### 6.3 Comportamento do Sistema em Mudanças no CNPq

| Mudança | Impacto | Comportamento do Sistema |
|---|---|---|
| Novos pesquisadores | Detectado automaticamente | Adicionados com ativo=S, sexo e UF inferidos |
| Pesquisadores removidos | Detectado automaticamente | Marcados ativo=N, dados preservados |
| Pesquisadores que voltaram | Detectado automaticamente | Reativados com ativo=S |
| Nova UF/instituição | UF fica N/A | Alerta no dashboard |
| Colunas renomeadas | Alerta crítico | Dashboard exibe erro em vermelho |
| CNPq indisponível | Aviso no dashboard | Usa dataset do GitHub automaticamente |
| GitHub indisponível | Aviso no dashboard | Usa arquivo local automaticamente |

---

## 7. Implantação

### 7.1 Processo de Deploy

1. Desenvolvimento e testes locais com Python
2. Versionamento no GitHub (`elengreice/projeto-cnpq`)
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
- Rankings pré-calculados de UFs
- Exemplos das primeiras 10 linhas do dataset
- 14 regras obrigatórias de comportamento

### 8.2 Protocolo de Comunicação

- **System message:** contexto pré-calculado + 14 regras
- **User message:** pergunta do usuário
- **Assistant message:** resposta em português

---

## 9. Qualidade e Resiliência

### 9.1 Resiliência do Sistema

| Componente | Mecanismo de Resiliência |
|---|---|
| Carregamento de dados | Fallback triplo: CNPq → GitHub → local |
| Enrichment Agent | Reinício automático do driver, 3 tentativas por pesquisador |
| Dataset | Campo ativo preserva histórico de pesquisadores removidos |
| Query Agent | Dados pré-calculados evitam erros de interpretação |
| Dashboard | Validações automáticas alertam sobre problemas |

### 9.2 Exemplo Real do Log de Operações

```
2026-05-26 22:38:48 | INFO | DASHBOARD INICIADO | CNPq disponivel. Dataset atualizado. Total: 480
2026-05-26 22:38:48 | INFO | VALIDACAO DO DATASET | Dataset valido com 480 pesquisadores
2026-05-26 22:39:02 | INFO | FILTRO APLICADO | UF: ['SP']
2026-05-26 22:39:22 | INFO | EXPORTACAO CSV | Total de registros exportados: 95
2026-05-26 22:39:28 | INFO | EXPORTACAO PDF | Total de registros exportados: 95
2026-05-26 22:40:15 | INFO | CONSULTA LINGUAGEM NATURAL | Pergunta: Em qual estado tem mais mulheres?
2026-05-26 22:40:16 | INFO | RESPOSTA GERADA | Pergunta respondida com sucesso
```

---

## 10. Conclusão

O sistema multi-agentes desenvolvido atende a todos os requisitos propostos. Foi construído com tecnologias modernas e gratuitas, com foco em funcionalidade, resiliência, precisão e boas práticas de engenharia de software.

### 10.1 Principais Desafios e Soluções

| Desafio | Solução Adotada |
|---|---|
| Firewall bloqueando Streamlit local | Deploy no Streamlit Community Cloud |
| CNPq bloqueando acesso do Streamlit Cloud | Fallback triplo com dataset no GitHub |
| CAPTCHA no Currículo Lattes | Selenium com resolução manual |
| Sessão do Selenium sendo perdida | Reinício automático com retomada de progresso |
| Cartão brasileiro rejeitado na OpenAI | Migração para Groq API gratuita |
| Modelo Groq descontinuado | Atualização para llama-3.1-8b-instant |
| 96 pesquisadores com sexo indefinido | Dicionário manual de nomes brasileiros |
| Área de atuação incorreta | Correção de 10 registros |
| Modelo errando cálculos numéricos | Pré-cálculo de estatísticas no Python |
| Erro 413 - contexto muito grande | Redução e otimização do contexto |
| Pesquisadores novos/removidos no CNPq | Campo ativo com detecção automática |
| Código misturando responsabilidades | Refatoração com data_loader.py separado |
| gender-guesser ausente do requirements | Adicionado ao requirements.txt |
| Google Scholar não disponível | Campo N/A com justificativa documentada |

### 10.2 Limitações Conhecidas

- **Google Scholar:** não obtido automaticamente sem risco de dados incorretos
- **Enrichment de novos:** novos pesquisadores entram sem dados do Lattes (requer execução manual do scraper)
- **Atualização de dados:** requer execução manual dos scrapers localmente
- **Selenium:** não pode rodar no Streamlit Cloud (requer ambiente local)

### 10.3 Possíveis Melhorias Futuras

- Automação completa da atualização de dados via agendamento
- Integração com a API oficial do Lattes quando disponível
- Busca automatizada do Google Scholar
- Script automatizado para enriquecer novos pesquisadores com dados do Lattes
- Notificações automáticas quando o dataset ficar desatualizado
