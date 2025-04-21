import {defineStore} from 'pinia';
import axios from "axios";

export const useProjectsStore = defineStore('projects', {
    state: () => ({
        currentProject: null,
        projects: []
    }),
    actions: {
        async fetchProjects() {
            try {
                const response = await axios.get('http://localhost:8000/project/list/', {
                    withCredentials: true
                });
                this.projects = response.data;

                if (this.projects.length > 0 && !this.currentProject) {
                    this.setCurrentProject(this.projects[0]);
                }

                return this.projects;
            } catch (error) {
                console.error('Ошибка загрузки проектов:', error);
                return [];
            }
        },
        setCurrentProject(project) {
            this.currentProject = project;
            localStorage.setItem('lastViewedProject', project.id.toString());
        }
    }
});