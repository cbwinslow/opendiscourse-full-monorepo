#!/usr/bin/env node

// Basic example of using the Cipher MCP Server
// This demonstrates how other AI agents can integrate with Cipher

import { spawn } from 'child_process';
import { readFileSync } from 'fs';

// Configuration
const CIPHER_BINARY = '/home/foomanchu8008/Documents/Cline/MCP/cipher/dist/src/app/index.cjs';
const OPENROUTER_API_KEY = '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';

console.log('🚀 Cipher MCP Server - Basic Usage Example');
console.log('==========================================');

// Start the Cipher MCP server
const cipherProcess = spawn('node', [
  CIPHER_BINARY,
  '--mode', 'mcp'
], {
  env: {
    ...process.env,
    'MCP_SERVER_MODE': 'aggregator',
    'OPENROUTER_API_KEY': OPENROUTER_API_KEY
  },
  stdio: ['pipe', 'pipe', 'pipe']
});

console.log('✅ Cipher MCP Server started');
console.log('📋 Available tools:');
console.log('   • cipher_memory_search - Search stored knowledge');
console.log('   • cipher_extract_and_operate_memory - Manage memory operations');
console.log('   • cipher_store_reasoning_memory - Store reasoning traces');
console.log('   • cipher_extract_reasoning_steps - Extract reasoning steps');
console.log('   • cipher_evaluate_reasoning - Evaluate reasoning quality');
console.log('   • cipher_search_reasoning_patterns - Search reasoning patterns');
console.log('   • cipher_bash - Execute bash commands');

console.log('\n🔧 Example MCP Request (simulated):');
console.log(JSON.stringify({
  method: 'tools/list',
  jsonrpc: '2.0',
  id: 1
}, null, 2));

console.log('\n💡 Usage Tips:');
console.log('   1. Store important information with cipher_extract_and_operate_memory');
console.log('   2. Search your knowledge base with cipher_memory_search');
console.log('   3. Analyze reasoning with cipher_evaluate_reasoning');
console.log('   4. Execute commands with cipher_bash');

console.log('\n🌟 Next Steps:');
console.log('   • Integrate this server with your AI client');
console.log('   • Use the setup.sh script for easy configuration');
console.log('   • Check the README.md for detailed integration guides');

// Handle server output
cipherProcess.stdout.on('data', (data) => {
  console.log(`[CIPHER STDOUT]: ${data.toString().trim()}`);
});

cipherProcess.stderr.on('data', (data) => {
  console.log(`[CIPHER STDERR]: ${data.toString().trim()}`);
});

cipherProcess.on('close', (code) => {
  console.log(`\n🔚 Cipher MCP Server exited with code ${code}`);
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down Cipher MCP Server...');
  cipherProcess.kill('SIGINT');
  process.exit(0);
});

console.log('\n🔄 Server is running... Press Ctrl+C to stop');
