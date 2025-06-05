<template>
    <div class="group-container">
        <div class="group-header">
            <div class="header-content">
                <div class="title-section">
                    <h1 class="group-title">
                        {{ group.name }}
                        <button @click="deleteGroup" class="delete-btn">
                            <i class="bi bi-trash3"></i>
                        </button>
                    </h1>
                </div>
            </div>
            <nav class="group-tabs">
                <router-link
                    :to="{ name: 'group-members', params: { id: groupId } }"
                    class="tab-item"
                    exact-active-class="active"
                >
                    Участники
                </router-link>
                <router-link
                    :to="{ name: 'group-projects', params: { id: groupId } }"
                    class="tab-item"
                    exact-active-class="active"
                >
                    Проекты
                </router-link>
            </nav>
        </div>

        <div class="group-content">
            <div class="sidebar">
                <div class="info-card">
                    <h3 class="card-title">Основная информация</h3>
                    <div class="info-item">
                        <label>Участников:</label>
                        <span>{{ membersCount }}</span>
                    </div>
                    <div class="info-item">
                        <label>Доступных проектов:</label>
                        <span>{{ projectsCount }}</span>
                    </div>
                </div>
            </div>

            <div class="main-content">
                <div v-if="$route.name.includes('group-add-member')">
                    <router-view></router-view>
                </div>
                <div v-if="!$route.name.includes('group-add-member')">
                    <div v-if="$route.path.includes('/projects')" class="projects-section">
                        <h2>Доступные проекты группы</h2>
                        <button class="app-button link" @click="router().push(`/project/create`)">
                            <i class="bi bi-plus-lg"></i>
                            Создать проект
                        </button>

                        <div v-if="loading" class="loading-state">
                            <i class="bi bi-arrow-repeat"></i> Загрузка...
                        </div>

                        <div v-else-if="error" class="error-state">
                            {{ error }}
                        </div>

                        <div v-else>
                            <div v-if="projects.length === 0" class="empty-state">
                                В группе нет проектов
                            </div>

                            <div v-else class="projects-list scroll-container">
                                <div class="projects-table">
                                    <div class="table-header">
                                        <div class="col name">Название</div>
                                        <div class="col start-dates">Дата Начала</div>
                                        <div class="col end-dates">Дата окончания</div>
                                    </div>

                                    <div
                                        v-for="project in projects"
                                        :key="project.id"
                                        class="table-row"
                                    >
                                        <div class="col name">
                                    <span class="project-name" @click.stop="router().push(`/project/${project.id}`)">
                                        {{ project.name }}
                                    </span>
                                        </div>
                                        <div class="col start-date">
                                            {{ formatDate(project.start_time) || "Не указано" }}
                                        </div>
                                        <div class="col end-dates">
                                            {{ formatDate(project.end_time) || "Не указано" }}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div v-else-if="$route.path.includes('/')" class="members-section">
                        <div class="members-section">
                            <h2>Участники группы</h2>
                            <button class="app-button link" @click="router().push(`/group/${groupId}/add-member`)">
                                <i class="bi bi-plus-lg"></i>
                                Добавить участника
                            </button>

                            <div v-if="loading" class="loading-state">
                                <i class="bi bi-arrow-repeat"></i> Загрузка...
                            </div>

                            <div v-else-if="error" class="error-state">
                                {{ error }}
                            </div>

                            <div v-else>
                                <div v-if="members.length === 0" class="empty-state">
                                    В группе нет участников
                                </div>

                                <div v-else class="members-list scroll-container">
                                    <div class="members-table">
                                        <div class="table-header">
                                            <div class="col name">Имя</div>
                                            <div class="col email">Почта</div>
                                            <div class="col actions"></div>
                                        </div>

                                        <div
                                            v-for="member in members"
                                            :key="member.id"
                                            class="table-row"
                                        >
                                            <div class="col name">
                                                <i class="bi bi-person-circle"></i>
                                                <span class="emploee" @click.stop="goToUser(member.user)">
                                            {{ member.name }}
                                        </span>
                                            </div>
                                            <div class="col email">
                                        <span class="email">
                                            {{ member.email }}
                                        </span>
                                            </div>
                                            <div class="col actions">
                                        <span class="trash">
                                            <button class="trash-btn" @click="deleteMember(member.id)">
                                                <i class="bi bi-trash3"></i>
                                            </button>
                                        </span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios'
import router from "@/router";
import {useErrorHandling} from "@/utils/ErrorHandling";
import {useAuthStore} from "@/stores/auth";

export default {
    data() {
        return {
            loading: true,
            group: {},
            members: [],
            projects: [],
            error: null,
            allUsers: []
        }
    },
    computed: {
        groupId() {
            return this.$route.params.id
        },
        membersCount() {
            return this.members.length
        },
        projectsCount() {
            return this.projects.length
        }
    },
    async mounted() {
        await this.fetchGroup()
        await this.fetchGroupProjects()

    },
    watch: {
        '$route.query.refresh'(newVal) {
            if (newVal) {
                this.fetchGroup();
            }
        }
    },
    setup() {
        const {handleApiError} = useErrorHandling();
        return {handleApiError};
    },
    methods: {
        router() {
            return router
        },
        async fetchGroup() {
            try {
                this.loading = true;
                const authStore = useAuthStore();
                const currentUserId = authStore.user?.id;
                const response = await axios.get(
                    `http://localhost:8000/account/groups/`,
                    {withCredentials: true}
                );

                if (!response?.data || !Array.isArray(response.data)) {
                    const error = new Error('Invalid response format');
                    error.response = {
                        status: 500,
                        data: {message: 'Invalid server response'}
                    };
                    throw error;
                }

                const groupData = response.data.find(
                    group => group.id.toString() === this.groupId
                );

                if (!groupData) {
                    const error = new Error('Group not found');
                    error.response = {status: 404};
                    throw error;
                }else {
                    if(!groupData.users.includes(currentUserId)){
                        const error = new Error('Access denied to group');
                    error.response = {status: 403};
                    throw error;
                    }
                }

                const userPromises = groupData.users.map(userId =>
                    axios.get(`http://localhost:8000/account/users/${userId}/`, {withCredentials: true})
                        .then(response => response.data)
                        .catch(error => {
                            console.error(`Ошибка загрузки пользователя ${userId}:`, error);
                            return null;
                        })
                );

                const users = await Promise.all(userPromises);
                this.members = users.filter(user => user !== null);
                this.group = groupData;

            } catch (error) {
                this.handleApiError(error);
                this.error = 'Не удалось загрузить данные группы';
            } finally {
                this.loading = false;
            }
        },
        async fetchGroupProjects() {
            try {
                const response = await axios.get(
                    `http://localhost:8000/project`,
                    {withCredentials: true}
                )
                this.projects = response.data.filter(
                    project => project.group.toString() === this.groupId
                );
            } catch (error) {
                this.handleApiError(error)
                console.error('Ошибка загрузки проектов:', error)
            }
        },
        async deleteGroup() {
            if (!confirm('Вы уверены, что хотите удалить группу?')) return

            try {
                await axios.delete(
                    `http://localhost:8000/account/groups/${this.groupId}/`,
                    {
                        withCredentials: true,
                        headers: {
                            'X-CSRFToken': this.getCookie('csrftoken')
                        }
                    }
                )
                this.$router.push('/groups')
            } catch (error) {
                this.handleApiError(error)
                this.error = 'Ошибка при удалении группы'

            }
        },
        getCookie(name) {
            const value = `; ${document.cookie}`
            const parts = value.split(`; ${name}=`)
            if (parts.length === 2) return parts.pop().split(';').shift()
        },
        formatDate(dateString) {
            if (!dateString) return ''
            const options = {year: 'numeric', month: 'long', day: 'numeric'}
            return new Date(dateString).toLocaleDateString('ru-RU', options)
        },
        goToUser(userId) {
            this.$router.push({name: 'profile', params: {id: userId}});
        },
        async deleteMember(userId) {
            if (!confirm('Вы уверены, что хотите удалить участника из группы?')) return;

            try {
                await axios.delete(
                    `http://localhost:8000/account/groups/${this.groupId}/remove-user/${userId}/`,
                    {
                        withCredentials: true,
                        headers: {
                            'X-CSRFToken': this.getCookie('csrftoken')
                        }
                    }
                );

                this.members = this.members.filter(member => member.id !== userId);

                await this.fetchGroup();

            } catch (error) {
                this.handleApiError(error)
                console.error('Ошибка удаления участника:', error);
                alert(error.response?.data?.error || 'Не удалось удалить участника');
            }
        },
    }
}
</script>

<style scoped>
.group-container {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    color: #2B2B2B;
}

.group-header {
    background: #FFFFFF;
    border-bottom: 1px solid #DFE1E6;
    padding: 16px 32px;
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    height: 100%;
    margin-top: 12px;
}

.title-section {
    display: flex;
    align-items: center;
    gap: 16px;
}

.group-title {
    font-size: 24px;
    font-weight: 500;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 10px;
}

.group-tabs {
    display: flex;
    gap: 32px;
    border-bottom: 1px solid #DFE1E6;
}

.tab-item {
    padding: 12px 0;
    color: #5E6C84;
    text-decoration: none;
    border-bottom: 3px solid transparent;
    transition: all 0.2s;
}

.tab-item.active {
    color: #0052CC;
    border-bottom-color: #0052CC;
    font-weight: 500;
}

.group-content {
    display: grid;
    grid-template-columns: 280px 1fr;
    gap: 32px;
    padding: 24px 32px;
    background: #F4F5F7;
}

.info-card {
    background: #FFFFFF;
    border: 1px solid #DFE1E6;
    border-radius: 6px;
    padding: 16px;
    margin-bottom: 16px;
}

.card-title {
    font-size: 14px;
    font-weight: 600;
    color: #5E6C84;
    margin: 0 0 16px 0;
    text-transform: uppercase;
}

.info-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid #F4F5F7;
}

.info-item label {
    color: #5E6C84;
    font-size: 14px;
}

.info-item span {
    color: #172B4D;
    font-weight: 500;
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

.main-content {
    background: white;
    padding: 20px;
    border-radius: 6px;
    border: 1px solid #DFE1E6;
}

.members-table {
    background: #FFFFFF;
    border: 1px solid #DFE1E6;
    border-radius: 6px;
}

.table-header {
    display: flex;
    padding: 12px 16px;
    background: #FAFBFC;
    border-bottom: 1px solid #DFE1E6;
    font-size: 12px;
    color: #5E6C84;
    text-transform: uppercase;
}


.scroll-container {
    flex: 1;
    overflow-y: auto;
    border: 1px solid #DFE1E6;
    border-radius: 6px;
    margin-top: 15px;
    max-height: 400px;
    min-height: 0;
}

.members-table {
    min-height: min-content;
}

.app-button {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    border-radius: 3px;
    border: 1px solid #DFE1E6;
    background: #FFFFFF;
    color: #42526E;
    cursor: pointer;
    transition: all 0.2s;
}

.app-button.primary {
    background-color: #85ABEC;
    color: #FFFFFF;
}

.app-button.link {
    border: none;
    background: transparent;
    color: #0052CC;
}

.emploee {
    cursor: pointer;
    transition: color 0.2s;
}

/* Заголовки колонок */
.table-header {
    display: flex;
    padding: 12px 16px;
    gap: 15px;
}

.col {
    flex: 1;
    min-width: 0;
}

.col.name {
    flex: 2;
}

.col.email {
    flex: 3;
}

.col.actions {
    flex: 0 0 80px;
    display: flex;
    justify-content: flex-end;
}

.table-row {
    display: flex;
    gap: 15px;
    padding: 12px 16px;
    align-items: center;
}

.trash-btn {
    background: none;
    border: none;
    color: #e74c3c;
    cursor: pointer;
    padding: 5px;
    transition: opacity 0.2s;
}

.trash-btn:hover {
    opacity: 0.8;
}

.col.name, .col.email {
    display: flex;
    align-items: center;
}

.project-name {
    cursor: pointer;
}


</style>