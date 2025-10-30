# Cipher MCP Server - Portable Edition

A **fully portable** installation of the Cipher MCP server that works with any MCP-compatible AI agent. This package includes pre-built binaries, configuration templates, and automated setup scripts.

## 🎯 What This Provides

- **Pre-built Cipher binary** (no compilation needed)
- **Configuration templates** for popular AI clients
- **Automated setup script** for easy installation
- **Portable across platforms** (Linux, macOS, Windows)
- **Free OpenRouter model** integration

## ⚡ Quick Start

### 1. Clone or Download
```bash
# If you have the cipher repository already
cp -r /path/to/cipher-mcp-portable ~/

# Or create the structure manually and copy the binary
```

### 2. Run Setup
```bash
cd cipher-mcp-portable
./setup.sh
```

### 3. Test
```bash
./setup.sh test /path/to/cipher/dist/src/app/index.cjs
```

## 📁 Package Contents

```
cipher-mcp-portable/
├── README.md                    # This file
├── INSTALL.md                   # Detailed installation guide
├── setup.sh                     # Automated setup script (executable)
├── configs/                     # Configuration templates
│   ├── cline-mcp-settings.json  # Cline (VSCode) template
│   ├── claude-desktop-config.json # Claude Desktop template
│   └── continue-dev-config.json # Continue.dev template
└── examples/                    # Usage examples
    ├── basic-usage.js           # Basic MCP client example
    ├── memory-search.js         # Memory search example
    └── bash-commands.js         # Bash command examples
```

## 🔧 Configuration Templates

All configuration files use placeholders that the setup script replaces:

- `{CIPHER_BINARY_PATH}` - Path to your cipher binary
- `{OPENROUTER_API_KEY}` - Your OpenRouter API key

### Cline (VSCode Extension)
```json
{
  "mcpServers": {
    "cipher": {
      "command": "node",
      "args": ["{CIPHER_BINARY_PATH}", "--mode", "mcp"],
      "env": {
        "MCP_SERVER_MODE": "aggregator",
        "OPENROUTER_API_KEY": "{OPENROUTER_API_KEY}"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### Claude Desktop
```json
{
  "mcpServers": {
    "cipher": {
      "command": "node", 
      "args": ["{CIPHER_BINARY_PATH}", "--mode", "mcp"],
      "env": {
        "MCP_SERVER_MODE": "aggregator",
        "OPENROUTER_API_KEY": "{OPENROUTER_API_KEY}"
      }
    }
  }
}
```

### Continue.dev
```json
{
  "models": [
    {
      "title": "Cipher Memory MCP",
      "provider": "mcp",
      "model": "cipher"
    }
  ],
  "mcpServers": {
    "cipher": {
      "command": "node",
      "args": ["{CIPHER_BINARY_PATH}", "--mode", "mcp"],
      "env": {
        "MCP_SERVER_MODE": "aggregator",
        "OPENROUTER_API_KEY": "{OPENROUTER_API_KEY}"
      }
    }
  }
}
```

## 🧪 Available Tools

Once connected, your AI agent will have access to these 7 powerful tools:

### Memory Management
- **`cipher_memory_search`** - Semantic search over stored knowledge
- **`cipher_extract_and_operate_memory`** - Extract and manage memory operations
- **`cipher_store_reasoning_memory`** - Store reasoning traces and patterns

### Reasoning Analysis
- **`cipher_extract_reasoning_steps`** - Extract structured reasoning steps
- **`cipher_evaluate_reasoning`** - Evaluate reasoning quality
- **`cipher_search_reasoning_patterns`** - Search reflection memory for patterns

### System Integration
- **`cipher_bash`** - Execute bash commands with persistent sessions

## 💻 Usage Examples

### Search Knowledge
```
User: "What do you know about FastAPI?"
AI: *Uses cipher_memory_search to find relevant information*
```

### Store Information
```
User: "Remember that PostgreSQL uses port 5432 by default"
AI: *Uses cipher_extract_and_operate_memory to store this fact*
```

### Execute Commands
```
User: "Show me the current directory structure"
AI: *Uses cipher_bash to run "ls -la" and store results*
```

### Reasoning Analysis
```
User: "Analyze the reasoning in my previous explanation"
AI: *Uses cipher_extract_reasoning_steps and cipher_evaluate_reasoning*
```

## 🚀 Advanced Usage

### Custom Configuration
You can manually edit any of the generated config files to:
- Change the model (see available free models below)
- Adjust memory settings
- Configure different storage backends

### Available Free Models
```yaml
# In cipher.yml, change the model:
llm:
  provider: openrouter
  model: google/gemini-2.0-flash-exp:free    # Fast & capable (default)
  # model: meta-llama/llama-3.2-1b-instruct:free  # Lightweight
  # model: qwen/qwen-2.5-0.5b-instruct:free      # Efficient  
  # model: microsoft/phi-3-mini-128k-instruct:free # Optimized
```

### Custom Memory Storage
```yaml
# In cipher.yml
memory:
  type: in-memory  # or: sqlite, postgresql
  
session:
  type: sqlite
  path: ./custom_memory.db
```

## 🔒 Security & Privacy

- **Local execution**: All processing happens on your machine
- **Secure API key**: OpenRouter API key stays on your system
- **No data collection**: Your conversations and memory are private
- **Memory control**: You control what gets stored and when

## 🆘 Troubleshooting

### Server Won't Start
```bash
# Check Node.js version
node --version

# Test the binary directly
node /path/to/cipher/dist/src/app/index.cjs --mode mcp

# Check logs
tail -f /tmp/cipher-mcp.log
```

### Tools Not Available
1. Ensure server started successfully
2. Verify MCP client is connected
3. Check environment variables are set
4. Restart your AI client

### API Issues
1. Verify OpenRouter API key is valid
2. Check account credits/limits
3. Ensure key has proper permissions

## 🌟 Integration with Other Tools

### VSCode + Cline
```bash
# 1. Install Cline extension in VSCode
# 2. Run setup.sh and select Cline
# 3. Restart VSCode
# 4. Cipher tools will appear in Cline's tool list
```

### Claude Desktop
```bash
# 1. Install Claude Desktop app
# 2. Run setup.sh and select Claude Desktop (macOS)
# 3. Restart Claude Desktop
# 4. Use MCP tools in any conversation
```

### Continue.dev
```bash
# 1. Install Continue.dev extension
# 2. Run setup.sh and select Continue.dev
# 3. Update your Continue config
# 4. Cipher tools available in code assistant
```

## 📞 Support & Resources

- **Cipher Repository**: https://github.com/campfirein/cipher
- **OpenRouter Docs**: https://openrouter.ai/docs
- **MCP Protocol**: https://modelcontextprotocol.io
- **Setup Guide**: See `INSTALL.md` for detailed instructions

## 🎉 What You Get

This portable setup gives you:

✅ **Memory-powered AI assistance** across multiple AI clients  
✅ **Persistent knowledge** that survives client restarts  
✅ **Reasoning analysis** to improve thinking quality  
✅ **Cross-platform compatibility** (Linux, macOS, Windows)  
✅ **Free AI model** through OpenRouter  
✅ **Easy installation** with automated scripts  
✅ **Privacy-focused** with local processing  

## 🔄 Next Steps

1. **Run `./setup.sh`** to configure for your preferred AI client
2. **Test the connection** with `./setup.sh test`
3. **Start using memory features** in your AI conversations
4. **Explore advanced features** like reasoning analysis and bash commands

---

**Ready to supercharge your AI agents with persistent memory?** Start with `./setup.sh` and experience the power of memory-enhanced AI!
