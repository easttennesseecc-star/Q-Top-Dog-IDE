import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as os from 'os';

// Simpler e2e test focused on core functionality
test('background full flow: upload, export, import', async ({ page }) => {
  // Assumes dev server is running locally on 1431
  await page.goto('http://localhost:1431/', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(1000);
  
  // navigate to settings tab
  const settingsBtn = page.getByRole('button', { name: /Settings/i });
  await expect(settingsBtn).toBeVisible({ timeout: 10000 });
  await settingsBtn.click();
  
  // wait for settings panel to load
  await page.waitForTimeout(500);
  
  // Test 1: Switch to image kind and upload
  const imagePresetBtn = page.getByRole('button', { name: /Blurred Photo/i });
  await expect(imagePresetBtn).toBeVisible({ timeout: 10000 });
  await imagePresetBtn.click();
  
  // Create a minimal 10x10 PNG file for testing
  const tmpDir = os.tmpdir();
  const testImagePath = `${tmpDir}/test-image-${Date.now()}.png`;
  
  const pngHeader = Buffer.from([
    137, 80, 78, 71, 13, 10, 26, 10, // PNG signature
    0, 0, 0, 13, 73, 72, 68, 82, 0, 0, 0, 10, 0, 0, 0, 10, 8, 2, 0, 0, 0, 2, 80, 88, 229,
    0, 0, 0, 29, 116, 82, 78, 83, 0, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    0, 0, 0, 14, 73, 68, 65, 84, 8, 215, 99, 248, 207, 192, 0, 0, 0, 0, 1, 0, 1, 179, 235, 65, 200,
    0, 0, 0, 0, 73, 69, 78, 68, 174, 66, 96, 130
  ]);
  fs.writeFileSync(testImagePath, pngHeader);
  
  // Upload the test image
  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles(testImagePath);
  
  // Wait for the image to be processed
  await page.waitForTimeout(2000);
  
  // Verify upload was successful - image preview should be visible
  const imagePreview = page.locator('img[alt="preview"]');
  await expect(imagePreview).toBeVisible({ timeout: 10000 });
  
  // Test 2: Export settings
  const exportBtn = page.getByRole('button', { name: /Export/i });
  await expect(exportBtn).toBeVisible({ timeout: 5000 });
  
  // Listen for download and click export
  const downloadPromise = page.waitForEvent('download');
  await exportBtn.click();
  const download = await downloadPromise;
  
  // Verify download filename
  const filename = download.suggestedFilename();
  expect(filename).toMatch(/topdog-background\.(zip|json)/);
  
  // Save the exported file
  const exportedPath = `${tmpDir}/${filename}`;
  await download.saveAs(exportedPath);
  expect(fs.existsSync(exportedPath)).toBe(true);
  
  // Test 3: Verify export file is valid
  const exportContent = fs.readFileSync(exportedPath, 'utf-8');
  expect(exportContent.length).toBeGreaterThan(0);
  
  // Test 4: Import the exported settings
  const importLabel = page.locator('label').filter({ hasText: /Import/i });
  await expect(importLabel).toBeVisible({ timeout: 5000 });
  
  const importInput = importLabel.locator('input[type="file"]');
  await importInput.setInputFiles(exportedPath);
  
  // Wait for import to complete
  await page.waitForTimeout(2000);
  
  // Verify settings are still visible
  await expect(page.getByRole('button', { name: /Export/i })).toBeVisible({ timeout: 5000 });
  
  // Clean up temp files
  try { fs.unlinkSync(testImagePath); } catch (_) {}
  try { fs.unlinkSync(exportedPath); } catch (_) {}
  
  // Test passed
  expect(true).toBeTruthy();
});
