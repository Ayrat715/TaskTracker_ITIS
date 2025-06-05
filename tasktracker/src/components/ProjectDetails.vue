<template>
    <div class="project-container">
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


            </div>

            <nav class="project-tabs">
                <router-link
                    :to="`/project/${projectId}`"
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
                    :to="`/group/${project.group}`"
                    class="tab-item"
                    active-class="active"
                >
                    Команда
                </router-link>
                <router-link
                    :to="`/project/${project.id}/roles`"
                    class="tab-item"
                    active-class="active"
                >
                    Роли
                </router-link>
            </nav>
        </div>

        <div v-if="$route.path.includes('/roles')" class="roles-section">
            <div class="card-header">
                <h3 class="card-title">Роли проекта</h3>
                <form @submit.prevent="createRole" class="role-form">
                    <input
                        type="text"
                        v-model="newRoleName"
                        placeholder="Новая роль"
                        class="role-input"
                    />
                    <button type="submit" class="app-button primary">
                        <i class="bi bi-plus-lg"></i>
                        Создать
                    </button>
                </form>
            </div>

            <div class="roles-table">
                <div class="table-header">
                    <div class="col name">Название</div>
                    <div class="col actions">Действия</div>
                </div>

                <div v-if="loadingRoles" class="loading-state">
                    <i class="bi bi-arrow-repeat"></i> Загрузка...
                </div>

                <div v-else-if="rolesError" class="error-state">
                    {{ rolesError }}
                </div>

                <div v-else>
                    <div v-if="roles.length === 0" class="empty-state">
                        Нет созданных ролей
                    </div>

                    <div
                        v-for="role in roles"
                        :key="role.id"
                        class="table-row"
                    >
                        <div class="col name">
                                    <span v-if="editingRoleId !== role.id">
                                        {{ role.name }}
                                    </span>
                            <input
                                v-else
                                type="text"
                                v-model="editedRoleName"
                                class="edit-input"
                            />
                        </div>
                        <div class="col actions">
                            <template v-if="editingRoleId !== role.id">
                                <button
                                    @click="startEdit(role)"
                                    class="icon-button edit"
                                >
                                    <i class="bi bi-pencil"></i>
                                </button>
                                <button
                                    @click="deleteRole(role.id)"
                                    class="icon-button delete"
                                >
                                    <i class="bi bi-trash3"></i>
                                </button>
                            </template>
                            <template v-else>
                                <button
                                    @click="updateRole(role)"
                                    class="app-button primary small"
                                >
                                    Сохранить
                                </button>
                                <button
                                    @click="cancelEdit"
                                    class="app-button link small"
                                >
                                    Отмена
                                </button>
                            </template>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div v-else-if="$route.path.includes('/team')" class="team-section">
            <div class="card-header">
                <h3 class="card-title">Управление командой проекта</h3>
                <button class="app-button primary" @click="showAddForm = !showAddForm">
                    <i class="bi bi-plus-lg"></i>
                    Добавить участника
                </button>
            </div>

            <div v-if="showAddForm" class="add-form">
                <div v-if="allUsersAdded" class="no-users-message">
                    <i class="bi bi-info-circle"></i>
                    Все участники группы уже добавлены в проект
                </div>

                <div v-else>
                    <div class="form-group">
                        <label>Пользователь:</label>
                        <select v-model="newEmployee.user" class="form-select">
                            <option v-for="user in availableUsers" :key="user.id" :value="user.id">
                                {{ user.email }}
                            </option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Роль:</label>
                        <select v-model="newEmployee.role" class="form-select">
                            <option v-for="role in roles" :key="role.id" :value="role.id">
                                {{ role.name }}
                            </option>
                        </select>
                    </div>
                    <div class="form-actions">
                        <button @click="addEmployee" class="app-button primary">
                            Добавить
                        </button>
                        <button @click="showAddForm = false" class="app-button link">
                            Отмена
                        </button>
                    </div>
                </div>
            </div>

            <div class="members-table">
                <div class="table-header">
                    <div class="col name">Имя</div>
                    <div class="col role">Роль</div>
                    <div class="col actions">Действия</div>
                </div>

                <div v-if="loadingEmployees" class="loading-state">
                    <i class="bi bi-arrow-repeat"></i> Загрузка...
                </div>

                <div v-else>
                    <div v-for="employee in employees" :key="employee.id" class="table-row">
                        <div class="col name">
                            <i class="bi bi-person-circle"></i>
                            {{ employee.user_name }}
                        </div>
                        <div class="col role">
                    <span class="role-badge">
                        {{ getRoleName(employee.role) }}
                    </span>
                        </div>
                        <div class="col actions">
                            <button @click="removeEmployee(employee.id)" class="icon-button delete">
                                <i class="bi bi-trash3"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div v-else>

            <div class="project-content">
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
                </div>

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
                        </div>
                        <button class="app-button link"
                                @click="router().push(`/project/${projectId}/team`)">
                            <i class="bi bi-plus-lg"></i>
                            Добавить участника
                        </button>

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
    </div>
</template>

<script>
import axios from 'axios'
import router from "@/router";
import {useErrorHandling} from "@/utils/ErrorHandling";

export default {
    data() {
        return {
            loading: true,
            loadingEmployees: true,
            error: null,
            project: {},
            employees: [],
            roles: [],
            groups: [],
            loadingRoles: false,
            rolesError: null,
            newRoleName: '',
            editingRoleId: null,
            editedRoleName: '',
            showAddForm: false,
            newEmployee: {
                user: null,
                role: null
            },
            availableUsers: [],
            allUsersAdded: false,
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
        if (this.$route.path.includes('/roles')) {
            await this.fetchRoles()
        }
        if (this.$route.path.includes('/team')) {
            await this.fetchAvailableUsers()
        }
    },
    watch: {
        '$route'(to) {
            if (to.path.includes('/roles')) {
                this.fetchRoles()
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
        async fetchGroups() {
            try {
                const response = await axios.get(
                    `http://localhost:8000/account/groups/`,
                    {withCredentials: true}
                )
                this.groups = response.data
            } catch (error) {
                this.handleApiError(error);
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
                if (!this.project) {
                    const error = new Error('Project not found');
                    error.response = {status: 404};
                    throw error;
                }
            } catch (error) {
                this.handleApiError(error);
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
                this.handleApiError(error);
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
                this.handleApiError(error);
                this.error = 'Ошибка при удалении проекта'
            }
        },
        getCookie(name) {
            const value = `; ${document.cookie}`
            const parts = value.split(`; ${name}=`)
            if (parts.length === 2) return parts.pop().split(';').shift()
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
        },
        async fetchRoles() {
            try {
                this.loadingRoles = true
                this.rolesError = null
                const response = await axios.get(
                    `http://localhost:8000/project/${this.projectId}/roles/`,
                    {withCredentials: true}
                )
                this.roles = response.data
            } catch (error) {
                this.handleApiError(error);
                this.rolesError = 'Не удалось загрузить роли проекта'
            } finally {
                this.loadingRoles = false
            }
        },

        startEdit(role) {
            this.editingRoleId = role.id
            this.editedRoleName = role.name
        },

        cancelEdit() {
            this.editingRoleId = null
            this.editedRoleName = ''
        },

        async createRole() {
            if (!this.newRoleName.trim()) return
            const roleExists = this.roles.some(
                role => role.name.toLowerCase() === this.newRoleName.trim().toLowerCase()
            );

            if (roleExists) {
                alert('Роль с таким именем уже существует');
                return;
            }

            try {
                await axios.post(
                    `http://localhost:8000/project/${this.projectId}/roles/`,
                    {name: this.newRoleName},
                    {
                        withCredentials: true,
                        headers: {
                            'X-CSRFToken': this.getCookie('csrftoken')
                        }
                    }
                )
                this.newRoleName = ''
                await this.fetchRoles()
            } catch (error) {
                console.error('Ошибка создания роли:', error)
                alert('Не удалось создать роль. Проверьте уникальность названия.')
            }
        },

        async updateRole(role) {
            if (!this.editedRoleName.trim()) return

            try {
                await axios.put(
                    `http://localhost:8000/project/${this.projectId}/roles/${role.id}/`,
                    {name: this.editedRoleName},
                    {
                        withCredentials: true,
                        headers: {
                            'X-CSRFToken': this.getCookie('csrftoken')
                        }
                    }
                )
                this.cancelEdit()
                await this.fetchRoles()
            } catch (error) {
                console.error('Ошибка обновления роли:', error)
                alert('Не удалось обновить роль.')
            }
        },

        async deleteRole(roleId) {
            if (!confirm('Вы уверены, что хотите удалить роль?')) return

            try {
                await axios.delete(
                    `http://localhost:8000/project/${this.projectId}/roles/${roleId}/`,
                    {
                        withCredentials: true,
                        headers: {
                            'X-CSRFToken': this.getCookie('csrftoken')
                        }
                    }
                )
                await this.fetchRoles()
            } catch (error) {
                console.error('Ошибка удаления роли:', error)
                alert('Не удалось удалить роль. Возможно, она используется участниками.')
            }
        },
        async fetchAvailableUsers() {
            try {
                const projectGroup = this.groups.find(g => g.id === this.project.group);
                if (!projectGroup) {
                    console.error('Группа проекта не найдена');
                    this.availableUsers = [];
                    return;
                }

                const groupUserIds = projectGroup.users || [];
                const existingUserIds = this.employees.map(emp => emp.user);

                const availableUserIds = groupUserIds.filter(
                    userId => !existingUserIds.includes(userId)
                );
                this.allUsersAdded = availableUserIds.length === 0;
                if (this.allUsersAdded) {
                    this.availableUsers = [];
                    return;
                }

                const userRequests = availableUserIds.map(userId =>
                    axios.get(`http://localhost:8000/account/users/${userId}/`, {
                        withCredentials: true
                    })
                );

                const responses = await Promise.all(userRequests);

                this.availableUsers = responses.map(response => response.data);
                console.log(this.availableUsers + "availableUsers")

            } catch (error) {
                console.error('Ошибка загрузки пользователей:', error);
                this.availableUsers = [];
            }
        },

        async addEmployee() {
            try {
                await axios.post(
                    `http://localhost:8000/project/${this.projectId}/employees/`,
                    {
                        user: this.newEmployee.user,
                        role: this.newEmployee.role
                    },
                    {
                        withCredentials: true,
                        headers: {'X-CSRFToken': this.getCookie('csrftoken')}
                    }
                );

                this.showAddForm = false;
                this.newEmployee = {user: null, role: null};
                await this.fetchEmployees();
            } catch (error) {
                console.error('Ошибка добавления участника:', error);
                alert('Не удалось добавить участника');
            }
        },

        async removeEmployee(employeeId) {
            if (!confirm('Удалить участника из проекта?')) return;

            try {
                await axios.delete(
                    `http://localhost:8000/project/${this.projectId}/employees/${employeeId}/`,
                    {
                        withCredentials: true,
                        headers: {'X-CSRFToken': this.getCookie('csrftoken')}
                    }
                );
                await this.fetchEmployees();
            } catch (error) {
                console.error('Ошибка удаления участника:', error);
                alert('Не удалось удалить участника');
            }
        }
    }
}
</script>


<style scoped>
.project-container {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    color: #2B2B2B;
}

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

.emploee {
    cursor: pointer;
    transition: color 0.2s;
}

.roles-section {
    background: white;
    padding: 20px;
    border-radius: 6px;
    border: 1px solid #DFE1E6;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.role-form {
    display: flex;
    gap: 10px;
}

.role-input {
    padding: 8px 12px;
    border: 1px solid #DFE1E6;
    border-radius: 3px;
    width: 250px;
}

.edit-input {
    padding: 6px 10px;
    border: 1px solid #DFE1E6;
    border-radius: 3px;
    width: 100%;
}

.roles-table {
    border: 1px solid #DFE1E6;
    border-radius: 6px;
    overflow: hidden;
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
    flex: 1;
}

.col.name {
    width: 70%;
}

.col.actions {
    width: 30%;
    display: flex;
    justify-content: flex-end;
    gap: 10px;
}

.icon-button {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 16px;
    padding: 5px;
}

.icon-button.edit {
    color: #5E6C84;
}

.icon-button.edit:hover {
    color: #0052CC;
}

.icon-button.delete {
    color: #5E6C84;
}

.icon-button.delete:hover {
    color: #DE350B;
}

.app-button.small {
    padding: 6px 10px;
    font-size: 13px;
}

.loading-state, .empty-state, .error-state {
    padding: 20px;
    text-align: center;
    color: #5E6C84;
}

.error-state {
    color: #DE350B;
}

.team-section {
    background: white;
    padding: 20px;
    border-radius: 6px;
    border: 1px solid #DFE1E6;
}

.add-form {
    margin: 20px 0;
    padding: 15px;
    border: 1px solid #DFE1E6;
    border-radius: 6px;
    background: #FAFBFC;
}

.form-group {
    margin-bottom: 15px;
}

.form-select {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #DFE1E6;
    border-radius: 3px;
}

.form-actions {
    display: flex;
    gap: 10px;
    margin-top: 15px;
}
</style>