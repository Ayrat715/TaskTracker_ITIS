<template>
  <div class="register-container">
    <div class="register-form">
      <h2 class="form-title">Регистрация</h2>
      <form @submit.prevent="register" class="form">
        <div class="form-group">
          <input
              v-model="email"
              type="email"
              placeholder="Адрес электронной почты"
              required
              class="form-input"
          >
        </div>
        <div class="form-group">
          <input
              v-model="name"
              type="text"
              placeholder="Логин"
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
        <div class="form-group">
          <input
              v-model="password2"
              type="password"
              placeholder="Подтвердите пароль"
              required
              class="form-input"
          >
        </div>
        <p class="login-link">Уже есть аккаунт? <a href="/login">Войти</a></p>
        <button type="submit" class="submit-btn">Зарегистрироваться</button>
      </form>
      <p v-if="error" class="error-message">{{ error }}</p>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      email: '',
      name: '',
      password: '',
      password2: '',
      error: ''
    }
  },
  methods: {
    async register() {
      if (this.password !== this.password2) {
        this.error = 'Пароли не совпадают'
        return
      }
      const passwordErrors = this.validatePassword(this.password);
      if (passwordErrors.length > 0) {
        this.error = passwordErrors.join(', ');
        return;
      }

      try {
        await axios.post('http://localhost:8000/account/registration-user/', {
          email: this.email,
          name: this.name,
          password: this.password,
          password2: this.password2
        });


        this.$router.push('/login')
      } catch (err) {
        if (err.response) {
          if (err.response.data.email) {
            this.error = err.response.data.email.join(' ')
          } else if (err.response.data.password) {
            this.error = err.response.data.password.join(' ')
          } else if (err.response.data.name) {
            this.error = err.response.data.name.join(' ')
          } else {
            this.error = err.response.data.detail || 'Ошибка регистрации'
          }
        } else if (err.request) {
          this.error = 'Не удалось соединиться с сервером'
        } else {
          this.error = 'Произошла ошибка'
        }
        console.error('Registration error:', err)
      }
    },
    validatePassword(password) {
    const errors = [];

    if (password.length < 8) {
      errors.push('Пароль должен содержать минимум 8 символов');
    }

    if (/^\d+$/.test(password)) {
      errors.push('Пароль не может состоять только из цифр');
    }

    const commonPasswords = ['password', '12345678', 'qwertyui'];
    if (commonPasswords.includes(password.toLowerCase())) {
      errors.push('Слишком простой пароль');
    }

    return errors;
  },
  }
}
</script>

<style>

body {
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
}

.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #F3F4F6;
  padding: 16px;
}

.register-form {
  width: 100%;
  max-width: 500px;
  padding: 32px;
}

.form-title {
  text-align: center;
  margin-bottom: 20px;
  color: #333;
  font-size: 26px;
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
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #3B82F6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.submit-btn {
  width: 100%;
  background-color: #3B82F6;
  color: white;
  border: none;
  padding: 10px 12px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
  box-sizing: border-box;
}

.submit-btn:hover {
  background-color: #2563eb;
}

.login-link {
  text-align: center;
  margin-top: 6px;
  color: #666;
}

.login-link a {
  color: #3B82F6;
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}

.error-message {
  color: #ef4444;
  text-align: center;
  margin-top: 16px;
}
</style>