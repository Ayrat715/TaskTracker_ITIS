<template>
    <div class="project-edit-container">
        <div class="edit-header">
            <h2>Редактирование проекта</h2>
            <router-link
                :to="`/project/${projectId}`"
                class="back-link"
            >
                <i class="bi bi-arrow-left"></i> Назад к проекту
            </router-link>
        </div>

        <form @submit.prevent="submitForm" class="edit-form">
            <div class="form-section">
                <div class="form-column">
                    <div class="form-group">
                        <label>Название проекта *</label>
                        <input
                            type="text"
                            v-model="formData.name"
                            required
                            class="form-control"
                        >
                    </div>

                    <div class="form-group">
                        <label>Описание проекта</label>
                        <textarea
                            v-model="formData.description"
                            class="form-control"
                            rows="5"
                        ></textarea>
                    </div>
                </div>

                <div class="form-column">
                    <div class="form-group">
                        <label>Группа проекта *</label>
                        <select
                            v-model="formData.group"
                            required
                            class="form-control"
                        >
                            <option
                                v-for="group in groups"
                                :value="group.id"
                                :key="group.id"
                                :selected="group.id === formData.group"
                            >
                                {{ group.name }}
                            </option>
                        </select>
                    </div>

                    <div class="date-fields">
                        <div class="form-group">
                            <label>Дата начала *</label>
                            <input
                                type="date"
                                v-model="formData.start_time"
                                required
                                class="form-control"
                            >
                        </div>

                        <div class="form-group">
                            <label>Дата окончания *</label>
                            <input
                                type="date"
                                v-model="formData.end_time"
                                required
                                class="form-control"
                                :min="formData.start_time"
                            >
                        </div>
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
                    Удалить проект
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
import {useAuthStore} from '@/stores/auth'

export default {
    data() {
        return {
            loading: false,
            error: null,
            formData: {
                name: '',
                description: '',
                group: null,
                start_time: '',
                end_time: ''
            },
            groups: []
        }
    },
    computed: {
        projectId() {
            return this.$route.params.id
        }
    },
    async mounted() {
        await this.fetchProjectData()
        await this.fetchUserGroups()
    },
    methods: {
        async fetchProjectData() {
            try {
                const response = await axios.get(
                    `http://localhost:8000/project/${this.projectId}/`,
                    {withCredentials: true}
                )
                this.formData = {
                    name: response.data.name,
                    description: response.data.description,
                    group: response.data.group,
                    start_time: response.data.start_time.split('T')[0],
                    end_time: response.data.end_time.split('T')[0]
                }
            } catch (error) {
                this.error = 'Не удалось загрузить данные проекта'
            }
        },

        async fetchUserGroups() {
            try {
                const authStore = useAuthStore()
                const response = await axios.get(
                    'http://localhost:8000/account/groups/',
                    {withCredentials: true}
                )
                this.groups = response.data.filter(group =>
                    group.users.includes(authStore.user?.id))
            } catch (error) {
                console.error('Ошибка загрузки групп:', error)
                this.error = 'Не удалось загрузить список групп'
            }
        },

        async submitForm() {
            try {
                this.loading = true
                this.error = null

                // Валидация
                if (new Date(this.formData.start_time) > new Date(this.formData.end_time)) {
                    throw new Error('Дата окончания должна быть позже даты начала')
                }

                const payload = {
                    ...this.formData,
                    start_time: this.formData.start_time + 'T00:00:00',
                    end_time: this.formData.end_time + 'T23:59:59'
                }

                await axios.put(
                    `http://localhost:8000/project/${this.projectId}/`,
                    payload,
                    {
                        withCredentials: true,
                        headers: {
                            'X-CSRFToken': this.getCookie('csrftoken')
                        }
                    }
                )

                this.$router.push(`/project/${this.projectId}`)
            } catch (error) {
                this.error = this.getErrorMessage(error)
            } finally {
                this.loading = false
            }
        },

        async deleteProject() {
            if (!confirm('Вы уверены, что хотите удалить проект?')) return

            try {
                await axios.delete(
                    `http://localhost:8000/project/${this.projectId}/`, {
                        withCredentials: true,
                        headers: {
                            'X-CSRFToken': this.getCookie('csrftoken')
                        }
                    }),
                this.$router.push('/projects')
            } catch (error) {
                this.error = 'Ошибка при удалении проекта'
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
                    return error.response.data?.detail || 'Некорректные данные'
                }
                return 'Ошибка сервера'
            }
            return error.message || 'Произошла ошибка'
        }
    }
}
</script>

<style scoped>
.project-edit-container {
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
    min-height: 120px;
    resize: vertical;
}

.date-fields {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
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
</style>