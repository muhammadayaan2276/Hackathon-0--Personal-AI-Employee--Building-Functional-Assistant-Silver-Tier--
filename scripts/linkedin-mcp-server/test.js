#!/usr/bin/env node
/**
 * Test Script for LinkedIn MCP Server - Persistent Context Version
 * 
 * Uses a persistent browser profile for more reliable LinkedIn sessions
 */

import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import readline from 'readline';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// =============================================================================
// Configuration
// =============================================================================

const SESSION_DIR = path.join(__dirname, '.linkedin-session');
const SESSION_FILE = path.join(SESSION_DIR, 'cookies.json');
const USER_DATA_DIR = path.join(SESSION_DIR, 'user-data');

// Ensure directories exist
if (!fs.existsSync(SESSION_DIR)) {
  fs.mkdirSync(SESSION_DIR, { recursive: true });
}
if (!fs.existsSync(USER_DATA_DIR)) {
  fs.mkdirSync(USER_DATA_DIR, { recursive: true });
}

// =============================================================================
// Helper Functions
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

async function loadSession() {
  if (fs.existsSync(SESSION_FILE)) {
    try {
      const data = fs.readFileSync(SESSION_FILE, 'utf-8');
      const parsed = JSON.parse(data);
      return Array.isArray(parsed) ? parsed : null;
    } catch (error) {
      console.error('Failed to load session:', error.message);
      return null;
    }
  }
  return null;
}

// =============================================================================
// Test Functions
// =============================================================================

/**
 * Test: Check session using persistent context
 */
async function testCheckSession() {
  console.log('\n🔍 Test: Check LinkedIn Session');
  console.log('='.repeat(50));

  const session = await loadSession();
  if (!session) {
    console.log('\n⚠️  No existing session found');
    console.log('   Run "npm run auth" first to authenticate');
    return false;
  }

  console.log('\n✓ Session file found');
  console.log(`  Cookies: ${session.length}`);

  // Check for essential LinkedIn cookies
  const hasLiAt = session.some(c => c.name === 'li_at');
  const hasLiApm = session.some(c => c.name === 'liap');
  console.log(`  li_at cookie: ${hasLiAt ? '✓ present' : '❌ missing'}`);
  console.log(`  li_ap cookie: ${hasLiApm ? '✓ present' : '❌ missing'}`);

  // Use persistent context for more reliable sessions
  console.log('\n📍 Opening LinkedIn with persistent browser profile...');
  
  const browser = await chromium.launchPersistentContext(USER_DATA_DIR, {
    headless: false,
    viewport: { width: 1920, height: 1080 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    args: [
      '--disable-blink-features=AutomationControlled',
      '--disable-features=IsolateOrigins,site-per-process',
    ],
  });

  const page = browser.pages()[0] || await browser.newPage();

  console.log('  Navigating to LinkedIn...');
  await page.goto('https://www.linkedin.com/feed/', {
    waitUntil: 'commit',
    timeout: 30000
  });

  // Wait for page to load
  await page.waitForTimeout(8000);

  // Take a screenshot
  await page.screenshot({ path: path.join(__dirname, 'debug-session.png') });
  console.log('  Debug screenshot saved: debug-session.png');

  // Check current URL
  const currentUrl = page.url();
  console.log(`  Current URL: ${currentUrl}`);

  // Check if we're on login page
  const isOnLoginPage = currentUrl.includes('/login') || currentUrl.includes('/checkpoint/');
  
  if (isOnLoginPage) {
    console.log('\n❌ Session invalid - redirected to login');
    console.log('   LinkedIn rejected the session cookies.');
    console.log('\n   Solution: Run "npm run auth" to re-authenticate');
    await browser.close();
    return false;
  }

  // Check for logged in indicators
  const isLoggedIn = await page.evaluate(() => {
    // Multiple indicators of being logged in - updated selectors for 2026 LinkedIn
    const indicators = {
      hasNavMe: !!document.querySelector('[data-control-name="nav.me"]'),
      hasCompose: !!document.querySelector('[data-control-name="compose"]'),
      hasFeed: !!document.querySelector('[data-id="feed"]'),
      hasStartPost: !!document.querySelector('button[aria-label*="Start a post"]'),
      hasPostInput: !!document.querySelector('[placeholder*="Start a post"]'),
      isOnFeed: window.location.href.includes('/feed/'),
      hasMeMenu: !!document.querySelector('[aria-label*="Me"]'),
      hasProfileIcon: !!document.querySelector('img[src*="profile"]'),
    };
    
    const trueCount = Object.values(indicators).filter(v => v).length;
    console.log('  Login indicators:', indicators);
    console.log(`  True count: ${trueCount}`);
    
    // If any 2+ indicators are true, consider logged in
    return trueCount >= 2;
  });

  console.log('\n' + (isLoggedIn ? '✅' : '❌') + ` Session ${isLoggedIn ? 'valid' : 'invalid'}`);

  if (isLoggedIn) {
    const profileInfo = await page.evaluate(() => {
      const nameElement = document.querySelector('[data-control-name="nav.me"]');
      return {
        name: nameElement?.textContent?.trim() || 'Unknown',
        url: window.location.href
      };
    });

    console.log(`  Profile: ${profileInfo.name}`);
    console.log(`  URL: ${profileInfo.url}`);
    console.log('\n✅ SUCCESS! Your LinkedIn session is working!');
    console.log('   You can now use the MCP server to post to LinkedIn.');
  }

  await browser.close();
  return isLoggedIn;
}

/**
 * Test: Login (if needed)
 */
async function testLogin() {
  console.log('\n🔐 Test: LinkedIn Login');
  console.log('='.repeat(50));

  const session = await loadSession();
  if (session) {
    console.log('\n⊘ Skipping: Session already exists');
    console.log('   To test login, delete .linkedin-session/cookies.json');
    return;
  }

  console.log('\n⚠️  No existing session. Run "npm run auth" to authenticate.');
}

/**
 * Test: Take screenshot
 */
async function testScreenshot() {
  console.log('\n📸 Test: Take Screenshot');
  console.log('='.repeat(50));

  const session = await loadSession();
  if (!session) {
    console.log('\n⊘ Skipping: No session available');
    return;
  }

  const browser = await chromium.launchPersistentContext(USER_DATA_DIR, {
    headless: false,
    viewport: { width: 1920, height: 1080 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  });

  const page = browser.pages()[0] || await browser.newPage();

  console.log('  Navigating to LinkedIn...');
  await page.goto('https://www.linkedin.com/feed/', {
    waitUntil: 'commit',
    timeout: 30000
  });

  await page.waitForTimeout(5000);

  const screenshotPath = path.join(__dirname, 'test-screenshot.png');
  await page.screenshot({ path: screenshotPath });

  console.log('\n✓ Screenshot saved');
  console.log(`  File: ${screenshotPath}`);

  await browser.close();
}

/**
 * Test: Publish post
 */
async function testPublishPost() {
  console.log('\n📝 Test: Publish Post');
  console.log('='.repeat(50));

  const session = await loadSession();
  if (!session) {
    console.log('\n⊘ Skipping: No session available');
    return;
  }

  console.log('\n⚠️  This will PUBLISH a test post to your LinkedIn!');
  console.log('   The post will be visible to your connections.');

  const rl = createInterface(process.stdin, process.stdout);
  const confirm = await new Promise(resolve => {
    rl.question('   Continue? (yes/no): ', resolve);
  });

  if (confirm.toLowerCase() !== 'yes') {
    console.log('  ⊘ Skipped');
    return;
  }

  const testContent = `Testing LinkedIn MCP Server automation! 🚀

This is an automated test post for the Personal AI Employee system.

#Testing #Automation #AI`;

  const browser = await chromium.launchPersistentContext(USER_DATA_DIR, {
    headless: false,
    viewport: { width: 1920, height: 1080 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  });

  const page = browser.pages()[0] || await browser.newPage();

  console.log('\n📍 Navigating to LinkedIn...');
  await page.goto('https://www.linkedin.com/feed/', {
    waitUntil: 'commit',
    timeout: 30000
  });

  await page.waitForTimeout(5000);

  // Check if logged in first
  const isOnLogin = page.url().includes('/login');
  if (isOnLogin) {
    console.log('  ❌ Not logged in. Run "npm run auth" first.');
    await browser.close();
    return;
  }

  // Click "Start a post"
  console.log('  Opening post composer...');
  
  let startPostButton = await page.$('button[aria-label*="Start a post"]');
  if (!startPostButton) {
    startPostButton = await page.$('[data-control-name="compose"]');
  }
  
  if (!startPostButton) {
    console.log('  ❌ Could not find post button');
    await browser.close();
    return;
  }

  await startPostButton.click();
  await page.waitForTimeout(2000);

  // Wait for dialog
  try {
    await page.waitForSelector('[role="dialog"]', { timeout: 10000 });
  } catch (e) {
    console.log('  ❌ Post dialog did not open');
    await browser.close();
    return;
  }
  
  await page.waitForTimeout(1000);

  // Type content
  console.log('  Entering content...');
  const editor = await page.$('[role="textbox"]');
  if (editor) {
    await editor.focus();
    await page.keyboard.type(testContent, { delay: 80 });
    await page.waitForTimeout(1000);
  } else {
    console.log('  ❌ Could not find editor');
    await browser.close();
    return;
  }

  // Click Post button
  console.log('  Publishing...');
  let postButton = await page.$('button[aria-label*="Post"]');
  
  if (!postButton) {
    const buttons = await page.$$('button');
    for (const btn of buttons) {
      const text = await btn.textContent();
      if (text && text.includes('Post')) {
        postButton = btn;
        break;
      }
    }
  }
  
  if (postButton) {
    await postButton.click();
    await page.waitForTimeout(5000);
  } else {
    console.log('  ❌ Could not find Post button');
    await browser.close();
    return;
  }

  // Check result
  const currentUrl = page.url();
  console.log('\n✓ Post action completed');
  console.log(`  Current URL: ${currentUrl}`);

  // Take screenshot
  const screenshotPath = path.join(__dirname, 'post-screenshot.png');
  await page.screenshot({ path: screenshotPath });
  console.log(`  Screenshot: ${screenshotPath}`);
  console.log('\n✅ Check your LinkedIn profile to verify the post was published!');

  await browser.close();
}

// =============================================================================
// Main Test Runner
// =============================================================================

async function runTests() {
  console.log('\n🧪 LinkedIn MCP Server - Test Suite');
  console.log('='.repeat(50));
  console.log('\n💡 Using persistent browser profile for reliable sessions');
  console.log(`   Profile location: ${USER_DATA_DIR}`);

  // Test 1: Check session
  const hasValidSession = await testCheckSession();
  await pause();

  // Test 2: Login (if needed)
  await testLogin();
  await pause();

  // Test 3: Screenshot
  await testScreenshot();
  await pause();

  // Test 4: Publish post (optional)
  if (hasValidSession) {
    await testPublishPost();
  } else {
    console.log('\n⚠️  Session is invalid. Skipping post test.');
    console.log('   Run "npm run auth" to re-authenticate.');
  }

  console.log('\n' + '='.repeat(50));
  console.log('✅ All tests completed!');
  console.log('='.repeat(50));
}

// =============================================================================
// Entry Point
// =============================================================================

runTests().catch((error) => {
  console.error('\n❌ Fatal error:', error);
  console.error('Stack:', error.stack);
  process.exit(1);
});
