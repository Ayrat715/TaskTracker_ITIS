<template>
    <div class="task-details-page">
        <div class="history-header">
            <div class="filters">
                <div class="search-container">
                    <SearchInput
                        v-model="searchQuery"
                        placeholder="Поиск задач..."
                        @focus="showResults = true"
                    />
                    <div v-if="showResults && filteredTasks.length" class="search-results">
                        <div
                            v-for="result in filteredTasks"
                            :key="result.id"
                            class="search-result-item"
                            @click="navigateToTask(result)"
                        >
                            {{ result.name }} (TAS-{{ result.task_number }})
                        </div>
                    </div>
                    <div v-else></div>

                </div>
            </div>
            <CreateTaskBtn></CreateTaskBtn>
        </div>

        <div class="task-content">
            <div class="left-column">
                <div class="task-main-info">
                    <h1>{{ task.name }}
                        <button @click="editTask" class="edit-btn"><i class="bi bi-pencil"></i></button>
                        <button @click="deleteTask" class="delete-btn"><i class="bi bi-trash3"></i></button>
                    </h1>

                    <div class="task-meta">
                        <span class="task-id">TAS-{{ task.task_number }}</span>
                        <span class="task-status">
                            {{ task.status?.type || 'Статус отсутствует' }}
                        </span>
                    </div>
                </div>

                <div class="task-section">
                    <h3>Описание</h3>
                    <p class="description-text">{{ task.description || 'Описание отсутствует' }}</p>
                </div>

                <div class="task-section" v-if="task.comments?.length">
                    <h3>Комментарии ({{ task.comments.length }})</h3>
                    <div class="comments-list">
                        <div v-for="comment in task.comments" :key="comment.id" class="comment">
                            <div class="comment-header">
                                <span class="comment-author">{{ comment.author.name }}</span>
                                <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
                            </div>
                            <div class="comment-text">{{ comment.body }}</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="right-column">
                <div class="details-section">
                    <h3>Детали задачи</h3>
                    <div class="details-list">
                        <div class="detail-item">
                            <label>Приоритет</label>
                            <span>{{ task.priority?.type || 'Не указан' }}</span>
                        </div>

                        <div class="detail-item">
                            <label>Автор</label>
                            <span class="author" @click.stop="goToUser(task.author?.user)">
                                {{ task.author?.user_name }}
                            </span>
                        </div>

                        <div class="detail-item">
                            <label>Исполнители</label>
                            <span class="executors">
                                <template v-if="task.executors?.length">
                                    <span
                                        v-for="executor in task.executors"
                                        :key="executor.id"
                                        class="executor"
                                        @click.stop="goToUser(executor.user)"
                                    >{{ executor.user_name }}
                                    </span>
                                </template>
                                <span v-else>не определен</span>
                            </span>
                        </div>

                        <div class="detail-item">
                            <label>Дата создания</label>
                            <span>{{ formatDate(task.given_time) || 'Не установлена' }}</span>
                        </div>

                        <div class="detail-item">
                            <label>Дедлайн</label>
                            <span>{{ formatDate(task.end_time) || 'Не установлен' }}</span>
                        </div>

                        <div class="detail-item">
                            <label>Длительность</label>
                            <span>{{ task.predicted_duration || 'Не установлена' }}</span>
                        </div>

                        <div class="detail-item">
                            <label>Спринты</label>
                            <span>{{ sprintsNames || 'Не установлены' }}</span>
                        </div>

                        <div class="detail-item">
                            <label>Проект</label>
                            <span>{{ currentProject?.name || 'Не установлен' }}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>


<script>
import axios from 'axios'
import {useProjectsStore} from "@/stores/projects";
import CreateTaskBtn from "@/components/CreateTaskBtn.vue";
import SearchInput from "@/components/SearchInput.vue";
import {useErrorHandling} from "@/utils/ErrorHandling";

export default {
    name: 'TaskDetailsPage',
    components: {SearchInput, CreateTaskBtn},
    data() {
        return {
            task: {},
            error: null,
            searchQuery: '',
            searchResults: [],
            showResults: false,
            allTasks: [],
            sprints: [],
            currentSprint: null,
            tasks: []
        }
    },
    watch: {
        searchQuery(newVal) {
            this.showResults = newVal.length > 0;
        },
        '$route.params.id': {
            immediate: true,

        }
    },
    async mounted() {
        const projectsStore = useProjectsStore();
        this.currentProject = projectsStore.currentProject;
        await this.loadSprints();
        await this.loadProjectTasks();
        await this.loadTask()
        document.addEventListener('click', this.handleClickOutside);

    },
    beforeUnmount() {
        document.removeEventListener('click', this.handleClickOutside);
    },
    setup() {
        const {handleApiError} = useErrorHandling();
        return {handleApiError};
    },
    computed: {
        sprintsNames() {
            return this.task.sprints?.map(s => s.name).join(', ') || 'Не включена в спринт'
        },
        filteredTasks() {
            if (!this.searchQuery) return [];
            const searchLower = this.searchQuery.toLowerCase();

            return this.allTasks.filter(task => {
                const matchesSearch =
                    task.name.toLowerCase().includes(searchLower) ||
                    (task.description && task.description.toLowerCase().includes(searchLower));
                return matchesSearch && task.id !== this.task.id;
            });
        }

    },
    methods: {
        resetTaskState() {
            this.task = {};
            this.error = null;
            this.searchQuery = '';
            this.showResults = false;
        },
        async loadTask() {
            try {
                this.resetTaskState();

                const taskResponse = await axios.get(`http://localhost:8000/task/tasks/${this.$route.params.id}/`);

                if (!taskResponse.data.sprint_ids || taskResponse.data.sprint_ids.length === 0) {
                    const error = new Error('Задача не привязана к спринту');
                    error.response = {status: 404};
                    throw error;
                }

                const firstSprintId = taskResponse.data.sprint_ids[1];

                const sprintsResponse = await axios.get(`http://localhost:8000/task/sprints/`);
                const sprint = sprintsResponse.data.find(s => s.id === firstSprintId);
                if (!sprint) {
                    const error = new Error('Спринт не найден');
                    error.response = {status: 404};
                    throw error;
                }
                const projectId = sprint.project;


                const [executorsRes, prioritiesRes, statusesRes, sprintsRes] = await Promise.all([
                    axios.get(`http://localhost:8000/project/${projectId}/employees/`, {
                        withCredentials: true,
                    }),
                    axios.get('http://localhost:8000/task/priorities/'),
                    axios.get('http://localhost:8000/task/statuses/'),
                    axios.get(`http://localhost:8000/task/sprints/`)
                ]);
                 if ((await executorsRes).status === 403) {
                    const error = new Error('Access denied to project');
                    error.response = {status: 403};
                    throw error;
                }


                const sprintsMap = new Map(sprintsRes.data.map(s => [s.id, s]));
                const executorsMap = new Map(executorsRes.data.map(e => [e.id, e]));
                const prioritiesMap = new Map(prioritiesRes.data.map(p => [p.id, p]));
                const statusesMap = new Map(statusesRes.data.map(s => [s.id, s]));

                this.task = {
                    ...taskResponse.data,
                    sprints: taskResponse.data.sprint_ids?.length
                        ? taskResponse.data.sprint_ids.map(id => sprintsMap.get(id)).filter(Boolean)
                        : [],
                    executors: taskResponse.data.executor_ids?.length
                        ? taskResponse.data.executor_ids.map(id => executorsMap.get(id)).filter(Boolean)
                        : [],
                    priority: taskResponse.data.priority ? prioritiesMap.get(taskResponse.data.priority) : null,
                    status: taskResponse.data.status ? statusesMap.get(taskResponse.data.status) : null,
                    author: taskResponse.data.author ? executorsMap.get(taskResponse.data.author) : null,
                    projectId
                };

            } catch (error) {
                this.handleApiError(error);
                console.error('Ошибка загрузки задачи:', error);

                if (error.message === 'Задача не привязана к спринту') {
                    this.error = 'Задача не привязана к спринту. Невозможно определить проект.';
                } else {
                    this.error = 'Не удалось загрузить задачу';
                }
            }
        },

        async deleteTask() {
            if (confirm('Вы уверены, что хотите удалить задачу?')) {
                try {
                    await axios.delete(`http://localhost:8000/task/tasks/${this.task.id}/`)
                    this.$router.push('/')
                } catch (error) {
                    alert('Ошибка при удалении задачи')
                }
            }
        },

        editTask() {
            this.$router.push(`/tasks/${this.task.id}/edit`)
        },

        formatDate(dateString) {
            if (!dateString) return null
            return new Date(dateString).toLocaleDateString('ru-RU')
        },

        async loadProjectTasks() {
            try {
                const response = await axios.get(`http://localhost:8000/task/tasks/`);
                this.allTasks = response.data;
                const currentProjectSprintIds = this.sprints.map(s => s.id);


                this.allTasks = this.allTasks.filter(task =>
                    task.sprint_ids?.some(sprintId =>
                        currentProjectSprintIds.includes(sprintId)
                    )
                );


            } catch (error) {
                this.handleApiError(error);
                console.error('Ошибка загрузки задач:', error);
                this.allTasks = [];
            }
        },

        async loadSprints() {
            try {
                if (!this.currentProject?.id) {
                    console.log('Проект не выбран, загрузка спринтов пропущена');
                    this.sprints = [];
                    this.currentSprint = null;
                    return;
                }

                const response = await axios.get('http://localhost:8000/task/sprints/');
                const allSprints = response.data;

                this.sprints = allSprints.filter(sprint =>
                    sprint.project === this.currentProject.id
                );

                this.sprints.sort((a, b) =>
                    new Date(b.start_time) - new Date(a.start_time)
                );

                const projectsStore = useProjectsStore();
                let selectedSprint = projectsStore.currentSprint;

                if (selectedSprint) {
                    const sprintExists = this.sprints.some(s =>
                        s.id === selectedSprint.id &&
                        s.project === this.currentProject.id
                    );

                    if (!sprintExists) {
                        selectedSprint = null;
                        projectsStore.setCurrentSprint(null);
                    }
                }

                if (!selectedSprint && this.sprints.length > 0) {
                    const now = new Date();

                    selectedSprint = this.sprints.find(sprint => {
                        const start = new Date(sprint.start_time);
                        const end = new Date(sprint.end_time);
                        return start <= now && now <= end;
                    });

                    if (!selectedSprint) {
                        selectedSprint = this.sprints[0];
                    }

                    projectsStore.setCurrentSprint(selectedSprint);
                }

                this.currentSprint = selectedSprint?.id || null;

                if (this.currentSprint) {
                    await this.loadProjectTasks();
                } else {
                    this.tasks = [];
                }

            } catch (error) {
                this.handleApiError(error);
                console.error('Ошибка при загрузке спринтов:', error);
                this.sprints = [];
                this.currentSprint = null;

                const projectsStore = useProjectsStore();
                projectsStore.setCurrentSprint(null);
            }
        },
        navigateToTask(task) {
            this.$router.push(`/tasks/${task.id}`);
            this.showResults = false;
            this.searchQuery = '';
        },
        handleClickOutside(e) {
            const searchContainer = this.$el.querySelector('.search-container');
            if (!searchContainer.contains(e.target)) {
                this.showResults = false;
            }
        },
        goToUser(userId) {
            this.$router.push(`/user/${userId}`);
        }
    }
}
</script>

<style scoped>
.task-details-page {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 16px;
}

.history-header {
    display: flex;
    margin-bottom: 24px;
    padding: 8px 0;
    border-bottom: 1px solid #e5e5e5;
}

.edit-btn, .delete-btn {
    padding: 4px 8px;
    border: none;
    background: none;
    cursor: pointer;
    font-size: 14px;
}

.edit-btn:hover, .delete-btn:hover {
    text-decoration: underline;
}

.task-main-info {
    margin-bottom: 32px;
}

.task-main-info h1 {
    font-size: 24px;
    margin: 0 0 8px 0;
    color: #2c3e50;
}

.task-meta {
    display: flex;
    align-items: center;
    gap: 16px;
}

.task-id {
    color: #7f8c8d;
    font-size: 14px;
}

.task-status {
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 12px;
    background: #e8e8e8;
}

.task-content {
    display: flex;
    gap: 32px;
}

.left-column {
    flex: 1;
    min-width: 0;
}

.right-column {
    width: 320px;
    flex-shrink: 0;
}

.task-section {
    margin-bottom: 32px;
}

.task-section h3 {
    font-size: 18px;
    margin: 0 0 16px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid #e5e5e5;
}

.description-text {
    line-height: 1.6;
    margin: 0;
    white-space: pre-wrap;
}

.details-section {
    background: #f8f9fa;
    border-radius: 4px;
    padding: 16px;
}

.details-section h3 {
    font-size: 16px;
    margin: 0 0 16px 0;
}

.details-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.detail-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.detail-item label {
    font-size: 12px;
    color: #7f8c8d;
    font-weight: 500;
}

.detail-item span {
    font-size: 14px;
    word-break: break-word;
}

.comments-list {
    border: 1px solid #e5e5e5;
    border-radius: 4px;
}

.comment {
    padding: 16px;
    border-bottom: 1px solid #e5e5e5;
}

.comment:last-child {
    border-bottom: none;
}

.comment-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.comment-author {
    font-weight: 600;
    font-size: 14px;
}

.comment-date {
    color: #7f8c8d;
    font-size: 12px;
}

.comment-text {
    font-size: 14px;
    line-height: 1.5;
}

.history-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 15px;
    padding: 20px 20px 40px;
    max-height: 20px;
}

.filters {
    display: flex;
    gap: 15px;
    align-items: center;
}

.search-container {
    position: relative;
    width: 300px;
}

.search-results {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    max-height: 300px;
    overflow-y: auto;
    background: white;
    border: 1px solid #e5e5e5;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    z-index: 1000;
    margin-top: 4px;
}

.search-result-item {
    padding: 10px 15px;
    cursor: pointer;
    transition: background 0.2s;
    font-size: 14px;
}

.search-result-item:hover {
    background: #f8f9fa;
}

.filters {
    position: relative;
}

.author {
    cursor: pointer;
    transition: color 0.2s;
}

.executors {
    cursor: pointer;
    transition: color 0.2s;
}

.executor {
    cursor: pointer;
    transition: color 0.2s;
    margin-right: 4px;
}

.executor:hover {
    color: #6498F1;
    text-decoration: underline;
}

.executors {
    display: inline-flex;
    flex-wrap: wrap;
    gap: 4px;
}
</style>