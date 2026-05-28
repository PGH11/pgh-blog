---
title: "Hermes Session Recorder 插件实践：用生命周期 Hook 还原 Agent 调用链"
slug: "session-recorder-plugin-blog"
date: 2026-05-29
category: "AI Agent"
tags:
  - Hermes
  - Session Recorder
  - AI Agent
summary: "记录 session-recorder 插件如何通过 Hermes 生命周期 Hook 捕获 Agent 内部事件，并用 JSONL 还原一次请求的调用链路。"
---

# Hermes Session Recorder 插件实践：用生命周期 Hook 还原 Agent 调用链

调试 AI Agent 工作流时，最难的往往不是接口有没有返回，而是一次用户请求在 Agent 内部到底经历了什么。

在一个典型的 Hermes 集成里，一条请求可能经过前端、业务 API 服务、Hermes 容器、Hermes Agent、技能系统、工具调用、模型供应商 API。外层 HTTP 日志只能证明“请求进来了”，但很难回答“Agent 内部触发了几次模型调用”“最终是哪一轮输出”“技能链路有没有走到预期节点”。

`session-recorder` 插件就是为了解决这个问题。它不侵入 Hermes 主流程，而是挂在 Hermes 插件生命周期 Hook 上，把关键节点写成 JSONL 日志。这样我们可以按 session 回放 Agent 内部发生过的事件。

本文重点讲两个部分：

1. 插件基于哪些生命周期 Hook 工作。
2. 每个 Hook 会注入哪些日志事件。

## 一、插件解决的问题

一次 Hermes 请求大致会经过这条链路：

```text
前端 / API Client
  -> 业务 API 服务
  -> Hermes 容器
  -> Hermes Agent
  -> skill / tool
  -> LLM Provider API
```

没有插件时，我们只能看到外层服务日志，例如请求 URL、响应状态码、接口返回体。可一旦问题出在 Hermes Agent 内部，就会很难定位：

- 当前请求到底进入了哪个 Hermes 容器？
- 插件有没有在新容器里启用？
- 外层传入的 `session_id` 和 Hermes 内部日志文件名是不是同一个？
- 一条用户消息为什么触发了多次模型调用？
- 哪些事件是用户回合，哪些事件是 Hermes 内部模型请求？
- 当前调用走的是哪个 `provider`、`base_url`、`api_mode`？
- 当前日志为什么有 `api_request input=""`？

`session-recorder` 的定位是：记录 Hermes Agent 内部真实触发的生命周期事件，而不是替代业务服务日志。

## 二、日志保存位置

插件默认把日志写在插件目录下：

```text
<plugin_dir>/session-records/<session_id>.jsonl
```

在 Docker 容器里，常见路径是：

```text
/opt/data/plugins/session-recorder/session-records/
```

例如：

```text
/opt/data/plugins/session-recorder/session-records/2bc3c23fbd0b3be1fd710a63452ed58d.jsonl
```

注意：文件名来自 Hermes Agent 内部拿到的 `session_id`。它不一定等于前端或外层业务服务传入的会话 ID。排查时应该先列出容器里的最新日志文件。

```bash
docker exec -it <hermes-container> sh -lc 'ls -lt /opt/data/plugins/session-recorder/session-records | head -20'
```

## 三、为什么使用 JSONL

插件使用 JSON Lines 格式，一行就是一个 JSON 对象：

```json
{"event":"session_start","session_id":"session_51","timestamp":"2026-05-25T07:04:49+00:00"}
{"event":"api_request","session_id":"session_51","api_call_count":1,"input":""}
{"event":"turn","session_id":"session_51","input":"请帮我整理这段内容","output":"..."}
```

JSONL 的好处很直接：

- 可以边写边看，适合 `tail -f`。
- 可以用 `grep` 搜索 session、关键词、字段。
- 单行损坏通常不影响其他事件。
- 后续容易导入 Python、jq、日志系统或数据库。

## 四、开发原理：插件注册与生命周期 Hook

插件目录很简单：

```text
session-recorder/
  __init__.py
  plugin.yaml
  README.md
```

`plugin.yaml` 声明插件信息和希望监听的 Hook：

```yaml
name: session-recorder
version: 1.0.0
description: "Record each conversation turn input and output."
author: "Hermes Agent"
hooks:
  - on_session_start
  - pre_api_request
  - post_llm_call
  - on_session_finalize
```

Hermes 加载插件时会导入 `__init__.py`，执行 `register(ctx)`：

```python
def register(ctx) -> None:
    ctx.register_hook("on_session_start", _on_session_start)
    ctx.register_hook("pre_api_request", _on_pre_api_request)
    ctx.register_hook("post_llm_call", _on_post_llm_call)
    ctx.register_hook("on_session_finalize", _on_session_finalize)
```

这就是整个插件的核心：不改 Hermes 主代码，只把处理函数挂到 Hermes 暴露的生命周期节点上。

### Hook 与事件对应关系

| 生命周期 Hook | 触发时机 | 注入事件 | 主要用途 |
|---|---|---|---|
| `on_session_start` | Hermes 会话开始 | `session_start` | 标记 session 文件创建和基础环境 |
| `pre_api_request` | 每次请求模型前 | `api_request` | 记录模型调用元信息 |
| `post_llm_call` | 一轮 LLM 调用链结束后 | `turn` | 记录真实用户输入和最终输出 |
| `on_session_finalize` | Hermes 会话结束 | `session_finalize` | 标记会话结束状态 |

一个用户请求不一定只对应一次 `api_request`。Hermes 可能会为了技能加载、上下文整理、工具执行、多轮推理而多次调用模型。因此日志中经常会看到多个 `api_request`，最后才出现一条 `turn`。

## 五、事件一：`session_start`

`session_start` 由 `on_session_start` Hook 注入，表示 Hermes Agent 会话开始。

示例：

```json
{
  "event": "session_start",
  "metadata": {},
  "model": "MiniMax-M2.7-highspeed",
  "platform": "api_server",
  "session_id": "2bc3c23fbd0b3be1fd710a63452ed58d",
  "timestamp": "2026-05-27T07:02:12+00:00"
}
```

主要字段：

| 字段 | 说明 |
|---|---|
| `event` | 固定为 `session_start` |
| `session_id` | Hermes 内部会话 ID，也是默认日志文件名 |
| `model` | 当前会话使用的模型 |
| `platform` | 调用来源，例如 `api_server` |
| `metadata` | Hook 传入的额外信息 |
| `timestamp` | UTC 时间 |

这个事件的价值是确认插件确实被加载，并且当前会话已经开始写日志。

## 六、事件二：`api_request`

`api_request` 由 `pre_api_request` Hook 注入，表示 Hermes 即将发起一次模型请求。

当前线上版本不记录 system prompt。它主要记录模型调用的元信息，例如 provider、base_url、api_mode、token 估算、当前第几次模型调用。

示例：

```json
{
  "api_call_count": 1,
  "api_mode": "anthropic_messages",
  "base_url": "https://api.minimaxi.com/anthropic",
  "event": "api_request",
  "input": "",
  "messages": [],
  "metadata": {
    "approx_input_tokens": 3837,
    "max_tokens": null,
    "message_count": 2,
    "request_char_count": 15345,
    "task_id": "2bc3c23fbd0b3be1fd710a63452ed58d",
    "tool_count": 26
  },
  "model": "MiniMax-M2.7-highspeed",
  "platform": "api_server",
  "provider": "minimax-cn",
  "request_message_count": 0,
  "session_id": "2bc3c23fbd0b3be1fd710a63452ed58d",
  "timestamp": "2026-05-27T07:02:12+00:00"
}
```

主要字段：

| 字段 | 说明 |
|---|---|
| `event` | 固定为 `api_request` |
| `api_call_count` | 当前 session 中第几次模型 API 调用 |
| `api_mode` | 模型调用协议，例如 `anthropic_messages` |
| `provider` | 模型供应商，例如 `minimax-cn` |
| `base_url` | 实际模型 API 地址 |
| `model` | 本次模型名 |
| `input` | 当前 Hook 能提取到的请求输入；提取不到时为空字符串 |
| `messages` | 当前 Hook 能拿到的消息摘要；拿不到时为空数组 |
| `request_message_count` | 当前 Hook 捕获到的请求消息数量 |
| `metadata.approx_input_tokens` | Hermes 估算的输入 token 数 |
| `metadata.message_count` | Hermes 内部消息数量统计 |
| `metadata.request_char_count` | 请求字符数估算 |
| `metadata.tool_count` | 当前暴露给模型的工具数量 |

### 为什么 `api_request.input` 会是空的

`api_request` 记录的是“模型请求级事件”，不是“用户回合事件”。

当 Hook 没有拿到完整模型 payload 时，插件无法从 `messages` 中提取 user 内容，于是会出现：

```json
{
  "event": "api_request",
  "input": "",
  "messages": [],
  "request_message_count": 0
}
```

这不代表用户发了空消息，也不代表前端传参丢了。它只表示：Hermes 确实触发了一次内部模型调用，但当前插件版本没有记录这次模型请求正文。

真实用户输入应该看 `turn` 事件。

## 七、事件三：`turn`

`turn` 由 `post_llm_call` Hook 注入，表示一轮 Hermes 对话完成。

它是链路排查时最重要的事件，因为它记录了真实用户输入和最终输出。

示例：

```json
{
  "event": "turn",
  "history_message_count": 4,
  "input": "/skill example-skill 你好",
  "metadata": {},
  "model": "MiniMax-M2.7-highspeed",
  "output": "{\"status\":\"ok\",\"result\":\"已完成处理\"}",
  "platform": "api_server",
  "session_id": "2bc3c23fbd0b3be1fd710a63452ed58d",
  "timestamp": "2026-05-27T07:02:23+00:00"
}
```

主要字段：

| 字段 | 说明 |
|---|---|
| `event` | 固定为 `turn` |
| `input` | 本轮用户输入 |
| `output` | Hermes 最终返回内容 |
| `history_message_count` | 当前历史消息数量 |
| `model` | 当前模型 |
| `platform` | 调用平台 |
| `metadata` | Hook 附加信息 |

如果你想确认用户到底传了什么、技能最终输出了什么，优先看 `turn`。

## 八、事件四：`session_finalize`

`session_finalize` 由 `on_session_finalize` Hook 注入，表示会话结束。

示例：

```json
{
  "completed": true,
  "event": "session_finalize",
  "interrupted": false,
  "metadata": {},
  "model": "MiniMax-M2.7-highspeed",
  "platform": "api_server",
  "session_id": "session_51",
  "timestamp": "2026-05-25T07:05:10+00:00"
}
```

主要字段：

| 字段 | 说明 |
|---|---|
| `completed` | 会话是否正常完成 |
| `interrupted` | 是否被中断 |
| `metadata` | Hook 附加信息 |

当前排查中，最常看的通常是 `session_start`、`api_request` 和 `turn`。`session_finalize` 更适合做完整会话归档或统计。

## 九、一次真实日志怎么读

下面是一段典型日志：

```text
07:02:12 session_start
07:02:12 api_request input=""
07:02:17 api_request input=""
07:02:23 turn input="/skill example-skill 你好"
07:02:44 api_request input=""
07:02:53 api_request input=""
07:03:19 api_request input=""
07:03:39 turn input="/skill another-example 继续处理"
```

这代表：

1. Hermes 会话在 `07:02:12` 开始。
2. Hermes 内部先触发了两次模型调用。
3. 第一轮用户请求最终在 `07:02:23` 完成，输出了一个结构化结果。
4. 后续又进入另一个技能或处理阶段。
5. Hermes 内部触发三次模型调用。
6. 第二轮最终在 `07:03:39` 完成，输出了下一阶段结果。

中间多条 `api_request input=""` 是 Hermes 自己触发的内部模型请求，不是用户发送空消息。

## 十、写入逻辑：所有事件统一走 `_write_event`

所有 Hook 最终都会调用统一的写入函数：

```python
def _write_event(session_id: str, event: dict[str, Any]) -> None:
    if _env_bool("HERMES_SESSION_RECORDER_DISABLED"):
        return

    base = _recording_dir()
    path = base / f"{_safe_session_id(session_id)}.jsonl"
    line = json.dumps(event, ensure_ascii=False, sort_keys=True, default=repr)

    with _LOCK:
        base.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
```

这里有几个关键点：

- `HERMES_SESSION_RECORDER_DISABLED=1` 可以临时停用写入。
- `_recording_dir()` 支持自定义日志目录。
- `_safe_session_id()` 会清理不适合做文件名的字符。
- `ensure_ascii=False` 保证中文按原文写入。
- `_LOCK` 防止并发写文件时内容交叉。

## 十一、session_id 如何变成日志文件名

日志文件路径由 `session_id` 决定：

```python
path = base / f"{_safe_session_id(session_id)}.jsonl"
```

`_safe_session_id()` 主要做三件事：

1. 空值变成 `unknown-session`。
2. 非字母、数字、下划线、点、横线的字符替换成 `_`。
3. 文件名最长截断到 180 个字符。

例如：

```text
session/one -> session_one.jsonl
```

哈希形式的 session id 会保持原样：

```text
2bc3c23fbd0b3be1fd710a63452ed58d.jsonl
```

## 十二、当前版本的隐私边界

当前线上使用的是不记录 system prompt 的版本。

这意味着：

- 不会在 JSONL 里写入完整 `system_prompt`。
- `api_request` 更偏向模型请求元信息。
- 用户真实输入和最终输出仍然通过 `turn` 事件记录。
- 如果 Hook 没有拿到 messages，`api_request.messages` 会是空数组。

这个设计适合线上调试：既能确认 Hermes 内部是否发生了模型调用，又避免把过长、敏感、经常包含策略的 system prompt 写进日志。

如果后续需要“看请求正文但不看 system”，可以扩展成只记录非 system 消息：

```json
{
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."},
    {"role": "tool", "content": "..."}
  ]
}
```

同时跳过：

```json
{"role": "system", "content": "..."}
```

## 十三、新容器启用流程

新建或重建 Hermes 容器后，需要重新拷贝并启用插件。

单个容器：

```bash
cd ~/Desktop/hermes_skill
git pull

docker exec -it <hermes-container> sh -lc 'mkdir -p /opt/data/plugins/session-recorder'
docker cp ~/Desktop/hermes_skill/session-recorder/. <hermes-container>:/opt/data/plugins/session-recorder/
docker exec -it <hermes-container> sh -lc 'chown -R hermes:hermes /opt/data/plugins/session-recorder'
docker exec -it <hermes-container> sh -lc 'HERMES_HOME=/opt/data /opt/hermes/.venv/bin/hermes plugins enable session-recorder'
docker restart <hermes-container>
```

两个容器一起处理：

```bash
cd ~/Desktop/hermes_skill
git pull

for c in <hermes-container-a> <hermes-container-b>; do
  docker exec -it "$c" sh -lc 'mkdir -p /opt/data/plugins/session-recorder'
  docker cp ~/Desktop/hermes_skill/session-recorder/. "$c":/opt/data/plugins/session-recorder/
  docker exec -it "$c" sh -lc 'chown -R hermes:hermes /opt/data/plugins/session-recorder'
  docker exec -it "$c" sh -lc 'HERMES_HOME=/opt/data /opt/hermes/.venv/bin/hermes plugins enable session-recorder'
  docker restart "$c"
done
```

启用提示里的 “Takes effect on next session” 很重要。启用后需要新 session 才会生效，重启容器最直接。

## 十四、检查插件是否启用

检查配置：

```bash
docker exec -it <hermes-container> sh -lc 'grep -nA6 "^plugins:" /opt/data/config.yaml'
```

期望看到：

```yaml
plugins:
  enabled:
  - session-recorder
  disabled: []
```

检查插件文件：

```bash
docker exec -it <hermes-container> sh -lc 'ls -la /opt/data/plugins/session-recorder'
```

检查是否产生日志：

```bash
docker exec -it <hermes-container> sh -lc 'ls -lt /opt/data/plugins/session-recorder/session-records 2>/dev/null | head -20 || echo "no logs yet"'
```

如果 `session-records` 不存在，不一定是错误。它通常会在第一次成功写入事件时创建。

## 十五、常用查看命令

查看最新日志文件：

```bash
docker exec -it <hermes-container> sh -lc 'ls -lt /opt/data/plugins/session-recorder/session-records | head -20'
```

查看某个 session：

```bash
docker exec -it <hermes-container> sh -lc 'cat /opt/data/plugins/session-recorder/session-records/<session_id>.jsonl'
```

查看最后 80 行：

```bash
docker exec -it <hermes-container> sh -lc 'tail -n 80 /opt/data/plugins/session-recorder/session-records/<session_id>.jsonl'
```

两个容器一起看：

```bash
for c in <hermes-container-a> <hermes-container-b>; do
  echo "===== $c ====="
  docker exec -it "$c" sh -lc 'ls -lt /opt/data/plugins/session-recorder/session-records 2>/dev/null | head -20 || echo "no logs yet"'
done
```

搜索关键字：

```bash
docker exec -it <hermes-container> sh -lc 'grep -R -n "关键词" /opt/data/plugins/session-recorder/session-records || echo "not found"'
```

## 十六、常见问题

### 1. 为什么 `api_request.input` 是空？

因为它是模型请求级事件，不是用户回合事件。当前 Hook 没拿到请求正文时，`input` 就会是空字符串。真实用户输入看 `turn.input`。

### 2. 为什么一个用户请求对应多条 `api_request`？

因为 Hermes 内部可能多次调用模型。技能加载、上下文整理、工具执行、最终回答，都可能触发模型请求。

### 3. 为什么某个容器没日志，另一个容器有日志？

说明当前请求可能实际打到了另一个 Hermes 容器。先看外层服务的 Hermes 地址配置：

```bash
grep -n "HERMES_DEFAULT_PORT\|HERMES_BASE_URL" .env
```

再分别检查两个容器：

```bash
docker ps
```

### 4. 为什么插件目录存在，但没有 `session-records`？

目录只会在第一次写日志时创建。需要发起一次新请求，再查看。

### 5. 为什么启用了插件还是没有日志？

按顺序检查：

1. 容器是否是当前请求实际命中的容器。
2. `config.yaml` 里是否启用了 `session-recorder`。
3. 启用后是否重启或开启了新 session。
4. 插件目录权限是否归 `hermes:hermes`。
5. 当前请求是否真的进入 Hermes Agent，而不是停在外层业务服务。

## 十七、环境变量

插件支持几个环境变量：

| 环境变量 | 作用 |
|---|---|
| `HERMES_SESSION_RECORDER_DIR` | 自定义日志目录 |
| `HERMES_SESSION_RECORDER_DISABLED=1` | 临时停用日志写入 |
| `HERMES_SESSION_RECORDER_MAX_CHARS` | 限制单个文本字段最大长度 |
| `HERMES_SESSION_RECORDER_MARK_BOUNDARIES=0` | 不写 session start / finalize 边界事件 |

当前线上版本不记录 system prompt，因此不建议在博客里展示 system 相关日志样例。

## 十八、后续可增强点

当前插件已经能回答“请求有没有进入 Hermes”“触发了几次模型调用”“最终输出是什么”。后续还可以增强：

- 给 `api_request` 增加耗时字段。
- 给 `turn` 增加本轮总耗时。
- 只记录非 system messages，方便排查上下文传递。
- 增加 `error` 事件，记录异常栈摘要。
- 增加 `container_id` 或 `port` 字段，方便区分多个 Hermes 容器。
- 增加日志轮转，避免长期运行后文件过大。

## 总结

`session-recorder` 的关键不在于“多写几行日志”，而在于它挂到了 Hermes Agent 的生命周期 Hook 上。

外层 HTTP 日志看到的是接口请求。Session Recorder 看到的是 Agent 内部事件：

- 会话什么时候开始。
- 模型请求什么时候发生。
- 一轮用户请求最终输出了什么。
- 会话什么时候结束。

对复杂 Agent 工作流来说，这类日志比单纯的接口日志更接近问题现场。它让我们能把一次黑盒调用拆成可追踪的事件序列，也让“是不是 Hermes 自己触发的”“为什么 input 是空的”“到底命中了哪个容器”这些问题变得可以直接验证。
