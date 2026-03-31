#!/usr/bin/env node
/**
 * Test Script for Email MCP Server
 * 
 * Tests all available tools:
 * - email_list
 * - email_read
 * - email_draft
 * - email_send
 * - email_mark_read
 */

import { google } from 'googleapis';
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import readline from 'readline';

const __dirname = dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: join(__dirname, '.env') });

// =============================================================================
// Configuration
// =============================================================================

const CONFIG = {
  clientId: process.env.GMAIL_CLIENT_ID,
  clientSecret: process.env.GMAIL_CLIENT_SECRET,
  refreshToken: process.env.GMAIL_REFRESH_TOKEN,
  senderEmail: process.env.GMAIL_SENDER_EMAIL,
};

// Validate configuration
const required = ['GMAIL_CLIENT_ID', 'GMAIL_CLIENT_SECRET', 'GMAIL_REFRESH_TOKEN', 'GMAIL_SENDER_EMAIL'];
const missing = required.filter(key => !CONFIG[key.toLowerCase().replace('gmail_', 'GMAIL_')]);

if (missing.length > 0) {
  console.error('❌ Missing configuration:', missing.join(', '));
  console.error('\nRun "npm run auth" first to set up credentials');
  process.exit(1);
}

// =============================================================================
// Gmail Setup
// =============================================================================

const oauth2Client = new google.auth.OAuth2(
  CONFIG.clientId,
  CONFIG.clientSecret,
  'urn:ietf:wg:oauth:2.0:oob'
);

oauth2Client.setCredentials({
  refresh_token: CONFIG.refreshToken,
});

const gmail = google.gmail({ version: 'v1', auth: oauth2Client });

// =============================================================================
// Test Functions
// =============================================================================

function createInterface(input, output) {
  return readline.createInterface({ input, output, terminal: false });
}

async function pause(message = 'Press Enter to continue...') {
  const rl = createInterface(process.stdin, process.stdout);
  return new Promise(resolve => {
    rl.question(message, () => {
      rl.close();
      resolve();
    });
  });
}

/**
 * Test: List recent emails
 */
async function testListEmails() {
  console.log('\n📋 Test: List Recent Emails');
  console.log('='.repeat(50));

  try {
    const response = await gmail.users.messages.list({
      userId: 'me',
      maxResults: 5,
      q: 'is:inbox',
    });

    const messages = response.data.messages || [];
    console.log(`\n✓ Found ${messages.length} emails\n`);

    for (const msg of messages.slice(0, 3)) {
      const full = await gmail.users.messages.get({
        userId: 'me',
        id: msg.id,
        format: 'metadata',
        metadataHeaders: ['From', 'Subject', 'Date'],
      });

      const headers = full.data.payload?.headers || [];
      const getHeader = (name) => headers.find(h => h.name === name)?.value || '';

      console.log(`  ID: ${msg.id}`);
      console.log(`  From: ${getHeader('From')}`);
      console.log(`  Subject: ${getHeader('Subject')}`);
      console.log(`  Date: ${getHeader('Date')}`);
      console.log('  ---');
    }

    return messages.length > 0 ? messages[0].id : null;
  } catch (error) {
    console.error('❌ Error:', error.message);
    return null;
  }
}

/**
 * Test: Read an email
 */
async function testReadEmail(messageId) {
  if (!messageId) {
    console.log('\n⊘ Skipping: No message ID available');
    return;
  }

  console.log('\n📖 Test: Read Email');
  console.log('='.repeat(50));

  try {
    const response = await gmail.users.messages.get({
      userId: 'me',
      id: messageId,
      format: 'full',
    });

    const headers = response.data.payload?.headers || [];
    const getHeader = (name) => headers.find(h => h.name === name)?.value || '';

    console.log(`\n✓ Email retrieved`);
    console.log(`  From: ${getHeader('From')}`);
    console.log(`  To: ${getHeader('To')}`);
    console.log(`  Subject: ${getHeader('Subject')}`);

    // Decode body
    let body = '';
    if (response.data.payload?.body?.data) {
      body = Buffer.from(response.data.payload.body.data, 'base64').toString('utf-8');
    }

    console.log(`\n  Body preview: ${body.substring(0, 200)}...`);
  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

/**
 * Test: Create a draft email
 */
async function testCreateDraft() {
  console.log('\n📝 Test: Create Draft Email');
  console.log('='.repeat(50));

  const testEmail = {
    to: CONFIG.senderEmail, // Send to self for testing
    subject: `Test Draft - ${new Date().toISOString()}`,
    body: 'This is a test draft email created by the Email MCP Server.\n\nYou can safely delete this email.',
  };

  try {
    // Create email message
    const message = [
      `From: ${CONFIG.senderEmail}`,
      `To: ${testEmail.to}`,
      `Subject: ${testEmail.subject}`,
      'MIME-Version: 1.0',
      'Content-Type: text/plain; charset="UTF-8"',
      '',
      testEmail.body,
    ].join('\r\n');

    const encoded = Buffer.from(message).toString('base64').replace(/\+/g, '-').replace(/\//g, '_');

    const response = await gmail.users.drafts.create({
      userId: 'me',
      requestBody: {
        message: { raw: encoded },
      },
    });

    console.log(`\n✓ Draft created successfully`);
    console.log(`  Draft ID: ${response.data.id}`);
    console.log(`  Subject: ${testEmail.subject}`);
    console.log(`\n  Check your Gmail drafts folder to verify`);

    return response.data.id;
  } catch (error) {
    console.error('❌ Error:', error.message);
    return null;
  }
}

/**
 * Test: Send an email
 */
async function testSendEmail() {
  console.log('\n📤 Test: Send Email');
  console.log('='.repeat(50));

  const testEmail = {
    to: CONFIG.senderEmail, // Send to self for testing
    subject: `Test Sent Email - ${new Date().toISOString()}`,
    body: 'This is a test email sent by the Email MCP Server.\n\nYou can safely delete this email.',
  };

  console.log(`\n  To: ${testEmail.to}`);
  console.log(`  Subject: ${testEmail.subject}`);
  console.log('\n  ⚠️  This will SEND a real email!');

  const rl = createInterface(process.stdin, process.stdout);
  await new Promise(resolve => {
    rl.question('  Continue? (yes/no): ', (answer) => {
      rl.close();
      if (answer.toLowerCase() !== 'yes') {
        console.log('  ⊘ Skipped');
        resolve('skip');
      } else {
        resolve('send');
      }
    });
  });

  try {
    // Create email message
    const message = [
      `From: ${CONFIG.senderEmail}`,
      `To: ${testEmail.to}`,
      `Subject: ${testEmail.subject}`,
      'MIME-Version: 1.0',
      'Content-Type: text/plain; charset="UTF-8"',
      '',
      testEmail.body,
    ].join('\r\n');

    const encoded = Buffer.from(message).toString('base64').replace(/\+/g, '-').replace(/\//g, '_');

    const response = await gmail.users.messages.send({
      userId: 'me',
      requestBody: {
        raw: encoded,
      },
    });

    console.log(`\n✓ Email sent successfully`);
    console.log(`  Message ID: ${response.data.id}`);
    console.log(`  Thread ID: ${response.data.threadId}`);
    console.log(`\n  Check your inbox to verify`);

    return { id: response.data.id, threadId: response.data.threadId };
  } catch (error) {
    console.error('❌ Error:', error.message);
    return null;
  }
}

/**
 * Test: Mark email as read
 */
async function testMarkRead(threadId) {
  if (!threadId) {
    console.log('\n⊘ Skipping: No thread ID available');
    return;
  }

  console.log('\n✓ Test: Mark Email as Read');
  console.log('='.repeat(50));

  try {
    await gmail.users.messages.modify({
      userId: 'me',
      id: threadId,
      requestBody: {
        removeLabelIds: ['UNREAD'],
      },
    });

    console.log(`\n✓ Email marked as read`);
    console.log(`  Thread ID: ${threadId}`);
  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

// =============================================================================
// Main Test Runner
// =============================================================================

async function runTests() {
  console.log('\n🧪 Email MCP Server - Test Suite');
  console.log('='.repeat(50));
  console.log(`\n  Authenticated as: ${CONFIG.senderEmail}`);
  console.log(`  Time: ${new Date().toISOString()}`);

  let messageId = null;
  let threadId = null;

  // Test 1: List emails
  messageId = await testListEmails();
  await pause();

  // Test 2: Read email
  await testReadEmail(messageId);
  await pause();

  // Test 3: Create draft
  await testCreateDraft();
  await pause();

  // Test 4: Send email
  const sentResult = await testSendEmail();
  if (sentResult) {
    threadId = sentResult.threadId;
  }
  await pause();

  // Test 5: Mark as read
  await testMarkRead(threadId);

  console.log('\n' + '='.repeat(50));
  console.log('✅ All tests completed!');
  console.log('='.repeat(50));
}

// =============================================================================
// Entry Point
// =============================================================================

runTests().catch((error) => {
  console.error('\n❌ Fatal error:', error);
  process.exit(1);
});
