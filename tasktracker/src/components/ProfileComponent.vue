<template>
    <div class="user-profile">
        <div class="profile-header">
            <h2>Профиль пользователя
            </h2>
        </div>

        <div class="profile-content">
            <div v-if="loading" class="loading">Загрузка...</div>
            <div v-else-if="error" class="error">{{ error }}</div>
            <template v-else>
                <div class="profile-section">
                    <h3>Основная информация</h3>
                    <div class="profile-info">
                        <div class="info-item">
                            <label>Имя:</label>
                            <span>{{ userData.name }}</span>
                        </div>
                        <div class="info-item">
                            <label>Email:</label>
                            <span>{{ userData.email }}</span>
                        </div>
                    </div>
                </div>

                <div class="profile-section" v-if="groups.length">
                    <h3>Группы</h3>
                    <div class="groups-list">
                        <div v-for="group in groups" :key="group.id" class="group-item">
                            {{ group.name }}
                        </div>
                    </div>
                </div>
            </template>
        </div>
    </div>
</template>

<script>
import axios from "axios";
import {useAuthStore} from '@/stores/auth';
import {useErrorHandling} from "@/utils/ErrorHandling";

export default {
    name: 'UserProfile',
    data() {
        return {
            userData: {},
            groups: [],
            loading: true,
            error: null,
            authStore: useAuthStore()
        }
    },
    computed: {
        isCurrentUser() {
            return this.authStore.user?.id.toString() === this.$route.params.id;
        }
    },
    async mounted() {
        await this.fetchUserData();
    },
    watch: {
        '$route.params.id': {
            handler: 'fetchUserData',
            immediate: true
        }
    },
    setup() {
        const {handleApiError} = useErrorHandling();
        return {handleApiError};
    },
    methods: {
        async fetchUserData() {
            this.loading = true;
            this.error = null;

            try {
                const response = await axios.get(
                    `http://localhost:8000/account/users/${this.$route.params.id}/`,
                    {withCredentials: true}
                );

                this.userData = response.data;
                this.groups = response.data.groups || [];
            } catch (error) {
                this.handleApiError(error);
                this.error = this.getErrorMessage(error);
            } finally {
                this.loading = false;
            }
        },
        getErrorMessage(error) {
            if (error.response?.status === 404) {
                return 'Пользователь не найден';
            }
            return 'Ошибка загрузки данных';
        }
    }
}
</script>


<style scoped>
.user-profile {
    max-width: 800px;
    margin: 20px auto;
    padding: 20px;
}

.profile-header h2 {
    color: #2c3e50;
    border-bottom: 2px solid #6498F1;
    padding-bottom: 10px;
}

.profile-section {
    margin: 25px 0;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 6px;
}

.profile-section h3 {
    color: #34495e;
    margin-bottom: 15px;
}

.info-item {
    display: flex;
    margin-bottom: 10px;
}

.info-item label {
    font-weight: 600;
    min-width: 120px;
    color: #7f8c8d;
}


.setting-item label {
    font-weight: 500;
    color: #444;
}

.setting-item select {
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    background: white;
}

/* Обновленные стили */

.loading, .error {
    padding: 20px;
    text-align: center;
    font-size: 1.1em;
}

.groups-list {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.group-item {
    background: #e9ecef;
    padding: 8px 15px;
    border-radius: 4px;
    font-size: 0.9em;
}

.edit-button {
    margin-left: 20px;
}

.edit-btn {
    padding: 4px 8px;
    border: none;
    background: none;
    cursor: pointer;
    font-size: 14px;
}

.edit-btn:hover {
    text-decoration: underline;
}

</style>