import {defineStore} from 'pinia';
import axios from "axios";

export const useTasksStore = defineStore('tasks', {
    state: () => ({
        priorities: [],
    }),
    actions: {
        async fetchPriorities() {
            try {
                this.priorities = await axios.get('http://localhost:8000/task/priorities');
            } catch (error) {
                console.error('Ошибка загрузки приоритетов:', error);
            }
        },
        setProjectTaskNumbers(taskNumbers) {
            this.projectTaskNumbers = taskNumbers;
        }
    }
});