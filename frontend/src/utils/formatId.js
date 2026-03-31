export function formatSlipId(id) {
  const year = new Date().getFullYear()
  const padded = String(id).padStart(3, '0')
  return `786-110-${year}${padded}`
}