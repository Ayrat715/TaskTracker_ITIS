import {createRouter, createWebHistory} from 'vue-router';
import RegisterComponent from "@/components/RegisterComponent.vue";
import NotFoundComponent from "@/components/NotFoundComponent.vue";
import LoginComponent from "@/components/LoginComponent.vue";
import {useAuthStore} from "@/stores/auth";
import AgileBoardComponent from "@/components/AgileBoardComponent.vue";
import ProfileComponent from "@/components/ProfileComponent.vue";
import TaskHistory from "@/components/TaskHistory.vue";


const routes = [
    {path: `/`, component: AgileBoardComponent, name: "home"},
    {path: `/register`, component: RegisterComponent, name: "register"},
    {path: `/login`, component: LoginComponent, name: "login"},
    {path: '/:pathMatch(.*)*', name: 'notFound', component: NotFoundComponent},
    {path: `/profile/:id`, component: ProfileComponent, name: "profile"},
    {path: '/tasks', name: 'TaskHistory', component: TaskHistory}

];

const router = createRouter({
    history: createWebHistory(),
    routes,
})

//, meta: { requiresAuth: true }
router.beforeEach((to) => {
    const auth = useAuthStore()
    if (to.meta.requiresAuth && !auth.isAuthenticated) {
        return {name: 'login'}
    }
})

export default router;
