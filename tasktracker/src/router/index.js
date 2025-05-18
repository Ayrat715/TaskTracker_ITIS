import {createRouter, createWebHistory} from 'vue-router';
import RegisterComponent from "@/components/RegisterComponent.vue";
import NotFoundComponent from "@/components/NotFoundComponent.vue";
import LoginComponent from "@/components/LoginComponent.vue";
import {useAuthStore} from "@/stores/auth";
import AgileBoardComponent from "@/components/AgileBoardComponent.vue";
import ProfileComponent from "@/components/ProfileComponent.vue";
import TaskHistory from "@/components/TaskHistory.vue";
import TaskDetails from "@/components/TaskDetails.vue";
import TaskEdit from "@/components/TaskEdit.vue";
import ProjectCreate from "@/components/ProjectCreate.vue";
import ProjectDetails from "@/components/ProjectDetails.vue";
import ProjectList from "@/components/ProjectList.vue";
import ProjectEdit from "@/components/ProjectEdit.vue";
import GroupCreate from "@/components/GroupCreate.vue";


const routes = [
    {path: `/`, component: AgileBoardComponent, name: "home", meta: {requiresAuth: true}},
    {path: `/register`, component: RegisterComponent, name: "register", meta: {guestOnly: true}},
    {path: `/login`, component: LoginComponent, name: "login", meta: {guestOnly: true}},
    {path: '/:pathMatch(.*)*', name: 'notFound', component: NotFoundComponent},
    {path: `/user/:id`, component: ProfileComponent, name: "profile", meta: {requiresAuth: true}},
    {path: '/tasks', name: 'TaskHistory', component: TaskHistory, meta: {requiresAuth: true}},
    {path: '/tasks/:id', name: 'task-details', component: TaskDetails, meta: {requiresAuth: true}},
    {path: '/tasks/:id/edit', name: 'task-edit', component: TaskEdit, meta: {requiresAuth: true}},
    {path: '/project/create', name: 'project-create', component: ProjectCreate, meta: {requiresAuth: true}},
    {path: '/project/:id', name: 'project-detail', component: ProjectDetails, meta: {requiresAuth: true}},
    {path: '/projects', name: 'project-list', component: ProjectList, meta: {requiresAuth: true}},
    {path: '/project/:id/edit', name: 'project-edit', component: ProjectEdit, meta: {requiresAuth: true}},
    {path: '/group/create', name: 'group-create', component: GroupCreate, meta: {requiresAuth: true}},

];

const router = createRouter({
    history: createWebHistory(),
    routes,
})
router.beforeEach(async (to) => {
    const auth = useAuthStore();

    try {
        const isAuthenticated = await auth.checkAuth();

        if (to.meta.guestOnly && isAuthenticated) {
            return {name: 'home'}
        }
        if (to.meta.requiresAuth && !isAuthenticated) {
            return {name: 'login', query: {redirect: to.fullPath}};
        }
    } catch (error) {
        console.error('Auth check error:', error);
    }
});
export default router;