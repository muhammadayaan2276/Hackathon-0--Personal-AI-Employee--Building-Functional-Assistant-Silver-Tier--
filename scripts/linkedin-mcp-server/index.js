#!/usr/bin/env node
/**
 * LinkedIn MCP Server for Personal AI Employee (Silver Tier)
 * 
 * Provides LinkedIn automation via Playwright and Model Context Protocol (MCP)
 * 
 * Tools available:
 * - linkedin_check_session: Verify if logged in
 * - linkedin_login: Authenticate with LinkedIn
 * - linkedin_post_publish: Publish a new post
 * - linkedin_post_draft: Create a draft post
 * - linkedin_take_screenshot: Capture current page
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { chromium } from 'playwright';
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
  linkedinEmail: process.env.LINKEDIN_EMAIL,
  linkedinPassword: process.env.LINKEDIN_PASSWORD,
};

const SESSION_DIR = join(__dirname, '.linkedin-session');
const SESSION_FILE = join(SESSION_DIR, 'cookies.json');
const STATE_FILE = join(SESSION_DIR, 'state.json');
const USER_DATA_DIR = join(SESSION_DIR, 'user-data');

// Ensure session directory exists
if (!fs.existsSync(SESSION_DIR)) {
  fs.mkdirSync(SESSION_DIR, { recursive: true });
}

// Browser instance (singleton)
let browser = null;
let context = null;
let page = null;

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Get or create browser instance
 */
async function getBrowser() {
  if (!browser) {
    browser = await chromium.launch({
      headless: false, // Show browser for debugging
      args: ['--disable-blink-features=AutomationControlled'],
    });
  }
  return browser;
}

/**
 * Get or create browser context with session
 */
async function getContext() {
  if (!context) {
    // Use persistent context for more reliable sessions
    browser = await chromium.launchPersistentContext(USER_DATA_DIR, {
      headless: false,
      viewport: { width: 1280, height: 720 },
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
      args: [
        '--disable-blink-features=AutomationControlled',
        '--disable-features=IsolateOrigins,site-per-process',
      ],
    });
    
    context = browser;
    console.error('Loaded persistent browser profile');
  }
  return context;
}

/**
 * Get or create page
 */
async function getPage() {
  if (!page) {
    const context = await getContext();
    // Use existing page or create new one
    page = context.pages()[0] || await context.newPage();

    // Hide automation detection
    await page.addInitScript(() => {
      delete navigator.__proto__.webdriver;
    });
  }
  return page;
}

/**
 * Save session cookies
 */
async function saveSession() {
  try {
    const context = await getContext();
    const cookies = await context.cookies();
    fs.writeFileSync(SESSION_FILE, JSON.stringify(cookies, null, 2));
    console.error('Saved LinkedIn session cookies');
  } catch (error) {
    console.error('Failed to save session:', error.message);
  }
}

/**
 * Check if currently logged in to LinkedIn
 */
async function checkLinkedInLogin() {
  try {
    const page = await getPage();
    
    // Navigate to LinkedIn feed
    await page.goto('https://www.linkedin.com/feed/', { 
      waitUntil: 'networkidle',
      timeout: 30000 
    });
    
    // Wait a moment for page to load
    await page.waitForTimeout(3000);
    
    // Check for indicators of being logged in
    const isLoggedIn = await page.evaluate(() => {
      // Look for profile icon or feed elements that only appear when logged in
      const profileIcon = document.querySelector('[data-control-name="nav.me"]');
      const feedPosts = document.querySelector('[data-id="feed"]');
      const startPostBox = document.querySelector('[data-control-name="compose"]');
      
      return !!(profileIcon || startPostBox);
    });
    
    // Also check URL - if redirected to login, not logged in
    const currentUrl = page.url();
    const isOnLoginPage = currentUrl.includes('/login') || currentUrl.includes('/checkpoint/');
    
    return isLoggedIn && !isOnLoginPage;
  } catch (error) {
    console.error('Error checking login status:', error.message);
    return false;
  }
}

/**
 * Login to LinkedIn
 */
async function loginToLinkedIn(email, password) {
  const page = await getPage();
  
  // Navigate to LinkedIn login
  await page.goto('https://www.linkedin.com/login', { 
    waitUntil: 'networkidle',
    timeout: 30000 
  });
  
  await page.waitForTimeout(2000);
  
  // Fill in credentials
  await page.fill('#username', email);
  await page.fill('#password', password);
  
  // Click sign in
  await page.click('button[type="submit"]');
  
  // Wait for navigation
  await page.waitForNavigation({ waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(3000);
  
  // Handle any checkpoint/challenge if present
  const currentUrl = page.url();
  if (currentUrl.includes('/checkpoint/')) {
    console.error('LinkedIn security checkpoint detected. Manual verification may be required.');
    return { success: false, requiresVerification: true };
  }
  
  // Check if login was successful
  const isLoggedIn = await checkLinkedInLogin();
  
  if (isLoggedIn) {
    await saveSession();
    return { success: true };
  } else {
    return { success: false, error: 'Login failed - invalid credentials or security check' };
  }
}

/**
 * Publish a post to LinkedIn
 */
async function publishPost(content, imagePath = null) {
  const page = await getPage();
  
  // Navigate to LinkedIn feed
  await page.goto('https://www.linkedin.com/feed/', { 
    waitUntil: 'networkidle',
    timeout: 30000 
  });
  
  await page.waitForTimeout(2000);
  
  // Click on "Start a post" button
  const startPostButton = await page.$('[data-control-name="compose"]');
  if (!startPostButton) {
    return { 
      success: false, 
      error: 'Could not find post creation button. May not be logged in.' 
    };
  }
  
  await startPostButton.click();
  await page.waitForTimeout(1000);
  
  // Wait for post dialog to appear
  await page.waitForSelector('[role="dialog"]', { timeout: 10000 });
  await page.waitForTimeout(500);
  
  // Find the text editor and type content
  const editor = await page.$('[role="textbox"]');
  if (!editor) {
    return { success: false, error: 'Could not find post editor' };
  }
  
  // Type the content
  await editor.focus();
  await page.keyboard.type(content, { delay: 50 });
  await page.waitForTimeout(500);
  
  // Add image if provided
  if (imagePath && fs.existsSync(imagePath)) {
    // Click on media/photo button
    const mediaButton = await page.$('input[type="file"]');
    if (mediaButton) {
      await mediaButton.setInputFiles(imagePath);
      await page.waitForTimeout(2000);
    }
  }
  
  // Click Post button
  const postButton = await page.$('button[aria-label*="Post"]');
  if (!postButton) {
    // Try alternative selector
    const postButtons = await page.$$('button');
    for (const btn of postButtons) {
      const text = await btn.textContent();
      if (text.includes('Post')) {
        await btn.click();
        break;
      }
    }
  } else {
    await postButton.click();
  }
  
  await page.waitForTimeout(3000);
  
  // Check if post was published (look for confirmation or return to feed)
  const currentUrl = page.url();
  const isOnFeed = currentUrl.includes('/feed/');
  
  // Take screenshot
  const screenshot = await page.screenshot({ encoding: 'base64', type: 'png' });
  
  if (isOnFeed) {
    return { 
      success: true, 
      message: 'Post published successfully',
      postUrl: currentUrl,
      screenshot: screenshot 
    };
  } else {
    return { 
      success: false, 
      error: 'Post may not have been published. Check LinkedIn manually.',
      screenshot: screenshot 
    };
  }
}

/**
 * Take a screenshot of current page
 */
async function takeScreenshot() {
  try {
    const page = await getPage();
    const screenshot = await page.screenshot({ encoding: 'base64', type: 'png' });
    return { success: true, screenshot };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * Log activity to vault
 */
function logActivity(action, details) {
  const vaultDir = join(__dirname, '..', '..', 'AI_Employee_Vault');
  const logsDir = join(vaultDir, 'Logs');
  
  if (!fs.existsSync(logsDir)) {
    fs.mkdirSync(logsDir, { recursive: true });
  }
  
  const logFile = join(logsDir, `linkedin_mcp_${new Date().toISOString().split('T')[0]}.md`);
  const timestamp = new Date().toISOString();
  
  const logEntry = `\n## ${timestamp}\n- **Action:** ${action}\n- **Details:** ${JSON.stringify(details, null, 2)}\n`;
  
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
   * Check if logged in to LinkedIn
   */
  linkedin_check_session: async (args) => {
    try {
      const isLoggedIn = await checkLinkedInLogin();
      
      let profileName = null;
      let profileUrl = null;
      
      if (isLoggedIn) {
        const page = await getPage();
        const profileInfo = await page.evaluate(() => {
          const nameElement = document.querySelector('[data-control-name="nav.me"]');
          if (nameElement) {
            return {
              name: nameElement.textContent?.trim() || 'Unknown',
              url: window.location.href
            };
          }
          return null;
        });
        
        if (profileInfo) {
          profileName = profileInfo.name;
          profileUrl = profileInfo.url;
        }
      }
      
      return {
        success: true,
        loggedIn: isLoggedIn,
        profileName,
        profileUrl,
        message: isLoggedIn ? 'LinkedIn session active' : 'Not logged in',
      };
    } catch (error) {
      console.error('Error checking session:', error);
      return {
        success: false,
        loggedIn: false,
        error: error.message,
      };
    }
  },

  /**
   * Login to LinkedIn
   */
  linkedin_login: async (args) => {
    const { email, password } = args;
    
    if (!email || !password) {
      // Try from environment
      if (CONFIG.linkedinEmail && CONFIG.linkedinPassword) {
        return await loginToLinkedIn(CONFIG.linkedinEmail, CONFIG.linkedinPassword);
      }
      return { 
        success: false, 
        error: 'Email and password required. Provide in arguments or set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in .env' 
      };
    }
    
    const result = await loginToLinkedIn(email, password);
    logActivity('linkedin_login', { email, success: result.success });
    return result;
  },

  /**
   * Publish a post to LinkedIn
   */
  linkedin_post_publish: async (args) => {
    const { content, imagePath } = args;
    
    if (!content) {
      throw new Error('Post content is required');
    }
    
    // Check if logged in first
    const isLoggedIn = await checkLinkedInLogin();
    if (!isLoggedIn) {
      return {
        success: false,
        error: 'Not logged in to LinkedIn. Run linkedin_login first.',
      };
    }
    
    // Publish the post
    const result = await publishPost(content, imagePath);
    
    logActivity('linkedin_post_publish', { 
      contentLength: content.length, 
      hasImage: !!imagePath,
      success: result.success 
    });
    
    return result;
  },

  /**
   * Create a draft post (not yet supported - returns info)
   */
  linkedin_post_draft: async (args) => {
    return {
      success: false,
      error: 'Draft posts are not supported via automation. Use linkedin_post_publish to post directly.',
      suggestion: 'Save your draft content in /Pending_Approval/ folder instead.',
    };
  },

  /**
   * Take a screenshot
   */
  linkedin_take_screenshot: async (args) => {
    return await takeScreenshot();
  },
};

// =============================================================================
// MCP Server Setup
// =============================================================================

const server = new Server(
  {
    name: 'linkedin-mcp-server',
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
        name: 'linkedin_check_session',
        description: 'Check if currently logged in to LinkedIn. Returns session status and profile info.',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
      {
        name: 'linkedin_login',
        description: 'Login to LinkedIn. Provide email/password or use LINKEDIN_EMAIL and LINKEDIN_PASSWORD from .env',
        inputSchema: {
          type: 'object',
          properties: {
            email: {
              type: 'string',
              description: 'LinkedIn email address',
            },
            password: {
              type: 'string',
              description: 'LinkedIn password',
            },
          },
        },
      },
      {
        name: 'linkedin_post_publish',
        description: 'Publish a post to LinkedIn. Content is required, image path is optional.',
        inputSchema: {
          type: 'object',
          properties: {
            content: {
              type: 'string',
              description: 'Post content (max 3000 characters). Include hashtags at the end.',
            },
            imagePath: {
              type: 'string',
              description: 'Absolute path to image file (PNG, JPG). Optional.',
            },
          },
          required: ['content'],
        },
      },
      {
        name: 'linkedin_post_draft',
        description: 'Create a draft post. Note: LinkedIn does not support draft creation via automation.',
        inputSchema: {
          type: 'object',
          properties: {
            content: {
              type: 'string',
              description: 'Draft content',
            },
          },
        },
      },
      {
        name: 'linkedin_take_screenshot',
        description: 'Take a screenshot of the current LinkedIn page.',
        inputSchema: {
          type: 'object',
          properties: {},
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
// Cleanup on Exit
// =============================================================================

process.on('SIGINT', async () => {
  console.error('Shutting down...');
  if (browser) {
    await browser.close();
  }
  process.exit(0);
});

// =============================================================================
// Server Startup
// =============================================================================

async function main() {
  console.error('Starting LinkedIn MCP Server...');
  console.error('Session directory:', SESSION_DIR);

  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error('LinkedIn MCP Server running on stdio');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
