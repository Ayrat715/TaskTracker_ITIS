<template>
    <div class="agile-board">

        <AgileBoardHeader
            :current-project="currentProject || {}"
            :sprints="sprints"
            :current-sprint="sprints.find(s => s.id === currentSprint) || {}"
            @sprint-changed="changeSprint"
            @search-changed="handleSearch"
            @project-changed="changeProject"
        />

        <div class="columns-header-wrapper">
            <div class="columns-header-container">
                <div
                    v-for="column in columns"
                    :key="column.id"
                    class="column-header"
                >
                    <h3>{{ column.title }} ({{ columnTasks(column).length }})</h3>
                </div>
            </div>
        </div>
        <div class="board-container">
            <div
                v-for="column in columns"
                :key="column.id"
                class="board-column"
                @dragover.prevent
                @dragenter.prevent
                @drop="onDrop($event, column)"
                :data-column-id="column.id"
            >

                <draggable
                    :list="columnTasks(column)"
                    group="tasks"
                    item-key="id"
                    class="task-list"
                    @end="onDragEnd"
                >
                    <template #item="{ element: task }">
                        <TaskCardComponent
                            :task="task"
                            :data-id="task.id"
                            draggable="true"
                            @dragstart="onDragStart($event, task)"
                        />
                    </template>
                </draggable>
            </div>
        </div>

        <TaskDetailsModalComponent
            v-if="selectedTask"
            :task="selectedTask"
            :sprints="sprints"
            @close="selectedTask = null"
            @save="saveTask"
        />
    </div>
</template>

<script>
import axios from 'axios'
import draggable from 'vuedraggable'
import {useAuthStore} from '@/stores/auth'
import {useProjectsStore} from '@/stores/projects'
import TaskCardComponent from "@/components/TaskCardComponent.vue";
import AgileBoardHeader from "@/components/AgileBoardHeader.vue";
import TaskDetailsModalComponent from "@/components/TaskDetailsModalComponent.vue";
import {mapActions, mapState} from "pinia";

export default {
    name: 'AgileBoard',
    components: {draggable, AgileBoardHeader, TaskCardComponent, TaskDetailsModalComponent},
    data() {
        return {
            sprints: [],
            currentSprint: null,
            currentProject: null,
            tasks: [],
            selectedTask: null,
            columns: [],
            priorities: [],
            categories: [],
            searchQuery: '',
            allTasks: [],
            authStore: useAuthStore(),

        }
    },
    async mounted() {
        const projectsStore = useProjectsStore();
        await projectsStore.fetchProjects();

        if (!projectsStore.currentProject && projectsStore.projects.length) {
            projectsStore.setCurrentProject(projectsStore.projects[0]);
        }
        this.currentProject = projectsStore.currentProject;

        await this.loadStatuses()
        await this.loadPriorities()
        // this.loadCategories()
        await this.loadSprints()
    },
    computed: {
        ...mapState(useProjectsStore, ['currentProject', 'projects'])
    },
    methods: {
        ...mapActions(useProjectsStore, ['setCurrentProject']),
        handleSearch(query) {
            this.searchQuery = query.toLowerCase();
            if (!query) {
                this.tasks = [...this.allTasks];
            } else {
                this.tasks = this.allTasks.filter(task =>
                    task.name.toLowerCase().includes(this.searchQuery) ||
                    task.description.toLowerCase().includes(this.searchQuery) ||
                    (task.executor && task.executor.name.toLowerCase().includes(this.searchQuery)))
            }
        },
        async loadTasks() {
            try {
                if (!this.currentSprint) {
                    this.tasks = [];
                    return;
                }

                const response = await axios.get(`http://localhost:8000/task/tasks/?sprint=${this.currentSprint}`);

                const [executorsResponse, prioritiesResponse] = await Promise.all([
                    axios.get(`http://localhost:8000/project/${this.currentProject.id}/employees/`),
                    axios.get('http://localhost:8000/task/priorities/')
                ]);


                const executorsMap = new Map(executorsResponse.data.map(e => [e.id, e]));
                const prioritiesMap = new Map(prioritiesResponse.data.map(p => [p.id, p]));

                this.allTasks = response.data.map(task => ({
                    ...task,
                    sprint: task.sprints_ids || [],
                    executors: task.executor_ids?.length
                        ? task.executor_ids.map(id => executorsMap.get(id)).filter(Boolean)
                        : [],
                    priority: task.priority ? prioritiesMap.get(task.priority) : null,
                    status: this.getStatusType(task.status),
                }));
                this.tasks = [...this.allTasks];
            } catch (error) {
                console.error('Ошибка при загрузке задач:', error);
                this.tasks = [];
            }
        },
        getStatusType(statusId) {
            const statusStr = statusId.toString();
            const status = this.taskStatuses.find(s => s.id.toString() === statusStr);
            return status ? status.type : 'planned';
        },
        async changeSprint(sprint) {
            const projectsStore = useProjectsStore();
            projectsStore.setCurrentSprint(sprint);
            this.currentSprint = sprint.id;
            await this.loadTasks();
        },
        async changeProject(project) {
            const projectsStore = useProjectsStore();
            projectsStore.setCurrentProject(project);
            this.currentProject = project;
            await this.loadSprints();
        },

        onDragStart(event, task) {
            event.dataTransfer.setData('taskId', task.id.toString())
            this.draggedTask = task
        },
        async onDrop(event, column) {
            event.preventDefault();
            const taskId = event.dataTransfer.getData('taskId');
            const task = this.tasks.find(t => t.id.toString() === taskId);

            if (task && task.status !== column.apiStatus) {
                try {
                    const statusId = this.taskStatuses.find(s => s.type === column.apiStatus)?.id;
                    if (!statusId) return;

                    await axios.patch(`http://localhost:8000/task/tasks/${taskId}/`, {
                        status: statusId
                    });

                    task.status = column.apiStatus;
                } catch (error) {
                    console.error('Ошибка при обновлении статуса задачи:', error);
                }
            }
        },

        async onDragEnd(evt) {
            const taskId = evt.item.dataset.id;
            const newStatus = this.getStatusFromColumn(evt.to);

            try {
                const statusId = this.taskStatuses.find(s => s.type === newStatus)?.id;
                if (!statusId) return;

                await axios.patch(`http://localhost:8000/task/tasks/${taskId}/`, {
                    status: statusId
                });

                const task = this.tasks.find(t => t.id.toString() === taskId);
                if (task) task.status = newStatus;

            } catch (error) {
                console.error('Ошибка при обновлении статуса задачи:', error);
                await this.loadTasks();
            }
        },

        async loadPriorities() {
            try {
                const response = await axios.get('http://localhost:8000/task/priorities/')
                this.priorities = response.data
            } catch (error) {
                console.error('Ошибка при загрузке приоритетов:', error)
            }
        },
        async loadStatuses() {
            try {
                const response = await axios.get('http://localhost:8000/task/statuses/')
                this.taskStatuses = response.data

                this.columns = this.taskStatuses.map(status => ({
                    id: status.id.toString(),
                    title: status.type,
                    apiStatus: status.type
                }))
            } catch (error) {
                console.error('Ошибка при загрузке статусов:', error)
            }
        },
        async loadSprints() {
            try {
                if (!this.currentProject) return;

                const response = await axios.get('http://localhost:8000/task/sprints/');

                this.sprints = response.data.filter(sprint =>
                    sprint.project === this.currentProject.id
                );

                if (this.sprints.length) {
                    this.sprints.sort((a, b) =>
                        new Date(b.start_time) - new Date(a.start_time)
                    );

                    const projectsStore = useProjectsStore();
                    let selectedSprint = projectsStore.currentSprint;
                    if (selectedSprint) {
                        const sprintExists = this.sprints.some(s =>
                            s.id === selectedSprint.id &&
                            s.project === this.currentProject.id);
                        if (!sprintExists) {
                            selectedSprint = null;
                        }
                    }

                    if (!selectedSprint) {
                        const now = new Date();
                        selectedSprint = this.sprints.find(sprint => {
                            const start = new Date(sprint.start_time);
                            const end = new Date(sprint.end_time);
                            return start <= now && now <= end;
                        }) || this.sprints[0];
                    }

                    if (selectedSprint) {
                        projectsStore.setCurrentSprint(selectedSprint);
                        this.currentSprint = selectedSprint.id;
                    } else {
                        this.currentSprint = null;
                    }
                    await this.loadTasks();
                } else {
                    this.currentSprint = null;
                }
            } catch (error) {
                console.error('Ошибка при загрузке спринтов:', error);
                this.currentSprint = null;
            }
        },
        columnTasks(column) {
            return this.tasks.filter(task => {
                const inCurrentSprint = task.sprint_ids && task.sprint_ids.includes(this.currentSprint);

                const statusMatches = task.status === column.apiStatus ||
                    (task.status && task.status.toString() === column.id);

                return inCurrentSprint && statusMatches;
            });
        },
        openTaskDetails(task) {
            this.selectedTask = {...task}
        },
        async saveTask(taskData) {
            try {
                if (!taskData.name || !taskData.executors?.length || !taskData.sprint || !taskData.start_time) {
                    throw new Error('Missing required fields')
                }
                if (!Array.isArray(taskData.sprint)) {
                    taskData.sprint = [taskData.sprint]
                }

                const taskToSave = {
                    ...taskData,
                    sprint: Array.isArray(taskData.sprint) ? taskData.sprint : [taskData.sprint],
                    author: this.authStore.user.id,
                    given_time: taskData.given_time || new Date().toISOString(),
                    end_time: taskData.end_time || null,
                    priority: taskData.priority || null,
                    category: taskData.category || null,
                    nlp_metadata: taskData.nlp_metadata || null
                }

                if (taskToSave.start_time && taskToSave.end_time &&
                    new Date(taskToSave.start_time) >= new Date(taskToSave.end_time)) {
                    throw new Error('End time must be after start time')
                }

                const sprintProjects = this.sprints
                    .filter(s => taskToSave.sprint.includes(s.id))
                    .map(s => s.project)

                if (!sprintProjects.includes(taskToSave.executor.project_id)) {
                    throw new Error('Исполнитель не принадлежит проекту спринта')
                }

                if (taskData.id) {
                    await axios.put(`http://localhost:8000/task/tasks/${taskData.id}/`, taskToSave)
                } else {
                    await axios.post('http://localhost:8000/task/tasks/', taskToSave)
                }
                await this.loadTasks()
                this.selectedTask = null
            } catch (error) {
                console.error('Ошибка при сохранении задачи:', error)
                if (error.response) {
                    if (error.response.status === 403) {
                        alert('Ошибка: Исполнитель не принадлежит проекту спринта')
                    } else if (error.response.status === 400) {
                        alert(`Ошибка данных: ${JSON.stringify(error.response.data)}`)
                    }
                } else {
                    alert(`Ошибка: ${error.message}`)
                }
            }
        },
        getStatusFromColumn(columnElement) {
            const columnId = columnElement.closest('.board-column').dataset.columnId
            const column = this.columns.find(col => col.id === columnId)
            return column ? column.apiStatus : 'TODO'
        }
    }
}
</script>


<style scoped>
.agile-board {
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    display: flex;
    flex-direction: column;
    height: 100%;
    width: 100%;
    margin: 0;
    padding: 0;
    min-width: min-content;
}

.board-container {
    display: flex;
    flex: 1;
    background: #f5f5f5;
    min-height: 0;
    margin: 0;
    overflow-x: hidden;
    width: 100%;
    border-top: 1px solid #6498F1;
    transform: translateX(0);
    transition: transform 0.3s ease;
    min-width: min-content;
}

.board-container,
.columns-header-container {
    display: flex;
    min-width: min-content;
}

.board-column {
    position: relative;
    margin: 0 4px;
    flex: 1;
    min-width: 200px;
    display: flex;
    flex-direction: column;

}

.board-column:not(:last-child)::after {
    content: "";
    position: absolute;
    top: 0;
    right: -6px;
    height: 100%;
    width: 1px;
    background-color: #6498F1;

}

.board-column,
.column-header {
    flex: 1;
    min-width: 0;
    position: relative;
    box-sizing: border-box;
}


.columns-header-wrapper {
    background-color: #AFC2E3;
    border-bottom: 1px solid #6498F1;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
    position: relative;
}

.columns-header-container {
    display: flex;
    width: 100%;
    min-width: min-content;
}

.column-header {
    flex: 1;
    padding: 0 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 25px;
    min-height: 25px;
    position: relative;
    box-sizing: border-box;
}

.column-header:not(:last-child)::after {
    content: "";
    position: absolute;
    right: -2px;
    top: 0;
    height: 100%;
    width: 1px;
    background-color: #6498F1;
}

.column-header h3 {
    margin: 0;
    font-size: 14px;
    font-weight: 600;
    color: #333;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    width: 100%;
    text-align: center;
    line-height: 25px;
}

.board-column .column-header {
    flex: 1;
    min-width: 200px;
    position: relative;
}

.task-list {
    padding: 8px;
    min-height: 100px;
    flex-grow: 1;
    overflow-y: auto;
}

</style>