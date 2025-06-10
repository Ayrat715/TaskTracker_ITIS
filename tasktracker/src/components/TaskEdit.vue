<template>
    <div class="task-edit-container">
        <div class="edit-header">
            <h2>Редактирование задачи</h2>
            <router-link
                :to="`/tasks/${$route.params.id}`"
                class="back-link"
            >
                <i class="bi bi-arrow-left"></i> Назад к задаче
            </router-link>
        </div>

        <form @submit.prevent="saveTask" class="edit-form">
            <div class="form-section">
                <div class="form-column">
                    <div class="form-group">
                        <label>Название *</label>
                        <input
                            type="text"
                            v-model="formData.name"
                            required
                            class="form-control"
                        >
                    </div>

                    <div class="form-group">
                        <label>Описание</label>
                        <textarea
                            v-model="formData.description"
                            class="form-control"
                            rows="5"
                        ></textarea>
                    </div>

                    <div class="form-group">
                        <label>Исполнители</label>
                        <multiselect
                            v-model="formData.executors"
                            :options="employees"
                            :multiple="true"
                            label="user_name"
                            track-by="id"
                            :searchable="true"
                        >
                            <template v-slot:tag="{ option, remove }">
                                <div class="multiselect__tag">
                                    <span
                                        class="executor-link"
                                    >
                                        {{ option.user_name }}
                                    </span>
                                    <i class="multiselect__tag-icon" @click.stop="remove(option)"></i>
                                </div>
                            </template>
                        </multiselect>
                    </div>
                </div>

                <div class="form-column">
                    <div class="form-group">
                        <label>Статус *</label>
                        <select
                            v-model="formData.status"
                            required
                            class="form-control"
                        >
                            <option
                                v-for="status in statuses"
                                :key="status.id"
                                :value="status.id"
                            >
                                {{ status.type }}
                            </option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label>Приоритет *</label>
                        <select
                            v-model="formData.priority"
                            required
                            class="form-control"
                        >
                            <option
                                v-for="priority in priorities"
                                :key="priority.id"
                                :value="priority.id"
                            >
                                {{ priority.type }}
                            </option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label>Дедлайн</label>
                        <input
                            type="datetime-local"
                            v-model="formData.end_time"
                            class="form-control"
                            :min="dateLimits.min"
                            :max="dateLimits.max"
                        >
                    </div>

                    <div class="form-group">
                        <label>Спринты</label>
                        <multiselect
                            v-model="formData.sprints"
                            :options="availableSprints"
                            label="name"
                            track-by="id"
                            :multiple="true"
                            :searchable="false"
                        ></multiselect>
                    </div>
                </div>
            </div>

            <div class="form-actions">
                <button
                    type="submit"
                    class="save-btn"
                    :disabled="loading"
                >
                    <span v-if="loading">Сохранение...</span>
                    <span v-else>Сохранить изменения</span>
                </button>
                <button
                    type="button"
                    @click="deleteProject"
                    class="delete-btn"
                    :disabled="loading"
                >
                    Удалить задачу
                </button>
            </div>

            <div v-if="error" class="error-message">
                <i class="bi bi-exclamation-circle"></i>
                {{ error }}
            </div>
        </form>
    </div>
</template>

<script>
import axios from 'axios'
import Multiselect from 'vue-multiselect'
import {useProjectsStore} from "@/stores/projects"
import {useErrorHandling} from "@/utils/ErrorHandling";

export default {
    components: {Multiselect},
    data() {
        return {
            loading: false,
            error: null,
            statuses: [],
            priorities: [],
            employees: [],
            availableSprints: [],
            formData: {
                name: '',
                description: '',
                status: null,
                priority: null,
                end_time: '',
                sprints: [],
                executors: []
            }
        }
    },
    async mounted() {
        const projectsStore = useProjectsStore()
        await projectsStore.fetchProjects()

        if (!projectsStore.currentProject && projectsStore.projects.length) {
            projectsStore.setCurrentProject(projectsStore.projects[0])
        }

        this.currentProject = projectsStore.currentProject
        await Promise.all([
            this.loadStatuses(),
            this.loadPriorities(),
            this.loadEmployees(),
            this.loadSprints()
        ])
        this.loadTask()
    },
    setup() {
        const {handleApiError} = useErrorHandling();
        return {handleApiError};
    },
    methods: {
        async loadTask() {
            try {
                const response = await axios.get(
                    `http://localhost:8000/task/tasks/${this.$route.params.id}/`
                )
                const firstSprintId = response.data.sprint_ids[0];
                const sprintsResponse = await axios.get(`http://localhost:8000/task/sprints/`);
                const sprint = sprintsResponse.data.find(s => s.id === firstSprintId);
                if (!sprint) {
                    const error = new Error('Спринт не найден');
                    error.response = {status: 404};
                    throw error;
                }
                const projectId = sprint.project;
                const executorsRes = axios.get(`http://localhost:8000/project/${projectId}/employees/`, {
                    withCredentials: true,
                })
                if ((await executorsRes).status === 403) {
                    const error = new Error('Access denied to project');
                    error.response = {status: 403};
                    throw error;
                }
                this.formData = response.data

                if (this.formData.sprint_ids) {
                    this.formData.sprints = this.availableSprints.filter(s =>
                        this.formData.sprint_ids.includes(s.id)
                    )
                }

                if (this.formData.executor_ids) {
                    this.formData.executors = this.employees.filter(e =>
                        this.formData.executor_ids.includes(e.id)
                    )
                }
            } catch (error) {
                this.handleApiError(error);
                this.error = 'Не удалось загрузить данные задачи'
            }
        },

        async loadStatuses() {
            try {
                const response = await axios.get('http://localhost:8000/task/statuses/')
                this.statuses = response.data
            } catch (error) {
                this.handleApiError(error);
                console.error('Ошибка загрузки статусов:', error)
            }
        },

        async loadPriorities() {
            try {
                const response = await axios.get('http://localhost:8000/task/priorities/')
                this.priorities = response.data
            } catch (error) {
                this.handleApiError(error);
                console.error('Ошибка загрузки приоритетов:', error)
            }
        },

        async loadEmployees() {
            try {
                const response = await axios.get(
                    `http://localhost:8000/project/${this.currentProject.id}/employees/`,
                    {withCredentials: true}
                )
                this.employees = response.data
            } catch (error) {
                this.handleApiError(error);
                console.error('Ошибка загрузки сотрудников:', error)
            }
        },

        async loadSprints() {
            try {
                const response = await axios.get('http://localhost:8000/task/sprints/')
                this.availableSprints = response.data
                    .filter(sprint => sprint.project === this.currentProject.id)
                    .sort((a, b) => new Date(b.start_time) - new Date(a.start_time))
            } catch (error) {
                this.handleApiError(error);
                console.error('Ошибка загрузки спринтов:', error)
            }
        },

        async saveTask() {
            try {
                this.loading = true
                this.error = null

                const payload = {
                    ...this.formData,
                    sprint_ids: this.formData.sprints.map(s => s.id),
                    executor_ids: this.formData.executors.map(e => e.id)
                }

                await axios.put(
                    `http://localhost:8000/task/tasks/${this.$route.params.id}/`,
                    payload
                )

                this.$router.push(`/tasks/${this.$route.params.id}`)
            } catch (error) {
                this.handleApiError(error);
                this.error = this.getErrorMessage(error)
                console.error('Детали ошибки:', error.response?.data)
            } finally {
                this.loading = false
            }
        },

        cancel() {
            this.$router.go(-1)
        },

        getErrorMessage(error) {
            if (error.response) {
                if (error.response.status === 400) {
                    return error.response.data?.detail || 'Некорректные данные'
                }
                return 'Ошибка сервера'
            }
            return error.message || 'Произошла неизвестная ошибка'
        },
    },
    computed: {
        dateLimits() {
            const limits = {}
            if (this.formData.sprints?.length) {
                limits.min = Math.min(...this.formData.sprints.map(s =>
                    new Date(s.start_time).getTime()
                ))
                limits.max = Math.max(...this.formData.sprints.map(s =>
                    new Date(s.end_time).getTime()
                ))
            }
            return {
                min: limits.min ? new Date(limits.min).toISOString().slice(0, 16) : null,
                max: limits.max ? new Date(limits.max).toISOString().slice(0, 16) : null
            }
        }
    }
}
</script>


<style scoped>
.task-edit-container {
    max-width: 1000px;
    margin: 2rem auto;
    padding: 0 1rem;
}

.edit-header {
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #e1e4e8;
}

.back-link {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    color: #42526e;
    text-decoration: none;
    font-size: 0.9rem;
}

.back-link:hover {
    color: #0052cc;
}

.edit-form {
    padding: 2rem;
}

.form-section {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    margin-bottom: 2rem;
}

.form-column {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.form-group label {
    font-weight: 600;
    color: #5e6c84;
    font-size: 0.9rem;
}

.form-control {
    padding: 0.75rem;
    border: 1px solid #dfe1e6;
    border-radius: 4px;
    font-size: 1rem;
    transition: border-color 0.2s;
}

.form-control:focus {
    outline: none;
    border-color: #85abec;
    box-shadow: 0 0 0 2px rgba(133, 171, 236, 0.2);
}

textarea.form-control {
    min-height: 116px;
    resize: vertical;
}

.form-actions {
    display: flex;
    gap: 1rem;
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid #ebecf0;
}

.save-btn {
    background: #85abec;
    color: white;
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: opacity 0.2s;
}

.save-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}

.cancel-btn {
    background: #f4f5f7;
    color: #42526e;
    padding: 0.75rem 1.5rem;
    border: 1px solid #dfe1e6;
    border-radius: 4px;
    cursor: pointer;
    transition: background 0.2s;
}

.cancel-btn:hover {
    background: #ebecf0;
}

.error-message {
    margin-top: 1.5rem;
    padding: 1rem;
    background: #ffebe6;
    color: #de350b;
    border-radius: 4px;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

::v-deep .multiselect {
    border: 1px solid #dfe1e6;
    border-radius: 3px;
    transition: border-color 0.2s;
    padding-bottom: 3px;
    background-color: #ffffff;

}

::v-deep .multiselect--active {
    border-color: #0052cc;
    box-shadow: 0 0 0 1px #0052cc;
}

::v-deep .multiselect__tags {
    min-height: 36px;
    padding: 6px 40px 0 8px;
    border: none;
}

::v-deep .multiselect__tag {
    background: #e1e4e8;
    color: #172b4d;
    border-radius: 12px;
    padding: 4px 8px;
    margin: 2px;
}

::v-deep .multiselect__tag-icon:after {
    color: #6b778c;
    font-size: 14px;
}

::v-deep .multiselect__tag-icon:hover {
    background: #dfe1e6;
}

::v-deep .multiselect__placeholder {
    color: #6b778c;
    margin-bottom: 4px;
}

::v-deep .multiselect__input {
    border: none;
    padding: 0;
    margin: 0;
}

::v-deep .multiselect__option {
    padding: 12px 16px;
    width: 100%;
    box-sizing: border-box;
    transition: all 0.2s;
    display: flex;
    align-items: center;
}

::v-deep .multiselect__option--selected {
    background: #f4f5f7;
    color: #172b4d;
    font-weight: normal;
}

::v-deep .multiselect__content-wrapper {
    width: 100%;
    min-width: 100%;
    max-width: 100%;
    box-sizing: border-box;
    overflow-x: hidden;
    border: 1px solid #dfe1e6;
    border-radius: 3px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    margin-top: 3px;
}

::v-deep .multiselect__content {
    min-width: 100%;
    max-width: 100%;
    white-space: normal;
    list-style: none;
    padding-left: 0;
}

::v-deep .multiselect__option {
    word-break: break-word;
    padding-right: 20px;
}

::v-deep .multiselect__single {
    background: transparent;
    margin: 0;
    padding: 0;

}

::v-deep .multiselect__select:before {
    border-color: #6b778c transparent transparent;
    border-width: 6px 6px 0;
}

/* Ховер для опций */
::v-deep .multiselect__option--highlight:after {
    display: none;
}

::v-deep .multiselect__tags {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    min-height: 40px;
    padding: 4px 40px 0 12px;
}

::v-deep .multiselect__tag {
    margin: 2px 4px 2px 0;
    align-self: center;
}

::v-deep .multiselect__placeholder {
    align-self: center;
    margin-top: 0;
    padding: 4px 0;
}

::v-deep .multiselect__option:hover {
    background: rgba(100, 152, 241, 0.1) !important;
}

::v-deep .multiselect__input {
    padding: 8px 12px;
    font-size: 14px;
    color: #172b4d;
    background: transparent;
    border: none;
    border-radius: 3px;
    margin: 2px 0;
}

::v-deep .multiselect__input::placeholder {
    color: #6b778c;
    opacity: 1;
}

.delete-btn {
    background: #ffebe6;
    color: #de350b;
    padding: 0.75rem 1.5rem;
    border: 1px solid #ff8f73;
    border-radius: 4px;
    cursor: pointer;
    transition: background 0.2s;
}

.delete-btn:hover {
    background: #ffd3cd;
}
</style>