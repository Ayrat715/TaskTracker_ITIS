<template>
    <div class="project-container">
        <!-- Хедер проекта -->
        <div class="project-header">
            <div class="header-content">
                <div class="title-section">
                    <h1 class="project-title">
                        {{ project.name }}
                    </h1>
                    <button class="edit-btn" @click="router().push(`/project/${projectId}/edit`)">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button @click="deleteProject" class="delete-btn"><i class="bi bi-trash3"></i></button>
                </div>

                <!--                <div class="header-actions">-->
                <!--                    <button class="app-button primary" @click="router().push(`/project/${projectId}/edit`)">-->
                <!--                        <i class="bi bi-pencil"></i>-->
                <!--                        Редактировать-->
                <!--                    </button>-->
                <!--                </div>-->
            </div>

            <nav class="project-tabs">
                <router-link
                    :to="`/projects/${projectId}/overview`"
                    class="tab-item"
                    active-class="active"
                >
                    Обзор
                </router-link>
                <router-link
                    :to="`/tasks`"
                    class="tab-item"
                    active-class="active"
                >
                    Задачи
                </router-link>
                <router-link
                    :to="`/projects/${projectId}/team`"
                    class="tab-item"
                    active-class="active"
                >
                    Команда
                </router-link>
            </nav>
        </div>

        <!-- Основной контент -->
        <div class="project-content">
            <!-- Левая панель -->
            <div class="sidebar">
                <div class="info-card">
                    <h3 class="card-title">Основная информация</h3>
                    <div class="info-item">
                        <label>Группа:</label>
                        <span>{{ getGroupName(project.group) }}</span>
                    </div>
                    <div class="info-item">
                        <label>Дата начала:</label>
                        <span>{{ formatDate(project.start_time) }}</span>
                    </div>
                    <div class="info-item">
                        <label>Дата окончания:</label>
                        <span>{{ formatDate(project.end_time) }}</span>
                    </div>
                </div>

                <!--                <div class="info-card">-->
                <!--                    <h3 class="card-title">Статистика</h3>-->
                <!--                    <div class="stats-item">-->
                <!--                        <div class="stat-value">24</div>-->
                <!--                        <div class="stat-label">Открытых задач</div>-->
                <!--                    </div>-->
                <!--                    <div class="stats-item">-->
                <!--                        <div class="stat-value">8</div>-->
                <!--                        <div class="stat-label">Участников</div>-->
                <!--                    </div>-->
                <!--                </div>-->
            </div>

            <!-- Правая основная область -->
            <div class="main-content">
                <div class="description-card">
                    <h3 class="card-title">Описание</h3>
                    <div class="description-text">
                        {{ project.description || 'Добавьте описание проекта' }}
                    </div>
                </div>
                <br>

                <div class="team-card">
                    <div class="card-header">
                        <h3 class="card-title">Участники команды</h3>
                        <button class="app-button link" @click="router().push(`/team/add`)">
                            <i class="bi bi-plus-lg"></i>
                            Добавить участника
                        </button>
                    </div>

                    <div class="members-table">
                        <div class="table-header">
                            <div class="col name">Имя</div>
                            <div class="col role">Роль</div>
                            <div class="col load">Нагрузка</div>
                        </div>

                        <div
                            v-for="employee in employees"
                            :key="employee.id"
                            class="table-row"
                        >
                            <div class="col name">
                                <i class="bi bi-person-circle"></i>
                                <span class="emploee" @click.stop="goToUser(employee.user)">
                                    {{ employee.user_name }}
                                </span>
                            </div>
                            <div class="col role">
                                <span class="role-badge">
                                    {{ getRoleName(employee.role) }}
                                </span>
                            </div>
                            <div class="col load">
                                <div class="load-bar">
                                    <div
                                        class="progress"
                                        :style="{ width: employee.current_load + '%' }"
                                    ></div>
                                    <span class="percentage">{{ employee.current_load }}%</span>
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

export default {
    data() {
        return {
            loading: true,
            loadingEmployees: true,
            error: null,
            project: {},
            employees: [],
            roles: [],
            groups: []
        }
    },
    computed: {
        projectId() {
            return this.$route.params.id
        },
    },

    async mounted() {
        await this.fetchProject()
        await this.fetchEmployees()
        await this.fetchRoles()
        await this.fetchGroups()
    },
    methods: {
        router() {
            return router
        },
        async fetchGroups() {
            try {
                const response = await axios.get(
                    `http://localhost:8000/account/groups/`,
                    {withCredentials: true}
                )
                this.groups = response.data
            } catch (error) {
                console.error('Ошибка загрузки групп:', error)
                this.groups = []
            }
        },
        async fetchProject() {
            try {
                this.loading = true
                const response = await axios.get(`http://localhost:8000/project/${this.projectId}/`, {
                    withCredentials: true
                })
                this.project = response.data

            } catch (error) {
                this.error = 'Не удалось загрузить данные проекта'
            } finally {
                this.loading = false
            }
        },
        getGroupName(groupId) {
            const groupStr = groupId;
            const group = this.groups.find(g => g.id === groupStr);
            return group ? group.name : 'Не указано';
        },
        async fetchEmployees() {
            try {
                this.loadingEmployees = true
                const response = await axios.get(
                    `http://localhost:8000/project/${this.projectId}/employees/`, {
                        withCredentials: true
                    })
                this.employees = response.data


            } catch (error) {
                this.error = 'Не удалось загрузить участников проекта'
            } finally {
                this.loadingEmployees = false
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
                    }
                )
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

        async fetchRoles() {
            try {
                const response = await axios.get(
                    `http://localhost:8000/project/${this.projectId}/roles/`, {
                        withCredentials: true
                    })
                this.roles = response.data
            } catch (error) {
                console.error('Ошибка загрузки ролей:', error)
            }
        },

        getRoleName(roleId) {
            const role = this.roles.find(r => r.id === roleId)
            return role ? role.name : 'Не указано'
        },

        formatDate(dateString) {
            if (!dateString) return ''
            const options = {year: 'numeric', month: 'long', day: 'numeric'}
            return new Date(dateString).toLocaleDateString('ru-RU', options)
        },
        goToUser(userId) {
            this.$router.push({name: 'profile', params: {id: userId}});
        }
    }
}
</script>


<style scoped>
.project-container {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    color: #2B2B2B;
}

/* Хедер проекта */
.project-header {
    background: #FFFFFF;
    border-bottom: 1px solid #DFE1E6;
    padding: 16px 32px;
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
}

.title-section {
    display: flex;
    align-items: center;
    gap: 16px;
}

.project-title {
    font-size: 24px;
    font-weight: 500;
    margin: 0;
}

.project-key {
    color: #5E6C84;
    font-weight: 400;
}

.project-status {
    padding: 4px 8px;
    border-radius: 3px;
    font-size: 12px;
    font-weight: 500;
    text-transform: uppercase;
}

.status-planned {
    background: #FFF0B3;
    color: #172B4D;
}

.status-active {
    background: #DEEBFF;
    color: #0747A6;
}

.status-completed {
    background: #E3FCEF;
    color: #006644;
}

/* Табы */
.project-tabs {
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

/* Основной контент */
.project-content {
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

/* Таблица участников */
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

.table-row {
    display: flex;
    align-items: center;
    padding: 12px 16px;
    border-bottom: 1px solid #F4F5F7;
}

.col {
    padding: 0 8px;
}

.col.name {
    width: 40%;
}

.col.role {
    width: 25%;
}

.col.load {
    width: 25%;
}

.col.actions {
    width: 10%;
}

.role-badge {
    background: #EAECF0;
    padding: 4px 8px;
    border-radius: 3px;
    font-size: 12px;
}

.load-bar {
    position: relative;
    background: #EAECF0;
    height: 24px;
    border-radius: 3px;
    overflow: hidden;
}

.progress {
    height: 100%;
    background: #00B8D9;
    transition: width 0.3s ease;
}

.percentage {
    position: absolute;
    right: 8px;
    top: 50%;
    transform: translateY(-50%);
    color: #FFFFFF;
    font-size: 12px;
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

.icon-button {
    border: none;
    background: none;
    color: #5E6C84;
    cursor: pointer;
    padding: 4px;
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
.emploee{
    cursor: pointer;
    transition: color 0.2s;
}
</style>