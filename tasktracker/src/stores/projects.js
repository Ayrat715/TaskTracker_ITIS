import {defineStore} from 'pinia';
import axios from "axios";
import {useAuthStore} from "@/stores/auth";

export const useProjectsStore = defineStore('projects', {
    state: () => ({
        currentProject: JSON.parse(localStorage.getItem('lastViewedProject')) || null,
        currentSprint: JSON.parse(localStorage.getItem('lastViewedSprint')) || null,
        projects: [],
        sprints: []
    }),
    actions: {
        async fetchSprints() {
            try {
                const response = await axios.get(
                    `http://localhost:8000/task/sprints/`
                );
                this.sprints = response.data.filter(sprint =>
                    sprint.project === this.currentProject.id
                );
            } catch (error) {
                console.error('Ошибка загрузки спринтов:', error);
                this.sprints = [];
            }
        },
        async fetchProjects() {
            try {
                const response = await axios.get('http://localhost:8000/project/', {
                    withCredentials: true
                });
                this.projects = response.data;

                const authStore = useAuthStore();
                if (authStore.isAuthenticated) {
                    const lastProject = JSON.parse(localStorage.getItem('lastViewedProject'));
                    const lastSprint = JSON.parse(localStorage.getItem('lastViewedSprint'));

                    if (lastProject) {
                        this.currentProject = lastProject;
                    } else if (this.projects.length > 0) {
                        this.setCurrentProject(this.projects[0]);
                    }

                    if (lastSprint) {
                        this.currentSprint = lastSprint;
                    }
                }

                return this.projects;
            } catch (error) {
                console.error('Ошибка загрузки проектов:', error);
                return [];
            }
        },
        setCurrentProject(project) {
            const authStore = useAuthStore();
            if (authStore.isAuthenticated) {
                this.currentProject = project;
                localStorage.setItem('lastViewedProject', JSON.stringify(project));
            }
        },
        setCurrentSprint(sprint) {
            const authStore = useAuthStore();
            if (authStore.isAuthenticated) {
                this.currentSprint = sprint;
                localStorage.setItem('lastViewedSprint', JSON.stringify(sprint));
            }
        }
    }
});