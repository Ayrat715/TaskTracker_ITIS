<template>
    <div class="login-container">
        <div class="login-form">
            <h2 class="form-title">Войти в TaskTracker</h2>
            <form @submit.prevent="handleLogin" class="form">
                <div class="form-group">
                    <input
                        v-model="email"
                        type="email"
                        placeholder="Email"
                        required
                        class="form-input"
                    >
                </div>
                <div class="form-group">
                    <input
                        v-model="password"
                        type="password"
                        placeholder="Пароль"
                        required
                        class="form-input"
                    >
                </div>
                <div class="remember-me">
                    <label>
                        <input
                            type="checkbox"
                            v-model="rememberMe"
                        />
                        Запомнить меня
                    </label>
                </div>
                <button type="submit" class="submit-btn" :disabled="loading">
                    Войти
                </button>
                <p class="register-link">
                    Нет аккаунта?
                    <router-link to="/register">Зарегистрироваться</router-link>
                </p>
            </form>
            <p v-if="error" class="error-message">{{ error }}</p>
        </div>
    </div>
</template>

<script>
import {useRouter} from 'vue-router'
import axios from 'axios'
import {useAuthStore} from '@/stores/auth'

export default {
    name : 'LoginComponent',
    data() {
        return {
            email: '',
            password: '',
            rememberMe: false,
            error: '',
            loading: false
        }
    },
    setup() {
        const authStore = useAuthStore()
        const router = useRouter()
        return {authStore, router}
    },
    mounted() {
        const savedEmail = localStorage.getItem('rememberedEmail')
        if (savedEmail) {
            this.email = savedEmail
            this.rememberMe = true
        }
    },
    methods: {
        async handleLogin() {
            this.error = ''
            this.loading = true

            try {
                const response = await axios.post('http://localhost:8000/account/login-user/', {
                    email: this.email,
                    password: this.password
                }, {
                    withCredentials: true,
                    headers: {
                        'X-CSRFToken': this.getCookie('csrftoken'),
                        'Content-Type': 'application/json'
                    }
                })

                this.authStore.setUser(response.data.user)

                if (this.rememberMe) {
                    localStorage.setItem('rememberedEmail', this.email)
                } else {
                    localStorage.removeItem('rememberedEmail')
                }

                await this.router.push({name: 'home'})
            } catch (err) {
                if (err.response) {
                    if (err.response.status === 400) {
                        this.error = 'Неверные email или пароль'
                    } else {
                        this.error = 'Ошибка сервера. Попробуйте позже.'
                    }
                } else {
                    this.error = 'Ошибка сети. Проверьте подключение.'
                }
            } finally {
                this.loading = false
            }
        },
        getCookie(name) {
            const value = `; ${document.cookie}`
            const parts = value.split(`; ${name}=`)
            if (parts.length === 2) return parts.pop().split(';').shift()
        }
    }
}
</script>

<style scoped>
.login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background-color: #f3f4f6;
    padding: 16px;
}

.login-form {
    width: 100%;
    max-width: 400px;
    padding: 40px;

}

.form-title {
    text-align: center;
    margin-bottom: 24px;
    color: #333;
    font-size: 40px;
}

.form {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.form-group {
    margin-bottom: 6px;
}

.form-input {
    width: 100%;
    padding: 6px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
    transition: border-color 0.2s;
    box-sizing: border-box;
}

.form-input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.submit-btn {
    background-color: #3b82f6;
    color: white;
    border: none;
    padding: 6px;
    border-radius: 6px;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.3s;
}

.submit-btn:hover:not(:disabled) {
    background-color: #2563eb;
}

.submit-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}

.remember-me {
    display: flex;
    align-items: center;
    gap: 8px;
}

.remember-me label {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
}

.remember-me input[type="checkbox"] {
    appearance: none;
    -webkit-appearance: none;
    width: 18px;
    height: 18px;
    border: 1px solid #000;
    border-radius: 3px;
    cursor: pointer;
    position: relative;
    outline: none;
}

.remember-me input[type="checkbox"]:checked {
    background-color: #000;
}

.remember-me input[type="checkbox"]:checked::after {
    content: "✓";
    color: white;
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    font-size: 12px;
}

.register-link {
    text-align: center;
    margin-top: 16px;
    color: #666;
}

.register-link a {
    color: #3b82f6;
    text-decoration: none;
}

.register-link a:hover {
    text-decoration: underline;
}

.error-message {
    color: #ef4444;
    text-align: center;
    margin-top: 16px;
}
</style>