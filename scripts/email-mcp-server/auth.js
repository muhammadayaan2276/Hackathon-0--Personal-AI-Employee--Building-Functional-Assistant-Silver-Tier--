#!/usr/bin/env node
/**
 * Gmail OAuth2 Authentication Script
 * 
 * Run this script to obtain your Gmail refresh token.
 * The token will be saved to .env file for the MCP server.
 */

import { google } from 'googleapis';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import readline from 'readline';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// =============================================================================
// Configuration
// =============================================================================

const CREDENTIALS_FILE = path.join(__dirname, '..', '..', 'gmail_credentials.json');
const ENV_FILE = path.join(__dirname, '.env');
const ENV_EXAMPLE_FILE = path.join(__dirname, '.env.example');

const SCOPES = [
  'https://www.googleapis.com/auth/gmail.send',
  'https://www.googleapis.com/auth/gmail.compose',
  'https://www.googleapis.com/auth/gmail.modify',
  'https://www.googleapis.com/auth/gmail.readonly',
];

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Create .env.example file
 */
function createEnvExample() {
  const content = `# Gmail MCP Server Configuration
# Copy this file to .env and fill in your values

# OAuth2 Credentials (from Google Cloud Console)
GMAIL_CLIENT_ID=your-client-id-here
GMAIL_CLIENT_SECRET=your-client-secret-here

# Refresh Token (obtained from running auth.js)
GMAIL_REFRESH_TOKEN=your-refresh-token-here

# Your Gmail Address
GMAIL_SENDER_EMAIL=your-email@gmail.com
`;
  fs.writeFileSync(ENV_EXAMPLE_FILE, content);
  console.log('✓ Created .env.example file');
}

/**
 * Load OAuth2 credentials
 */
function loadCredentials() {
  if (!fs.existsSync(CREDENTIALS_FILE)) {
    console.error('❌ Credentials file not found:', CREDENTIALS_FILE);
    console.error('\nPlease download gmail_credentials.json from Google Cloud Console:');
    console.error('1. Go to https://console.cloud.google.com');
    console.error('2. Enable Gmail API');
    console.error('3. Create OAuth 2.0 credentials (Desktop app)');
    console.error('4. Download and save as gmail_credentials.json in project root');
    process.exit(1);
  }

  const content = fs.readFileSync(CREDENTIALS_FILE, 'utf-8');
  return JSON.parse(content);
}

/**
 * Create readline interface for user input
 */
function createInterface(input, output) {
  return readline.createInterface({
    input,
    output,
    terminal: false,
  });
}

/**
 * Get authorization code from user
 */
function getAuthorizationCode(authUrl) {
  return new Promise((resolve) => {
    console.log('\n🔐 Authorize this app by visiting the following URL:');
    console.log(authUrl);
    console.log('\n📋 After authorizing, paste the authorization code here:\n');

    const rl = createInterface(process.stdin, process.stdout);
    rl.question('', (code) => {
      rl.close();
      resolve(code.trim());
    });
  });
}

/**
 * Save tokens to .env file
 */
function saveToEnv(clientId, clientSecret, refreshToken, email) {
  let content = '';

  // Read existing .env if it exists
  if (fs.existsSync(ENV_FILE)) {
    content = fs.readFileSync(ENV_FILE, 'utf-8') + '\n';
  }

  // Update or add new values
  const lines = content.split('\n').filter(line => line.trim());
  const updated = new Map();

  // Parse existing lines
  for (const line of lines) {
    const [key, ...valueParts] = line.split('=');
    if (key && valueParts.length) {
      updated.set(key.trim(), valueParts.join('=').trim());
    }
  }

  // Update Gmail values
  updated.set('GMAIL_CLIENT_ID', clientId);
  updated.set('GMAIL_CLIENT_SECRET', clientSecret);
  updated.set('GMAIL_REFRESH_TOKEN', refreshToken);
  updated.set('GMAIL_SENDER_EMAIL', email);

  // Write back
  const newContent = Array.from(updated.entries())
    .map(([key, value]) => `${key}=${value}`)
    .join('\n');

  fs.writeFileSync(ENV_FILE, newContent);
  console.log('✓ Saved credentials to .env file');
}

// =============================================================================
// Main Authentication Flow
// =============================================================================

async function authenticate() {
  console.log('📧 Gmail OAuth2 Authentication\n');
  console.log('='.repeat(50));

  // Load credentials
  const credentials = loadCredentials();
  const { client_id, client_secret, redirect_uris } = credentials.web || credentials.installed;

  if (!client_id || !client_secret) {
    console.error('❌ Invalid credentials file format');
    process.exit(1);
  }

  console.log('✓ Loaded OAuth2 credentials');

  // Create OAuth2 client
  const oauth2Client = new google.auth.OAuth2(
    client_id,
    client_secret,
    redirect_uris?.[0] || 'urn:ietf:wg:oauth:2.0:oob'
  );

  // Generate authorization URL
  const authUrl = oauth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: SCOPES,
    prompt: 'consent', // Force refresh token generation
  });

  // Get authorization code from user
  const code = await getAuthorizationCode(authUrl);

  if (!code) {
    console.error('❌ No authorization code provided');
    process.exit(1);
  }

  console.log('\n⏳ Exchanging code for tokens...');

  // Exchange code for tokens
  try {
    const { tokens } = await oauth2Client.getToken(code);
    
    if (!tokens.refresh_token) {
      console.error('❌ No refresh token received. Make sure to use prompt=consent.');
      console.error('\nTry again with a fresh authorization.');
      process.exit(1);
    }

    console.log('✓ Received refresh token');

    // Get user's email address
    oauth2Client.setCredentials(tokens);
    const oauth2 = google.oauth2({ version: 'v2', auth: oauth2Client });
    const userInfo = await oauth2.userinfo.get();
    
    console.log('✓ Authenticated as:', userInfo.data.email);

    // Save to .env
    saveToEnv(
      client_id,
      client_secret,
      tokens.refresh_token,
      userInfo.data.email
    );

    console.log('\n' + '='.repeat(50));
    console.log('✅ Authentication complete!');
    console.log('\n📝 Next steps:');
    console.log('   1. Verify .env file has correct values');
    console.log('   2. Run: npm start (to start MCP server)');
    console.log('   3. Test with: node test.js');

  } catch (error) {
    console.error('❌ Authentication failed:', error.message);
    process.exit(1);
  }
}

// =============================================================================
// Entry Point
// =============================================================================

// Create .env.example first
createEnvExample();

// Run authentication
authenticate().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
