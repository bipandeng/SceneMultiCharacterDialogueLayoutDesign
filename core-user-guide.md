# Core 用户指南

## 概述

AutoGen Core 提供了一种简单快速构建**事件驱动、分布式、可扩展、弹性**的 AI 智能体系统的方法。

智能体使用 [Actor 模型](https://en.wikipedia.org/wiki/Actor_model) 开发。你可以在本地构建和运行智能体系统，当你准备好时，可以轻松迁移到云端的分布式系统。

---

## 核心特性

| 特性 | 说明 |
|------|------|
| **异步消息传递** | 智能体通过异步消息通信，支持事件驱动和请求/响应通信模型 |
| **可扩展 & 分布式** | 支持跨组织边界的复杂智能体网络场景 |
| **多语言支持** | 目前支持 Python 和 Dotnet 互操作，更多语言即将推出 |
| **模块化 & 可扩展** | 高度可定制，支持自定义智能体、记忆即服务、工具注册表和模型库 |
| **可观测 & 可调试** | 轻松追踪和调试智能体系统 |
| **事件驱动架构** | 构建事件驱动、分布式、可扩展、弹性的 AI 智能体系统 |

---

## 架构特点

### 1. 异步消息传递
```
智能体 A ──异步消息──→ 智能体 B
     ↑                    │
     └────响应消息─────────┘
```
- 非阻塞通信
- 支持事件驱动模式
- 支持请求/响应模式

### 2. 分布式架构
```
┌─────────────┐     ┌─────────────┐
│   节点 1     │     │   节点 2     │
│  智能体 A    │ ←─→ │  智能体 B    │
└─────────────┘     └─────────────┘
        ↑                    ↑
        └────────┬───────────┘
                 ↓
          ┌─────────────┐
          │   节点 3     │
          │  智能体 C    │
          └─────────────┘
```
- 智能体可分布在不同节点
- 支持跨组织边界
- 弹性故障恢复

### 3. Actor 模型
每个智能体是一个独立的 Actor：
- 有自己的状态
- 通过消息与其他 Actor 通信
- 独立处理消息
- 并发安全

---

## 适用场景

| 场景 | 说明 |
|------|------|
| 业务流程自动化 | 确定性和动态的智能体工作流 |
| 多智能体协作研究 | 探索智能体之间的协作模式 |
| 分布式应用 | 多语言、多节点的分布式智能体系统 |

---

## 与 AgentChat 的关系

```
┌─────────────────────────────────┐
│         AgentChat               │  ← 高级 API，易于使用
│    (预定义智能体、团队模式)       │
└────────────────┬────────────────┘
                 │ 基于
                 ↓
┌─────────────────────────────────┐
│         autogen-core            │  ← 底层框架，更灵活
│    (事件驱动、Actor 模型)        │
└─────────────────────────────────┘
```

- **AgentChat**：适合快速原型开发，提供开箱即用的智能体和团队
- **Core**：适合生产级系统，需要更多控制和自定义

---

## 快速开始

```python
import asyncio
from autogen_core import AgentId, MessageContext, RoutedAgent, SingleThreadedAgentRuntime
from dataclasses import dataclass

@dataclass
class Message:
    content: str

class MyAgent(RoutedAgent):
    async def on_message(self, message: Message, ctx: MessageContext):
        print(f"收到消息: {message.content}")

async def main():
    runtime = SingleThreadedAgentRuntime()
    await MyAgent.register(runtime, "my_agent", lambda: MyAgent("My Agent"))
    
    agent_id = AgentId("my_agent", "default")
    runtime.start()
    await runtime.send_message(Message("Hello!"), agent_id)
    await runtime.stop()

asyncio.run(main())
```

---

## 相关链接

- [快速开始](https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/quickstart.html)
- [设计模式](https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/design-patterns/intro.html)
- [GitHub 仓库](https://github.com/microsoft/autogen)
