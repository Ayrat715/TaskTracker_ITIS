<template>
  <button @click="handleLogout">Выйти</button>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();

const handleLogout = async () => {
  await authStore.logout();
  this.$router.push('/login')
};
</script>