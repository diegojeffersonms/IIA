# Documentação Técnica - ChatBotService

## Índice
1. [Visão Geral](#visão-geral)
2. [Arquitetura](#arquitetura)
3. [Dependências](#dependências)
4. [Componentes Principais](#componentes-principais)
5. [Fluxo de Execução](#fluxo-de-execução)
6. [Descrição Detalhada dos Métodos](#descrição-detalhada-dos-métodos)
7. [Configuração](#configuração)
8. [Diagramas](#diagramas)

---

## Visão Geral

O módulo `chatbot.py` implementa um serviço de assistente virtual especializado em design de interiores, utilizando inteligência artificial através de modelos de linguagem (LLM). O serviço é capaz de processar consultas textuais e imagens, fornecendo aconselhamento profissional sobre design de interiores em Português de Portugal.

### Funcionalidades Principais
- Processamento de consultas textuais sobre design de interiores
- Análise de imagens de espaços interiores
- Geração de sugestões de melhoria personalizadas
- Priorização de alterações com alto impacto e custo razoável
- Respostas estruturadas em Português de Portugal

---

## Arquitetura

O serviço utiliza uma arquitetura baseada em grafos de estados (State Graph) implementada através da biblioteca LangGraph. Esta abordagem permite definir fluxos de trabalho complexos com múltiplos nós de processamento e roteamento condicional.

### Padrão Arquitetural
- **Padrão**: Grafo de Estados com Roteamento Condicional
- **Framework**: LangGraph
- **Modelos LLM**: ChatOllama (llama3 e llava)
- **Tipo**: Serviço Stateful

---

## Dependências

### Bibliotecas Externas

```python
langgraph.graph         # StateGraph, END - Framework para grafos de estados
langchain_core.messages # HumanMessage, SystemMessage - Tipos de mensagens
langchain_ollama        # ChatOllama - Interface para modelos Ollama
os                      # Gestão de variáveis de ambiente
base64                  # Codificação de imagens
```

### Requisitos de Sistema
- **Servidor Ollama**: Necessário para executar os modelos LLM
- **Modelos Ollama**:
  - `llama3`: Modelo de texto para processamento de linguagem natural
  - `llava`: Modelo de visão para análise de imagens
- **URL Base**: Configurável via variável de ambiente `OLLAMA_BASE_URL` (padrão: `http://localhost:11434`)

---

## Componentes Principais

### 1. GraphState

```python
class GraphState(dict):
    pass
```

**Propósito**: Classe de estado do grafo que herda de `dict`.

**Estrutura de Dados**:
- `messages`: Lista de mensagens trocadas na conversação
- `image_bytes`: Bytes da imagem (opcional)
- `image_description`: Descrição gerada da imagem (opcional)

**Tipo**: Contentor de estado imutável entre nós do grafo

---

### 2. ChatBotService

Classe principal que encapsula toda a lógica do serviço de chatbot.

#### 2.1. Atributos

| Atributo | Tipo | Descrição |
|----------|------|-----------|
| `model_texto` | ChatOllama | Instância do modelo llama3 para processamento textual |
| `model_vision` | ChatOllama | Instância do modelo llava para análise de imagens |
| `graph_app` | CompiledGraph | Grafo de estados compilado (criado após `build_graph()`) |

#### 2.2. Configuração de Modelos

Ambos os modelos são configurados com:
- **streaming**: `True` - Permite respostas em tempo real
- **base_url**: URL do servidor Ollama (configurável)

---

## Fluxo de Execução

### Diagrama de Fluxo

```
┌─────────────┐
│   ENTRADA   │
│  (Estado)   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│     ROUTER      │◄─── Verifica se existe 'image_bytes'
│  (Condicional)  │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────┐ ┌──────────┐
│ VISION  │ │   TEXT   │
│  NODE   │ │   NODE   │
└────┬────┘ └─────┬────┘
     │            │
     │            ▼
     │        ┌──────┐
     │        │ END  │
     │        └──────┘
     ▼
┌──────────────────┐
│ IMPROVE_SPACE    │
│      NODE        │
└────────┬─────────┘
         │
         ▼
      ┌──────┐
      │ END  │
      └──────┘
```

### Descrição do Fluxo

1. **Entrada**: O estado contém mensagens e opcionalmente bytes de imagem
2. **Router**: Decide o caminho com base na presença de imagem
   - **Com imagem** → `vision_llm` → `improve_space_node` → FIM
   - **Sem imagem** → `text_llm` → FIM

---

## Descrição Detalhada dos Métodos

### `__init__(self)`

**Propósito**: Inicializa o serviço com os modelos necessários.

**Ações**:
1. Cria instância do modelo de texto (llama3)
2. Cria instância do modelo de visão (llava)
3. Configura ambos com streaming ativo

**Parâmetros**: Nenhum

**Retorno**: Nenhum

---

### `vision_node(self, state: GraphState) -> dict`

**Propósito**: Processa imagens e gera descrições detalhadas do espaço interior.

**Fluxo de Processamento**:
1. Extrai a última mensagem do utilizador e os bytes da imagem do estado
2. Codifica a imagem em base64
3. Cria uma mensagem multimodal (texto + imagem)
4. Invoca o modelo de visão com prompt do sistema
5. Retorna o estado atualizado com a descrição da imagem

**Parâmetros**:
- `state` (GraphState): Estado atual contendo:
  - `messages`: Lista de mensagens
  - `image_bytes`: Bytes da imagem a processar

**Retorno**: Dicionário com:
- `messages`: Mensagens originais (inalteradas)
- `image_description`: Lista contendo a resposta do modelo de visão

**Prompt do Sistema**:
```
You are an Interior Design Assistant. 
Your job is to describe everything that you can see at the image, 
your output will be used to provide targeted interior design suggestions.
```

**Nota Técnica**: A imagem é codificada como URL de dados (data URL) no formato `data:image/png;base64,{base64_string}`.

---

### `text_node(self, state: GraphState) -> dict`

**Propósito**: Processa consultas puramente textuais sem contexto de imagem.

**Fluxo de Processamento**:
1. Extrai as mensagens do estado
2. Invoca o modelo de texto com prompt especializado
3. Retorna resposta em Português de Portugal

**Parâmetros**:
- `state` (GraphState): Estado atual contendo:
  - `messages`: Lista de mensagens da conversação

**Retorno**: Dicionário com:
- `messages`: Lista contendo apenas a resposta do modelo

**Prompt do Sistema**:
```
You are an Interior Design Assistant. 
Your job is to give clear, practical and professional interior design advice. 
When possible, structure the answer with bullet points or numbered steps. 
If the user goal is to increase sale value, prioritize changes with 
high impact and reasonable cost.
You must translate all answers to Portugal Portuguese.
```

**Características do Prompt**:
- Enfatiza clareza e profissionalismo
- Solicita estruturação com pontos ou passos numerados
- Prioriza retorno sobre investimento
- Garante tradução para PT-PT

---

### `improve_space_node(self, state: GraphState) -> dict`

**Propósito**: Processa consultas com contexto de imagem, combinando a descrição visual com a consulta textual.

**Fluxo de Processamento**:
1. Extrai mensagens e descrição da imagem do estado
2. Constrói prompt enriquecido com contexto visual
3. Invoca o modelo de texto
4. Retorna sugestões específicas baseadas na imagem

**Parâmetros**:
- `state` (GraphState): Estado atual contendo:
  - `messages`: Lista de mensagens da conversação
  - `image_description`: Descrição gerada pelo nó de visão

**Retorno**: Dicionário com:
- `messages`: Lista contendo a resposta do modelo

**Prompt do Sistema**:
```
You are an Interior Design Assistant.
Your job is to improve the clarity and professionalism of interior design advice. 
When possible, structure the answer with bullet points or numbered steps. 
If the user goal is to increase sale value, prioritize changes with 
high impact and reasonable cost.
You must translate all assistant answers to Portugal Portuguese.
```

**Mensagem Adicional**: 
- Adiciona contexto: `"The image description is: {image_description}."`

**Diferença em relação ao text_node**:
- Recebe contexto visual adicional
- Foca em "melhorar" a clareza (refinamento)
- Trabalha com duas fontes de informação

---

### `router(self, state: GraphState) -> str`

**Propósito**: Determina o caminho de execução no grafo baseado no conteúdo do estado.

**Lógica de Decisão**:
```python
if state.get('image_bytes'):
    return "vision"
return "text"
```

**Parâmetros**:
- `state` (GraphState): Estado atual

**Retorno**: 
- `"vision"`: Se existir `image_bytes` no estado
- `"text"`: Caso contrário

**Tipo**: Função de roteamento condicional

---

### `build_graph(self) -> None`

**Propósito**: Constrói e compila o grafo de estados que define o fluxo de trabalho do chatbot.

**Estrutura do Grafo**:

```python
workflow = StateGraph(dict)

# Nós
workflow.add_node("vision_llm", self.vision_node)
workflow.add_node("text_llm", self.text_node)
workflow.add_node("improve_space_node", self.improve_space_node)

# Ponto de entrada condicional
workflow.set_conditional_entry_point(
    self.router, 
    {"vision": "vision_llm", "text": "text_llm"}
)

# Arestas (transições)
workflow.add_edge("vision_llm", "improve_space_node")
workflow.add_edge("text_llm", END)
workflow.add_edge("improve_space_node", END)

# Compilação
self.graph_app = workflow.compile()
```

**Componentes**:

1. **Nós do Grafo**:
   - `vision_llm`: Processa imagens
   - `text_llm`: Processa texto simples
   - `improve_space_node`: Combina visão com texto

2. **Ponto de Entrada Condicional**:
   - Usa o método `router` para decidir o caminho inicial
   - Mapeamento: `{"vision": "vision_llm", "text": "text_llm"}`

3. **Arestas (Transições)**:
   - `vision_llm` → `improve_space_node`: Após análise de imagem, melhora sugestões
   - `text_llm` → `END`: Consultas textuais terminam diretamente
   - `improve_space_node` → `END`: Término após melhoramento

**Parâmetros**: Nenhum

**Retorno**: Nenhum (define atributo `self.graph_app`)

**Efeito Colateral**: Cria e armazena o grafo compilado em `self.graph_app`

---

## Configuração

### Variáveis de Ambiente

| Variável | Descrição | Valor Padrão | Obrigatório |
|----------|-----------|--------------|-------------|
| `OLLAMA_BASE_URL` | URL do servidor Ollama | `http://localhost:11434` | Não |

### Exemplo de Configuração

```bash
# Linux/macOS
export OLLAMA_BASE_URL="http://192.168.1.100:11434"

# Windows (PowerShell)
$env:OLLAMA_BASE_URL="http://192.168.1.100:11434"

# Windows (CMD)
set OLLAMA_BASE_URL=http://192.168.1.100:11434
```

### Requisitos de Modelos

Antes de utilizar o serviço, certifique-se de que os modelos estão instalados no Ollama:

```bash
ollama pull llama3
ollama pull llava
```

---

## Diagramas

### Diagrama de Classes

```
┌─────────────────────────────────────────┐
│          ChatBotService                 │
├─────────────────────────────────────────┤
│ - model_texto: ChatOllama              │
│ - model_vision: ChatOllama             │
│ - graph_app: CompiledGraph             │
├─────────────────────────────────────────┤
│ + __init__()                           │
│ + vision_node(state): dict             │
│ + text_node(state): dict               │
│ + improve_space_node(state): dict      │
│ + router(state): str                   │
│ + build_graph(): None                  │
└─────────────────────────────────────────┘
         │
         │ usa
         ▼
┌─────────────────────┐
│    GraphState       │
├─────────────────────┤
│ (herda de dict)     │
└─────────────────────┘
```

### Diagrama de Sequência - Consulta com Imagem

```
Utilizador   Router   VisionNode   ImproveNode   Resultado
    │           │          │            │             │
    │──Estado──▶│          │            │             │
    │           │          │            │             │
    │           │──visão──▶│            │             │
    │           │          │            │             │
    │           │          │──análise──▶│             │
    │           │          │            │             │
    │           │          │  (descrição imagem)      │
    │           │          │            │             │
    │           │          │◀───────────│             │
    │           │          │            │             │
    │           │          │            │──melhorar──▶│
    │           │          │            │             │
    │           │          │            │ (sugestões) │
    │           │          │            │             │
    │◀──────────────────────────────────────resposta──│
```

### Diagrama de Sequência - Consulta Textual

```
Utilizador   Router   TextNode   Resultado
    │           │         │          │
    │──Estado──▶│         │          │
    │           │         │          │
    │           │──texto─▶│          │
    │           │         │          │
    │           │         │──proc.──▶│
    │           │         │          │
    │           │         │(resposta)│
    │           │         │          │
    │◀───────────────────────────────│
```

---

## Casos de Uso

### Caso de Uso 1: Consulta Textual Simples

**Entrada**:
```python
state = {
    "messages": [
        HumanMessage(content="Como posso melhorar a sala de estar?")
    ]
}
```

**Processamento**:
- Router → text_llm → END

**Saída Esperada**:
- Sugestões gerais de design de interiores
- Resposta em Português de Portugal
- Estruturada em pontos ou passos

---

### Caso de Uso 2: Análise de Imagem

**Entrada**:
```python
state = {
    "messages": [
        HumanMessage(content="Como melhorar este espaço para aumentar o valor de venda?")
    ],
    "image_bytes": b'...'  # bytes da imagem
}
```

**Processamento**:
- Router → vision_llm → improve_space_node → END

**Saída Esperada**:
- Descrição detalhada do espaço
- Sugestões específicas baseadas na imagem
- Priorização de alterações com alto ROI
- Resposta em Português de Portugal

---

## Considerações Técnicas

### Performance
- **Streaming**: Ativado em ambos os modelos para respostas progressivas
- **Processamento**: Sequencial através do grafo
- **Latência**: Depende do servidor Ollama e hardware disponível

### Escalabilidade
- **Stateless por Execução**: Cada invocação é independente
- **Servidor Ollama**: Ponto único de falha - considerar alta disponibilidade
- **Memória**: Dependente do tamanho das imagens processadas

### Segurança
- **Validação de Entrada**: Não implementada - considerar adicionar
- **Sanitização de Imagens**: Não implementada
- **Rate Limiting**: Não implementado
- **Autenticação**: Não implementada

### Limitações
1. **Idioma de Entrada dos Modelos**: Os prompts do sistema estão em inglês
2. **Formato de Imagem**: Assume PNG na codificação (embora possa aceitar outros)
3. **Tamanho de Imagem**: Sem limite explícito - pode causar problemas de memória
4. **Histórico de Conversação**: Gerido externamente ao serviço
5. **Erros**: Sem tratamento explícito de exceções

---

## Melhorias Futuras Sugeridas

1. **Tratamento de Erros**:
   ```python
   try:
       resp = self.model_vision.invoke([...])
   except Exception as e:
       logger.error(f"Erro ao processar imagem: {e}")
       return {"error": "Falha no processamento"}
   ```

2. **Validação de Estado**:
   ```python
   def router(self, state):
       if not state.get('messages'):
           raise ValueError("Estado inválido: 'messages' obrigatório")
       # ...
   ```

3. **Logging**:
   ```python
   import logging
   logger = logging.getLogger(__name__)
   ```

4. **Configuração Externa**:
   ```python
   from pydantic import BaseSettings
   
   class Settings(BaseSettings):
       ollama_url: str = "http://localhost:11434"
       text_model: str = "llama3"
       vision_model: str = "llava"
   ```

5. **Testes Unitários**:
   - Testar cada nó individualmente
   - Mock dos modelos LLM
   - Validação de fluxos do grafo

---

## Glossário

- **LLM**: Large Language Model - Modelo de Linguagem Grande
- **LangGraph**: Framework para construção de aplicações com grafos de estados
- **Ollama**: Plataforma para executar modelos LLM localmente
- **llama3**: Modelo de linguagem de texto da Meta
- **llava**: Large Language and Vision Assistant - Modelo multimodal
- **StateGraph**: Grafo de estados para orquestração de fluxos
- **Streaming**: Transmissão progressiva de respostas
- **Base64**: Esquema de codificação binária para texto
- **Data URL**: URL que contém dados inline (ex: imagens)
- **ROI**: Return on Investment - Retorno sobre Investimento

---

## Referências

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Documentation](https://python.langchain.com/)
- [Ollama Documentation](https://ollama.ai/docs)
- [Llama 3 Model Card](https://ai.meta.com/llama/)
- [LLaVA Model](https://llava-vl.github.io/)

---

**Versão do Documento**: 1.0  
**Data**: 9 de Janeiro de 2026  
**Autor**: Gerado automaticamente  
**Estado**: Documentação Técnica Completa
