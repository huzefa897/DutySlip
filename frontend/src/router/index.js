import { createRouter, createWebHistory } from 'vue-router'
import Home from '../pages/Home.vue'
import TripList from '../pages/TripList.vue'
import CreateTrip from '../pages/CreateTrip.vue'
import InvoiceList from '../pages/InvoiceList.vue'
import InvoiceDetail from '../pages/InvoiceDetail.vue'
import CreateInvoice from '../pages/CreateInvoice.vue'
import Cars from '../pages/Cars.vue'
import Settings from '../pages/Settings.vue'
import BackupSettings from '../pages/BackupSettings.vue'
import Companies from '../pages/Companies.vue'


const routes = [
  { path: '/',                      component: Home },
  { path: '/duty-slips',            component: TripList },
  { path: '/duty-slips/create',     component: CreateTrip },
  { path: '/invoices',              component: InvoiceList },
  { path: '/invoices/create',       component: CreateInvoice },
  { path: '/invoices/:id',          component: InvoiceDetail },
  { path: '/cars',                  component: Cars },
  { path: '/settings',              component: Settings },
  { path: '/settings/backup',       component: BackupSettings },
  { path: '/companies',             component: Companies },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
