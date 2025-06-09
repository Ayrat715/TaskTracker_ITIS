<template>
    <div class="error-page">
        <div class="error-content">
            <div class="error-icon">
                <i class="bi bi-search"></i>
            </div>
            <h1>Страница не найдена</h1>
            <p>Запрашиваемый ресурс не существует или был перемещен.</p>
            <div class="error-actions">
                <button class="app-button primary" @click="goBack">
                    <i class="bi bi-arrow-left"></i> Назад
                </button>
                <button class="app-button" @click="goHome">
                    <i class="bi bi-house"></i> На главную
                </button>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    methods: {
        goBack() {
            this.$router.go(-2);
        },
        goHome() {
            this.$router.push({name: 'home'});
        }
    }
}
</script>

<style scoped>
.error-page {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    padding: 20px;
    background: linear-gradient(135deg, #f8f9fa, #e9ecef);
}

.error-content {
    text-align: center;
    max-width: 600px;
    padding: 40px;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.error-icon {
    font-size: 80px;
    color: #6c757d;
    margin-bottom: 25px;
}

.error-icon i {
    opacity: 0.7;
}

h1 {
    font-size: 32px;
    color: #343a40;
    margin-bottom: 15px;
}

p {
    font-size: 18px;
    color: #6c757d;
    margin-bottom: 30px;
    line-height: 1.6;
}

.error-actions {
    display: flex;
    gap: 15px;
    justify-content: center;
    flex-wrap: wrap;
}

.app-button {
    min-width: 150px;
    padding: 12px 20px;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 500;
    transition: all 0.3s ease;
}

.app-button.primary {
    background: #0d6efd;
    color: white;
    border: none;
}

.app-button.primary:hover {
    background: #0b5ed7;
    transform: translateY(-2px);
    box-shadow: 0 4px 10px rgba(13, 110, 253, 0.3);
}

.app-button {
    background: white;
    color: #495057;
    border: 1px solid #dee2e6;
}

.app-button:hover {
    background: #f8f9fa;
    transform: translateY(-2px);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
}

@media (max-width: 576px) {
    .error-content {
        padding: 25px;
    }

    h1 {
        font-size: 26px;
    }

    p {
        font-size: 16px;
    }

    .error-actions {
        flex-direction: column;
    }

    .app-button {
        width: 100%;
    }
}
</style>