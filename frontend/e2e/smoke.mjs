import puppeteer from 'puppeteer-core'
import fs from 'fs'

async function findChrome() {
  const candidates = [
    'C:/Program Files/Google/Chrome/Application/chrome.exe',
    'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
    'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
    'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
  ]
  for (const p of candidates) {
    try {
      if (fs.existsSync(p)) return p
    } catch {}
  }
  return null
}

async function main() {
  const executablePath = await findChrome()
  const browser = await puppeteer.launch({
    executablePath: executablePath || undefined,
    headless: 'new',
    args: ['--no-sandbox','--disable-setuid-sandbox']
  })
  const page = await browser.newPage()
  const base = 'http://127.0.0.1:3000'
  const routes = ['/', '/dashboard', '/bills', '/ai-assistant', '/community']
  for (const r of routes) {
    await page.goto(base + r, { waitUntil: 'domcontentloaded', timeout: 20000 })
    const content = await page.content()
    if (!content || content.length < 100) throw new Error('Content too short for ' + r)
    console.log('OK', r)
  }
  await browser.close()
}

main().catch((e) => { console.error(e); process.exit(1) })
