<template>
    <div class="tasks-history-page">
        <div class="history-header">
            <div class="filters">

                <SearchInput
                    v-model="searchQuery"
                    placeholder="Поиск задач..."
                />
            </div>
            <CreateTaskBtn></CreateTaskBtn>
        </div>

        <div class="tasks-table-container">
            <div class="tasks-table-wrapper">
                <div v-if="error" class="error-message">{{ error }}</div>
                <div v-else-if="filteredTasks.length === 0" class="empty-message">
                    Задачи не найдены
                </div>

                <table v-else class="tasks-table">
                    <thead>
                    <tr>
                        <th class="favorite-col"></th>
                        <th class="id-col">ID</th>
                        <th class="task-col">Задача</th>
                        <th class="status-col">Состояние</th>

                    </tr>
                    </thead>
                    <tbody>
                    <tr v-for="task in filteredTasks" :key="task.id" @click="router().push(`/tasks/${task.id}`)">
                        <td class="favorite-col">
                            <i
                                v-if="task.isCurrentUserExecutor"
                                class="bi bi-star-fill"
                                style="color: gold"
                            ></i>
                        </td>
                        <td class="id-col">TAS-{{ task.task_number }}</td>
                        <td class="task-col">
                            <div class="task-name">{{ task.name }}</div>
                        </td>
                        <td class="status-col">
                            <span class="status-badge">
                                {{ getStatusName(task.status) }}
                            </span>
                        </td>
                    </tr>
                    <tr class="fill-row">
                        <td class="favorite-col"></td>
                        <td class="id-col"></td>
                        <td class="task-col"></td>
                        <td class="status-col"></td>
                    </tr>
                    </tbody>
                </table>
            </div>
        </div>

    </div>
</template>

<script>
import {mapState} from "pinia";
import {useProjectsStore} from "@/stores/projects";
import axios from "axios";
import SearchInput from "@/components/SearchInput.vue";
import CreateTaskBtn from "@/components/CreateTaskBtn.vue";
import {useAuthStore} from "@/stores/auth";
import router from "@/router";
import {useErrorHandling} from "@/utils/ErrorHandling";

export default {
    components: {CreateTaskBtn, SearchInput},

    data() {
        return {
            tasks: [],
            error: null,
            selectedTask: null,
            searchQuery: "",
            statusFilter: "all",
            taskStatuses: [],
            statusMap: {},
            currentSprint: null,
            allProjectSprints: [],
            executorsMap: new Map(),
            prioritiesMap: new Map(),
            currentUser: useAuthStore().user
        };
    },

    computed: {
        ...mapState(useProjectsStore, ["currentProject"]),

        filteredTasks() {
            return this.tasks.filter(task => {
                const statusMatch = this.statusFilter === "all" || task.status === this.statusFilter;
                const textMatch = this.searchQuery === "" ||
                    task.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
                    (task.description && task.description.toLowerCase().includes(this.searchQuery.toLowerCase()));
                return statusMatch && textMatch;
            }).sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        },

    },
    setup() {
        const {handleApiError} = useErrorHandling();
        return {handleApiError};
    },
    mounted() {
        this.loadTasks();
        this.loadStatuses();
    },

    methods: {
        router() {
            return router
        },
        async loadTasks() {
            this.loading = true;
            this.error = null;

            try {
                await this.loadSprints();

                if (!this.currentProject || !this.allProjectSprints.length) {
                    this.tasks = [];
                    return;
                }

                const [executorsResponse, prioritiesResponse] = await Promise.all([
                    axios.get(`http://localhost:8000/project/${this.currentProject.id}/employees/`, {
                        withCredentials: true,
                    }),
                    axios.get('http://localhost:8000/task/priorities/')
                ]);

                const currentUserEmployeeIds = executorsResponse.data
                    .filter(e => e.user === this.currentUser?.id)
                    .map(e => e.id);

                this.executorsMap = new Map(executorsResponse.data.map(e => [e.id, e]));
                this.prioritiesMap = new Map(prioritiesResponse.data.map(p => [p.id, p]));

                const sprintIds = this.allProjectSprints.map(sprint => sprint.id);

                const response = await axios.get(`http://localhost:8000/task/tasks/`);
                const projectTasks = response.data.filter(task => {
                    return task.sprint_ids && task.sprint_ids.some(sprintId => sprintIds.includes(sprintId))
                });

                this.tasks = projectTasks.map(task => ({
                    ...task,
                    sprint: task.sprint_ids || [],
                    executors: task.executor_ids?.length
                        ? task.executor_ids.map(id => this.executorsMap.get(id)).filter(Boolean)
                        : [],
                    priority: task.priority ? this.prioritiesMap.get(task.priority) : null,
                    status: this.getStatusName(task.status),
                    isCurrentUserExecutor: task.executor_ids?.some(executorId =>
                        currentUserEmployeeIds.includes(executorId)
                    )
                }));

            } catch (error) {
                this.handleApiError(error);
                console.error("Ошибка загрузки задач:", error);
                this.error = "Не удалось загрузить задачи";
                this.tasks = [];
            } finally {
                this.loading = false;
            }
        },
        async loadSprints() {
            try {
                if (!this.currentProject) return;

                const response = await axios.get('http://localhost:8000/task/sprints/');

                this.allProjectSprints = response.data.filter(sprint =>
                    sprint.project === this.currentProject.id
                );
            } catch (error) {
                this.handleApiError(error);
                console.error('Ошибка при загрузке спринтов:', error);
                this.currentSprint = null;
                this.allProjectSprints = [];
            }
        },
        async loadStatuses() {
            try {
                const response = await axios.get('http://localhost:8000/task/statuses/');
                this.taskStatuses = response.data;
                this.statusMap = response.data.reduce((map, status) => {
                    map[status.id] = status.type;
                    return map;
                }, {});
            } catch (error) {
                this.handleApiError(error);
                console.error('Ошибка при загрузке статусов:', error);
            }
        },

        getStatusName(statusId) {
            return this.statusMap[statusId] || statusId;
        }


    },

};
</script>

<style scoped>
.tasks-history-page {
    max-width: 1400px;
    margin: 0 auto;
    height: calc(100vh - 40px);
    display: flex;
    flex-direction: column;
}

.history-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 15px;
    padding: 20px;
    max-height: 20px;
}

.filters {
    display: flex;
    gap: 15px;
    align-items: center;
}

.task-name {
    font-weight: 500;
    margin-bottom: 4px;
}

.status-badge {
    display: inline-block;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.85em;
    font-weight: 500;
}

.loading-message, .error-message, .empty-message {
    text-align: center;
    padding: 20px;
    color: #666;
}

.error-message {
    color: #ff4444;
}

.favorite-col {
    width: 50px;
    text-align: center;
}

.id-col {
    width: 60px;
    text-align: center;
}

.task-col {
    width: calc(100% - 410px);
    text-align: left;
}

.status-col {
    width: 250px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    text-align: center;
}

.tasks-table {
    width: 100%;
    margin-top: 10px;
    border-collapse: collapse;
    border-spacing: 0;
    background-color: #f5f5f5;
    table-layout: fixed;
    height: 100%;
}

.tasks-table tr:not(.fill-row):hover {
    background-color: #f9f9f9;
    cursor: pointer;
}

.tasks-table th,
.tasks-table td {
    padding: 8px 12px;
    border-right: 1px solid #6498F1;
    border-bottom: 1px solid #6498F1;
}

.tasks-table th {
    background-color: #AFC2E3;
    font-weight: 600;
    position: sticky;
    top: 0;
}

.tasks-table th:last-child,
.tasks-table td:last-child {
    border-right: none;
}

.tasks-table td:first-child {
    border-bottom: none;
}

.tasks-table tr:last-child td {
    border-bottom: none;
}

.tasks-table tr:hover td {
}

.column-header h3 {
    margin: 0;
    font-size: 14px;
    font-weight: 600;
    color: #333;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    width: 100%;
    text-align: center;
}

.tasks-table-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
}

.tasks-table-wrapper {
    flex: 1;
    min-height: 0;
    overflow: auto;
}

.fill-row {
    height: 100%;
}

.fill-row td {
    border-right: 1px solid #6498F1;
    border-bottom: none;
    padding: 0;
    height: 100%;
}

.fill-row td:last-child {
    border-right: none;
}
</style>