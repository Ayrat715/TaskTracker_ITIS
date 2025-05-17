<template>
    <div class="task-card" @click="$emit('click')">
        <div class="task-header">
            <span class="task-id">TAS-{{task.task_number}}</span>
            <h4 class="task-title">{{ task.name }}</h4>
        </div>
        <div class="task-footer">
            <div class="executors">
                <span v-if="task.executors?.length">
                    {{ task.executors.map(e => e.name).join(', ') }}
                </span>
                <span v-else>не определен</span>
            </div>
            <span class="priority">
                <i class="bi bi-flag"></i>
                {{ task.priority.type }}
            </span>
            <span class="time">до {{ formatTime(task.given_time) }}</span>
        </div>
    </div>
</template>

<script>
import {useAuthStore} from "@/stores/auth";
import {useTasksStore} from '@/stores/tasks';
import {onMounted} from "vue";

export default {
    name: 'TaskCard',
    setup() {
        const tasksStore = useTasksStore();
        const authStore = useAuthStore();

        onMounted(() => {
            tasksStore.fetchPriorities();
        });

        return {authStore, tasksStore};
    },
    props: {
        task: {
            type: Object,
            required: true
        }
    },
    methods: {
        formatTime(timeString) {
            if (!timeString) return 'Без срока';
            const date = new Date(timeString);
            return date.toLocaleDateString('ru-RU');
        }
    },

}
</script>

<style scoped>
.task-card {
    position: relative;
    height: 80px !important;
    border: 1px solid #e5e5e5;
    border-radius: 4px;
    padding: 8px 12px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: all 0.2s;
    overflow: hidden;
    background: white;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border-left: 4px solid #00EAFF;
}

.task-card:hover {
    border-color: #b3b3b3;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.task-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
}

.task-id {
    font-size: 12px;
    font-weight: 600;
    color: #555;
    white-space: nowrap;
}

.task-title {
    margin: 0;
    font-size: 14px;
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    flex-grow: 1;
}

.task-footer {
    position: absolute;
    bottom: 8px;
    left: 12px;
    right: 12px;
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: #666;
}

.executor {
    flex: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.priority {
    margin: 0 8px;
    color: #ff6b00;
    font-weight: 500;
}

.time {
    font-style: italic;
}
</style>