#!/usr/bin/env node
/**
 * Email MCP Server for Personal AI Employee (Silver Tier)
 * 
 * Provides Gmail integration via Model Context Protocol (MCP)
 * 
 * Tools available:
 * - email_send: Send an email immediately
 * - email_draft: Create a draft email
 * - email_mark_read: Mark email(s) as read
 * - email_list: List recent emails
 * - email_read: Read a specific email
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { google } from 'googleapis';
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import fs from 'fs';

// Load environment variables
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
const missingConfig = [];
if (!CONFIG.clientId) missingConfig.push('GMAIL_CLIENT_ID');
if (!CONFIG.clientSecret) missingConfig.push('GMAIL_CLIENT_SECRET');
if (!CONFIG.refreshToken) missingConfig.push('GMAIL_REFRESH_TOKEN');
if (!CONFIG.senderEmail) missingConfig.push('GMAIL_SENDER_EMAIL');

if (missingConfig.length > 0) {
  console.error(`Missing required configuration: ${missingConfig.join(', ')}`);
  console.error('Please set these environment variables or create a .env file');
  process.exit(1);
}

// =============================================================================
// Gmail API Setup
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
// Helper Functions
// =============================================================================

/**
 * Encode email content to base64url format
 */
function encodeBase64Url(str) {
  return Buffer.from(str)
    .toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
}

/**
 * Decode base64url content
 */
function decodeBase64Url(str) {
  let base64 = str.replace(/-/g, '+').replace(/_/g, '/');
  while (base64.length % 4) {
    base64 += '=';
  }
  return Buffer.from(base64, 'base64').toString('utf-8');
}

/**
 * Create RFC 2822 formatted email
 */
function createEmailMessage({ to, subject, body, inReplyTo, references }) {
  let message = [
    `From: ${CONFIG.senderEmail}`,
    `To: ${to}`,
    `Subject: ${subject}`,
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset="UTF-8"',
    'Content-Transfer-Encoding: 7bit',
  ];

  if (inReplyTo) {
    message.push(`In-Reply-To: ${inReplyTo}`);
  }

  if (references) {
    message.push(`References: ${references}`);
  }

  message.push('', body);

  return message.join('\r\n');
}

/**
 * Log activity to the vault logs
 */
function logActivity(action, details) {
  const vaultDir = join(__dirname, '..', '..', 'AI_Employee_Vault');
  const logsDir = join(vaultDir, 'Logs');
  
  // Ensure logs directory exists
  if (!fs.existsSync(logsDir)) {
    fs.mkdirSync(logsDir, { recursive: true });
  }

  const logFile = join(logsDir, `email_mcp_${new Date().toISOString().split('T')[0]}.md`);
  const timestamp = new Date().toISOString();
  
  const logEntry = `\n## ${timestamp}\n- **Action:** ${action}\n- **Details:** ${JSON.stringify(details)}\n`;

  try {
    fs.appendFileSync(logFile, logEntry);
  } catch (error) {
    console.error('Failed to write log:', error);
  }
}

// =============================================================================
// Tool Implementations
// =============================================================================

const tools = {
  /**
   * Send an email immediately
   */
  email_send: async (args) => {
    const { to, subject, body, inReplyTo, threadId } = args;

    if (!to || !subject || !body) {
      throw new Error('Missing required fields: to, subject, body');
    }

    try {
      // Create email message
      const rawMessage = createEmailMessage({ to, subject, body, inReplyTo });
      const encodedMessage = encodeBase64Url(rawMessage);

      // Send via Gmail API
      const response = await gmail.users.messages.send({
        userId: 'me',
        requestBody: {
          raw: encodedMessage,
          threadId: threadId || undefined,
        },
      });

      // Log the action
      logActivity('email_send', { to, subject, messageId: response.data.id });

      return {
        success: true,
        messageId: response.data.id,
        threadId: response.data.threadId,
        message: `Email sent successfully to ${to}`,
      };
    } catch (error) {
      console.error('Error sending email:', error);
      logActivity('email_send_failed', { to, subject, error: error.message });
      throw new Error(`Failed to send email: ${error.message}`);
    }
  },

  /**
   * Create a draft email
   */
  email_draft: async (args) => {
    const { to, subject, body, inReplyTo } = args;

    if (!to || !subject || !body) {
      throw new Error('Missing required fields: to, subject, body');
    }

    try {
      // Create email message
      const rawMessage = createEmailMessage({ to, subject, body, inReplyTo });
      const encodedMessage = encodeBase64Url(rawMessage);

      // Create draft via Gmail API
      const response = await gmail.users.drafts.create({
        userId: 'me',
        requestBody: {
          message: {
            raw: encodedMessage,
          },
        },
      });

      // Log the action
      logActivity('email_draft', { to, subject, draftId: response.data.id });

      return {
        success: true,
        draftId: response.data.id,
        message: `Draft created successfully for ${to}`,
        preview: body.substring(0, 100) + (body.length > 100 ? '...' : ''),
      };
    } catch (error) {
      console.error('Error creating draft:', error);
      logActivity('email_draft_failed', { to, subject, error: error.message });
      throw new Error(`Failed to create draft: ${error.message}`);
    }
  },

  /**
   * Mark email(s) as read
   */
  email_mark_read: async (args) => {
    const { messageIds, threadIds } = args;

    if (!messageIds && !threadIds) {
      throw new Error('Must provide either messageIds or threadIds');
    }

    try {
      const idsToProcess = messageIds || [];
      const results = [];

      // If threadIds provided, get message IDs from threads
      if (threadIds) {
        for (const threadId of threadIds) {
          const thread = await gmail.users.threads.get({
            userId: 'me',
            id: threadId,
          });
          
          const messages = thread.data.messages || [];
          for (const msg of messages) {
            if (!idsToProcess.includes(msg.id)) {
              idsToProcess.push(msg.id);
            }
          }
        }
      }

      // Mark each message as read by removing UNREAD label
      for (const messageId of idsToProcess) {
        await gmail.users.messages.modify({
          userId: 'me',
          id: messageId,
          requestBody: {
            removeLabelIds: ['UNREAD'],
          },
        });
        results.push(messageId);
      }

      // Log the action
      logActivity('email_mark_read', { count: results.length, messageIds: results });

      return {
        success: true,
        markedCount: results.length,
        messageIds: results,
        message: `Marked ${results.length} email(s) as read`,
      };
    } catch (error) {
      console.error('Error marking emails as read:', error);
      logActivity('email_mark_read_failed', { error: error.message });
      throw new Error(`Failed to mark emails as read: ${error.message}`);
    }
  },

  /**
   * List recent emails
   */
  email_list: async (args) => {
    const { maxResults = 10, query = '', labelIds = [] } = args;

    try {
      const response = await gmail.users.messages.list({
        userId: 'me',
        maxResults: Math.min(maxResults, 100),
        q: query,
        labelIds: labelIds,
      });

      const messages = response.data.messages || [];
      const emailList = [];

      // Get details for each message
      for (const msg of messages.slice(0, 5)) {
        const fullMessage = await gmail.users.messages.get({
          userId: 'me',
          id: msg.id,
          format: 'metadata',
          metadataHeaders: ['From', 'To', 'Subject', 'Date'],
        });

        const headers = fullMessage.data.payload?.headers || [];
        const getHeader = (name) => headers.find(h => h.name === name)?.value || '';

        emailList.push({
          id: msg.id,
          threadId: msg.threadId,
          from: getHeader('From'),
          to: getHeader('To'),
          subject: getHeader('Subject'),
          date: getHeader('Date'),
          snippet: fullMessage.data.snippet,
        });
      }

      return {
        success: true,
        count: messages.length,
        messages: emailList,
        message: `Found ${messages.length} email(s)`,
      };
    } catch (error) {
      console.error('Error listing emails:', error);
      throw new Error(`Failed to list emails: ${error.message}`);
    }
  },

  /**
   * Read a specific email
   */
  email_read: async (args) => {
    const { messageId } = args;

    if (!messageId) {
      throw new Error('Missing required field: messageId');
    }

    try {
      const response = await gmail.users.messages.get({
        userId: 'me',
        id: messageId,
        format: 'full',
      });

      const message = response.data;
      const headers = message.payload?.headers || [];
      const getHeader = (name) => headers.find(h => h.name === name)?.value || '';

      // Decode body
      let body = '';
      if (message.payload?.body?.data) {
        body = decodeBase64Url(message.payload.body.data);
      } else if (message.payload?.parts) {
        for (const part of message.payload.parts) {
          if (part.mimeType === 'text/plain' && part.body?.data) {
            body = decodeBase64Url(part.body.data);
            break;
          }
        }
      }

      return {
        success: true,
        email: {
          id: message.id,
          threadId: message.threadId,
          from: getHeader('From'),
          to: getHeader('To'),
          subject: getHeader('Subject'),
          date: getHeader('Date'),
          body: body,
          labels: message.labelIds || [],
        },
        message: `Email retrieved successfully`,
      };
    } catch (error) {
      console.error('Error reading email:', error);
      throw new Error(`Failed to read email: ${error.message}`);
    }
  },
};

// =============================================================================
// MCP Server Setup
// =============================================================================

const server = new Server(
  {
    name: 'email-mcp-server',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Handle list tools request
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'email_send',
        description: 'Send an email immediately via Gmail. Use this for approved email replies.',
        inputSchema: {
          type: 'object',
          properties: {
            to: {
              type: 'string',
              description: 'Recipient email address',
            },
            subject: {
              type: 'string',
              description: 'Email subject line',
            },
            body: {
              type: 'string',
              description: 'Email body content',
            },
            inReplyTo: {
              type: 'string',
              description: 'Message-ID of email being replied to (optional)',
            },
            threadId: {
              type: 'string',
              description: 'Gmail thread ID for threading (optional)',
            },
          },
          required: ['to', 'subject', 'body'],
        },
      },
      {
        name: 'email_draft',
        description: 'Create a draft email in Gmail without sending. Use for review before sending.',
        inputSchema: {
          type: 'object',
          properties: {
            to: {
              type: 'string',
              description: 'Recipient email address',
            },
            subject: {
              type: 'string',
              description: 'Email subject line',
            },
            body: {
              type: 'string',
              description: 'Email body content',
            },
            inReplyTo: {
              type: 'string',
              description: 'Message-ID of email being replied to (optional)',
            },
          },
          required: ['to', 'subject', 'body'],
        },
      },
      {
        name: 'email_mark_read',
        description: 'Mark email(s) as read in Gmail. Provide messageIds or threadIds.',
        inputSchema: {
          type: 'object',
          properties: {
            messageIds: {
              type: 'array',
              items: { type: 'string' },
              description: 'Array of Gmail message IDs to mark as read',
            },
            threadIds: {
              type: 'array',
              items: { type: 'string' },
              description: 'Array of Gmail thread IDs to mark as read',
            },
          },
        },
      },
      {
        name: 'email_list',
        description: 'List recent emails from Gmail. Supports query filters.',
        inputSchema: {
          type: 'object',
          properties: {
            maxResults: {
              type: 'number',
              description: 'Maximum number of emails to return (default: 10, max: 100)',
            },
            query: {
              type: 'string',
              description: 'Gmail search query (e.g., "is:unread", "from:client@example.com")',
            },
            labelIds: {
              type: 'array',
              items: { type: 'string' },
              description: 'Gmail label IDs to filter by (e.g., ["UNREAD", "IMPORTANT"])',
            },
          },
        },
      },
      {
        name: 'email_read',
        description: 'Read a specific email by its Gmail message ID.',
        inputSchema: {
          type: 'object',
          properties: {
            messageId: {
              type: 'string',
              description: 'Gmail message ID to read',
            },
          },
          required: ['messageId'],
        },
      },
    ],
  };
});

// Handle tool call request
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  console.error(`Calling tool: ${name}`);
  console.error(`Arguments:`, JSON.stringify(args, null, 2));

  if (!tools[name]) {
    throw new Error(`Unknown tool: ${name}`);
  }

  try {
    const result = await tools[name](args || {});
    
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2),
        },
      ],
    };
  } catch (error) {
    console.error(`Tool error: ${name}`, error);
    
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            success: false,
            error: error.message,
          }, null, 2),
        },
      ],
      isError: true,
    };
  }
});

// =============================================================================
// Server Startup
// =============================================================================

async function main() {
  console.error('Starting Email MCP Server...');
  console.error('Configuration loaded for:', CONFIG.senderEmail);

  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error('Email MCP Server running on stdio');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
