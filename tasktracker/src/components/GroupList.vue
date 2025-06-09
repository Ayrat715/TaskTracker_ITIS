<template>
    <div class="group-list-container">
        <div class="list-header">
            <div class="header-content">
                <h1 class="list-title">Группы</h1>
            </div>

            <div class="header-content">
                <SearchInput
                    v-model="searchQuery"
                    placeholder="Поиск групп..."
                    @search="handleSearch"
                />
                <router-link
                    to="/group/create"
                    class="primary-button"
                >
                    <i class="bi bi-plus-lg"></i>
                    Новая группа
                </router-link>
            </div>
        </div>

        <div class="content-wrapper">
            <div v-if="loading" class="loading-state">
                <div class="spinner"></div>
                Загрузка групп...
            </div>

            <div v-else-if="error" class="error-state">
                <i class="bi bi-exclamation-circle"></i>
                {{ error }}
            </div>

            <div v-else-if="filteredGroups.length === 0" class="empty-state">
                <i class="bi bi-people"></i>
                Нет доступных групп
            </div>

            <table v-else class="groups-table">
                <thead>
                <tr>
                    <th
                        v-for="header in tableHeaders"
                        :key="header.key"
                        @click="sortBy(header.key)"
                        :class="{sortable: header.sortable}"
                    >
                        {{ header.title }}
                        <i
                            v-if="sortKey === header.key"
                            class="bi"
                            :class="sortOrder === 'asc' ? 'bi-sort-up' : 'bi-sort-down'"
                        ></i>
                    </th>
                </tr>
                </thead>
                <tbody>
                <tr
                    v-for="group in sortedGroups"
                    :key="group.id"
                    @click="openGroup(group.id)"
                >
                    <td>
                        <i class="bi bi-people"></i>
                        {{ group.name }}
                    </td>
                    <td>{{ group.users_count || 0 }}</td>
                    <td>{{ group.projects_count || 0 }}</td>
                </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>

<script>
import axios from 'axios'
import SearchInput from "@/components/SearchInput.vue";
import {useAuthStore} from "@/stores/auth";
import {useErrorHandling} from "@/utils/ErrorHandling";

export default {
    components: {SearchInput},
    data() {
        return {
            loading: true,
            error: null,
            groups: [],
            searchQuery: '',
            sortKey: 'name',
            sortOrder: 'asc',
            tableHeaders: [
                {title: 'Название', key: 'name', sortable: true},
                {title: 'Участники', key: 'users_count', sortable: true},
                {title: 'Проекты', key: 'projects_count', sortable: true}
            ]
        }
    },
    computed: {
        filteredGroups() {
            return this.groups.filter(group =>
                group.name.toLowerCase().includes(this.searchQuery.toLowerCase()))
        },
        sortedGroups() {
            return [...this.filteredGroups].sort((a, b) => {
                const modifier = this.sortOrder === 'asc' ? 1 : -1

                if (this.sortKey === 'users_count' || this.sortKey === 'projects_count') {
                    return (a[this.sortKey] - b[this.sortKey]) * modifier
                }

                if (a[this.sortKey] < b[this.sortKey]) return -1 * modifier
                if (a[this.sortKey] > b[this.sortKey]) return 1 * modifier
                return 0
            })
        }
    },
    async mounted() {
        await this.loadUserGroups();
    },
    setup() {
        const {handleApiError} = useErrorHandling();
        return {handleApiError};
    },
    methods: {
        async loadUserGroups() {
            this.loading = true;
            try {
                const authStore = useAuthStore();
                const currentUserId = authStore.user?.id;

                const response = await axios.get(
                    'http://localhost:8000/account/groups/',
                    {withCredentials: true}
                );

                const projectsResponse = await axios.get(
                    'http://localhost:8000/project/',
                    {withCredentials: true}
                );
                const allGroups = response.data || [];
                if (!Array.isArray(allGroups)) {
                    throw new Error('Некорректный формат данных групп');
                }

                const userGroups = allGroups.filter(group =>
                    group && group.users && Array.isArray(group.users) && group.users.includes(currentUserId)
                );
                const allProjects = projectsResponse.data || [];
                if (!Array.isArray(allProjects)) {
                    throw new Error('Некорректный формат данных проектов');
                }

                const projectsByGroup = {};
                allProjects.forEach(project => {
                    if (project && project.group) {
                        const groupId = project.group;

                        if (userGroups.some(g => g.id === groupId)) {
                            projectsByGroup[groupId] = (projectsByGroup[groupId] || 0) + 1;
                        }
                    }
                });

                this.groups = userGroups.map(group => ({
                    ...group,
                    users_count: group.users ? group.users.length : 0,
                    projects_count: projectsByGroup[group.id] || 0
                }));


            } catch (error) {
                this.handleApiError(error);
                if (error.response?.status === 403) {
                    this.$router.push('/login');
                } else {
                    console.error('Ошибка загрузки групп:', error);
                    this.error = 'Не удалось загрузить список групп';
                    this.groups = [];
                }
            } finally {
                this.loading = false;
            }
        },
        sortBy(key) {
            if (this.sortKey === key) {
                this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc'
            } else {
                this.sortKey = key
                this.sortOrder = 'asc'
            }
        },
        openGroup(id) {
            this.$router.push(`/group/${id}`)
        },
        handleSearch() {
        }
    }
}
</script>

<style scoped>
.group-list-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 24px;
}

.list-header {
    margin-bottom: 32px;
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
}

.list-title {
    font-size: 24px;
    font-weight: 500;
    margin: 0;
    color: #172b4d;
}

.primary-button {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    background-color: #85ABEC;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    text-decoration: none;
    transition: background-color 0.2s;
}

.primary-button:hover {
    background-color: #6C96D8;
}

.controls-row {
    display: flex;
    gap: 16px;
    align-items: center;
}

.search-input {
    position: relative;
    flex-grow: 1;
    max-width: 400px;
}

.search-input input {
    width: 100%;
    padding: 8px 32px 8px 12px;
    border: 1px solid #dfe1e6;
    border-radius: 4px;
    font-size: 14px;
}

.search-input .bi {
    position: absolute;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
    color: #5e6c84;
}

.groups-table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    border: 1px solid #dfe1e6;
    border-radius: 4px;
    overflow: hidden;
}

.groups-table th,
.groups-table td {
    padding: 12px 16px;
    text-align: left;
    border-bottom: 1px solid #ebecf0;
}

.groups-table th {
    background-color: #f4f5f7;
    color: #5e6c84;
    font-weight: 600;
    font-size: 14px;
}

.groups-table tbody tr {
    transition: background-color 0.2s;
    cursor: pointer;
}

.groups-table tbody tr:hover {
    background-color: #fafbfc;
}

.sortable {
    cursor: pointer;
    user-select: none;
}

.sortable:hover {
    background-color: #ebecf0;
}

.group-name {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 500;
    color: #172b4d;
}

.loading-state,
.error-state,
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
    padding: 40px;
    color: #5e6c84;
    background: white;
    border: 1px solid #dfe1e6;
    border-radius: 4px;
}

.spinner {
    width: 32px;
    height: 32px;
    border: 3px solid rgba(0, 82, 204, 0.1);
    border-top-color: #0052cc;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

.groups-table td:first-child {
    width: 50%;
}

.groups-table td:nth-child(2),
.groups-table td:nth-child(3) {
    width: 25%;
    text-align: center;
}
</style>