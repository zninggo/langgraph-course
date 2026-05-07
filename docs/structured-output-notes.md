# LangChain 与 LLM 集成问题记录

## 1. thinking 模型与 `with_structured_output` 不兼容

### 现象

使用 `llm.with_structured_output(PydanticModel)` 时，thinking 模型（如 mimo-v2.5-pro）返回的内容包含思考过程：

```
{thinking}...思考过程...{/thinking}{"binary_score": false}
```

导致 JSON 解析失败：

```
pydantic_core.ValidationError: Invalid JSON: key must be a string at line 1 column 2
```

### 原因

LangChain 的 `with_structured_output` 在 pydantic v2 下默认使用 `json_schema` 方法，该方法要求模型在 `content` 中返回纯 JSON。

但 thinking 模型的 `content` 会包含 `{thinking}...` 等思考过程，不是纯 JSON，导致解析失败。

### 两种方法对比

| 方法 | 数据来源 | thinking 模型兼容性 |
|------|----------|---------------------|
| `json_schema`（pydantic v2 默认） | 解析 `content` | 不兼容 |
| `function_calling` | 读 `tool_calls` | 兼容，忽略 `content` |

### 解决方案

显式指定 `method="function_calling"`：

```python
# 修复前
chain = RunnableLambda(build_messages) | llm.with_structured_output(MyModel)

# 修复后
chain = RunnableLambda(build_messages) | llm.with_structured_output(MyModel, method="function_calling")
```

---


## 2. pydantic v1 schema 警告

### 现象

```
UserWarning: Received a Pydantic BaseModel V1 schema. This is not supported by method="json_schema".
Please use method="function_calling" or specify schema via JSON Schema or Pydantic V2 BaseModel.
Overriding to method="function_calling".
```

### 原因

使用 `pydantic.v1.BaseModel` 定义模型时，langchain 检测到 v1 schema，自动回退到 `function_calling` 方法。

### 解决方案

统一使用 `pydantic.BaseModel`（v2）：

```python
# 错误
from pydantic.v1 import BaseModel, Field

# 正确
from pydantic import BaseModel, Field
```

---

