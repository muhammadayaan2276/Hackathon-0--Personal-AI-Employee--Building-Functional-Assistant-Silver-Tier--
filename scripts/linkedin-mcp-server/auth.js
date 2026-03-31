#!/usr/bin/env node
/**
 * LinkedIn Authentication Script - Persistent Context Version
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

/**
 * Save session cookies
 */
async function saveSession(context) {
  const cookies = await context.cookies();
  
  // Fix cookie domains for broader matching
  const fixedCookies = cookies.map(cookie => ({
    ...cookie,
    domain: cookie.domain === '.www.linkedin.com' ? '.linkedin.com' : cookie.domain,
  }));
  
  fs.writeFileSync(SESSION_FILE, JSON.stringify(fixedCookies, null, 2));
  console.log('✓ Saved LinkedIn session cookies');
  console.log(`  Location: ${SESSION_FILE}`);
  console.log(`\n💡 Session also saved in browser profile: ${USER_DATA_DIR}`);
}

/**
 * Load existing session
 */
function loadSession() {
  if (fs.existsSync(SESSION_FILE)) {
    try {
      return JSON.parse(fs.readFileSync(SESSION_FILE, 'utf-8'));
    } catch (error) {
      console.error('Could not load existing session:', error.message);
    }
  }
  return null;
}

// =============================================================================
// Main Authentication Flow
// =============================================================================

async function authenticate() {
  console.log('💼 LinkedIn Authentication - Persistent Context Version\n');
  console.log('='.repeat(50));
  console.log(`\n📁 Browser profile location: ${USER_DATA_DIR}`);

  // Check for existing session
  const existingSession = loadSession();
  if (existingSession) {
    console.log('\n⚠️  Found existing session');
    console.log('\nSession file:', SESSION_FILE);
    
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    const answer = await new Promise(resolve => {
      rl.question('\nDelete existing session and re-authenticate? (y/n): ', resolve);
    });
    rl.close();
    
    if (answer.toLowerCase() !== 'y') {
      console.log('\nTo use this session with MCP server: npm start');
      return;
    }
    
    // Close any running browsers first
    try {
      await fs.promises.rm(USER_DATA_DIR, { recursive: true, force: true });
      console.log('✓ Cleared browser profile');
    } catch (e) {
      console.log('⚠️  Could not clear browser profile - close any open browsers and try again');
    }
    
    fs.unlinkSync(SESSION_FILE);
    console.log('✓ Deleted old session');
  }

  console.log('\n🔐 Starting LinkedIn login...');
  console.log('\n⚠️  A browser window will open with a persistent profile.');
  console.log('   Please login to LinkedIn manually.');
  console.log('   Wait until you see your feed, then the browser will close automatically.\n');

  // Launch persistent browser context
  const browser = await chromium.launchPersistentContext(USER_DATA_DIR, {
    headless: false,
    viewport: { width: 1280, height: 720 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    args: [
      '--disable-blink-features=AutomationControlled',
      '--disable-features=IsolateOrigins,site-per-process',
    ],
  });

  const page = browser.pages()[0] || await browser.newPage();

  // Navigate to LinkedIn login
  console.log('📍 Navigating to LinkedIn...');
  await page.goto('https://www.linkedin.com/login', {
    waitUntil: 'commit',
    timeout: 30000
  });

  console.log('✓ Browser opened. Please login to LinkedIn.');
  console.log('\n💡 Tip: Check "Remember me" to stay logged in longer.');
  console.log('\n⏳ Waiting for you to login (max 120 seconds)...\n');

  // Wait for user to login (max 120 seconds)
  const maxWaitTime = 120;
  let waitedTime = 0;
  
  while (waitedTime < maxWaitTime) {
    await new Promise(resolve => setTimeout(resolve, 1000));
    waitedTime++;
    
    // Check URL every 2 seconds
    if (waitedTime % 2 === 0) {
      const currentUrl = page.url();
      console.log(`\r   Time: ${waitedTime}s - URL: ${currentUrl.substring(0, 60)}...`);
      
      // Check if we're on the feed page (logged in)
      if (currentUrl.includes('/feed/')) {
        console.log('\n\n✓ Login detected! Waiting for page to fully load...');
        await page.waitForTimeout(5000);
        
        // Verify we're still on feed after waiting
        const finalUrl = page.url();
        if (finalUrl.includes('/feed/')) {
          console.log('✓ Page fully loaded!');
          break;
        }
      }
    }
  }

  console.log('\n');

  // Check current URL
  const currentUrl = page.url();
  console.log('📍 Final URL:', currentUrl);

  // Check if logged in
  const isLoggedIn = currentUrl.includes('/feed/') ||
                     currentUrl.includes('/mynetwork/') ||
                     currentUrl.includes('/in/');

  if (isLoggedIn) {
    console.log('✓ Login successful!');

    // Wait a moment for all cookies to be set
    await page.waitForTimeout(2000);
    
    // Save session
    await saveSession(browser);
    
    // Verify session was saved correctly
    const savedSession = loadSession();
    if (savedSession && savedSession.length > 0) {
      const hasLiAt = savedSession.some(c => c.name === 'li_at');
      console.log(`\n✓ Session saved with ${savedSession.length} cookies`);
      console.log(`  li_at cookie: ${hasLiAt ? '✓ present' : '❌ missing'}`);
    } else {
      console.log('\n⚠️  Warning: Session may not have been saved correctly!');
    }

    // Get profile info
    try {
      const profileInfo = await page.evaluate(() => {
        const nameElement = document.querySelector('[data-control-name="nav.me"]');
        return {
          name: nameElement?.textContent?.trim() || 'Unknown',
          url: window.location.href
        };
      });

      console.log('\n✅ Authentication complete!');
      console.log(`   Logged in as: ${profileInfo.name}`);
    } catch (e) {
      console.log('\n✅ Authentication complete!');
    }

    console.log('\n📝 Next steps:');
    console.log('   1. Run: npm test (to verify session)');
    console.log('   2. Run: npm start (to start MCP server)');
  } else {
    console.log('\n⚠️  Login may not be complete.');
    console.log('   Current URL:', currentUrl);
    console.log('   Please try again if authentication fails.');
  }

  // Wait 2 more seconds then close
  await new Promise(resolve => setTimeout(resolve, 2000));
  await browser.close();

  console.log('\n✅ Done!');
}

// =============================================================================
// Entry Point
// =============================================================================

authenticate().catch((error) => {
  console.error('\n❌ Fatal error:', error.message);
  console.error('Stack:', error.stack);
  process.exit(1);
});
