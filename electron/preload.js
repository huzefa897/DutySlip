const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('dutyslip', {
  checkDocker:   () => ipcRenderer.invoke('check-docker'),
  startApp:      () => ipcRenderer.invoke('start-app'),
  stopApp:       () => ipcRenderer.invoke('stop-app'),
  checkUpdates:  () => ipcRenderer.invoke('check-updates'),
  openBrowser:   (url) => ipcRenderer.invoke('open-browser', url),
  getVersion:    () => ipcRenderer.invoke('get-version'),
  onStatus:      (cb) => ipcRenderer.on('status-update', (_, msg) => cb(msg)),
  onLog:         (cb) => ipcRenderer.on('log-update', (_, msg) => cb(msg)),
})