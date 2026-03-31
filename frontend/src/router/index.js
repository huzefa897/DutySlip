import { createRouter, createWebHistory } from 'vue-router'
import Home from '../pages/Home.vue'
import EntryList from '../pages/EntryList.vue'
import CreateEntry from '../pages/CreateEntry.vue'
import DutySlipList from '../pages/DutySlipList.vue'
import DutySlipDetail from '../pages/DutySlipDetail.vue'
import CreateDutySlip from '../pages/CreateDutySlip.vue'
import Cars from '../pages/Cars.vue'
import Settings from '../pages/Settings.vue'
import Companies from '../pages/Companies.vue'


const routes = [
  { path: '/',                    component: Home },
  { path: '/entries',             component: EntryList },
  { path: '/entries/create',      component: CreateEntry },
  { path: '/dutyslips',           component: DutySlipList },
  { path: '/dutyslips/create',    component: CreateDutySlip },
  { path: '/dutyslips/:id',       component: DutySlipDetail },
  { path: '/cars',                component: Cars },
  { path: '/settings',            component: Settings },
  { path: '/companies',           component: Companies },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})