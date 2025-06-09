<template>
    <div class="add-member-form">
        <h2>Добавить участника в группу</h2>

        <div class="search-row" ref="searchContainer">
            <div class="search-section">
                <SearchInput
                    v-model="userSearch"
                    placeholder="Поиск пользователей по email"
                    @search="searchUsers"
                    @focus="showResults = true"
                    :debounce-time="300"
                />

                <div v-if="searchResults.length === 0 && userSearch" class="empty-state">
                    Пользователи не найдены
                </div>
                <div v-if="searchResults.length && showResults" class="search-results">
                    <div
                        v-for="user in searchResults"
                        :key="user.id"
                        class="user-item"
                        @click="selectUser(user)"
                    >
                        <i class="bi bi-person-circle"></i>
                        {{ user.email }}
                    </div>
                </div>
            </div>

            <button
                class="btn btn-primary"
                :disabled="selectedUsers.length === 0"
                @click="addToGroup"
            >
                Добавить выбранного пользователя
            </button>
        </div>
        <div v-if="selectedUsers.length > 0" class="selected-users-section">
            <h3>Выбранные участники:</h3>
            <div class="selected-users-list">
                <div
                    v-for="user in selectedUsers"
                    :key="user.id"
                    class="selected-user-item"
                >
                    <div class="user-info">
                        <i class="bi bi-person-circle"></i>
                        {{ user.email }}
                    </div>
                    <button
                        class="btn-remove"
                        @click="removeSelectedUser(user.id)"
                    >
                        <i class="bi bi-x-lg"></i>
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios'
import SearchInput from "@/components/SearchInput.vue";
import {useAuthStore} from "@/stores/auth";
import {useErrorHandling} from "@/utils/ErrorHandling";

export default {
    components: {SearchInput},
    data() {
        return {
            userSearch: '',
            searchResults: [],
            selectedUsers: [],
            groupId: this.$route.params.id,
            showResults: false,
            authStore: useAuthStore(),
            currentMembers: [],
            isSearching: false
        }
    },
    async mounted() {
        document.addEventListener('click', this.handleClickOutside);
        await this.fetchCurrentMembers();
    },
    beforeUnmount() {
        document.removeEventListener('click', this.handleClickOutside);
    },
    async created() {
        await useAuthStore().checkAuth()
    },
    watch: {
        userSearch(newVal) {
            this.showResults = newVal.length > 0;
        }
    },
    setup() {
        const {handleApiError} = useErrorHandling();
        return {handleApiError};
    },
    methods: {
        async fetchCurrentMembers() {
            try {
                this.loading = true;
                const response = await axios.get(
                    `http://localhost:8000/account/groups/`,
                    {withCredentials: true}
                );

                const groupData = response.data.find(
                    group => group.id.toString() === this.groupId
                );

                this.currentMembers = groupData.users;
            } catch (error) {
                this.handleApiError(error);
                console.error('Ошибка загрузки участников:', error);
            }
        },
        async searchUsers() {
            if (!this.userSearch.trim()) {
                this.searchResults = [];
                return;
            }
            this.isSearching = true;
            try {
                const response = await axios.get('http://localhost:8000/account/users/', {
                    params: {email: this.userSearch},
                    withCredentials: true
                })

                const searchTerm = this.userSearch.toLowerCase();
                this.searchResults = response.data.filter(user => {
                    const isMatch = user.email.toLowerCase().includes(searchTerm);
                    const isNotCurrentMember = !this.currentMembers.includes(user.id);
                    const isNotSelected = !this.selectedUsers.some(u => u.id === user.id);

                    return isMatch && isNotCurrentMember && isNotSelected;
                });
            } catch (error) {
                this.handleApiError(error);
                console.error('Ошибка поиска:', error)
            }
        },

        selectUser(user) {
            this.selectedUsers.push(user);
            this.userSearch = '';
            this.searchResults = [];
            this.showResults = false;
        },
        removeSelectedUser(userId) {
            this.selectedUsers = this.selectedUsers.filter(user => user.id !== userId);
        },

        async addToGroup() {
            if (this.selectedUsers.length === 0) return;

            try {
                const requests = this.selectedUsers.map(user =>
                    axios.put(
                        `http://localhost:8000/account/groups/${this.groupId}/`,
                        {add_user_id: user.id},
                        {
                            withCredentials: true,
                            headers: {
                                'X-CSRFToken': this.getCookie('csrftoken')
                            }
                        }
                    )
                );
                await Promise.all(requests);

                this.$emit('users-added', this.selectedUsers);
                this.$router.replace({
                    path: `/group/${this.groupId}`,
                    query: {refresh: Date.now()}
                });
            } catch (error) {
                this.handleApiError(error);
                console.error('Ошибка добавления:', error)
                            alert(error.response?.data?.error || 'Ошибка добавления пользователя')
            }
        },
        handleClickOutside(e) {
            if (!this.$refs.searchContainer.contains(e.target)) {
                this.showResults = false;
            }
        },
        getCookie(name) {
            const value = `; ${document.cookie}`
            const parts = value.split(`; ${name}=`)
            if (parts.length === 2) return parts.pop().split(';').shift()
        },
    }
}
</script>

<style scoped>

.add-member-form {
    display: flex;
    flex-direction: column;
    gap: 20px;
    background: white;

}

.add-member-section h2 {
    font-size: 18px;
    font-weight: 600;
    margin: 0 0 10px 0;
    color: #2B2B2B;
}

.search-section {
    position: relative;
}

.search-results {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    max-height: 300px;
    overflow-y: auto;
    background: white;
    border: 1px solid #DFE1E6;
    border-radius: 0 0 4px 4px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    z-index: 1000;
    margin-top: 5px;
}

.search-section {
    max-width: 445px;
}

.user-item {
    padding: 12px 15px;
    cursor: pointer;
    transition: background 0.2s;
    border-bottom: 1px solid #F4F5F7;
}

.user-item:last-child {
    border-bottom: none;
}

.user-item:hover {
    background: #f8f9fa;
}

.btn {
    padding: 8px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: opacity 0.2s;
    font-size: 14px;
    font-weight: 500;
}

.btn-primary {
    background: #6498F1;
    color: white;
    align-self: flex-start;
    padding: 8px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: opacity 0.2s;
    font-size: 14px;
    font-weight: 500;
}

.btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}

.search-row {
    display: flex;
    gap: 15px;
    align-items: flex-start;
    position: relative;
    margin-bottom: 20px;
}

.search-section {
    flex-grow: 1;
    position: relative;
}

.selected-users-section {
    margin-top: 20px;
    border-top: 1px solid #eee;
    padding-top: 20px;
}

.selected-users-section h3 {
    font-size: 16px;
    margin-bottom: 10px;
    color: #555;
}

.selected-users-list {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.selected-user-item {
    display: flex;
    align-items: center;
    background: #f0f5ff;
    border-radius: 20px;
    padding: 8px 15px;
    border: 1px solid #d0e0ff;
}

.user-info {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-right: 10px;
}

.btn-remove {
    background: none;
    border: none;
    color: #888;
    cursor: pointer;
    padding: 0;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: all 0.2s;
}

.btn-remove:hover {
    background: #ffebee;
    color: #f44336;
}
</style>