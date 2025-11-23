# 迁移说明 - 从 OpenRouter 到原生 API

本文档记录了项目从使用 OpenRouter 聚合服务迁移到直接调用各提供商原生 API 的变更。

## 变更概述

**迁移日期**: 2025-11-23
**原因**: 降低成本，避免 OpenRouter 的 markup 费用，直接使用用户已有的 API key

## 主要变更

### 1. 移除的功能
- ❌ 移除 OpenRouter API 集成
- ❌ 移除 Grok (xAI) 模型（用户不需要）

### 2. 新增的功能
- ✅ 直接调用 OpenAI API
- ✅ 直接调用 Anthropic API
- ✅ 直接调用 Google Gemini API
- ✅ 支持多个独立 API key 配置
- ✅ 自动消息格式转换（适配各提供商的格式差异）

## 文件变更清单

### 修改的文件

#### 1. `backend/config.py`
**变更内容：**
- 移除 `OPENROUTER_API_KEY` 和 `OPENROUTER_API_URL`
- 新增 `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`
- 新增各提供商的 API URL 配置
- 移除 Grok 模型，更新模型列表为真实可用的模型

**之前：**
```python
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
COUNCIL_MODELS = [
    "openai/gpt-5.1",
    "google/gemini-3-pro-preview",
    "anthropic/claude-sonnet-4.5",
    "x-ai/grok-4",
]
```

**之后：**
```python
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

COUNCIL_MODELS = [
    "openai/gpt-4o",
    "google/gemini-2.0-flash-exp",
    "anthropic/claude-sonnet-4.5",
]
```

#### 2. `backend/openrouter.py`
**变更内容：**
- 完全重写文件逻辑
- 新增 `query_openai()` - OpenAI API 客户端
- 新增 `query_anthropic()` - Anthropic API 客户端（包含消息格式转换）
- 新增 `query_google()` - Google Gemini API 客户端（包含消息格式转换）
- 修改 `query_model()` - 添加路由逻辑，根据 provider 前缀调用对应客户端
- 保持 `query_models_parallel()` 接口不变，确保向后兼容

**关键实现细节：**

1. **Anthropic API 格式转换**：
   - 提取 system message 到独立字段
   - 移除 system role 的消息
   - 添加 `max_tokens` 参数（必需）

2. **Google Gemini API 格式转换**：
   - 将 system message 转换为 `systemInstruction`
   - 将 `assistant` role 转换为 `model` role
   - 使用 `parts` 数组包装消息内容
   - URL 中包含 API key（不在 header）

3. **错误处理**：
   - 每个 API 客户端独立捕获异常
   - 失败时返回 None，不中断其他模型查询
   - 打印详细错误信息便于调试

#### 3. `README.md`
**变更内容：**
- 更新项目描述，移除 OpenRouter 引用
- 更新 API key 配置说明（从单个改为三个）
- 更新模型配置示例
- 添加模型标识符格式说明
- 更新技术栈描述
- 添加 macOS 部署指南链接

#### 4. `DEPLOYMENT_MAC.md`
**变更内容：**
- 更新系统要求（三个 API key）
- 更新 API key 获取步骤（分别说明三个提供商）
- 更新模型配置示例和说明
- 更新故障排查部分（多提供商错误处理）
- 更新项目结构说明
- 更新性能优化建议（模型速度对比）
- 更新安全注意事项（多提供商账单检查）

### 新增的文件

#### 1. `.env.example`
**内容：**
```bash
# OpenAI API Key
OPENAI_API_KEY=sk-...

# Anthropic API Key
ANTHROPIC_API_KEY=sk-ant-...

# Google AI API Key (for Gemini)
GOOGLE_API_KEY=AIza...
```

**用途：**
- 作为用户配置模板
- 说明所需的环境变量
- 包含获取 API key 的链接

#### 2. `MIGRATION_NOTES.md`（本文档）
**用途：**
- 记录迁移过程
- 说明技术决策
- 提供给未来开发者参考

## API 格式差异处理

### OpenAI API
- ✅ 使用标准的 messages 格式
- ✅ 支持 system/user/assistant roles
- ✅ 简单的 Authorization header
- ✅ 不需要额外转换

### Anthropic API
- ⚠️ system message 需要单独提取到 `system` 字段
- ⚠️ 必须包含 `max_tokens` 参数
- ⚠️ 使用 `x-api-key` header
- ⚠️ 响应格式：`data['content'][0]['text']`

### Google Gemini API
- ⚠️ system message 转换为 `systemInstruction`
- ⚠️ assistant role 改为 model role
- ⚠️ 内容需要用 `parts` 数组包装
- ⚠️ API key 在 URL query string 中
- ⚠️ 响应格式：`data['candidates'][0]['content']['parts'][0]['text']`

## 成本影响

### 之前（使用 OpenRouter）
- OpenRouter markup: ~5-20%
- 需要在 OpenRouter 充值
- 统一计费

### 之后（使用原生 API）
- ✅ 无 markup，按原厂价格计费
- ✅ 直接使用已有的 API key
- ✅ 各提供商独立计费
- ✅ 长期成本更低

## 向后兼容性

### 保持不变的接口
- ✅ `query_model(model, messages, timeout)` - 函数签名不变
- ✅ `query_models_parallel(models, messages)` - 函数签名不变
- ✅ 返回格式：`{'content': str, 'reasoning_details': Optional[str]}`
- ✅ `backend/council.py` - 无需修改
- ✅ `backend/main.py` - 无需修改
- ✅ 前端代码 - 无需修改

### 需要用户操作的变更
- ⚠️ 必须更新 `.env` 文件（从 1 个 key 改为 3 个 keys）
- ⚠️ 可选：更新 `backend/config.py` 中的模型标识符

## 测试建议

部署后建议测试以下场景：

1. **基本功能测试**：
   - [ ] 提交一个简单问题，确认三个阶段都正常工作
   - [ ] 检查 Stage 1 是否显示所有模型的响应
   - [ ] 检查 Stage 2 是否显示互评和排名
   - [ ] 检查 Stage 3 是否显示最终答案

2. **API 连接测试**：
   - [ ] OpenAI API 是否正常响应
   - [ ] Anthropic API 是否正常响应
   - [ ] Google Gemini API 是否正常响应

3. **错误处理测试**：
   - [ ] 删除某个 API key，确认其他模型仍能工作
   - [ ] 使用错误的 API key，查看错误信息
   - [ ] 网络中断时的表现

4. **消息格式测试**：
   - [ ] 测试包含 system message 的对话
   - [ ] 测试多轮对话
   - [ ] 测试长文本输入

## 已知限制

1. **Google Gemini API**：
   - 免费额度有限制
   - 某些高级功能可能不可用

2. **Anthropic API**：
   - 需要显式设置 `max_tokens`（已在代码中设为 4096）
   - 某些模型可能需要更高的限额

3. **模型可用性**：
   - 各提供商的模型名称可能变化
   - 需要参考官方文档确认最新模型名

## 故障排查

### 常见问题

**问题 1: "Error querying OpenAI model"**
- 检查 `OPENAI_API_KEY` 是否正确
- 检查账户余额
- 检查模型名称是否正确

**问题 2: "Error querying Anthropic model"**
- 检查 `ANTHROPIC_API_KEY` 是否正确
- 检查是否有足够的配额
- Anthropic API 可能有使用限制

**问题 3: "Error querying Google model"**
- 检查 `GOOGLE_API_KEY` 是否正确
- 检查 API 是否已启用
- 检查模型名称格式

**问题 4: 所有模型都失败**
- 检查网络连接
- 检查 `.env` 文件是否在正确位置
- 检查环境变量是否加载（重启后端）

## 回滚方案

如果需要回滚到 OpenRouter：

1. 恢复 `backend/config.py` 的旧版本
2. 恢复 `backend/openrouter.py` 的旧版本
3. 更新 `.env` 文件为 `OPENROUTER_API_KEY=...`
4. 重启后端服务

或者使用 git：
```bash
git revert <commit-hash>
```

## 未来改进建议

1. **添加更多提供商**：
   - Cohere
   - Mistral AI
   - Together AI

2. **优化错误处理**：
   - 添加重试机制
   - 更详细的错误日志
   - 用户友好的错误提示

3. **配置增强**：
   - UI 配置界面（不需要编辑代码）
   - 动态添加/删除模型
   - 模型参数自定义（temperature, max_tokens 等）

4. **性能优化**：
   - 缓存常见问题的答案
   - 流式响应支持
   - 并发限制和速率控制

## 总结

本次迁移成功实现了：
- ✅ 移除 OpenRouter 依赖，降低成本
- ✅ 移除不需要的 Grok 模型
- ✅ 支持直接使用原生 API
- ✅ 保持代码的向后兼容性
- ✅ 提供详细的文档和配置说明

用户现在可以：
- 💰 使用自己的 API key，无需额外付费
- 🎯 灵活配置所需的模型
- 🔧 更容易调试和定制
- 📊 独立跟踪各提供商的使用情况

---

**维护者注意**: 请在修改配置或添加新模型时更新本文档。
