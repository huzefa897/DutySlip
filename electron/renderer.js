const statusText = document.getElementById('status-text')
const dot        = document.getElementById('dot')
const btnStart   = document.getElementById('btn-start')
const btnStop    = document.getElementById('btn-stop')
const btnDocker  = document.getElementById('btn-docker')
const btnUpdate  = document.getElementById('btn-update')
const versionEl  = document.getElementById('version')
const updateBadge = document.getElementById('update-badge')

// ── Set version ───────────────────────────────────────────────
window.dutyslip.getVersion().then(v => {
  versionEl.textContent = `v${v}`
})


// ── Status updates from main process ─────────────────────────
window.dutyslip.onStatus(({ message, state }) => {
  statusText.textContent = message
  dot.className = 'dot'
  if (state === 'running')  { dot.classList.add('green');  addLog(message, 'success') }
  if (state === 'loading')  { dot.classList.add('yellow'); addLog(message, 'warning') }
  if (state === 'stopped')  { dot.classList.add('red');    addLog(message) }
  if (state === 'error')    { dot.classList.add('red');    addLog(message, 'error') }

  const isRunning = state === 'running'
  const isLoading = state === 'loading'
  btnStart.disabled = isLoading
  btnStop.disabled  = !isRunning && !isLoading
})



// ── Start ─────────────────────────────────────────────────────
btnStart.addEventListener('click', async () => {
  btnStart.disabled = true
  addLog('Starting application...', 'info')
  await window.dutyslip.startApp()
})
// ── Stop ──────────────────────────────────────────────────────
btnStop.addEventListener('click', async () => {
  btnStop.disabled = true
  addLog('Stopping application...', 'warning')
  statusText.textContent = 'Stopping...'
  dot.className = 'dot yellow'
  await window.dutyslip.stopApp()
})

// ── Download Docker ───────────────────────────────────────────
btnDocker.addEventListener('click', () => {
  window.dutyslip.openBrowser('https://www.docker.com/products/docker-desktop')
})

// ── Check for updates ─────────────────────────────────────────
btnUpdate.addEventListener('click', async () => {
  btnUpdate.disabled = true
  btnUpdate.querySelector('span:first-child').textContent = '...'
  addLog('Checking for updates...', 'info')
  statusText.textContent = 'Checking for updates...'
  dot.className = 'dot yellow'

  const result = await window.dutyslip.checkUpdates()

  btnUpdate.disabled = false
  btnUpdate.querySelector('span:first-child').textContent = '↑'

  if (result.error) {
    addLog('Could not check for updates', 'error')
    statusText.textContent = 'Could not check for updates.'
    dot.className = 'dot red'
    return
  }

  if (result.updateAvailable) {
    addLog(`Update available — ${result.latest}`, 'warning')
    statusText.textContent = `Update available — ${result.latest}`
    dot.className = 'dot yellow'
    updateBadge.style.display = 'inline'
    updateBadge.style.cursor = 'pointer'
    updateBadge.addEventListener('click', () => {
      window.dutyslip.openBrowser(result.releaseUrl)
    })
  } else {
    addLog(`Up to date — v${result.current}`, 'success')
    statusText.textContent = `Up to date — v${result.current}`
    dot.className = 'dot green'
  }
})
const logBox = document.getElementById('log-box')

function addLog(message, type = '') {
  const line = document.createElement('div')
  line.className = `log-line ${type}`

  // timestamp
  const time = new Date().toLocaleTimeString('en-AU', {
    hour: '2-digit', minute: '2-digit', second: '2-digit'
  })

  line.textContent = `[${time}] ${message}`
  logBox.appendChild(line)

  // auto scroll to bottom
  logBox.scrollTop = logBox.scrollHeight

  // keep max 50 lines
  while (logBox.children.length > 50) {
    logBox.removeChild(logBox.firstChild)
  }
}

// ── Initial status check ──────────────────────────────────────
addLog('Checking Docker status...', 'info')
window.dutyslip.onLog(({ message, type }) => {
  addLog(message, type)
})
window.dutyslip.checkDocker()