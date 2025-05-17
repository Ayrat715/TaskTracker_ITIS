<template>
    <button class="new-task-btn" @click="createNewTask">
        Новая задача
    </button>
</template>

<script>
export default {
    name: "CreateTaskBtn",
    methods:{
        createNewTask() {
            this.$router.push('/task/create');
        },
    }

}
</script>

<style scoped>
.new-task-btn {
    background-color: #85ABEC;
    color: white;
    border: none;
    border-radius: 4px;

    font-size: 14px;
    cursor: pointer;
    margin-left: auto;
    white-space: nowrap;
    transition: background-color 0.2s;
    height: 24px;
    width: 145px;
    text-align: center;
    justify-content: center;
}

.new-task-btn:hover {
    background-color: #6C96D8;
}

</style>