<template>
    <div class="app">
        <header v-if="showHeaderSideBar">
            <h1>Task Tracker</h1>
        </header>

        <main>
            <router-view></router-view>
        </main>
    </div>
</template>

<script>


export default {
    name: 'App',
    computed: {
        showHeaderSideBar() {
            return this.$route.name !== 'notFound' && this.$route.name !== 'register' && this.$route.name !== 'login';
        },
    },
}
</script>

<style>

</style>

