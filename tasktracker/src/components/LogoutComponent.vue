<template>
    <button @click="handleLogout">Выйти</button>
</template>

<script>
import {useAuthStore} from '@/stores/auth';

export default {
    name : 'LogoutComponent',
    data() {
        return {
            authStore: null
        };
    },
    created() {
        this.authStore = useAuthStore();
    },
    methods: {
        async handleLogout() {
            await this.authStore.logout();
            this.$router.push('/login');
        }
    }
}
</script>