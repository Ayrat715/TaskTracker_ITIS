<template>
    <div class="project-list-container">
        <div class="list-header">
            <div class="header-content">
                <h1 class="list-title">Проекты</h1>
            </div>

            <div class="header-content">
                <SearchInput
                    v-model="searchQuery"
                    placeholder="Поиск проектов..."
                    @search="handleSearch"
                />
                <router-link
                    to="/project/create"
                    class="primary-button"
                >
                    <i class="bi bi-plus-lg"></i>
                    Новый проект
                </router-link>
            </div>
        </div>

        <div class="content-wrapper">
            <div v-if="loading" class="loading-state">
                <div class="spinner"></div>
                Загрузка проектов...
            </div>

            <div v-else-if="error" class="error-state">
                <i class="bi bi-exclamation-circle"></i>
                {{ error }}
            </div>

            <div v-else-if="filteredProjects.length === 0" class="empty-state">
                <i class="bi bi-folder"></i>
                Нет доступных проектов
            </div>

            <table v-else class="projects-table">
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
                    v-for="project in sortedProjects"
                    :key="project.id"
                    @click="openProject(project.id)"
                >
                    <td>
                        <i class="bi bi-folder"></i>
                        {{ project.name }}
                    </td>
                    <td>{{ formatDate(project.start_time) }}</td>
                    <td>{{ formatDate(project.end_time) }}</td>
                    <td>
              <span class="status-badge" :class="getStatusClass(project)">
                {{ getProjectStatus(project) }}
              </span>
                    </td>
                </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>

<script>
import axios from 'axios'
import SearchInput from "@/components/SearchInput.vue";

export default {
    components: {SearchInput},
    data() {
        return {
            loading: true,
            error: null,
            projects: [],
            searchQuery: '',
            sortKey: 'name',
            sortOrder: 'asc',
            tableHeaders: [
                {title: 'Название', key: 'name', sortable: true},
                {title: 'Начало', key: 'start_time', sortable: true},
                {title: 'Окончание', key: 'end_time', sortable: true},
                {title: 'Статус', key: 'status', sortable: true}
            ]
        }
    },
    computed: {
        filteredProjects() {
            return this.projects.filter(project =>
                project.name.toLowerCase().includes(this.searchQuery.toLowerCase()))
        },
        sortedProjects() {
            return [...this.filteredProjects].sort((a, b) => {
                const modifier = this.sortOrder === 'asc' ? 1 : -1
                if (a[this.sortKey] < b[this.sortKey]) return -1 * modifier
                if (a[this.sortKey] > b[this.sortKey]) return 1 * modifier
                return 0
            })
        }
    },
    async mounted() {
        this.loadUserProjects();
    },
    methods: {
        async loadUserProjects() {
            this.loading = true;
            try {
                const response = await axios.get(
                    'http://localhost:8000/project/',
                    {withCredentials: true}
                );
                this.projects = response.data || [];
            } catch (error) {
                if (error.response?.status === 403) {
                    this.$router.push('/login');
                } else {
                    console.error('Ошибка загрузки проектов:', error);
                    this.projects = [];
                }
            } finally {
                this.loading = false;
            }
        },
        formatDate(dateString) {
            if (!dateString) return ''
            return new Date(dateString).toLocaleDateString('ru-RU')
        },
        getProjectStatus(project) {
            const now = new Date()
            const start = new Date(project.start_time)
            const end = new Date(project.end_time)

            if (now < start) return 'Запланирован'
            if (now > end) return 'Завершен'
            return 'Активен'
        },
        getStatusClass(project) {
            const status = this.getProjectStatus(project)
            return {
                'planned': status === 'Запланирован',
                'active': status === 'Активен',
                'completed': status === 'Завершен'
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
        openProject(id) {
            this.$router.push(`/project/${id}`)
        },
        handleSearch() {
            this.$emit('search-changed', this.searchQuery);
        }
    }
}
</script>

<style scoped>
.project-list-container {
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

.projects-table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    border: 1px solid #dfe1e6;
    border-radius: 4px;
    overflow: hidden;
}

.projects-table th,
.projects-table td {
    padding: 12px 16px;
    text-align: left;
    border-bottom: 1px solid #ebecf0;
}

.projects-table th {
    background-color: #f4f5f7;
    color: #5e6c84;
    font-weight: 600;
    font-size: 14px;
}

.projects-table tbody tr {
    transition: background-color 0.2s;
    cursor: pointer;
}

.projects-table tbody tr:hover {
    background-color: #fafbfc;
}

.sortable {
    cursor: pointer;
    user-select: none;
}

.sortable:hover {
    background-color: #ebecf0;
}

.project-name {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 500;
    color: #172b4d;
}

.status-badge {
    display: inline-block;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
    text-transform: uppercase;
}

.status-badge.planned {
    background-color: #fff0b3;
    color: #172b4d;
}

.status-badge.active {
    background-color: #deebff;
    color: #0747a6;
}

.status-badge.completed {
    background-color: #e3fcef;
    color: #006644;
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
</style>