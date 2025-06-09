<template>
    <div class="error-page">
        <div class="error-content">
            <div class="error-icon">
                <i class="bi bi-wifi-off"></i>
            </div>
            <h1>Проблемы с подключением</h1>
            <p>Не удалось установить соединение с сервером. Пожалуйста, проверьте:</p>
            <ul class="error-list">
                <li><i class="bi bi-check-circle"></i> Ваше интернет-подключение</li>
                <li><i class="bi bi-check-circle"></i> Настройки сети и VPN</li>
                <li><i class="bi bi-check-circle"></i> Работоспособность сервера</li>
            </ul>
            <div class="error-actions">
                <button class="app-button primary" @click="reloadPage">
                    <i class="bi bi-arrow-repeat"></i> Повторить попытку
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
        reloadPage() {
            window.location.reload();
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
    color: #dc3545;
    margin-bottom: 25px;
}

h1 {
    font-size: 32px;
    color: #343a40;
    margin-bottom: 20px;
}

p {
    font-size: 18px;
    color: #6c757d;
    margin-bottom: 15px;
    line-height: 1.6;
}

.error-list {
    text-align: left;
    max-width: 400px;
    margin: 0 auto 30px;
    padding-left: 20px;
    color: #495057;
}

.error-list li {
    margin-bottom: 10px;
    font-size: 16px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.error-list i {
    color: #198754;
}

.error-actions {
    display: flex;
    gap: 15px;
    justify-content: center;
    flex-wrap: wrap;
}

.app-button {
    min-width: 180px;
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