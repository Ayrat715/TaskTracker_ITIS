<template>
    <div class="agile-header">
        <div class="header-top">
            <div class="page-info">
                <span class="page-title">Доски Agile</span>
                <span class="divider">/</span>
                <div class="project-selector" @click="toggleProjectsDropdown" v-if="authStore.user">
                    <span class="project-name" @click="router().push(`/project/${currentProject.id}`)">{{
                            currentProject.name || 'Выберите проект'
                        }}</span>
                    <i class="bi"
                       :class="{'bi-chevron-down': !showProjectsDropdown, 'bi-chevron-up': showProjectsDropdown}"></i>

                    <div class="projects-dropdown" v-if="showProjectsDropdown">
                        <div
                            v-for="project in userProjects"
                            :key="project.id"
                            @click="selectProject(project)"
                            class="project-option"
                            :class="{'active': project.id === currentProject.id}"
                        >
                            {{ project.name }}
                        </div>
                    </div>
                </div>
                <div v-else>
                    <p>Пожалуйста, войдите в систему.</p>
                </div>
                <div class="search-box-container">
                    <div class="search-box">
                        <input type="text" class="search-input" placeholder="Поиск задач..." v-model="searchQuery">
                        <i class="bi bi-search"></i>
                    </div>
                </div>

            </div>


        </div>

        <div class="header-bottom" v-if="currentProject && currentProject.id">

            <div class="sprint-info-container">
                <div class="sprint-selector" @click="toggleSprintsDropdown">
                    <div class="current-sprint">
                        <span class="sprint-name">{{ currentSprint.name }}</span>
                        <span class="divider-line"></span>
                        <span class="sprint-dates">
                            {{ formatDate(currentSprint.start_time) }} - {{ formatDate(currentSprint.end_time) }}
                        </span>
                        <i class="bi"
                           :class="{'bi-chevron-down': !showSprintsDropdown, 'bi-chevron-up': showSprintsDropdown}"></i>
                    </div>

                    <div class="sprints-dropdown" v-if="showSprintsDropdown">
                        <div
                            v-for="sprint in sprints"
                            :key="sprint.id"
                            @click="selectSprint(sprint)"
                            class="sprint-option"
                        >
                            {{ sprint.name }} ({{ formatDate(sprint.start_time) }} - {{
                                formatDate(sprint.end_time)
                            }})
                        </div>
                    </div>

                </div>

                <div class="sprint-meta">
                    <span class="days-left" v-if="daysLeft !== null">
                        {{ daysLeft }} дней осталось
                    </span>
                    <span class="sprint-description" v-if="currentSprint.description"
                          :title="currentSprint.description">
                        Описание спринта: {{ currentSprint.description }}
                    </span>
                    <CreateTaskBtn :onClick="createSprint">Начать спринт</CreateTaskBtn>
                </div>
                <CreateTaskBtn></CreateTaskBtn>
            </div>


        </div>
    </div>

</template>

<script>
import {debounce} from 'lodash';
import axios from "axios";
import {useAuthStore} from "@/stores/auth";
import CreateTaskBtn from "@/components/CreateTaskBtn.vue";
import router from "@/router";
import {useErrorHandling} from "@/utils/ErrorHandling";


export default {
    components: {CreateTaskBtn},
    props: {
        currentProject: {
            type: Object,
            required: true,
            default: () => ({})
        },
        sprints: {
            type: Array,
            required: true
        },
        currentSprint: {
            type: Object,
            required: true,
            default: () => ({})
        }
    },
    data() {
        return {
            searchQuery: '',
            showSprintsDropdown: false,
            showProjectsDropdown: false,
            userProjects: [],
            loadingProjects: false,
            authStore: useAuthStore()

        }
    },
    computed: {
        daysLeft() {
            if (!this.currentSprint?.id || !this.currentSprint?.end_time) return null;
            const endDate = new Date(this.currentSprint.end_time);
            const today = new Date();
            const diffTime = endDate - today;
            if (diffTime < 0) {
                return 0
            }
            return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        }
    },
    mounted() {
        document.addEventListener('click', this.handleClickOutsideSprints);
        document.addEventListener('click', this.handleClickOutsideProjects);
        this.loadUserProjects();
    },
    beforeUnmount() {
        document.removeEventListener('click', this.handleClickOutsideSprints);
        document.addEventListener('click', this.handleClickOutsideProjects);

        this.debouncedSearch.cancel();
        this.loadUserProjects();
    },
    setup() {
        const {handleApiError} = useErrorHandling();
        return {handleApiError};
    },
    methods: {
        createSprint() {
            this.$router.push(`project/${this.currentProject.id}/sprint/create`);
        },
        router() {
            return router
        },
        formatDate(dateString) {
            if (!dateString) return '';
            const date = new Date(dateString);
            return date.toLocaleDateString('ru-RU');
        },
        toggleSprintsDropdown() {
            this.showSprintsDropdown = !this.showSprintsDropdown;
        },
        selectSprint(sprint) {
            this.$emit('sprint-changed', sprint);
            this.showSprintsDropdown = false;
        },
        handleClickOutsideSprints(event) {
            if (!this.showSprintsDropdown) return;

            const currentSprint = this.$el.querySelector('.current-sprint');
            const sprintDates = this.$el.querySelector('.sprint-dates');

            if (!currentSprint || !sprintDates) {
                this.showSprintsDropdown = false;
                return;
            }

            if (!currentSprint.contains(event.target) && !sprintDates.contains(event.target)) {
                this.showSprintsDropdown = false;
            }

        },
        handleClickOutsideProjects(event) {
            if (!this.showProjectsDropdown) return;

            const projects = this.$el.querySelector('.project-selector');

            if (!projects) {
                this.showProjectsDropdown = false;
                return;
            }

            if (!projects.contains(event.target)) {
                this.showProjectsDropdown = false;
            }
        },

        async loadUserProjects() {
            this.loadingProjects = true;
            try {
                const response = await axios.get(
                    'http://localhost:8000/project/',
                    {withCredentials: true}
                );
                this.userProjects = response.data || [];

            } catch (error) {
                this.handleApiError(error);
            } finally {
                this.loadingProjects = false;
            }
        },


        toggleProjectsDropdown() {
            if (this.userProjects.length === 0) {
                this.loadUserProjects().then(() => {
                    this.showProjectsDropdown = !this.showProjectsDropdown;
                });
            } else {
                this.showProjectsDropdown = !this.showProjectsDropdown;
            }
        },

        selectProject(project) {
            if (project.id !== this.currentProject.id) {
                this.$emit('project-changed', project);
            }
            this.showProjectsDropdown = false;
        },
        handleSearch() {
            this.$emit('search-changed', this.searchQuery);
        }

    },
    created() {
        this.debouncedSearch = debounce(this.handleSearch, 300);
        this.loadUserProjects();
    },
    watch: {
        searchQuery() {
            this.debouncedSearch();
        }
    }
}
</script>

<style scoped>
.agile-header {
    background-color: #F3F4F6;
    padding: 12px 20px;
    border-bottom: 1px solid #e5e5e5;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.header-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    position: relative;
}

.page-info {
    display: flex;
    align-items: center;
}

.search-box-container {
    flex: 0 0 300px;
    margin-right: 16px;
}

.search-box {
    width: 100%;
    margin-left: 50px;
}

.page-info {
    display: flex;
    align-items: center;
    font-size: 18px;
    flex: 1;

}


.page-title {
    font-weight: 400;
    color: #333;
}

.divider {
    margin: 0 8px;
    color: #999;
}

.project-name {
    font-weight: 400;
    color: #333;
    text-overflow: ellipsis;

}

.search-box {
    position: relative;
    width: 400px;
}

.search-box input {
    width: 100%;
    padding: 8px 12px 8px 32px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
}

.search-box .bi {
    position: absolute;
    left: 10px;
    top: 50%;
    transform: translateY(-50%);
    color: #999;
}

.search-input:focus {
    outline: none;
    border-color: #6498F1;
    box-shadow: 0 0 0 2px rgba(100, 152, 241, 0.2);
}

.header-bottom {
    width: 100%;
}

.sprint-info-container {
    display: flex;
    align-items: center;
    gap: 16px;
    width: 100%;
    flex-wrap: nowrap;
}

.sprint-selector {
    position: relative;
    display: flex;
    align-items: center;
    cursor: pointer;
    flex-shrink: 0;
}


.current-sprint {
    display: flex;
    align-items: center;
    padding: 6px 12px;
    border: 1px solid #6498F1;
    border-radius: 4px;
    background-color: #f8fafc;
    gap: 8px;
    height: 32px;
    box-sizing: border-box;
    white-space: nowrap;
}

.divider-line {
    width: 1px;
    height: 16px;
    background-color: #6498F1;
    margin: 0 4px;
}

.current-sprint span {
    margin-right: 6px;
}

.sprint-dates {
    color: #666;
    font-size: 14px;
}


.sprints-dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    max-height: 300px;
    overflow-y: auto;
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    z-index: 100;
}


.sprint-option {
    padding: 8px 12px;
    border-bottom: 1px solid #eee;
}

.sprint-option:hover {
    background-color: #f5f5f5;
}

.sprint-meta {
    display: flex;
    align-items: center;
    gap: 32px;
    flex: 1;
    min-width: 0;
}

.days-left {
    color: #FF3985;
    font-weight: 400;
}

.sprint-description {
    color: #666;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    min-width: 0;
}


.projects-dropdown {
    position: absolute;
    top: calc(100% + 8px);
    left: 0;
    min-width: 250px;
    max-height: 400px;
    overflow-y: auto;
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06);
    z-index: 1000;
    padding: 8px 0;
    transform-origin: top;
    animation: fadeIn 0.15s ease-out;
}


.project-option {
    padding: 10px 16px;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    color: #4a5568;
    font-size: 14px;
}

.project-option:hover {
    background-color: #f7fafc;
    color: #2d3748;
}

.project-name:hover {
    cursor: pointer;
}


.projects-dropdown::-webkit-scrollbar {
    width: 6px;
}

.projects-dropdown::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 3px;
}

.projects-dropdown::-webkit-scrollbar-thumb {
    background: #cbd5e0;
    border-radius: 3px;
}

.projects-dropdown::-webkit-scrollbar-thumb:hover {
    background: #a0aec0;
}
</style>
