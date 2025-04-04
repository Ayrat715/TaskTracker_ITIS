import { createRouter, createWebHistory } from 'vue-router';
import RegisterComponent from "@/components/RegisterComponent.vue";
import NotFoundComponent from "@/components/NotFoundComponent.vue";
import LoginComponent from "@/components/LoginComponent.vue";
import {useAuthStore} from "@/stores/auth";
import HomeComponent from "@/components/HomeComponent.vue";
import LogoutComponent from "@/components/LogoutComponent.vue";



const routes = [
     { path: `/`, component: HomeComponent, name: "home"},
     { path: `/register`, component: RegisterComponent, name: "register"},
     { path: `/login`, component: LoginComponent, name: "login"},
     { path: `/logout`, component: LogoutComponent, name: "logout"},
    { path: '/:pathMatch(.*)*', name: 'notFound', component: NotFoundComponent },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login' }
  }
})

export default router;