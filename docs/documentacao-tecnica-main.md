# Documentação Técnica - Aplicação Principal (main.py)

## Índice
1. [Visão Geral](#visão-geral)
2. [Arquitetura](#arquitetura)
3. [Dependências](#dependências)
4. [Componentes Principais](#componentes-principais)
5. [Fluxo de Execução](#fluxo-de-execução)
6. [Descrição Detalhada dos Componentes](#descrição-detalhada-dos-componentes)
7. [Interface de Utilizador](#interface-de-utilizador)
8. [Gestão de Estado](#gestão-de-estado)
9. [Integração com o Serviço de Chatbot](#integração-com-o-serviço-de-chatbot)
10. [Configuração e Execução](#configuração-e-execução)

---

## Visão Geral

O módulo `main.py` implementa a interface web interativa para o assistente virtual de design de interiores. Utiliza o framework **Hyperdiv** para criar uma aplicação web reativa e moderna, integrando-se com o serviço de chatbot baseado em modelos de linguagem (LLM).

### Funcionalidades Principais
- Interface de chat em tempo real
- Upload e visualização de imagens de espaços interiores
- Streaming de respostas do assistente
- Histórico de conversação persistente durante a sessão
- Interface multimodal (texto + imagem)
- Design responsivo e intuitivo

### Público-Alvo
- Proprietários de imóveis interessados em melhorar espaços
- Profissionais de design de interiores
- Agentes imobiliários que procuram aumentar o valor de propriedades

---

## Arquitetura

### Padrão Arquitetural
- **Padrão**: Model-View-Controller (MVC) Reativo
- **Framework**: Hyperdiv (framework web Python reativo)
- **Paradigma**: Programação Reativa Baseada em Estado
- **Renderização**: Server-Side Rendering com atualizações reativas

### Diagrama de Arquitetura

```
┌────────────────────────────────────────────────┐
│           Interface Web (Hyperdiv)             │
│  ┌──────────────┐  ┌──────────────────────┐   │
│  │  Templates   │  │   Componentes UI     │   │
│  │  & Layout    │  │   (form, text, etc)  │   │
│  └──────────────┘  └──────────────────────┘   │
└────────────┬───────────────────────────────────┘
             │
             │ Estado Reativo
             ▼
┌────────────────────────────────────────────────┐
│         Gestão de Estado (hd.state)            │
│  ┌─────────────────────────────────────────┐  │
│  │ messages, current_reply, img_data, etc  │  │
│  └─────────────────────────────────────────┘  │
└────────────┬───────────────────────────────────┘
             │
             │ Invocação de Tarefas
             ▼
┌────────────────────────────────────────────────┐
│      Lógica de Negócio (Funções)              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ request  │  │add_message│ │process_  │    │
│  │  ()      │  │    ()     │ │image_data│    │
│  └──────────┘  └──────────┘  └──────────┘    │
└────────────┬───────────────────────────────────┘
             │
             │ API/Stream
             ▼
┌────────────────────────────────────────────────┐
│        ChatBotService (LangGraph)              │
│  ┌─────────────────────────────────────────┐  │
│  │   Modelos LLM (Ollama)                  │  │
│  │   - llama3 (texto)                      │  │
│  │   - llava (visão)                       │  │
│  └─────────────────────────────────────────┘  │
└────────────────────────────────────────────────┘
```

---

## Dependências

### Bibliotecas Externas

```python
hyperdiv as hd              # Framework web reativo
base64                      # Codificação/descodificação de imagens
os                          # Operações do sistema operativo
services.chatbot            # Serviço de chatbot (ChatBotService)
```

### Requisitos de Sistema
- **Python**: 3.8+ (recomendado 3.13 baseado no ambiente virtual)
- **Framework**: Hyperdiv instalado
- **Servidor**: ChatBotService com modelos Ollama configurados
- **Browser**: Navegador web moderno (Chrome, Firefox, Safari, Edge)

### Dependências Indiretas
- ChatBotService (ver documentação separada)
- Modelos Ollama (llama3, llava)
- LangGraph e LangChain

---

## Componentes Principais

### 1. Plugin Personalizado: `file_picker`

```python
class file_picker(hd.Plugin):
    _assets_root = os.path.join(os.path.dirname(__file__), "assets")
    _assets = ["file_picker.js"]
    
    image_metadata = hd.Prop(hd.Any, None)
    disabled = hd.Prop(hd.Bool, False)
```

**Propósito**: Plugin customizado do Hyperdiv para seleção de ficheiros de imagem.

**Propriedades**:
- `_assets_root`: Diretório raiz dos assets JavaScript
- `_assets`: Lista de ficheiros JavaScript necessários (`file_picker.js`)
- `image_metadata`: Propriedade reativa que armazena metadados da imagem (nome, conteúdo)
- `disabled`: Propriedade booleana para desativar o seletor

**Tipo**: Plugin Hyperdiv com JavaScript integrado

**Estrutura de `image_metadata`**:
```python
{
    'name': 'example.png',      # Nome do ficheiro
    'content': 'data:image/...' # Conteúdo em base64 (data URL)
}
```

---

### 2. Variáveis Globais

#### `initial_message`
```python
initial_message = dict(
    role="assistant", 
    content="Olá! Sou um assistente de design de interiores, estou aqui para ajudar-te a melhorar o seu espaço e aumentar o valor da sua propriedade.", 
    id=0, 
    gpt_model=""
)
```

**Propósito**: Mensagem de boas-vindas inicial do assistente.

**Campos**:
- `role`: "assistant" - Identifica o emissor
- `content`: Texto de saudação em PT-PT
- `id`: 0 - Identificador único
- `gpt_model`: "" - Modelo usado (vazio para mensagem inicial)

---

#### `chatbot_service`
```python
chatbot_service = ChatBotService()
chatbot_service.build_graph()
```

**Propósito**: Instância global do serviço de chatbot.

**Inicialização**:
1. Cria instância de `ChatBotService`
2. Constrói o grafo de estados LangGraph

**Escopo**: Global - partilhado entre todas as sessões (nota: potencial limitação para escalabilidade)

---

## Descrição Detalhada dos Componentes

### Função: `add_message(role, content, state, gpt_model)`

**Propósito**: Adiciona uma nova mensagem ao histórico de conversação no estado.

**Parâmetros**:
- `role` (str): Papel do emissor da mensagem
  - Valores possíveis: `"user"`, `"assistant"`, `"system"`
- `content` (str): Conteúdo textual da mensagem
- `state` (hd.state): Objeto de estado do Hyperdiv
- `gpt_model` (str): Identificador do(s) modelo(s) usado(s) para gerar a mensagem

**Comportamento**:
1. Adiciona nova mensagem à tupla `state.messages`
2. Incrementa `state.message_id` para o próximo ID único
3. Inclui `state.img_data` na mensagem (se disponível)

**Estrutura da Mensagem**:
```python
{
    'role': 'user',
    'content': 'Como melhorar a sala?',
    'id': 1,
    'gpt_model': 'user',
    'img_data': 'data:image/png;base64,...'  # Opcional
}
```

**Nota**: Usa tupla (`+=`) para manter imutabilidade e garantir reatividade do Hyperdiv.

---

### Função: `process_image_data(base64_string)`

**Propósito**: Converte string base64 de imagem para bytes brutos.

**Parâmetros**:
- `base64_string` (str): String codificada em base64
  - Formato aceite: `"data:image/png;base64,iVBOR..."`
  - Formato aceite: `"iVBOR..."` (base64 direto)

**Retorno**: 
- `bytes`: Dados binários da imagem
- `None`: Se string vazia ou None

**Algoritmo**:
```python
if not base64_string:
    return None
    
if ";base64," in base64_string:
    # Remove prefixo "data:image/png;base64,"
    _, base64_data = base64_string.split(";base64,")
    return base64.b64decode(base64_data)
    
# Base64 direto sem prefixo
return base64.b64decode(base64_string)
```

**Casos de Uso**:
- Processar imagens enviadas via file_picker
- Preparar dados para o serviço de chatbot

---

### Função: `request(state)`

**Propósito**: Processa uma solicitação ao serviço de chatbot e atualiza o estado com a resposta.

**Parâmetros**:
- `state` (hd.state): Objeto de estado contendo mensagens e dados de imagem

**Fluxo de Execução**:

```
┌─────────────────────────────┐
│ 1. Processar img_data       │
│    (converter para bytes)   │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ 2. Preparar payload         │
│    - messages               │
│    - image_bytes            │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ 3. Stream do chatbot        │
│    (graph_app.stream)       │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ 4. Processar chunks         │
│    - Ignorar vision_llm     │
│    - Acumular content       │
│    - Registar modelos       │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ 5. Adicionar resposta       │
│    - add_message()          │
│    - Limpar estado          │
└─────────────────────────────┘
```

**Código Detalhado**:

```python
def request(state):
    # Passo 1: Processar imagem
    img_bytes = process_image_data(state.img_data)

    # Passo 2: Preparar payload e rastrear modelos
    models = set()
    
    # Passo 3: Stream do grafo
    for message_chunk, metadata in chatbot_service.graph_app.stream(
        {
            "messages": [
                dict(role=m["role"], content=m["content"]) 
                for m in state.messages
            ], 
            "image_bytes": img_bytes
        },
        stream_mode="messages"
    ):
        # Passo 4: Processar chunks
        node_name = metadata.get("langgraph_node")
        model_name = metadata.get("ls_model_name")
        models.add(model_name)

        # Ignorar saída do nó de visão
        if node_name == "vision_llm":
            continue

        # Acumular resposta
        if message_chunk.content:
            state.current_reply += message_chunk.content

    # Passo 5: Finalizar
    add_message("assistant", state.current_reply, state, ", ".join(models))
    state.current_reply = ""
    state.img_name = None
    state.img_data = None
```

**Características Importantes**:
1. **Streaming**: Respostas são acumuladas progressivamente em `state.current_reply`
2. **Filtragem**: Ignora outputs do nó `vision_llm` (descrições internas)
3. **Rastreamento de Modelos**: Regista todos os modelos usados na resposta
4. **Limpeza de Estado**: Remove dados de imagem após processamento

**Efeitos Colaterais**:
- Modifica `state.current_reply` (durante streaming)
- Adiciona mensagem ao `state.messages`
- Limpa `state.img_name` e `state.img_data`

---

### Função: `render_message(role, content, gpt_model=None, image_data=None)`

**Propósito**: Renderiza uma mensagem no interface de chat com estilos apropriados.

**Parâmetros**:
- `role` (str): Papel do emissor (`"user"` ou `"assistant"`)
- `content` (str): Conteúdo da mensagem
- `gpt_model` (str, opcional): Nome do modelo usado
- `image_data` (str, opcional): Data URL da imagem

**Renderização para Mensagens de Utilizador** (`role == "user"`):

```python
┌─────────────────────────────────────────┐
│  > Como melhorar a sala?          [user]│
│  [Imagem prévia]                        │
└─────────────────────────────────────────┘
```

**Estrutura HTML/Hyperdiv**:
```python
hd.hbox(
    # Estilo: fundo neutro, bordas arredondadas
    background_color="neutral-50",
    font_color="neutral-600",
    ...
)
    hd.vbox()
        hd.hbox()
            hd.icon("chevron-right")  # Seta
            hd.text(content)           # Texto
        
        if image_data:
            hd.image(image_data, width=10)  # Imagem
    
    hd.badge("user", pill=True)  # Badge de utilizador
```

**Renderização para Mensagens do Assistente** (`role == "assistant"`):

```python
┌─────────────────────────────────────────────────┐
│ **Sugestões para melhorar a sala:**             │
│ 1. Adicionar iluminação natural                 │
│ 2. Usar cores claras nas paredes                │
│                    [assistant (llama3, llava)] │
└─────────────────────────────────────────────────┘
```

**Estrutura HTML/Hyperdiv**:
```python
hd.hbox(
    # Estilo: sem fundo, texto escuro
    font_color="neutral-900",
    ...
)
    hd.markdown(content)  # Renderiza Markdown
    
    hd.badge(
        f"assistant ({gpt_model})",  # Badge com modelo
        pill=True, 
        variant="success"
    )
```

**Características**:
- **Suporte Markdown**: Mensagens do assistente suportam formatação Markdown
- **Visual Distintivo**: Cores e ícones diferentes para utilizador vs assistente
- **Informação de Modelo**: Mostra qual modelo gerou a resposta
- **Pré-visualização de Imagens**: Mostra imagens enviadas pelo utilizador

---

### Função: `main()`

**Propósito**: Função principal que define e executa a aplicação web.

**Estrutura Geral**:
```
main()
├── Inicializar Estado
├── Inicializar Task (tarefas assíncronas)
├── Criar Template (layout)
└── Renderizar Componentes
    ├── Área de Mensagens
    ├── Formulário de Input
    ├── Pré-visualização de Imagem
    ├── Spinner (carregamento)
    └── Botão de Limpar
```

#### Inicialização de Estado

```python
state = hd.state(
    messages=(initial_message,),  # Histórico de mensagens
    current_reply="",              # Resposta em construção
    gpt_model="",                  # Modelo atual
    message_id=0,                  # Contador de IDs
    img_name=None,                 # Nome do ficheiro de imagem
    img_data=None,                 # Dados da imagem (base64)
)
```

**Propriedades do Estado**:
| Propriedade | Tipo | Descrição |
|-------------|------|-----------|
| `messages` | tuple | Tupla de dicionários com histórico de mensagens |
| `current_reply` | str | Acumulador para resposta em streaming |
| `gpt_model` | str | Nome do modelo usado |
| `message_id` | int | Contador incremental para IDs únicos |
| `img_name` | str/None | Nome do ficheiro de imagem carregado |
| `img_data` | str/None | Data URL da imagem |

#### Template e Layout

```python
template = hd.template(
    title="Interior Design Chatbot", 
    logo="/assets/uminho-eng.jpeg",
    sidebar=False
)
```

**Configuração**:
- **Título**: "Interior Design Chatbot"
- **Logo**: Logotipo da UMinho Engenharia
- **Sidebar**: Desativada (interface simplificada)

#### Área de Mensagens

```python
with hd.box(direction="vertical-reverse", gap=1.5, vertical_scroll=True):
    # Resposta atual (streaming)
    if state.current_reply:
        hd.markdown(state.current_reply)
    
    # Histórico de mensagens (invertido)
    for e in reversed(state.messages):
        with hd.scope(e["id"]):
            if e["role"] == "system":
                continue
            render_message(...)
```

**Características**:
- **Direção Invertida**: Mensagens mais recentes no fundo
- **Scroll Vertical**: Permite navegação no histórico
- **Streaming em Tempo Real**: Mostra `current_reply` à medida que é gerado
- **Filtragem**: Ignora mensagens do sistema
- **Scoping**: Cada mensagem tem scope único para otimização

#### Formulário de Input

```python
with hd.form(direction="horizontal", width="100%") as form:
    with hd.box(...):
        uploader = file_picker(disabled=task.running)
        
        with hd.box(grow=1):
            prompt = form.text_input(
                placeholder="Converse com Interior Design Assistant...",
                autofocus=True,
                disabled=task.running,
                name="prompt",
            )
        
        prompt_submit = form.submit_button("Enviar", disabled=task.running)
```

**Componentes**:
1. **File Picker**: Upload de imagens
2. **Text Input**: Campo de texto para mensagens
3. **Submit Button**: Botão de envio

**Estados Desativados**: Todos os inputs são desativados durante `task.running`

#### Pré-visualização de Imagem

```python
if uploader.image_metadata:
    with hd.box(gap=1, border="1px solid #ddd", padding=1, border_radius="large"):
        hd.text(f"Arquivo: {state.img_name}")
        
        if state.img_data:
            hd.image(state.img_data, width=15)
```

**Comportamento**:
- Mostra quando uma imagem é selecionada
- Exibe nome do ficheiro e pré-visualização
- Estilo: Caixa com borda e cantos arredondados

#### Processamento de Submit

```python
if form.submitted:
    add_message("user", prompt.value, state, "user")
    prompt.reset()
    uploader.image_metadata = None
    task.rerun(request, state)
```

**Fluxo**:
1. Adiciona mensagem do utilizador ao estado
2. Limpa o campo de input
3. Remove metadados da imagem do uploader
4. Executa tarefa assíncrona `request(state)`

#### Indicador de Carregamento

```python
if task.running:
    with hd.box(font_size=4):
        hd.spinner(
            speed="5s",
            track_width=0.5
        )
```

**Características**:
- Mostra apenas quando tarefa está em execução
- Spinner animado com rotação de 5 segundos
- Tamanho grande (font_size=4)

#### Botão de Limpar

```python
if len(state.messages) > 0 or state.img_name:
    if hd.button(
        "Limpar Mensagens", 
        size="small", 
        variant="text", 
        disabled=task.running
    ).clicked:
        state.messages = (initial_message,)
        state.img_name = None
        state.img_data = None
        uploader.image_metadata = None
```

**Comportamento**:
- Visível quando há mensagens ou imagem carregada
- Desativado durante processamento
- Reset completo: volta ao estado inicial

---

## Interface de Utilizador

### Layout Visual

```
┌────────────────────────────────────────────────────┐
│  [Logo UMinho]  Interior Design Chatbot            │
├────────────────────────────────────────────────────┤
│                                                    │
│  ┌──────────────────────────────────────────────┐ │
│  │ **Sugestões:**                    [assistant]│ │
│  │ 1. ...                                       │ │
│  └──────────────────────────────────────────────┘ │
│                                                    │
│  ┌──────────────────────────────────────────────┐ │
│  │ > Como melhorar?              [user]         │ │
│  │ [imagem]                                     │ │
│  └──────────────────────────────────────────────┘ │
│                                                    │
│  ┌──────────────────────────────────────────────┐ │
│  │ Olá! Sou um assistente...      [assistant]   │ │
│  └──────────────────────────────────────────────┘ │
│                                                    │
├────────────────────────────────────────────────────┤
│  [📎] [____________________________] [Enviar]     │
│                                                    │
│  ┌──────────────────────────────────────────────┐ │
│  │ Arquivo: sala.png                            │ │
│  │ [imagem prévia]                              │ │
│  └──────────────────────────────────────────────┘ │
│                                                    │
│              [Limpar Mensagens]                    │
└────────────────────────────────────────────────────┘
```

### Fluxo de Interação do Utilizador

```
┌─────────────┐
│  Utilizador │
│   abre app  │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Vê mensagem inicial │
│   de boas-vindas    │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐       ┌──────────────────┐
│ Escreve mensagem    │◄──────┤  (Opcional)      │
│    no input         │       │ Carrega imagem   │
└──────┬──────────────┘       └──────────────────┘
       │
       ▼
┌─────────────────────┐
│  Clica "Enviar"     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Vê spinner          │
│ (processamento)     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Resposta aparece    │
│  em tempo real      │
│   (streaming)       │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Pode continuar      │
│   conversação       │
└─────────────────────┘
```

---

## Gestão de Estado

### Ciclo de Vida do Estado

```
INICIALIZAÇÃO
    │
    ├─► messages = (initial_message,)
    ├─► current_reply = ""
    ├─► message_id = 0
    ├─► img_name = None
    └─► img_data = None
    
UTILIZADOR ENVIA MENSAGEM
    │
    ├─► add_message("user", ...) → messages += nova_mensagem
    ├─► message_id += 1
    └─► Inicia task.rerun(request, state)
    
PROCESSAMENTO (request)
    │
    ├─► Loop de streaming
    │   └─► current_reply += chunk.content
    │
    └─► Finalização
        ├─► add_message("assistant", current_reply, ...)
        ├─► current_reply = ""
        ├─► img_name = None
        └─► img_data = None

LIMPAR CONVERSAÇÃO
    │
    ├─► messages = (initial_message,)
    ├─► img_name = None
    ├─► img_data = None
    └─► uploader.image_metadata = None
```

### Reatividade do Hyperdiv

O Hyperdiv utiliza um sistema reativo onde alterações ao estado desencadeiam automaticamente re-renderizações:

```python
# Alteração ao estado
state.current_reply += "novo texto"

# Desencadeia automaticamente
# ↓
# Re-renderização dos componentes que dependem de state.current_reply
```

**Princípios**:
1. **Imutabilidade de Tuplas**: `messages` usa tuplas para garantir reatividade
2. **Scoping**: `hd.scope(e["id"])` otimiza re-renderizações
3. **Tarefas Assíncronas**: `task.rerun()` permite operações não-bloqueantes

---

## Integração com o Serviço de Chatbot

### Contrato de Interface

**Entrada para `chatbot_service.graph_app.stream()`**:
```python
{
    "messages": [
        {"role": "user", "content": "Pergunta do utilizador"},
        {"role": "assistant", "content": "Resposta anterior"},
        ...
    ],
    "image_bytes": b'\x89PNG\r\n...'  # Opcional
}
```

**Saída (Stream)**:
```python
for message_chunk, metadata in stream(...):
    # message_chunk: Objeto de mensagem com .content
    # metadata: {
    #     "langgraph_node": "text_llm" | "vision_llm" | "improve_space_node",
    #     "ls_model_name": "llama3" | "llava"
    # }
```

### Mapeamento de Dados

```python
# Estado da Aplicação → Payload do Chatbot
state.messages → [dict(role=m["role"], content=m["content"]) for m in state.messages]
state.img_data → process_image_data() → image_bytes

# Resposta do Chatbot → Estado da Aplicação
message_chunk.content → state.current_reply (acumulação)
metadata.ls_model_name → models (conjunto)
state.current_reply → add_message("assistant", ...)
```

### Filtragem de Nós

```python
if node_name == "vision_llm":
    continue  # Ignora descrições internas de imagens
```

**Razão**: As descrições geradas pelo nó de visão são usadas internamente pelo nó `improve_space_node`. Não devem ser mostradas ao utilizador.

---

## Configuração e Execução

### Inicialização da Aplicação

```python
# Página Index (metadata SEO)
index_page = hd.index_page(
    title="MIA - Interior Design Chatbot",
    description="Interior Design Chatbot powered by Hyperdiv and Ollama.",
    keywords=("hyperdiv", "python", "ollama", "chatbot", "interior design", "uminho"),
    favicon="/assets/uminho.png",
)

# Executar aplicação
hd.run(main, index_page=index_page)
```

### Metadados da Página

| Propriedade | Valor |
|-------------|-------|
| **Título** | MIA - Interior Design Chatbot |
| **Descrição** | Interior Design Chatbot powered by Hyperdiv and Ollama. |
| **Keywords** | hyperdiv, python, ollama, chatbot, interior design, uminho |
| **Favicon** | /assets/uminho.png |

### Execução

**Comando**:
```bash
python src/main.py
```

**Servidor**:
- Hyperdiv inicia servidor web local
- URL típica: `http://localhost:8888`

### Estrutura de Assets

```
src/
├── main.py
└── assets/
    ├── file_picker.js      # Script do plugin de upload
    ├── uminho.png          # Favicon
    └── uminho-eng.jpeg     # Logo do cabeçalho
```

---

## Fluxo de Dados Completo

### Cenário: Utilizador Envia Mensagem com Imagem

```
1. UTILIZADOR
   │
   ├─► Seleciona imagem (file_picker)
   │   └─► uploader.image_metadata = {name: "sala.png", content: "data:image/..."}
   │
   ├─► state.img_name = "sala.png"
   ├─► state.img_data = "data:image/..."
   │
   ├─► Escreve "Como melhorar este espaço?"
   │
   └─► Clica "Enviar"

2. FORMULÁRIO (form.submitted)
   │
   ├─► add_message("user", "Como melhorar este espaço?", state, "user")
   │   ├─► state.messages += {role: "user", content: "...", img_data: "data:image/..."}
   │   └─► state.message_id = 1
   │
   ├─► prompt.reset()
   ├─► uploader.image_metadata = None
   │
   └─► task.rerun(request, state)

3. FUNÇÃO request()
   │
   ├─► img_bytes = process_image_data(state.img_data)
   │   └─► Converte "data:image/..." → bytes
   │
   ├─► payload = {
   │       "messages": [{"role": "user", "content": "..."}],
   │       "image_bytes": img_bytes
   │   }
   │
   └─► for chunk, metadata in chatbot_service.graph_app.stream(payload):

4. CHATBOT SERVICE
   │
   ├─► Router → vision_llm (tem image_bytes)
   │   └─► Descrição: "A sala tem paredes brancas, sofá azul..."
   │
   ├─► vision_llm → improve_space_node
   │   └─► Sugestões: "Para aumentar o valor:\n1. Adicionar plantas\n2. ..."
   │
   └─► Stream chunks

5. ACUMULAÇÃO (request loop)
   │
   ├─► if node_name == "vision_llm": continue
   │
   ├─► state.current_reply += "Para aumentar o valor:\n"
   ├─► state.current_reply += "1. Adicionar plantas\n"
   ├─► state.current_reply += "2. Melhorar iluminação\n"
   │
   └─► models.add("llama3"), models.add("llava")

6. FINALIZAÇÃO (request)
   │
   ├─► add_message("assistant", state.current_reply, state, "llama3, llava")
   │   └─► state.messages += {role: "assistant", content: "...", gpt_model: "..."}
   │
   ├─► state.current_reply = ""
   ├─► state.img_name = None
   └─► state.img_data = None

7. RENDERIZAÇÃO
   │
   ├─► Área de mensagens atualiza automaticamente
   │   ├─► Mensagem do utilizador com imagem
   │   └─► Resposta do assistente em Markdown
   │
   └─► Spinner desaparece (task.running = False)
```

---

## Diagramas

### Diagrama de Componentes UI

```
┌────────────────────────────────────────────┐
│           hd.template                      │
│  ┌──────────────────────────────────────┐ │
│  │         template.body                │ │
│  │  ┌────────────────────────────────┐  │ │
│  │  │   Área de Mensagens            │  │ │
│  │  │   (vertical-reverse scroll)    │  │ │
│  │  │  ┌──────────────────────────┐  │  │ │
│  │  │  │ current_reply (streaming)│  │  │ │
│  │  │  └──────────────────────────┘  │  │ │
│  │  │  ┌──────────────────────────┐  │  │ │
│  │  │  │ render_message() x N     │  │  │ │
│  │  │  └──────────────────────────┘  │  │ │
│  │  └────────────────────────────────┘  │ │
│  │  ┌────────────────────────────────┐  │ │
│  │  │   hd.form (input area)         │  │ │
│  │  │  ┌──────┐ ┌────────┐ ┌──────┐ │  │ │
│  │  │  │picker│ │  text  │ │submit│ │  │ │
│  │  │  └──────┘ └────────┘ └──────┘ │  │ │
│  │  └────────────────────────────────┘  │ │
│  │  ┌────────────────────────────────┐  │ │
│  │  │   Pré-visualização Imagem      │  │ │
│  │  └────────────────────────────────┘  │ │
│  │  ┌────────────────────────────────┐  │ │
│  │  │   hd.spinner (loading)         │  │ │
│  │  └────────────────────────────────┘  │ │
│  │  ┌────────────────────────────────┐  │ │
│  │  │   Botão Limpar                 │  │ │
│  │  └────────────────────────────────┘  │ │
│  └──────────────────────────────────────┘ │
└────────────────────────────────────────────┘
```

### Diagrama de Fluxo de Estado

```
┌─────────┐     submit      ┌─────────────┐
│  State  │────────────────►│ add_message │
│         │                 │   (user)    │
└────┬────┘                 └──────┬──────┘
     │                             │
     │                             ▼
     │                      ┌─────────────┐
     │                      │   State     │
     │                      │  updated    │
     │                      └──────┬──────┘
     │                             │
     │                             ▼
     │                      ┌─────────────┐
     │                      │task.rerun   │
     │                      │  (request)  │
     │                      └──────┬──────┘
     │                             │
     │                             ▼
     │                      ┌─────────────┐
     │                      │  Chatbot    │
     │                      │   Stream    │
     │                      └──────┬──────┘
     │                             │
     │            ┌────────────────┴────────────────┐
     │            │                                 │
     │            ▼                                 ▼
     │     ┌────────────┐                   ┌────────────┐
     │     │  Chunk 1   │                   │  Chunk N   │
     │     │ accumulate │                   │ accumulate │
     │     └─────┬──────┘                   └─────┬──────┘
     │           │                                │
     │           └────────────┬───────────────────┘
     │                        │
     │                        ▼
     │                 ┌─────────────┐
     │                 │add_message  │
     │                 │ (assistant) │
     │                 └──────┬──────┘
     │                        │
     └────────────────────────┘
              (cycle repeats)
```

---

## Considerações Técnicas

### Performance

**Otimizações**:
1. **Scoping**: `hd.scope(e["id"])` previne re-renderizações desnecessárias
2. **Direção Invertida**: `direction="vertical-reverse"` melhora performance em listas longas
3. **Streaming**: Respostas aparecem progressivamente, melhorando perceção de velocidade

**Limitações**:
1. **Instância Global**: `chatbot_service` é partilhado (não escalável para múltiplos utilizadores simultâneos)
2. **Histórico Ilimitado**: `state.messages` cresce indefinidamente (pode causar problemas de memória)
3. **Sem Paginação**: Todas as mensagens são renderizadas (impacto em conversações longas)

### Segurança

**Considerações**:
1. **Upload de Ficheiros**: Sem validação de tipo ou tamanho
2. **Injeção de Conteúdo**: Mensagens renderizadas como Markdown (potencial XSS se não sanitizado pelo Hyperdiv)
3. **Rate Limiting**: Não implementado
4. **Autenticação**: Não implementada
5. **HTTPS**: Dependente da configuração do servidor

**Recomendações**:
```python
# Validação de imagens
def validate_image(image_data):
    # Verificar tipo MIME
    # Verificar tamanho (< 10MB)
    # Verificar dimensões
    pass

# Rate limiting
from functools import lru_cache
import time

@lru_cache(maxsize=100)
def rate_limit(user_id):
    # Implementar lógica de rate limiting
    pass
```

### Escalabilidade

**Desafios**:
1. **Estado de Sessão**: Não persistente (perde-se ao recarregar)
2. **Instância Única**: `chatbot_service` global
3. **Memória**: Histórico cresce indefinidamente

**Soluções**:
```python
# Persistência de sessão
import redis
session_store = redis.Redis(...)

# Instância por sessão
def get_chatbot_service(session_id):
    # Criar/recuperar instância por sessão
    pass

# Limite de histórico
MAX_MESSAGES = 50
if len(state.messages) > MAX_MESSAGES:
    state.messages = state.messages[-MAX_MESSAGES:]
```

### Usabilidade

**Pontos Fortes**:
1. ✅ Interface intuitiva
2. ✅ Feedback visual (spinner, badges)
3. ✅ Streaming de respostas
4. ✅ Pré-visualização de imagens
5. ✅ Mensagens em PT-PT

**Melhorias Possíveis**:
1. Botão para parar geração
2. Histórico de conversações anteriores
3. Exportar conversação
4. Modo escuro
5. Notificações sonoras

---

## Casos de Uso

### Caso de Uso 1: Consulta Rápida Textual

**Cenário**: Utilizador quer dicas rápidas sem enviar imagem.

**Passos**:
1. Utilizador abre aplicação
2. Escreve "Cores recomendadas para sala de estar?"
3. Clica "Enviar"
4. Vê resposta com sugestões de cores

**Fluxo Técnico**: `text_llm` node → Resposta direta

---

### Caso de Uso 2: Análise de Espaço com Imagem

**Cenário**: Utilizador quer melhorar quarto para venda.

**Passos**:
1. Clica no file picker
2. Seleciona fotografia do quarto
3. Vê pré-visualização
4. Escreve "Como melhorar para aumentar valor de venda?"
5. Clica "Enviar"
6. Vê análise detalhada com sugestões priorizadas

**Fluxo Técnico**: `vision_llm` → `improve_space_node` → Resposta contextualizada

---

### Caso de Uso 3: Conversação Multi-Turn

**Cenário**: Utilizador quer refinar sugestões.

**Passos**:
1. Pergunta inicial: "Ideias para sala pequena?"
2. Resposta: Lista de sugestões
3. Pergunta de seguimento: "E quanto ao orçamento?"
4. Resposta: Sugestões ajustadas ao contexto anterior

**Fluxo Técnico**: Histórico de `state.messages` mantém contexto

---

## Limitações Identificadas

### 1. Gestão de Sessões
- **Problema**: Estado não persiste entre recarregamentos
- **Impacto**: Conversações perdidas ao fechar browser
- **Solução**: Implementar persistência (Redis, DB)

### 2. Escalabilidade
- **Problema**: Instância global de `chatbot_service`
- **Impacto**: Não suporta múltiplos utilizadores simultâneos eficientemente
- **Solução**: Pool de instâncias ou instância por sessão

### 3. Validação de Entrada
- **Problema**: Sem validação de uploads
- **Impacto**: Risco de segurança e erros
- **Solução**: Validar tipo MIME, tamanho, dimensões

### 4. Gestão de Erros
- **Problema**: Sem tratamento explícito de exceções
- **Impacto**: Aplicação pode falhar sem feedback ao utilizador
- **Solução**: Try-catch com mensagens de erro amigáveis

### 5. Histórico Ilimitado
- **Problema**: `state.messages` cresce indefinidamente
- **Impacto**: Problemas de memória e performance
- **Solução**: Limite de mensagens ou paginação

---

## Melhorias Futuras Sugeridas

### 1. Persistência de Sessão

```python
import json
import uuid

def save_session(session_id, state):
    with open(f"sessions/{session_id}.json", "w") as f:
        json.dump({
            "messages": list(state.messages),
            "message_id": state.message_id
        }, f)

def load_session(session_id):
    try:
        with open(f"sessions/{session_id}.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
```

### 2. Validação de Imagens

```python
from PIL import Image
import io

def validate_image(image_data):
    try:
        img_bytes = process_image_data(image_data)
        img = Image.open(io.BytesIO(img_bytes))
        
        # Validações
        if img.size[0] * img.size[1] > 10000000:  # 10MP
            return False, "Imagem muito grande"
        
        if img.format not in ["PNG", "JPEG", "JPG"]:
            return False, "Formato não suportado"
        
        return True, None
    except Exception as e:
        return False, str(e)
```

### 3. Botão de Parar Geração

```python
if task.running:
    if hd.button("Parar", variant="danger").clicked:
        task.cancel()
        state.current_reply = ""
```

### 4. Exportar Conversação

```python
def export_conversation(messages):
    content = "# Conversação de Design de Interiores\n\n"
    for msg in messages:
        if msg["role"] == "user":
            content += f"**Utilizador**: {msg['content']}\n\n"
        elif msg["role"] == "assistant":
            content += f"**Assistente**: {msg['content']}\n\n"
    return content

if hd.button("Exportar").clicked:
    markdown_content = export_conversation(state.messages)
    # Disponibilizar para download
```

### 5. Histórico de Conversações

```python
state = hd.state(
    conversations=[],  # Lista de conversações anteriores
    current_conversation_id=None,
    ...
)

def new_conversation():
    conversation_id = str(uuid.uuid4())
    state.conversations.append({
        "id": conversation_id,
        "title": "Nova Conversação",
        "messages": [initial_message]
    })
    state.current_conversation_id = conversation_id
```

---

## Glossário

- **Hyperdiv**: Framework Python para criar aplicações web reativas
- **State Management**: Gestão de estado reativo
- **Streaming**: Transmissão progressiva de dados
- **Plugin**: Componente customizado do Hyperdiv com JavaScript
- **Data URL**: URL que contém dados inline codificados (ex: `data:image/png;base64,...`)
- **Base64**: Esquema de codificação binária para texto
- **Task**: Tarefa assíncrona no Hyperdiv
- **Scope**: Contexto único para otimização de renderização
- **Markdown**: Linguagem de marcação leve para formatação de texto
- **Badge**: Componente UI para etiquetas/tags
- **Template**: Layout de página no Hyperdiv

---

## Estrutura de Ficheiros Relacionados

```
IIA/
├── src/
│   ├── main.py                      # ← Este ficheiro
│   ├── assets/
│   │   ├── file_picker.js           # Plugin de upload
│   │   ├── uminho.png               # Favicon
│   │   └── uminho-eng.jpeg          # Logo
│   └── services/
│       └── chatbot.py               # Serviço de chatbot
├── docs/
│   ├── documentacao-tecnica-main.md        # ← Esta documentação
│   └── documentacao-tecnica-chatbot.md     # Documentação do chatbot
└── pyproject.toml                   # Dependências do projeto
```

---

## Referências

- [Hyperdiv Documentation](https://hyperdiv.io/docs)
- [Hyperdiv API Reference](https://hyperdiv.io/docs/reference)
- [Python Base64 Module](https://docs.python.org/3/library/base64.html)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Markdown Guide](https://www.markdownguide.org/)

---

## Anexos

### A. Estrutura Completa de Mensagem

```python
{
    'role': 'user' | 'assistant' | 'system',
    'content': str,              # Conteúdo textual
    'id': int,                   # ID único
    'gpt_model': str,            # Modelo(s) usado(s)
    'img_data': str | None       # Data URL da imagem (opcional)
}
```

### B. Estrutura de image_metadata

```python
{
    'name': str,      # Nome do ficheiro (ex: "sala.png")
    'content': str    # Data URL (ex: "data:image/png;base64,...")
}
```

### C. Metadados do Stream do Chatbot

```python
{
    'langgraph_node': 'vision_llm' | 'text_llm' | 'improve_space_node',
    'ls_model_name': 'llama3' | 'llava'
}
```

---

**Versão do Documento**: 1.0  
**Data**: 9 de Janeiro de 2026  
**Autor**: Gerado automaticamente  
**Estado**: Documentação Técnica Completa  
**Ficheiro Documentado**: `src/main.py`
