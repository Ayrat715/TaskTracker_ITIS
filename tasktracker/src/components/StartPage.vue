<template>
    <div class="welcome-screen">
            <div class="welcome-card">
                <h2>Добро пожаловать в TaskTracker!</h2>
                <p>Начните работу, создав свой первый проект</p>

                <div class="welcome-actions">
                    <CreateTaskBtn class="new-group-btn" @click="router().push(`/project/create`)">Создать проект</CreateTaskBtn>
                    <CreateTaskBtn class="new-group-btn" @click="router().push(`/group/create`)">Создать группу</CreateTaskBtn>

                </div>

                <div class="welcome-features">
                    <div class="feature">
                        <i class="bi bi-kanban"></i>
                        <h4>Agile-доски</h4>
                        <p>Управляйте задачами с помощью гибких досок</p>
                    </div>

                    <div class="feature">
                        <i class="bi bi-people"></i>
                        <h4>Командная работа</h4>
                        <p>Создавайте группы и распределяйте задачи</p>
                    </div>

                    <div class="feature">
                        <i class="bi bi-graph-up"></i>
                        <h4>Отслеживание прогресса</h4>
                        <p>Контролируйте выполнение задач и спринтов</p>
                    </div>
                </div>
            </div>
        </div>
</template>
<script>
import CreateTaskBtn from "@/components/CreateTaskBtn.vue";

export default {
    name: "StartPage",
    components: {CreateTaskBtn}
}
</script>


<style scoped>
.welcome-screen {
    display: flex;
    justify-content: center;
    align-items: center;
    flex: 1;
    padding: 40px 20px;

}

.welcome-card {
    max-width: 100%;
    width: 100%;
    height: 100%;
    text-align: center;

}

.welcome-card h2 {
    font-size: 32px;
    margin-bottom: 16px;
    color: #2c3e50;
}

.welcome-card p {
    font-size: 18px;
    color: #7f8c8d;
    margin-bottom: 32px;
}

.welcome-actions {
    justify-content: center;
    gap: 16px;
    margin-bottom: 40px;
    display: flex;
    margin-left: 0;
}

.welcome-features {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 30px;
    margin-top: 40px;
}

.feature {
    padding: 25px;
    border-radius: 10px;
    background: #f8fafc;
    transition: transform 0.3s ease;
}

.feature:hover {
    transform: translateY(-5px);
}

.feature i {
    font-size: 48px;
    color: #6498F1;
    margin-bottom: 20px;
}

.feature h4 {
    font-size: 20px;
    margin-bottom: 12px;
    color: #2c3e50;
}

.feature p {
    font-size: 16px;
    color: #7f8c8d;
    margin-bottom: 0;
}

@media (max-width: 768px) {
    .welcome-actions {
        flex-direction: column;
    }

    .welcome-card {
        padding: 25px;
    }
}

create-task-btn {
    margin-left: 0;
}

.new-group-btn {
    margin-left: 0;
}
</style>