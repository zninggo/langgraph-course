# Python Typing 常用类型参考

## 基本类型

```python
x: int = 1
y: float = 1.0
s: str = "hello"
b: bool = True
n: None = None
```

## 容器类型

```python
from typing import List, Dict, Tuple, Set, Optional

# 列表
nums: list[int] = [1, 2, 3]          # Python 3.9+
nums: List[int] = [1, 2, 3]          # 兼容旧版

# 字典
d: dict[str, int] = {"a": 1}         # Python 3.9+
d: Dict[str, int] = {"a": 1}         # 兼容旧版

# 元组 - 固定长度
point: tuple[int, int] = (1, 2)
point: Tuple[int, int] = (1, 2)

# 元组 - 可变长度（所有元素同类型）
nums: tuple[int, ...] = (1, 2, 3)

# 集合
s: set[int] = {1, 2, 3}
```

## Union 与 Optional

```python
from typing import Union, Optional

# Union - 多选一
x: Union[str, int] = "hello"         # str 或 int
x: str | int = "hello"               # Python 3.10+ 语法

# Optional - 等价于 Union[X, None]
x: Optional[str] = None              # str 或 None
x: str | None = None                 # Python 3.10+ 语法
```

## Annotated - 附加元数据

```python
from typing import Annotated

# 给类型附加额外信息（Pydantic、FastAPI 等框架使用）
x: Annotated[int, Field(gt=0)]                          # 大于 0 的整数
x: Annotated[str, Field(min_length=1, max_length=100)]  # 长度限制字符串
x: Annotated[list[str], Field(min_length=1)]            # 非空列表

# LangGraph 中用作 reducer
from operator import add
messages: Annotated[list[str], add]  # 消息自动累加
```

## TypedDict - 类型化字典

```python
from typing import TypedDict, NotRequired

class User(TypedDict):
    name: str
    age: int
    email: NotRequired[str]  # 可选字段

user: User = {"name": "Alice", "age": 30}  # email 可省略
```

## Literal - 字面量类型

```python
from typing import Literal

direction: Literal["up", "down", "left", "right"] = "up"
status: Literal[200, 404, 500] = 200
```

## Callable - 函数类型

```python
from typing import Callable

# 参数类型 -> 返回类型
fn: Callable[[int, str], bool]  # 接受 (int, str)，返回 bool
fn: Callable[..., str]          # 任意参数，返回 str
fn: Callable[[], None]          # 无参数，无返回值
```

## TypeVar 与泛型

```python
from typing import TypeVar, Generic

T = TypeVar("T")

class Stack(Generic[T]):
    def __init__(self) -> None:
        self.items: list[T] = []

    def push(self, item: T) -> None:
        self.items.append(item)

    def pop(self) -> T:
        return self.items.pop()

# 使用
int_stack: Stack[int] = Stack()
int_stack.push(1)
```

## 常用类型工具

```python
from typing import (
    Any,          # 任意类型，跳过类型检查
    NoReturn,     # 永不返回（如抛异常的函数）
    TypeAlias,    # 类型别名（Python 3.10+）
    TypeGuard,    # 类型守卫，收窄类型
    overload,     # 函数重载装饰器
    Final,        # 不可变常量
    ClassVar,     # 类变量（非实例变量）
    Protocol,     # 结构化子类型（鸭子类型）
)
```

## 实际项目示例

### Pydantic 模型

```python
from pydantic import BaseModel, Field
from typing import Optional

class User(BaseModel):
    name: str = Field(description="用户名")
    age: int = Field(ge=0, le=150, description="年龄")
    email: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
```

### LangGraph State

```python
from typing import NotRequired, TypedDict
from langgraph.graph import MessagesState

class State(MessagesState):
    answer: NotRequired[str]
    score: NotRequired[float]
```

### FastAPI 路由

```python
from fastapi import APIRouter
from typing import Annotated
from pydantic import Field

router = APIRouter()

@router.get("/items")
async def get_items(
    q: Annotated[str, Field(min_length=1)],
    limit: Annotated[int, Field(ge=1, le=100)] = 10,
) -> list[dict[str, Any]]:
    ...
```

### 类型守卫

```python
from typing import TypeGuard

def is_string_list(val: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(x, str) for x in val)

def process(items: list[object]) -> None:
    if is_string_list(items):
        # 此处 items 被收窄为 list[str]
        print(items[0].upper())
```
