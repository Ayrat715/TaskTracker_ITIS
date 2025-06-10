<template>
    <div class="create-project-page">
        <div class="history-header">
            <div class="filters">
                <div class="search-container"></div>
            </div>
        </div>
        <h2>Создание нового проекта</h2>
        <form @submit.prevent="submitForm" class="project-form">
            <div class="form-group">
                <label>Название проекта *</label>
                <input
                    type="text"
                    v-model="formData.name"
                    required
                    class="form-control"
                    placeholder="Введите название проекта"
                >
            </div>

            <div class="form-group">
                <label>Описание проекта</label>
                <textarea
                    v-model="formData.description"
                    class="form-control"
                    rows="3"
                    placeholder="Введите описание проекта"
                ></textarea>
            </div>

            <div class="form-group">
                <label>Группа проекта *</label>
                <select
                    v-model="formData.group"
                    required
                    class="form-control"

                >
                    <option v-for="group in groups" :value="group.id" :key="group.id">
                        {{ group.name }}
                    </option>
                </select>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label>Дата начала *</label>
                    <input
                        type="datetime-local"
                        v-model="formData.start_time"
                        required
                        class="form-control"
                    >
                </div>

                <div class="form-group">
                    <label>Дата окончания *</label>
                    <input
                        type="datetime-local"
                        v-model="formData.end_time"
                        required
                        class="form-control"
                        :min="formData.start_time"
                    >
                </div>
            </div>

            <div class="form-actions">
                <button
                    type="submit"
                    class="btn btn-primary"
                >
                    {{ 'Создать проект' }}
                </button>
                <button type="button" @click="cancel" class="btn btn-secondary">Отмена</button>
            </div>

            <div v-if="error" class="alert alert-danger">
                {{ error }}
            </div>
        </form>
    </div>
</template>

<script>
import {mapActions} from 'pinia'
import {useProjectsStore} from '@/stores/projects'
import axios from "axios"
import {useAuthStore} from "@/stores/auth";
import {useErrorHandling} from "@/utils/ErrorHandling";

export default {
    data() {
        return {
            error: null,
            groups: [],
            formData: {
                name: '',
                description: '',
                group: null,
                start_time: '',
                end_time: ''
            },
            authStore: useAuthStore()
        }
    },
    async created() {
        await this.authStore.checkAuth()
        await this.fetchUserGroups()
    },
    setup() {
        const {handleApiError} = useErrorHandling();
        return {handleApiError};
    },

    methods: {
        ...mapActions(useProjectsStore, ['fetchProjects']),

        async fetchUserGroups() {
            try {
                const response = await axios.get('http://localhost:8000/account/groups/', {
                    withCredentials: true
                })
                this.groups = response.data.filter(group =>
                group.users.includes(this.authStore.user?.id)
            )
            } catch (error) {
                this.handleApiError(error);
                console.error('Ошибка загрузки групп:', error)
                this.error = 'Не удалось загрузить список групп'
            }
        },
        cancel() {
            this.$router.go(-1)
        },
        async submitForm() {
            try {
                this.error = null

                if (!this.formData.name.trim()) {
                    throw new Error('Название проекта обязательно')
                }
                if (!this.formData.group) {
                    throw new Error('Выберите группу проекта')
                }
                if (new Date(this.formData.start_time) > new Date(this.formData.end_time)) {
                    throw new Error('Дата окончания должна быть после даты начала')
                }

                const payload = {
                    name: this.formData.name,
                    description: this.formData.description,
                    group: this.formData.group,
                    start_time: this.formData.start_time,
                    end_time: this.formData.end_time
                }

                await axios.post('http://localhost:8000/project/', payload, {
                    withCredentials: true,
                    headers: {
                        'X-CSRFToken': this.getCookie('csrftoken')
                    }
                })

                await this.fetchProjects()
                this.$router.push('/projects')
            } catch (error) {
                this.handleApiError(error);
                console.error('Ошибка создания проекта:', error)
                this.error = this.getErrorMessage(error)
            } finally {
                this.loading = false
            }
        },
        getCookie(name) {
            const value = `; ${document.cookie}`
            const parts = value.split(`; ${name}=`)
            if (parts.length === 2) return parts.pop().split(';').shift()
        },

        getErrorMessage(error) {
            if (error.response) {
                if (error.response.status === 400) {
                    return error.response.data?.detail || 'Некорректные данные проекта'
                }
                if (error.response.status === 403) {
                    return 'Ошибка доступа'
                }
            }
            return error.message || 'Произошла неизвестная ошибка'
        }
    }
}
</script>

<style scoped>
.create-project-page {
    max-width: 800px;
    margin: 20px auto;
    padding: 20px;
}

.project-form {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.form-group {
    margin-bottom: 15px;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: 600;
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

.form-row {
    display: flex;
    gap: 20px;
    width: 100%;
}

.form-row .form-group {
    flex: 1;
    margin-bottom: 0;
}

.form-actions {
    display: flex;
    gap: 10px;
    justify-content: flex-end;
}

.btn {
    padding: 8px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: opacity 0.2s;
}

.btn-primary {
    background: #6498F1;
    color: white;
}

.btn-secondary {
    background: #ccc;
    color: #333;
}

.btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}

.alert-danger {
    padding: 10px;
    margin-top: 15px;
    border-radius: 4px;
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    color: #721c24;
}

select.form-control {
    appearance: none;
    background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
    background-repeat: no-repeat;
    background-position: right 8px center;
    background-size: 16px;
    padding-right: 32px;
}
.history-header {
    display: flex;
    margin-bottom: 24px;
    padding: 8px 0;
    border-bottom: 1px solid #e5e5e5;
}

</style>