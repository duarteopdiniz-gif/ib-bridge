import pw from '/root/.npm/_npx/e41f203b7505f1fb/node_modules/playwright/index.js';
const { chromium } = pw;

const outDir = '/projects/sandbox/ib-bridge/.agents/tasks/ib-bridge-logo-blend';
const url = 'http://127.0.0.1:8000/';

const browser = await chromium.launch();

async function run(name, width, height) {
  const ctx = await browser.newContext({ viewport: { width, height }, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.waitForTimeout(400);

  await page.screenshot({ path: `${outDir}/${name}-full.png`, fullPage: true });

  const hero = await page.$('.hero');
  if (hero) await hero.screenshot({ path: `${outDir}/${name}-hero.png` });

  const footer = await page.$('.site-footer');
  if (footer) {
    await footer.scrollIntoViewIfNeeded();
    await page.waitForTimeout(200);
    await footer.screenshot({ path: `${outDir}/${name}-footer.png` });
  }

  const header = await page.$('.site-header');
  if (header) {
    await page.evaluate(() => window.scrollTo(0,0));
    await page.waitForTimeout(200);
    await header.screenshot({ path: `${outDir}/${name}-navbar.png` });
  }

  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
  console.log(`${name}: horizontalOverflow=${overflow}`);

  await page.click('.lang-btn[data-lang="es"]');
  await page.waitForTimeout(300);
  const pill = await page.$eval('.hero-pill', el => el.textContent.trim());
  console.log(`${name}: ES pill="${pill}"`);
  await page.click('.lang-btn[data-lang="en"]');
  await page.waitForTimeout(200);

  await ctx.close();
}

await run('desktop', 1280, 900);
await run('mobile', 390, 844);

await browser.close();
console.log('done');
