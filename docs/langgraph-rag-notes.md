# LangGraph 与 RAG 流程问题记录

## 1. Python `:=` 海象运算符

### 现象

```python
if hallucination_grade := score.binary_score:
    ...
```

### 含义

`:=` 是 Python 3.8+ 的赋值表达式，会先把右侧值赋给变量，再用该值参与判断。

等价于：

```python
hallucination_grade = score.binary_score
if hallucination_grade:
    ...
```

如果右侧是字符串，注意非空字符串都是真值，例如 `"yes"` 和 `"no"` 都会进入 `if`。如果要判断具体值，应写成：

```python
if (hallucination_grade := score.binary_score) == "yes":
    ...
```

当前项目里 `binary_score` 定义为 `bool` 时，可以直接写：

```python
if score.binary_score:
    ...
```

---

## 2. Pydantic `Field(...)` 中的 `...`

### 示例

```python
class RouteQuery(BaseModel):
    datasource: Literal["vectorstore", "websearch"] = Field(
        ...,
        description="Given a user question choose to route it to web search or a vectorstore.",
    )
```

### 含义

`...` 是 Python 的 `Ellipsis` 对象。在 Pydantic 的 `Field(...)` 中表示该字段是必填字段。

```python
RouteQuery(datasource="vectorstore")  # 正确
RouteQuery(datasource="websearch")    # 正确
RouteQuery()                          # 报错，datasource 必填
```

`Literal["vectorstore", "websearch"]` 表示字段值只能是这两个字符串之一。

---

## 3. `set_entry_point`

`set_entry_point` 用于设置固定入口节点。

```python
graph.set_entry_point("retrieve_nodes")
```

等价于：

```python
graph.add_edge(START, "retrieve_nodes")
```

流程含义：

```text
START -> retrieve_nodes
```

每次运行图都会先进入同一个节点，不做路由判断。

---

## 4. `set_conditional_entry_point`

`set_conditional_entry_point` 用于设置条件入口节点。它会先执行一个路由函数，再根据返回值决定从哪个节点开始。

```python
def route_question(state) -> Literal["vectorstore", "websearch"]:
    if "agent" in state["question"]:
        return "vectorstore"
    return "websearch"

builder.set_conditional_entry_point(
    route_question,
    {
        "vectorstore": "retrieve_nodes",
        "websearch": "search",
    },
)
```

流程含义：

```text
START -> route_question
  -> retrieve_nodes
  -> search
```

它基本等价于在 `START` 上添加条件边：

```python
builder.add_conditional_edges(START, route_question, path_map)
```

适合在 RAG 流程最开始判断问题应该走向量库还是网络搜索。

---

## 5. `retrieve_nodes` 中的 `APIConnectionError`

### 现象

```text
openai.APIConnectionError: Connection error.
During task with name 'retrieve_nodes'
```

### 原因

`retrieve_nodes` 调用：

```python
documents = retriever.invoke(question)
```

`retriever` 来自 Chroma，查询时需要先用 `OpenAIEmbeddings` 把问题转成向量。当前 embedding 配置来自：

```python
embeddings = OpenAIEmbeddings(
    model="text-embedding-bge-m3",
    base_url=os.getenv("LOCAL_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
)
```

因此连接错误通常不是 LangGraph 节点逻辑错误，而是 embedding 服务不可访问。

重点检查：

1. `LOCAL_BASE_URL` 是否正确。
2. 本地或代理的 OpenAI-compatible embedding 服务是否启动。
3. `OPENAI_API_KEY` 是否存在。
4. `text-embedding-bge-m3` 是否是该服务支持的模型名。
5. 即使 `.chromadb` 已存在，查询问题时仍然需要调用 embedding 服务对问题向量化。

---

## 6. LangGraph 图为什么看起来很乱

### 直接冲突

如果同时存在：

```python
graph.add_edge(GENERATION_NODE, END)

graph.add_conditional_edges(GENERATION_NODE, grade_generation_grounded_in_documents_and_question, {
    "useful": END,
    "not useful": SEARCH_NODE,
    "not supported": GENERATION_NODE,
})
```

表示 `generation` 执行后既可以无条件结束，又要根据评分决定下一步。应删除无条件边，只保留条件边。

### 图仍然可能不好看

即使删掉无条件边，只要存在这些分支：

```python
"not useful": SEARCH_NODE,
"not supported": GENERATION_NODE,
```

图里仍然会有回边和自循环：

```text
generation -> search -> generation
generation -> generation
```

Mermaid 自动布局对循环结构不友好，所以 PNG 看起来绕是正常现象，不一定代表流程错误。

建议用 Mermaid 文本检查结构：

```python
print(app.get_graph().draw_mermaid())
```

然后复制到 Mermaid 在线编辑器查看。

---

## 7. 当前 RAG 流程理解

推荐理解为：

```text
START
  -> retrieve_nodes
  -> grade_documents
      -> generation
      -> search
  -> generation
      -> END
      -> search
      -> generation
```

其中：

- `grade_documents -> search`：检索文档不够相关，需要网络搜索。
- `grade_documents -> generation`：检索文档可用，直接生成。
- `generation -> END`：答案有事实依据且解决问题。
- `generation -> search`：答案没解决问题，补充搜索。
- `generation -> generation`：答案不受文档支持，尝试重新生成。

`generation -> generation` 是课程里常见的重试生成逻辑，但工程上要注意可能导致循环，真实项目通常会配合最大重试次数或递归限制。
