#!/usr/bin/env node
/**
 * Debug script to find LinkedIn selectors
 */

import { chromium } from 'playwright';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const USER_DATA_DIR = path.join(__dirname, '.linkedin-session', 'user-data');

async function debugSelectors() {
  console.log('🔍 LinkedIn Selector Debug\n');
  
  const browser = await chromium.launchPersistentContext(USER_DATA_DIR, {
    headless: false,
    viewport: { width: 1920, height: 1080 },
  });
  
  const page = browser.pages()[0] || await browser.newPage();
  
  console.log('📍 Navigating to LinkedIn...');
  await page.goto('https://www.linkedin.com/feed/', {
    waitUntil: 'commit',
    timeout: 30000
  });
  
  await page.waitForTimeout(5000);
  
  // Check if logged in
  const isOnLogin = page.url().includes('/login');
  if (isOnLogin) {
    console.log('❌ Not logged in');
    await browser.close();
    return;
  }
  
  console.log('✅ Logged in!');
  console.log(' URL:', page.url());
  
  // Find all elements related to "Start a post"
  const elements = await page.evaluate(() => {
    const results = [];
    
    // Find by text
    const allElements = document.querySelectorAll('*');
    allElements.forEach((el, index) => {
      const text = el.textContent?.trim();
      if (text && text.includes('Start a post') && index < 500) {
        const tag = el.tagName.toLowerCase();
        const id = el.id || 'no-id';
        const classes = el.className || 'no-class';
        const ariaLabel = el.getAttribute('aria-label') || 'no-aria-label';
        const role = el.getAttribute('role') || 'no-role';
        const contenteditable = el.getAttribute('contenteditable') || 'no-contenteditable';
        
        results.push({
          tag,
          id,
          classes: classes.split(' ').slice(0, 3).join('.'),
          ariaLabel,
          role,
          contenteditable,
          text: text.substring(0, 50),
        });
      }
    });
    
    return results.slice(0, 10);
  });
  
  console.log('\n📋 Elements with "Start a post":');
  elements.forEach((el, i) => {
    console.log(`\n${i + 1}. <${el.tag}>`);
    console.log(`   ID: ${el.id}`);
    console.log(`   Class: ${el.classes}`);
    console.log(`   aria-label: ${el.ariaLabel}`);
    console.log(`   role: ${el.role}`);
    console.log(`   contenteditable: ${el.contenteditable}`);
    console.log(`   Text: "${el.text}"`);
  });
  
  // Try to find clickable element
  console.log('\n🔍 Testing selectors...');
  
  const testSelectors = [
    'div[aria-label*="Start a post"]',
    '[placeholder*="Start a post"]',
    'button[aria-label*="Start a post"]',
    '.share-box-feed-entry__trigger',
    '[data-control-name="compose"]',
    'div[contenteditable="true"]',
    'button:has-text("Start a post")',
    'div:has-text("Start a post")',
    '[role="button"]:has-text("Start a post")',
  ];
  
  for (const selector of testSelectors) {
    try {
      const el = await page.$(selector);
      if (el) {
        const box = await el.boundingBox();
        console.log(`✓ ${selector}`);
        console.log(`  Box: ${JSON.stringify(box)}`);
      } else {
        console.log(`✗ ${selector} - not found`);
      }
    } catch (e) {
      console.log(`✗ ${selector} - error: ${e.message}`);
    }
  }
  
  await browser.close();
}

debugSelectors().catch(console.error);
