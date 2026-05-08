# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概览

这是一个 Python 3.11+ 的 LangGraph / LangChain RAG 课程项目。依赖由 `pyproject.toml` 和 `uv.lock` 管理，核心功能是：从网页抓取并写入 Chroma 向量库，运行带检索评分、必要时 Tavily 网络搜索、生成答案的 LangGraph 流程。

## 常用命令

```powershell
# 安装依赖
uv sync

# 运行全部测试
uv run pytest

# 运行单个测试文件
uv run pytest app/chains/tests/test_chains.py

# 运行单个测试函数
uv run pytest app/chains/tests/test_chains.py::test_retrieval_grader_answer_no

# 格式化代码
uv run black .
uv run isort .

# 构建/刷新 Chroma 本地向量库（会访问 ingestion.py 中的网页）
uv run python ingestion.py

# 运行 LangGraph 主流程并输出 graph.png
uv run python -m app.graph.graph
```

当前仓库未发现独立 lint、typecheck 或 build 脚本；不要在未确认前写入 CLAUDE.md 之外的假设命令。

## 环境变量

`.env` 由 `python-dotenv` 自动加载，LLM 和 embedding 配置来自环境变量：

- `OPENAI_MODEL`
- `OPENAI_BASE_URL`
- `OPENAI_API_KEY`
- `LOCAL_BASE_URL`（用于 `OpenAIEmbeddings`）
- Tavily 搜索依赖 `langchain_tavily.TavilySearch` 所需的 Tavily 环境变量

## 高层架构

- `ingestion.py` 是数据摄取和向量库入口：创建 `OpenAIEmbeddings`、`Chroma`、`retriever`；直接运行时抓取三篇 Lilian Weng 博客、切分文本并写入项目根目录下的 `.chromadb`。
- `llm.py` 统一创建 `ChatOpenAI` 实例，所有 chains 复用该对象。
- `app/graph/state.py` 定义 `GraphState`，包含 `question`、`generation`、`web_search`、`documents`，是节点间传递的共享状态。
- `app/graph/graph.py` 组装 LangGraph：`START -> retrieve_nodes -> grade_documents`；如果评分后 `web_search=True` 则走 `search -> generation`，否则直接 `generation`；当前还挂了生成结果评分的条件边。
- `app/nodes/` 存放图节点：`retrieve.py` 从 `ingestion.retriever` 检索；`grade_documents.py` 用 retrieval grader 过滤文档并决定是否搜索；`web_search.py` 调 Tavily 并把搜索内容追加为 `Document`；`generation_node.py` 拼接文档上下文并调用生成链。
- `app/chains/` 存放可复用 LangChain runnable：`generation.py` 从 LangSmith Hub 拉取 `rlm/rag-prompt`；`retrieval_grader.py`、`hallucination_grader.py`、`answer_grader.py` 使用结构化输出对检索相关性、幻觉和回答有效性打分。

## 注意事项

- `app/graph/graph.py` 在模块导入时会编译图并写出 `./graph.png`，测试或导入该模块可能产生文件副作用。
- 多个 chain 使用 `with_structured_output(..., method="function_calling")`，这是为了兼容会在 `content` 中输出 thinking 的模型；不要随意改回默认 JSON schema 方法。
- 现有测试会调用真实 LLM、向量库和可能的外部服务，运行前需要 `.env` 和 `.chromadb` 可用。
