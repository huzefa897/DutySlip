const { app, BrowserWindow, ipcMain, shell, Tray, Menu, nativeImage } = require('electron')
const { execSync, exec, spawn } = require('child_process')
const path = require('path')
const https = require('https')

const CURRENT_VERSION = app.getVersion()
const GITHUB_OWNER = 'huzefa897'
const GITHUB_REPO  = 'DutySlip'
const APP_URL      = 'http://localhost'
const HEALTH_URL   = 'http://localhost/api/cars/'
const COMPOSE_PROJECT_NAME = 'dutyslip'

let mainWindow = null
let isQuitting  = false

// ── Mac PATH fix ──────────────────────────────────────────────
if (process.platform === 'darwin') {
  process.env.PATH = [
    '/usr/local/bin',
    '/usr/bin',
    '/bin',
    '/usr/sbin',
    '/sbin',
    '/Applications/Docker.app/Contents/Resources/bin',
    process.env.PATH
  ].join(':')
}

// ── Helpers ───────────────────────────────────────────────────
function getComposePath() {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, 'docker-compose.yml')
  }
  return path.join(__dirname, '..', 'docker-compose.yml')
}

function getEnvPath() {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, '.env')
  }
  return path.join(__dirname, '..', '.env')
}

function sendLog(message, type = '') {
  if (mainWindow) {
    mainWindow.webContents.send('log-update', { message, type })
  }
}

function sendStatus(message, state) {
  if (mainWindow) {
    mainWindow.webContents.send('status-update', { message, state })
  }
}

function isDockerInstalled() {
  try {
    execSync('docker --version', { stdio: 'ignore' })
    return true
  } catch {
    return false
  }
}

function isDockerRunning() {
  try {
    execSync('docker info', { stdio: 'ignore' })
    return true
  } catch {
    try {
      execSync('docker context inspect', { stdio: 'ignore' })
      return true
    } catch {
      return false
    }
  }
}

function areContainersRunning() {
  try {
    const result = execSync(
      `docker compose -p ${COMPOSE_PROJECT_NAME} -f "${getComposePath()}" ps --services --filter status=running`,
      { encoding: 'utf8' }
    )
    return result.trim().includes('frontend')
  } catch {
    return false
  }
}

function waitForApp(retries = 60) {
  return new Promise((resolve, reject) => {
    let attempts = 0

    function check() {
      const http = require('http')
      http.get(HEALTH_URL, (res) => {
        if (res.statusCode === 200) {
          resolve()
        } else {
          retry()
        }
      }).on('error', retry)
    }

    function retry() {
      attempts++
      if (attempts >= retries) {
        reject(new Error('App did not start in time'))
      } else {
        setTimeout(check, 2000)
      }
    }

    check()
  })
}

// ── IPC: check docker ─────────────────────────────────────────
ipcMain.handle('check-docker', async () => {
  if (!isDockerInstalled()) {
    sendStatus('Docker not installed', 'stopped')
    sendLog('Docker not found on this machine', 'error')
    return { installed: false, running: false }
  }
  if (!isDockerRunning()) {
    sendStatus('Docker not running — open Docker Desktop first', 'stopped')
    sendLog('Docker daemon not responding', 'error')
    return { installed: true, running: false }
  }
  if (areContainersRunning()) {
    sendStatus('DutySlip is running', 'running')
    sendLog('Containers already running', 'success')
    return { installed: true, running: true, containersUp: true }
  }
  sendStatus('Ready to start', 'stopped')
  sendLog('Docker ready — click Start to launch', 'info')
  return { installed: true, running: true, containersUp: false }
})

// ── IPC: start app ────────────────────────────────────────────
ipcMain.handle('start-app', async () => {
  sendLog('Checking Docker installation...', 'info')

  if (!isDockerInstalled()) {
    sendStatus('Docker not installed — download it first', 'error')
    sendLog('Docker not found', 'error')
    return { success: false }
  }

  sendLog('Docker installed ✓', 'success')
  sendLog('Checking Docker daemon...', 'info')

  if (!isDockerRunning()) {
    sendStatus('Docker is not running — open Docker Desktop first', 'error')
    sendLog('Docker daemon not responding', 'error')
    return { success: false }
  }

  sendLog('Docker running ✓', 'success')
  sendLog('Checking containers...', 'info')

  // already running — just open browser
  if (areContainersRunning()) {
    sendLog('Containers already running — opening browser', 'success')
    sendStatus('DutySlip is running', 'running')
    shell.openExternal(APP_URL)
    return { success: true }
  }

  sendLog('Containers not running — starting now...', 'info')
  sendStatus('Building and starting (first run may take 5 mins)...', 'loading')

  const composePath = getComposePath()
  const envPath = getEnvPath()

  const docker = spawn('docker', [
    'compose',
    '-p', COMPOSE_PROJECT_NAME,
    '-f', composePath,
    '--env-file', envPath,
    'up', '-d', '--build', '--remove-orphans'
  ])

  docker.stdout.on('data', (data) => {
    const lines = data.toString().split('\n').filter(l => l.trim())
    lines.forEach(line => {
      if (line.includes('Pulling'))  { sendStatus('Downloading images...', 'loading');  sendLog(line.trim(), 'info') }
      if (line.includes('Building')) { sendStatus('Building app...', 'loading');        sendLog(line.trim(), 'info') }
      if (line.includes('Starting')) { sendStatus('Starting containers...', 'loading'); sendLog(line.trim(), 'warning') }
      if (line.includes('Started'))  { sendStatus('Almost ready...', 'loading');        sendLog(line.trim(), 'success') }
      if (line.includes('Error') || line.includes('error')) {
        sendLog(line.trim(), 'error')
      }
    })
  })

  docker.stderr.on('data', (data) => {
    const lines = data.toString().split('\n').filter(l => l.trim())
    lines.forEach(line => {
      if (line.includes('Pulling'))  { sendLog('Pulling ' + line.split('Pulling')[1]?.trim(), 'info') }
      if (line.includes('Building')) { sendLog('Building...', 'info') }
      if (line.includes('Starting')) { sendLog('Starting ' + line.split('Starting')[1]?.trim(), 'warning') }
      if (line.includes('error') || line.includes('Error')) {
        sendLog(line.trim(), 'error')
      }
    })
  })

  docker.on('close', (code) => {
    if (code !== 0) {
      sendStatus('Failed to start — check Docker is running', 'error')
      sendLog(`Docker exited with code ${code}`, 'error')
      return
    }

    sendStatus('Waiting for app to be ready...', 'loading')
    sendLog('Containers started — waiting for health check...', 'info')

    waitForApp(60)
      .then(() => {
        sendStatus('DutySlip is running', 'running')
        sendLog('App is ready ✓', 'success')
        shell.openExternal(APP_URL)
      })
      .catch(() => {
        sendStatus('Startup timed out — try again', 'error')
        sendLog('Health check timed out', 'error')
      })
  })

  return { success: true }
})

// ── IPC: stop app ─────────────────────────────────────────────
ipcMain.handle('stop-app', async () => {
  const composePath = getComposePath()
  const envPath = getEnvPath()

  sendLog('Stopping containers...', 'warning')

  exec(
    `docker compose -p ${COMPOSE_PROJECT_NAME} -f "${composePath}" --env-file "${envPath}" down`,
    (error) => {
      if (error) {
        sendStatus('Failed to stop containers', 'error')
        sendLog('Failed to stop containers', 'error')
      } else {
        sendStatus('DutySlip stopped', 'stopped')
        sendLog('Containers stopped ✓', 'success')
      }
    }
  )

  return { success: true }
})

// ── IPC: check for updates ────────────────────────────────────
ipcMain.handle('check-updates', async () => {
  return new Promise((resolve) => {
    const options = {
      hostname: 'api.github.com',
      path:     `/repos/${GITHUB_OWNER}/${GITHUB_REPO}/releases/latest`,
      headers:  { 'User-Agent': 'DutySlip-App' },
    }

    https.get(options, (res) => {
      let data = ''
      res.on('data', chunk => data += chunk)
      res.on('end', () => {
        try {
          const release = JSON.parse(data)
          const latest = release.tag_name?.replace('v', '')
          const current = CURRENT_VERSION
          const updateAvailable = latest && latest !== current
          resolve({
            current,
            latest,
            updateAvailable,
            releaseUrl: release.html_url,
          })
        } catch {
          resolve({ error: true })
        }
      })
    }).on('error', () => resolve({ error: true }))
  })
})

// ── IPC: open browser ─────────────────────────────────────────
ipcMain.handle('open-browser', (_, url) => {
  shell.openExternal(url)
})

// ── IPC: get version ──────────────────────────────────────────
ipcMain.handle('get-version', () => CURRENT_VERSION)

// ── Create window ─────────────────────────────────────────────
function createWindow() {
  mainWindow = new BrowserWindow({
    width:           360,
    height:          620,
    resizable:       false,
    titleBarStyle:   'hiddenInset',
    backgroundColor: '#030712',
    webPreferences: {
      preload:          path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration:  false,
    },
  })

  mainWindow.loadFile(path.join(__dirname, 'index.html'))

  mainWindow.on('close', (e) => {
    if (!isQuitting) {
      e.preventDefault()
      mainWindow.hide()
    }
  })
}

// ── App ready ─────────────────────────────────────────────────
app.whenReady().then(() => {
  createWindow()

  const trayIcon = nativeImage.createFromPath(
    path.join(__dirname, 'assets', 'tray.png')
  )
  const tray = new Tray(trayIcon.resize({ width: 16, height: 16 }))

  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Open DutySlip',
      click: () => {
        mainWindow.show()
        mainWindow.focus()
      }
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => {
        isQuitting = true
        app.quit()
      }
    }
  ])

  tray.setToolTip('DutySlip')
  tray.setContextMenu(contextMenu)
  tray.on('click', () => {
    mainWindow.show()
    mainWindow.focus()
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})

app.on('activate', () => {
  if (mainWindow) {
    mainWindow.show()
    mainWindow.focus()
  }
})

app.on('before-quit', () => {
  isQuitting = true
})
