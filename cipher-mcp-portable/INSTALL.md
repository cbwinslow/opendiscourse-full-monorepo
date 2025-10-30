# Cipher MCP Server - Portable Installation

## 🚀 Quick Setup for Any AI Agent

This package provides a portable installation of the Cipher MCP server that can be used by any MCP-compatible AI agent.

## 📦 What's Included

- **Pre-built Cipher MCP Server** (no compilation required)
- **Configuration templates** for different AI clients
- **Installation scripts** for easy setup
- **Portable binary** that works anywhere

## 🔧 Installation Methods

### Method 1: Use Existing Setup (Recommended)

If you already have the cipher repository set up:

```bash
# Copy the server configuration
cp /home/foomanchu8008/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json ./my-mcp-config.json

# Use the pre-built binary
node /home/foomanchu8008/Documents/Cline/MCP/cipher/dist/src/app/index.cjs --mode mcp
```

### Method 2: Standalone Setup

1. **Copy the cipher repository**:
   ```bash
   git clone https://github.com/campfirein/cipher.git
   cd cipher
   ```

2. **Install dependencies** (if not already built):
   ```bash
   npm install -g pnpm
   pnpm install
   pnpm run build:no-ui
   ```

3. **Use the binary**:
   ```bash
   node dist/src/app/index.cjs --mode mcp
   ```

## 🎯 AI Client Configurations

### Cline (VSCode Extension)

Add to your `cline_mcp_settings.json`:
```json
{
  "mcpServers": {
    "cipher": {
      "command": "node",
      "args": ["/path/to/cipher/dist/src/app/index.cjs", "--mode", "mcp"],
      "env": {
        "MCP_SERVER_MODE": "aggregator",
        "OPENROUTER_API_KEY": "your-api-key-here"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "cipher": {
      "command": "node",
      "args": ["/path/to/cipher/dist/src/app/index.cjs", "--mode", "mcp"],
      "env": {
        "MCP_SERVER_MODE": "aggregator", 
        "OPENROUTER_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Continue (Continue.dev)

Add to your MCP configuration:
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
      "args": ["/path/to/cipher/dist/src/app/index.cjs", "--mode", "mcp"],
      "env": {
        "MCP_SERVER_MODE": "aggregator",
        "OPENROUTER_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## 🧪 Available Tools

Once connected, the following tools are available:

1. **cipher_memory_search** - Search stored knowledge and memories
2. **cipher_extract_and_operate_memory** - Extract and manage memory operations
3. **cipher_store_reasoning_memory** - Store reasoning traces and patterns
4. **cipher_extract_reasoning_steps** - Extract structured reasoning steps
5. **cipher_evaluate_reasoning** - Evaluate reasoning quality and provide feedback
6. **cipher_search_reasoning_patterns** - Search reflection memory for reasoning patterns
7. **cipher_bash** - Execute bash commands with persistent sessions

## ⚙️ Environment Variables

Required environment variables:
- `OPENROUTER_API_KEY` - Your OpenRouter API key
- `MCP_SERVER_MODE` - Set to "aggregator" for MCP mode

Optional environment variables:
- `MEMORY_TYPE` - Type of memory storage (default: in-memory)
- `VECTOR_STORE_TYPE` - Vector storage type (default: in-memory)
- `LOG_LEVEL` - Logging level (default: info)

## 🔒 Security Notes

- Keep your OpenRouter API key secure
- The server runs locally on your machine
- No data is sent to external services except OpenRouter
- All memory storage is local unless configured otherwise

## 🆘 Troubleshooting

### Server Won't Start
```bash
# Check if Node.js is available
node --version

# Check if the binary exists
ls -la /path/to/cipher/dist/src/app/index.cjs

# Check logs
tail -f /tmp/cipher-mcp.log
```

### Tools Not Available
- Ensure the server started successfully
- Check that the MCP client is connected to the server
- Verify environment variables are set correctly

### API Key Issues
- Verify your OpenRouter API key is valid
- Check that the key has not expired
- Ensure the key has sufficient credits

## 🌟 Integration Examples

### Search Memory
```
Use cipher_memory_search to find information about "Python web frameworks"
```

### Store Information
```
Use cipher_extract_and_operate_memory to store the fact that "FastAPI is a modern Python web framework"
```

### Execute Commands
```
Use cipher_bash to run "ls -la" and store the results in memory
```

## 📞 Support

For issues with:
- **Cipher MCP Server**: Check the [GitHub repository](https://github.com/campfirein/cipher)
- **OpenRouter API**: Visit [OpenRouter documentation](https://openrouter.ai/docs)
- **MCP Protocol**: See the [MCP specification](https://modelcontextprotocol.io)
