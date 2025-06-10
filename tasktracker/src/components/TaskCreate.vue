<template>
    <div class="task-create-page">
        <div class="history-header">
            <div class="filters">
                <div class="search-container"></div>
            </div>
        </div>

        <div class="task-content">
            <form @submit.prevent="submitForm" class="task-form">
                <div class="left-column" :class="{ 'disabled-form': isTaskSaved}">
                    <div class="task-main-info">
                        <h1>Создание новой задачи</h1>
                    </div>

                    <div class="task-section">
                        <h3>Основная информация</h3>
                        <div class="form-group">
                            <label for="task-name">Название задачи*</label>
                            <input
                                type="text"
                                id="task-name"
                                v-model="formData.name"
                                required
                                class="form-control"
                            >
                        </div>

                        <div class="form-group">
                            <label for="task-description">Описание*</label>
                            <textarea
                                id="task-description"
                                v-model="formData.description"
                                required
                                class="form-control"
                            ></textarea>
                        </div>
                    </div>

                    <div class="task-section">
                        <h3>Детали задачи</h3>
                        <div class="form-row">
                            <div class="form-group">
                                <label for="task-priority">Приоритет*</label>
                                <select
                                    id="task-priority"
                                    v-model="formData.priority"
                                    required
                                    class="form-select"
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
                                <label for="task-status">Статус*</label>
                                <select
                                    id="task-status"
                                    v-model="formData.status"
                                    required
                                    class="form-select"
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
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label for="task-start">Дата начала</label>
                                <input
                                    type="datetime-local"
                                    id="task-start"
                                    v-model="formData.start_time"
                                    class="form-control"
                                >
                            </div>

                            <div class="form-group">
                                <label for="task-end">Дедлайн</label>
                                <input
                                    type="datetime-local"
                                    id="task-end"
                                    v-model="formData.end_time"
                                    class="form-control"
                                    :min="formData.start_time"
                                >
                            </div>
                        </div>
                    </div>
                </div>

                <div class="right-column">
                    <div v-if="!isTaskSaved">
                        <div class="details-section">
                            <h3>Назначение</h3>

                            <div class="form-group" >
                                <label for="task-sprints" >Спринты</label>
                                <div class="sprints-selector">
                                    <div class="selector-input" @click="toggleSprintsDropdown">
                                        <div class="selected-tags">
                                            <span v-for="sprint in selectedSprints" :key="sprint.id" class="tag">
                                                {{ sprint.name }}
                                                <span class="remove-tag" @click.stop="removeSprint(sprint.id)">×</span>
                                            </span>
                                            <span v-if="selectedSprints.length === 0" class="placeholder">Выберите спринты...</span>
                                        </div>
                                        <span class="dropdown-icon">▼</span>
                                    </div>

                                    <div v-show="isSprintsDropdownOpen" class="dropdown-content">
                                        <input
                                            v-model="sprintsSearch"
                                            type="text"
                                            placeholder="Поиск спринтов..."
                                            class="search-input"
                                            @input="filterSprints"
                                        >

                                        <div class="dropdown-actions">
                                            <button type="button" @click="selectAllSprints">Выбрать все</button>
                                            <button type="button" @click="clearSelectedSprints">Сбросить</button>
                                        </div>

                                        <div class="sprints-list">
                                            <div
                                                v-for="sprint in filteredSprints"
                                                :key="sprint.id"
                                                class="sprint-item"
                                                :class="{ 'selected': isSprintSelected(sprint.id) }"
                                                @click="toggleSprint(sprint.id)"
                                            >
                                                <input
                                                    type="checkbox"
                                                    :checked="isSprintSelected(sprint.id)"
                                                    @click.stop
                                                    @change="toggleSprint(sprint.id)"
                                                >
                                                <span>{{ sprint.name }}</span>
                                                <span class="sprint-date">{{
                                                        formatDate(sprint.start_date)
                                                    }} - {{ formatDate(sprint.end_date) }}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>


                            <div class="form-actions">
                                <button
                                    type="button"
                                    @click="cancel"
                                    class="btn-cancel"
                                >
                                    Отмена
                                </button>
                                <button
                                    type="button"
                                    @click="saveAndGetRecommendations"
                                    :disabled="isSubmitting"
                                    class="btn-recommend"
                                >
                                    <span v-if="isSubmitting">Сохранение...</span>
                                    <span v-else>Сохранить и добавить исполнителя</span>
                                </button>
                            </div>
                        </div>
                    </div>

                    <div v-else class="assignment-section">
                        <h3>Назначение исполнителей для задачи #{{ savedTaskId }}</h3>

                        <div class="recommended-executors" v-if="recommendedExecutors.length">
                            <h4>Рекомендованные:</h4>
                            <div class="executors-list">
                                <div
                                    v-for="executor in recommendedExecutors"
                                    :key="executor.id"
                                    class="executor-item"
                                    :class="{ 'selected': isExecutorSelected(executor.id) }"
                                    @click="toggleExecutor(executor.id)"
                                >
                                    {{ executor.user_name }}
                                </div>
                            </div>
                        </div>

                        <div class="all-executors">
                            <h4>Все доступные:</h4>
                            <div class="executors-list">
                                <div
                                    v-for="executor in allEmployees"
                                    :key="executor.id"
                                    class="executor-item"
                                    :class="{ 'selected': isExecutorSelected(executor.id) }"
                                    @click="toggleExecutor(executor.id)"
                                >
                                    {{ executor.user_name }}
                                </div>
                            </div>
                        </div>

                        <div class="form-actions">
                            <button
                                type="button"
                                @click="assignExecutors"
                                :disabled="isSubmitting"
                                class="btn-submit"
                            >
                                <span v-if="isSubmitting">Назначение...</span>
                                <span v-else>Назначить выбранных</span>
                            </button>
                            <button
                                type="button"
                                @click="cancelAssignment"
                                class="btn-cancel"
                            >
                                Вернуться к задаче
                            </button>
                        </div>
                    </div>
                </div>
            </form>
        </div>
    </div>
</template>

<script>
import axios from 'axios';
import {useProjectsStore} from '@/stores/projects';
import {useErrorHandling} from '@/utils/ErrorHandling';
import {useAuthStore} from "@/stores/auth";

export default {
    name: 'TaskCreatePage',
    setup() {
        const {handleApiError} = useErrorHandling();
        return {handleApiError};
    },
    data() {
        return {
            formData: {
                name: '',
                description: '',
                priority: null,
                status: null,
                start_time: null,
                end_time: null,
                executor_ids: [],
                sprint_ids: [],
            },
            priorities: [],
            statuses: [],
            availableSprints: [],
            allEmployees: [],
            recommendedExecutors: [],
            isSubmitting: false,
            currentProject: null,
            isTaskSaved: false,
            savedTaskId: null,
            isSprintsDropdownOpen: false,
            sprintsSearch: '',
            filteredSprints: [],
        };
    },
    async mounted() {
        const projectsStore = useProjectsStore();
        this.currentProject = projectsStore.currentProject;

        await Promise.all([
            this.loadPriorities(),
            this.loadStatuses(),
            this.loadSprints(),
            this.loadEmployees(),
        ]);
        document.addEventListener('click', this.closeSprintsDropdown);

    },
    computed: {
        selectedSprints() {
            return this.availableSprints.filter(sprint =>
                this.formData.sprint_ids.includes(sprint.id)
            );
        }
    },
    watch: {
        availableSprints: {
            immediate: true,
            handler(sprints) {
                this.filteredSprints = [...sprints];
            }
        }
    },
    beforeUnmount() {
        document.removeEventListener('click', this.closeSprintsDropdown);
    },
    methods: {

        async loadPriorities() {
            try {
                const response = await axios.get('http://localhost:8000/task/priorities/');
                this.priorities = response.data;
                if (this.priorities.length) {
                    this.formData.priority = this.priorities[0].id;
                }
            } catch (error) {
                console.error('Ошибка загрузки приоритетов:', error);
            }
        },
        async loadStatuses() {
            try {
                const response = await axios.get('http://localhost:8000/task/statuses/');
                this.statuses = response.data;
                if (this.statuses.length) {
                    this.formData.status = this.statuses.find(s => s.type === 'to_do')?.id || this.statuses[0].id;
                }
            } catch (error) {
                console.error('Ошибка загрузки статусов:', error);
            }
        },
        async loadSprints() {
            try {
                if (!this.currentProject?.id) return;

                const response = await axios.get('http://localhost:8000/task/sprints/');
                this.availableSprints = response.data.filter(
                    sprint => sprint.project === this.currentProject.id
                );
            } catch (error) {
                console.error('Ошибка загрузки спринтов:', error);
            }
        },
        async loadEmployees() {
            try {
                if (!this.currentProject?.id) return;

                const response = await axios.get(
                    `http://localhost:8000/project/${this.currentProject.id}/employees/`,
                    {withCredentials: true}
                );
                this.allEmployees = response.data;
            } catch (error) {
                console.error('Ошибка загрузки сотрудников:', error);
            }
        },
        toggleExecutor(executorId) {
            const index = this.formData.executor_ids.indexOf(executorId);
            if (index === -1) {
                this.formData.executor_ids.push(executorId);
            } else {
                this.formData.executor_ids.splice(index, 1);
            }
        },
        isExecutorSelected(executorId) {
            return this.formData.executor_ids.includes(executorId);
        },
        async submitForm() {
            this.isSubmitting = true;
            try {
                const payload = {
                    ...this.formData,
                    executor_ids: this.formData.executor_ids,
                    sprint_ids: this.formData.sprint_ids,
                };

                Object.keys(payload).forEach(key => {
                    if (payload[key] === null || payload[key] === '') {
                        delete payload[key];
                    }
                });

                const response = await axios.post(
                    'http://localhost:8000/task/tasks/',
                    payload,
                    {withCredentials: true}
                );

                this.$router.push(`/tasks/${response.data.id}`);
            } catch (error) {
                this.handleApiError(error);
                console.error('Ошибка создания задачи:', error);
                alert('Не удалось создать задачу');
            } finally {
                this.isSubmitting = false;
            }
        },
        cancel() {
            this.$router.go(-1);
        },
        async saveTask() {
            this.isSubmitting = true;
            try {
                const authUser = useAuthStore();
                const projectEmploees = await axios.get(
                    `http://localhost:8000/project/${this.currentProject.id}/employees/`,
                    {
                        withCredentials: true,
                        headers: {
                            'X-CSRFToken': this.getCookie('csrftoken')
                        }
                    }
                );
                const projectEmployeesData = projectEmploees.data.find(project => project.user === authUser.user.id);
                const payload = {
                    ...this.formData,
                    executor_ids: this.formData.executor_ids || [],
                    author: projectEmployeesData.id,
                };

                const response = await axios.post(
                    'http://localhost:8000/task/tasks/',
                    payload,
                    {
                        withCredentials: true,
                        headers: {
                            'X-CSRFToken': this.getCookie('csrftoken')
                        }
                    }
                );

                this.savedTaskId = response.data.id;
                this.isTaskSaved = true;
                this.$notify({
                    title: 'Задача сохранена',
                    message: `Задача #${this.savedTaskId} успешно создана`,
                    type: 'success'
                });

            } catch (error) {
                console.error('Ошибка сохранения задачи:', error);
            } finally {
                this.isSubmitting = false;
            }
        },

        async saveAndGetRecommendations() {
            await this.saveTask();
            await this.getRecommendations();
        },

        async getRecommendations() {
            try {

                const taskResponse = await axios.get(`http://localhost:8000/task/tasks/${this.savedTaskId}/`);

                const sprintId = this.formData.sprint_ids[0];
                const params = {
                    sprint: sprintId,
                    priority: this.formData.priority,
                    description: this.formData.description,
                    start_time: this.formData.start_time || new Date().toISOString(),
                    category: taskResponse.data.category
                };

                const response = await axios.get(
                    'http://localhost:8000/task/recommend/',
                    {params}
                );

                this.recommendedExecutors = this.allEmployees.filter(
                    emp => response.data.includes(emp.id)
                );

            } catch (error) {
                console.error('Ошибка получения рекомендаций:', error);
            }
        },

        async assignExecutors() {
            this.isSubmitting = true;
            try {
                await axios.patch(
                    `http://localhost:8000/task/tasks/${this.savedTaskId}/`,
                    {
                        executor_ids: this.formData.executor_ids
                    },
                    {
                        withCredentials: true,
                        headers: {
                            'X-CSRFToken': this.getCookie('csrftoken')
                        }
                    }
                );

                this.$router.push(`/tasks/${this.savedTaskId}`);

            } catch (error) {
                console.error('Ошибка выбора исполнителей:', error);
            } finally {
                this.isSubmitting = false;
            }
        },
        cancelAssignment() {
            this.$router.push(`/tasks/${this.savedTaskId}`);
        },
        getCookie(name) {
            const value = `; ${document.cookie}`
            const parts = value.split(`; ${name}=`)
            if (parts.length === 2) return parts.pop().split(';').shift()
        },
        toggleSprintsDropdown() {
            this.isSprintsDropdownOpen = !this.isSprintsDropdownOpen;
        },

        closeSprintsDropdown(event) {
            if (!this.$el.contains(event.target)) {
                this.isSprintsDropdownOpen = false;
            }
        },

        toggleSprint(sprintId) {
            const index = this.formData.sprint_ids.indexOf(sprintId);
            if (index === -1) {
                this.formData.sprint_ids.push(sprintId);
            } else {
                this.formData.sprint_ids.splice(index, 1);
            }
        },

        isSprintSelected(sprintId) {
            return this.formData.sprint_ids.includes(sprintId);
        },

        removeSprint(sprintId) {
            this.formData.sprint_ids = this.formData.sprint_ids.filter(id => id !== sprintId);
        },

        filterSprints() {
            if (!this.sprintsSearch) {
                this.filteredSprints = [...this.availableSprints];
                return;
            }

            const searchTerm = this.sprintsSearch.toLowerCase();
            this.filteredSprints = this.availableSprints.filter(sprint =>
                sprint.name.toLowerCase().includes(searchTerm) ||
                (sprint.description && sprint.description.toLowerCase().includes(searchTerm))
            );
        },

        selectAllSprints() {
            this.formData.sprint_ids = this.availableSprints.map(sprint => sprint.id);
        },

        clearSelectedSprints() {
            this.formData.sprint_ids = [];
        },

        formatDate(dateString) {
            if (!dateString) return '';
            const date = new Date(dateString);
            return date.toLocaleDateString('ru-RU', {
                day: '2-digit',
                month: '2-digit'
            });
        }
    }
}
</script>

<style scoped>
.task-create-page {
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

.task-content {
    display: flex;
    gap: 32px;
}

.task-form {
    display: flex;
    width: 100%;
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

    padding: 20px;

}

.task-section h3 {
    font-size: 18px;
    margin: 0 0 16px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid #e5e5e5;
    color: #2c3e50;
}

.form-group {
    margin-bottom: 20px;
}

.form-row {
    display: flex;
    gap: 15px;
}

.form-row .form-group {
    flex: 1;
    min-width: 0;
}


label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    color: #555;
}

.form-select {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
    transition: border-color 0.3s;
}


.form-select:focus{
    border-color: #6498F1;
    outline: none;
    box-shadow: 0 0 0 2px rgba(100, 152, 241, 0.2);
}

.details-section {

    padding: 20px;
    margin-bottom: 20px;
}


.executors-section h4 {
    margin: 10px 0 8px 0;
    font-size: 14px;
    color: #555;
}

.executors-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.executor-item {
    padding: 6px 12px;
    background: #e9ecef;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 13px;
}

.executor-item:hover {
    background: #dde6f5;
}

.executor-item.selected {
    background: #6498F1;
    color: white;
}

.form-actions {
    display: flex;
    gap: 10px;
    justify-content: flex-end;
    padding-top: 20px;
    border-top: 1px solid #eee;
    margin-top: 20px;
}

.btn-cancel, .btn-submit {
    padding: 10px 20px;
    border-radius: 4px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.3s;
}

.btn-cancel {
    background: #f8f9fa;
    border: 1px solid #ddd;
    color: #555;
}

.btn-cancel:hover {
    background: #e9ecef;
}

.btn-submit {
    background: #6498F1;
    border: none;
    color: white;
}

.btn-submit:hover {
    background: #4a7bc8;
}

.btn-submit:disabled {
    background: #a0b9f0;
    cursor: not-allowed;
}

.assignment-section {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
}

.assignment-section h3 {
    font-size: 18px;
    margin: 0 0 16px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid #e5e5e5;
    color: #2c3e50;
}

.btn-recommend {
    background: #4caf50;
    color: white;
    padding: 10px 20px;
    border-radius: 4px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.3s;
    border: none;
}

.btn-recommend:hover {
    background: #43a047;
}

.btn-recommend:disabled {
    background: #81c784;
    cursor: not-allowed;
}

.form-actions {
    display: flex;
    gap: 10px;
    justify-content: space-between;
    padding-top: 20px;
    border-top: 1px solid #eee;
    margin-top: 20px;
    flex-wrap: wrap;
}

.disabled-form {
    opacity: 0.6;
    pointer-events: none;
    position: relative;
}

.disabled-form::after {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.5);
    z-index: 10;
}

.form-control {
    width: 100%;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    box-sizing: border-box;
    transition: border-color 0.2s, box-shadow 0.2s;
}

.form-control:focus {
    outline: none;
    border-color: #6498F1;
    box-shadow: 0 0 0 2px rgba(100, 152, 241, 0.2);
}

textarea.form-control {
    min-height: 100px;
    resize: vertical;
}

.selector-input {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px 12px;
  cursor: pointer;
  background: white;
  min-height: 40px;
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  flex: 1;
}

.tag {
  background-color: #e9ecef;
  border-radius: 4px;
  padding: 4px 8px;
  display: flex;
  align-items: center;
  font-size: 13px;
}

.remove-tag {
  margin-left: 5px;
  cursor: pointer;
  font-weight: bold;
}

.remove-tag:hover {
  color: #ff6b6b;
}

.placeholder {
  color: #999;
}

.dropdown-icon {
  margin-left: 8px;
  font-size: 12px;
}
.sprints-selector {
  position: relative;
}
.dropdown-content {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 100;
  margin-top: 5px;
  max-height: 300px;
  overflow-y: auto;
}

.search-input {
  width: 100%;
  padding: 10px;
  border: none;
  border-bottom: 1px solid #eee;
  outline: none;
}

.search-input:focus {
  border-bottom-color: #6498F1;
}

.dropdown-actions {
  display: flex;
  padding: 8px;
  gap: 8px;
  border-bottom: 1px solid #eee;
}

.dropdown-actions button {
  flex: 1;
  padding: 6px;
  background: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.dropdown-actions button:hover {
  background: #e9ecef;
}

.sprints-list {
  padding: 5px 0;
}

.sprint-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  cursor: pointer;
  border-bottom: 1px solid #f5f5f5;
}

.sprint-item:hover {
  background-color: #f8f9fa;
}

.sprint-item.selected {
  background-color: #edf4ff;
}

.sprint-item input {
  margin-right: 10px;
}

.sprint-date {
  margin-left: auto;
  font-size: 12px;
  color: #777;
}
</style>