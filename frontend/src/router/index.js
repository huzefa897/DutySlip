import { createRouter, createWebHistory } from 'vue-router'
import EntryList from '../pages/EntryList.vue'
import CreateEntry from '../pages/CreateEntry.vue'
import DutySlipList from '../pages/DutySlipList.vue'
import DutySlipDetail from '../pages/DutySlipDetail.vue'
import CreateDutySlip from '../pages/CreateDutySlip.vue'

const routes = [
  { path: '/',                    component: EntryList },
  { path: '/entries/create',      component: CreateEntry },
  { path: '/dutyslips',           component: DutySlipList },
  { path: '/dutyslips/create',    component: CreateDutySlip },
  { path: '/dutyslips/:id',       component: DutySlipDetail },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})