import { createRouter, createWebHistory } from 'vue-router';
import RegisterComponent from "@/components/RegisterComponent.vue";
import NotFoundComponent from "@/components/NotFoundComponent.vue";



const routes = [
     { path: `/register`, component: RegisterComponent, name: "register"},
    { path: '/:pathMatch(.*)*', name: 'notFound', component: NotFoundComponent },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;