import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/animals/gallery'
    },
    {
      path: '/animals/gallery',
      name: 'AnimalGallery',
      component: () => import('@/views/AnimalGallery.vue'),
      meta: { title: '待领养小动物' }
    },
    {
      path: '/animals/apply/:id',
      name: 'AnimalApply',
      component: () => import('@/views/AnimalApply.vue'),
      meta: { title: '领养申请' }
    }
  ]
})

router.beforeEach((to, _from, next) => {
  if (to.meta.title) {
    document.title = `${to.meta.title} - 流浪猫狗救助领养中心`
  }
  next()
})

export default router
