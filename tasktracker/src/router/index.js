import {createRouter, createWebHistory} from 'vue-router';
import RegisterComponent from "@/components/RegisterComponent.vue";
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
import SprintCreate from "@/components/SprintCreate.vue";
import GroupDetails from "@/components/GroupDetails.vue";
import AddMember from "@/components/AddMember.vue";
import GroupList from "@/components/GroupList.vue";
import StartPage from "@/components/StartPage.vue";
import {useProjectsStore} from "@/stores/projects";
import AccessDenied from "@/components/AccessDenied.vue";
import NotFound from "@/components/NotFound.vue";
import NetworkError from "@/components/NetworkError.vue";
import {useErrorStore} from "@/stores/error";
import TaskCreate from "@/components/TaskCreate.vue";


const routes = [
    {path: `/`, component: AgileBoardComponent, name: "home", meta: {requiresAuth: true, requiresProjects: true}},
    {path: `/start`, component: StartPage, name: "start", meta: {requiresAuth: true}},
    {path: `/register`, component: RegisterComponent, name: "register", meta: {guestOnly: true}},
    {path: `/login`, component: LoginComponent, name: "login", meta: {guestOnly: true}},
    {path: `/user/:id`, component: ProfileComponent, name: "profile", meta: {requiresAuth: true}},
    {path: '/tasks', name: 'TaskHistory', component: TaskHistory, meta: {requiresAuth: true}},
    {path: '/tasks/:id', name: 'task-details', component: TaskDetails, meta: {requiresAuth: true}},
    {path: '/tasks/:id/edit', name: 'task-edit', component: TaskEdit, meta: {requiresAuth: true}},
    {path: '/project/create', name: 'project-create', component: ProjectCreate, meta: {requiresAuth: true}},
    {path: '/project/:id', name: 'project-detail', component: ProjectDetails, meta: {requiresAuth: true}},
    {path: '/projects', name: 'project-list', component: ProjectList, meta: {requiresAuth: true}},
    {path: '/project/:id/edit', name: 'project-edit', component: ProjectEdit, meta: {requiresAuth: true}},
    {path: '/group/create', name: 'group-create', component: GroupCreate, meta: {requiresAuth: true}},
    {path: '/project/:id/sprint/create', name: 'sprint-create', component: SprintCreate, meta: {requiresAuth: true}},
    {path: '/group/:id/add-member', name: 'add-member', component: AddMember, props: true, meta: {requiresAuth: true}},
    {path: '/groups', name: 'group-list', component: GroupList, props: true, meta: {requiresAuth: true}},
    {path: '/access-denied', name: 'access-denied', component: AccessDenied},
    {path: '/network-error', name: 'network-error', component: NetworkError},
    {path: '/not-found', name: 'not-found', component: NotFound},
    {path: '/:pathMatch(.*)*', redirect: '/not-found'},
    {path: '/task/create', name: 'task-create', component: TaskCreate},
    {
        path: '/group/:id',
        component: GroupDetails,
        children: [
            {
                path: '',
                name: 'group-members',
                component: GroupDetails, meta: {requiresAuth: true}
            },
            {
                path: 'projects',
                name: 'group-projects',
                component: GroupDetails, meta: {requiresAuth: true}
            },
            {
                path: 'add-member',
                name: 'group-add-member',
                component: AddMember, meta: {requiresAuth: true}
            }
        ], meta: {requiresAuth: true}
    },
    {
        path: '/project/:id',
        component: ProjectDetails,
        children: [
            {
                path: '',
                name: 'project-details',
                component: ProjectDetails, meta: {requiresAuth: true}
            },
            {
                path: 'roles',
                name: 'project-roles',
                component: GroupDetails, meta: {requiresAuth: true}
            },
            {
                path: 'team',
                name: 'project-team',
                component: GroupDetails, meta: {requiresAuth: true}
            }
        ]
    },


];

const router = createRouter({
    history: createWebHistory(),
    routes,
})
router.beforeEach(async (to) => {
    const auth = useAuthStore();
    const projectsStore = useProjectsStore();
    const errorStore = useErrorStore();

    const errorPages = ['access-denied', 'not-found', 'network-error']
    if (errorPages.includes(to.name)) {
        if (!errorStore.isErrorPageAllowed(to.name)) {
            return {name: 'home'}
        }
        errorStore.reset()
        return
    } else {
        errorStore.reset()
    }
    try {
        const isAuthenticated = await auth.checkAuth();

        if (to.meta.guestOnly && isAuthenticated) {
            return {name: 'home'}
        }
        if (to.meta.requiresAuth && !isAuthenticated) {
            return {name: 'login', query: {redirect: to.fullPath}};
        }
        if (to.meta.requiresProjects) {
            if (projectsStore.projects.length === 0) {
                await projectsStore.fetchProjects();
            }

            if (projectsStore.projects.length === 0) {
                return {name: 'start'};
            }
        }
    } catch (error) {
        console.error('Auth check error:', error);
    }
});
export default router;