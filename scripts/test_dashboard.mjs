// Headless smoke test: loads index.html, fails on any JS error or wrong row count.
// npm i puppeteer-core && CHROME_PATH=/usr/bin/google-chrome node scripts/test_dashboard.mjs [expectedRows]
import puppeteer from 'puppeteer-core';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';

const expected = Number(process.argv[2] || 263);
const file = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'index.html');
const browser = await puppeteer.launch({ executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome', args: ['--no-sandbox'] });
const page = await browser.newPage();
const errors = [];
page.on('pageerror', (e) => errors.push(e.message));
page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
page.on('requestfailed', (r) => errors.push('request failed: ' + r.url()));
await page.goto(pathToFileURL(file).href, { waitUntil: 'load' });
await page.click('#hideNone');
await page.click('#layoutSeg button[data-v=flat]');
const n = await page.evaluate(() => window.__HOOKS__.length);
const rows = await page.$$eval('#results tbody tr', (x) => x.length);
await browser.close();
console.log({ dataRows: n, tableRows: rows, errors });
if (errors.length || n !== expected || rows !== expected) process.exit(1);
console.log('OK');
