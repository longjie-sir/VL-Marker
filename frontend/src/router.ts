import { createRouter, createWebHistory } from 'vue-router'
import SitesView from './views/SitesView.vue'
import AboutView from './views/AboutView.vue'

const routes = [
  {
    path: '/',
    redirect: '/sites'
  },
  {
    path: '/sites',
    name: 'sites',
    component: SitesView
  },
  {
    path: '/about',
    name: 'about',
    component: AboutView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router