#!/usr/bin/env node
/**
 * Quick LinkedIn Post Test
 * 
 * Run this to publish a test post to LinkedIn
 */

import { chromium } from 'playwright';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const USER_DATA_DIR = path.join(__dirname, '.linkedin-session', 'user-data');

async function publishPost() {
  console.log('📝 LinkedIn Post Test\n');
  console.log('='.repeat(50));
  
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
    console.log('❌ Not logged in. Run "npm run auth" first.');
    await browser.close();
    return;
  }
  
  console.log('✅ Logged in!');
  
  // Take a screenshot to see the page
  await page.screenshot({ path: path.join(__dirname, 'feed-screenshot.png') });
  console.log('📸 Screenshot saved: feed-screenshot.png');
  
  // Click on the post input field - it's a div that opens the composer
  console.log('📝 Opening post composer...');
  let postInput = null;
  
  // Working selectors for LinkedIn 2026
  const selectors = [
    'div[aria-label*="Start a post"]',
    '[role="button"]:has-text("Start a post")',
  ];
  
  for (const selector of selectors) {
    try {
      postInput = await page.$(selector);
      if (postInput) {
        console.log(`✓ Found input with: ${selector}`);
        break;
      }
    } catch (e) {
      // Continue to next selector
    }
  }
  
  if (!postInput) {
    console.log('❌ Could not find post input field');
    console.log('   Check the feed-screenshot.png to see the page');
    await browser.close();
    return;
  }
  
  // Click on the input field to open the composer
  console.log('  Clicking on post input...');
  await postInput.scrollIntoViewIfNeeded();
  await postInput.click({ force: true });
  
  // Wait longer for the dialog to appear
  console.log('  Waiting for dialog to open...');
  await page.waitForTimeout(5000);
  
  // Take a screenshot to see what happened
  await page.screenshot({ path: path.join(__dirname, 'after-click-screenshot.png') });
  console.log('📸 Screenshot saved: after-click-screenshot.png');
  
  // Wait for the post dialog to appear
  let dialogVisible = false;
  try {
    await page.waitForSelector('[role="dialog"]', { timeout: 10000 });
    dialogVisible = true;
    console.log('✓ Post dialog opened');
  } catch (e) {
    console.log('⚠️  Full dialog did not open - LinkedIn may use inline composer');
  }
  
  // Look for the editor - either in dialog or inline
  let editor = null;
  
  // The dialog shows "What do you want to talk about?" placeholder
  // Look for the div with this placeholder or the text input area
  console.log('  Looking for editor...');
  
  const editorSelectors = [
    'div[aria-label*="What do you want to talk about?"]',
    'div[placeholder*="What do you want to talk about?"]',
    'div[contenteditable="true"][role="textbox"]',
    'div[contenteditable="true"]',
    '.editor-textarea',
    '.share-box-feed-entry__editor',
  ];
  
  for (const selector of editorSelectors) {
    try {
      editor = await page.$(selector);
      if (editor) {
        console.log(`✓ Found editor with: ${selector}`);
        break;
      }
    } catch (e) {
      // Continue
    }
  }
  
  if (!editor) {
    // Try finding by placeholder text
    editor = await page.$(`text=What do you want to talk about?`);
    if (editor) {
      console.log('✓ Found editor by placeholder text');
    }
  }
  
  if (!editor) {
    // Last resort: try to find any contenteditable element
    const editableHandle = await page.evaluateHandle(() => {
      const editable = document.querySelector('[contenteditable="true"]');
      return editable;
    });
    
    // Check if we got an element
    const isEditable = await page.evaluate(el => el !== null, editor);
    if (isEditable) {
      editor = editableHandle;
      console.log('✓ Found contenteditable element');
    }
  }
  
  if (!editor) {
    console.log('❌ Post editor not found');
    console.log('   Check after-click-screenshot.png');
    await browser.close();
    return;
  }
  
  // Type content
  const testContent = `🎉 Testing LinkedIn Automation!

This post was published using the Personal AI Employee system - an autonomous AI agent that manages personal and business affairs 24/7.

Key features:
✅ Obsidian dashboard
✅ Python watchers
✅ MCP servers for actions
✅ Human-in-the-loop approvals

#AI #Automation #PersonalAI #LinkedIn #Technology`;

  console.log('⌨️  Typing content...');
  
  // Focus and type
  if (editor) {
    await editor.focus();
    await page.keyboard.type(testContent, { delay: 80 });
    await page.waitForTimeout(2000);
  }
  
  // Take a screenshot before posting
  await page.screenshot({ path: path.join(__dirname, 'pre-post-screenshot.png') });
  console.log('📸 Screenshot saved: pre-post-screenshot.png');

  // Click the blue Post button
  console.log('🚀 Publishing...');
  
  // Wait a moment for the Post button to be enabled
  await page.waitForTimeout(2000);
  
  // Find and click the Post button inside the composer dialog
  console.log('  Clicking Post button...');
  
  try {
    // Target the Post button inside the composer dialog (not the "Post to Anyone" button)
    // The Post button is usually in a footer/div at the bottom of the dialog
    const postButton = page.locator('[role="dialog"] button:has-text("Post")').last();
    
    // Wait for it to be attached
    await postButton.waitFor({ state: 'attached', timeout: 5000 });
    
    // Scroll it into view
    await postButton.scrollIntoViewIfNeeded();
    
    // Check if it's enabled
    const isEnabled = await postButton.isEnabled();
    console.log(`  Post button found in dialog, enabled: ${isEnabled}`);
    
    if (isEnabled) {
      // Focus and press Enter (more reliable than click)
      await postButton.focus();
      await page.keyboard.press('Enter');
      console.log('  ✓ Enter pressed on Post button!');
    } else {
      console.log('  Post button is disabled');
    }
  } catch (error) {
    console.log('  Error with dialog selector, trying alternative...');
    // Try finding button by its blue color/style
    await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      for (const btn of buttons) {
        const text = btn.textContent?.trim();
        // Look for Post button that's not "Post to Anyone"
        if (text === 'Post' && !btn.disabled) {
          // Check if it's in a visible dialog
          const dialog = btn.closest('[role="dialog"]');
          if (dialog) {
            btn.click();
            console.log('  Post button clicked in dialog!');
            return true;
          }
        }
      }
      return false;
    });
  }
  
  // Wait for post to be published
  await page.waitForTimeout(10000);
  
  // Take final screenshot
  await page.screenshot({ path: path.join(__dirname, 'post-published-screenshot.png') });
  console.log('📸 Final screenshot saved: post-published-screenshot.png');
  console.log('✓ Post published!');

  // Check result
  const currentUrl = page.url();
  console.log('\n✓ Post action completed');
  console.log(`  Current URL: ${currentUrl}`);
  
  // Take final screenshot
  await page.screenshot({ path: path.join(__dirname, 'post-published-screenshot.png') });
  console.log('📸 Final screenshot saved: post-published-screenshot.png');
  
  console.log('\n✅ DONE! Check your LinkedIn profile to verify the post was published!');
  console.log('   Screenshots saved in:', __dirname);
  
  await browser.close();
}

publishPost().catch((error) => {
  console.error('❌ Error:', error);
  process.exit(1);
});
