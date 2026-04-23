import { createRouter, createWebHistory } from 'vue-router'
import LandingPage from '../pages/LandingPage.vue'
import NewInvoicePage from '../pages/NewInvoicePage.vue'
import InvoiceDetailPage from '../pages/InvoiceDetailPage.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: LandingPage
  },
  {
    path: '/new-invoice',
    name: 'NewInvoice',
    component: NewInvoicePage
  },
  {
    path: '/invoice/:id',
    name: 'InvoiceDetail',
    component: InvoiceDetailPage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
