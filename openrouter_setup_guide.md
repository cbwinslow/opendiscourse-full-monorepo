# Cipher MCP Server - OpenRouter Setup Guide

## ✅ Configuration Complete

The Cipher MCP server has been successfully configured to use OpenRouter with the **Gemini 2.0 Flash** free model.

## 🚀 Next Steps to Complete Setup

### 1. Get Your OpenRouter API Key

1. Visit [OpenRouter.ai](https://openrouter.ai/keys)
2. Sign up for a free account
3. Create a new API key
4. Copy your API key

### 2. Update Configuration Files

#### Option A: Update Environment File
Edit `/home/foomanchu8008/Documents/Cline/MCP/cipher/.env`:
```bash
OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here
```

#### Option B: Update MCP Settings (Recommended)
Edit `/home/foomanchu8008/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`:
```json
{
  "github.com/campfirein/cipher": {
    "command": "node",
    "args": ["/home/foomanchu8008/Documents/Cline/MCP/cipher/dist/src/app/index.cjs", "--mode", "mcp"],
    "env": {
      "MCP_SERVER_MODE": "aggregator",
      "OPENROUTER_API_KEY": "sk-or-v1-your-actual-api-key-here"
    },
    "disabled": false,
    "autoApprove": []
  }
}
```

### 3. Restart Cline

After updating your API key, restart or reload Cline to pick up the new configuration.

## 🎯 Available Free Models

Your current configuration uses: **google/gemini-2.0-flash-exp:free**

### Alternative Free Models You Can Use:

1. **Gemini 2.0 Flash** (Current - Fast & Capable)
   ```
   google/gemini-2.0-flash-exp:free
   ```

2. **Llama 3.2 1B** (Lightweight)
   ```
   meta-llama/llama-3.2-1b-instruct:free
   ```

3. **Qwen 2.5 0.5B** (Efficient)
   ```
   qwen/qwen-2.5-0.5b-instruct:free
   ```

4. **Phi-3 Mini** (Optimized)
   ```
   microsoft/phi-3-mini-128k-instruct:free
   ```

### To Switch Models:

Edit `/home/foomanchu8008/Documents/Cline/MCP/cipher/memAgent/cipher.yml`:
```yaml
llm:
  provider: openrouter
  model: meta-llama/llama-3.2-1b-instruct:free  # Change this line
  apiKey: $OPENROUTER_API_KEY
  maxIterations: 50
```

## 🧪 Test Your Setup

Once configured, the server will provide these 7 MCP tools:

1. **cipher_memory_search** - Search stored knowledge
2. **cipher_extract_and_operate_memory** - Extract and manage memory
3. **cipher_store_reasoning_memory** - Store reasoning traces
4. **cipher_extract_reasoning_steps** - Extract reasoning steps
5. **cipher_evaluate_reasoning** - Evaluate reasoning quality
6. **cipher_search_reasoning_patterns** - Search reasoning patterns
7. **cipher_bash** - Execute bash commands

## 📁 Key Files

- **Configuration**: `/home/foomanchu8008/Documents/Cline/MCP/cipher/memAgent/cipher.yml`
- **Environment**: `/home/foomanchu8008/Documents/Cline/MCP/cipher/.env`
- **MCP Settings**: `/home/foomanchu8008/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
- **Binary**: `/home/foomanchu8008/Documents/Cline/MCP/cipher/dist/src/app/index.cjs`

## 💡 Benefits of OpenRouter Free Models

- **No cost** for usage
- **Fast inference** (especially Gemini 2.0 Flash)
- **Reliable uptime**
- **Easy switching** between models
- **No complex setup** required

Your Cipher MCP server is now ready to use with a powerful, free AI model!
