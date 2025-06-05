<template>
    <div class="create-group-page">
        <h2>Создание новой группы</h2>
        <form @submit.prevent="submitForm" class="group-form">
            <div class="form-group">
                <label>Название группы *</label>
                <input
                    type="text"
                    v-model="formData.name"
                    required
                    class="form-control"
                    placeholder="Введите название группы"
                >
            </div>


            <div class="form-group">
                <label>Участники группы</label>
                <div class="user-search-wrapper" ref="searchContainer">
                    <SearchInput
                        v-model="userSearch"
                        placeholder="Поиск пользователей по email"
                        @search="searchUsers"
                        @focus="showResults = true"
                        :debounce-time="300"
                    />
                    <div v-if="searchResults.length && showResults" class="search-results">
                        <div
                            v-for="user in searchResults"
                            :key="user.id"
                            class="search-result-item"
                            @click="addUser(user)"
                        >
                            {{ user.email }}
                        </div>
                    </div>
                    <div v-else-if="!searchResults.length && userSearch" class="no-results-message">
                        Пользователи не найдены
                    </div>
                </div>

                <div v-if="selectedUsers.length" class="selected-users">
                    <div
                        v-for="user in selectedUsers"
                        :key="user.id"
                        class="selected-user"
                    >
                        <span @click.stop="goToUser(user.id)">{{ user.email }}</span>
                        <button
                            v-if="user.id !== authStore.user.id"
                            type="button"
                            @click="removeUser(user)"
                            class="remove-user-btn"
                        >
                            ×
                        </button>
                    </div>
                </div>
            </div>

            <div class="form-actions">
                <button
                    type="submit"
                    class="btn btn-primary"
                    :disabled="loading"
                >
                    {{ loading ? 'Создание...' : 'Создать группу' }}
                </button>
                <button
                    type="button"
                    @click="cancel"
                    class="btn btn-secondary"
                >
                    Отмена
                </button>
            </div>

            <div v-if="error" class="alert alert-danger">
                {{ error }}
            </div>
        </form>
    </div>
</template>

<script>
import axios from "axios"
import {useAuthStore} from "@/stores/auth"
import SearchInput from "@/components/SearchInput.vue";
import {useErrorHandling} from "@/utils/ErrorHandling";

export default {
    components: {SearchInput},
    data() {
        return {
            loading: false,
            error: null,
            userSearch: '',
            searchResults: [],
            selectedUsers: [],
            formData: {
                name: '',
                users: []
            },
            showResults: false,
            authStore: useAuthStore()
        }
    },
    async mounted() {
        document.addEventListener('click', this.handleClickOutside);
    },
    beforeUnmount() {
        document.removeEventListener('click', this.handleClickOutside);
    },
    watch: {
        userSearch(newVal) {
            this.showResults = newVal.length > 0;
        }
    },
    async created() {
        await useAuthStore().checkAuth()
        const authStore = useAuthStore()
        if (authStore.user) {
            this.selectedUsers.push(authStore.user)
        }
    },
    setup() {
        const {handleApiError} = useErrorHandling();
        return {handleApiError};
    },
    methods: {
        async searchUsers() {
            if (!this.userSearch) {
                this.searchResults = [];
                return;
            }

            try {
                const response = await axios.get(`http://localhost:8000/account/users/?email=${this.userSearch}`,
                    {
                        withCredentials: true
                    })
                this.searchResults = response.data.filter(user =>
                    !this.selectedUsers.some(u => u.id === user.id))
            } catch (error) {
                this.handleApiError(error);
                console.error('Ошибка поиска пользователей:', error)
            }
        },
        addUser(user) {
            if (!this.selectedUsers.some(u => u.id === user.id)) {
                this.selectedUsers.push(user)
                this.userSearch = ''
                this.searchResults = []
            }
        },
        removeUser(user) {
            if (user.id === this.authStore.user.id) {
                return;
            }
            this.selectedUsers = this.selectedUsers.filter(u => u.id !== user.id);
        },
        async submitForm() {
            try {
                this.loading = true
                this.error = null

                if (!this.formData.name.trim()) {
                    throw new Error('Название группы обязательно')
                }

                const payload = {
                    ...this.formData,
                    users: this.selectedUsers.map(user => user.id)
                }

                await axios.post('http://localhost:8000/account/groups/', payload, {
                    withCredentials: true,
                    headers: {
                        'X-CSRFToken': this.getCookie('csrftoken')
                    }
                })

                this.$router.push('/groups')
            } catch (error) {
                this.handleApiError(error);
                this.error = this.getErrorMessage(error)
            } finally {
                this.loading = false
            }
        },
        cancel() {
            this.$router.go(-1)
        },
        getCookie(name) {
            const value = `; ${document.cookie}`
            const parts = value.split(`; ${name}=`)
            if (parts.length === 2) return parts.pop().split(';').shift()
        },
        getErrorMessage(error) {
            if (error.response) {
                if (error.response.status === 400) {
                    return error.response.data?.detail || 'Некорректные данные группы'
                }
                if (error.response.status === 403) {
                    return 'Ошибка доступа'
                }
            }
            return error.message || 'Произошла неизвестная ошибка'
        },
        handleClickOutside(e) {
            if (!this.$refs.searchContainer.contains(e.target)) {
                this.showResults = false;
            }
        },
        goToUser(userId) {
            this.$router.push({name: 'profile', params: {id: userId}});
        }
    }
}
</script>

<style scoped>
.create-group-page {
    max-width: 500px;
    margin: 20px auto;
    padding: 20px;
    justify-content: center;

}

.group-form {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.form-group {
    margin-bottom: 15px;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: 600;
    color: #5e6c84;
}

.form-control {
    width: 445px;;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    box-sizing: border-box;
    transition: border-color 0.2s, box-shadow 0.2s;
}

.form-control:focus {
    outline: none;
    border-color: #6498F1;
    box-shadow: 0 0 0 2px rgba(100, 152, 241, 0.2);
}

textarea.form-control {
    min-height: 100px;
    resize: vertical;
}

.user-search-wrapper {
    position: relative;
}

.search-results {
    position: absolute;
    width: 100%;
    max-height: 200px;
    overflow-y: auto;
    background: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    z-index: 100;
}

.search-item {
    padding: 8px 12px;
    cursor: pointer;
    transition: background-color 0.2s;
}

.search-item:hover {
    background-color: #f5f5f5;
}

.selected-users {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 10px;
}

.selected-user {
    background: #e9ecef;
    padding: 4px 8px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    gap: 6px;
    cursor: pointer;
    transition: color 0.2s;
}


.remove-user-btn {
    background: none;
    border: none;
    color: #6c757d;
    cursor: pointer;
    padding: 0 4px;
}

.remove-user-btn:hover {
    color: #dc3545;
}

.form-actions {
    display: flex;
    gap: 10px;
    justify-content: flex-start;
}

.btn {
    padding: 8px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: opacity 0.2s;
}

.btn-primary {
    background: #6498F1;
    color: white;
}

.btn-secondary {
    background: #6c757d;
    color: white;
}

.btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}

.alert-danger {
    padding: 10px;
    margin-top: 15px;
    border-radius: 4px;
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    color: #721c24;
}

.user-search-wrapper {
    position: relative;
    max-width: 445px;
}

.search-results {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    max-height: 300px;
    overflow-y: auto;
    background: white;
    border: 1px solid #e5e5e5;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    z-index: 1000;
    margin-top: 4px;
}

.search-result-item {
    padding: 10px 15px;
    cursor: pointer;
    transition: background 0.2s;
    font-size: 14px;
}

.search-result-item:hover {
    background: #f8f9fa;
}

.no-results-message {
    padding: 10px 15px;
    color: #7f8c8d;
    font-style: italic;
}
</style>