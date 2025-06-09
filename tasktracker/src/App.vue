<template>
    <div class="app">
        <div class="app-container">
            <aside class="sidebar" v-if="showHeaderSideBar" :class="isCollapsed || isMobile ? 'collapsed': ''">
                <div class="sidebar-top">
                    <nav class="sidebar-nav">

                        <button class="nav-item create-btn" @click="showCreateMenu = !showCreateMenu" >
                            <span class="icon-wrapper"><i class="bi bi-plus-lg"></i></span>
                            <span>Создать</span>
                        </button>

                        <router-link to="/projects" class="nav-item">
                            <span class="icon-wrapper"><img src="../src/assets/projects.png"></span>
                            <span>Проекты</span>
                        </router-link>

                        <router-link to="/groups" class="nav-item">
                            <span class="icon-wrapper"><i class="bi bi-people"></i></span>
                            <span>Группы</span>
                        </router-link>
                    </nav>
                </div>

                <div class="sidebar-bottom">
                    <button class="nav-item profile-btn" @click="showProfileMenu = !showProfileMenu">
                        <span class="icon-wrapper"><i class="bi bi-person"></i></span>
                        <span class="username">{{ authStore.user?.name || 'Пользователь' }}</span>
                    </button>


                    <button class="nav-item collapse-btn"
                            @click="isCollapsed = !isCollapsed"
                            v-if="!isMobile || !isCollapsed">
                        <i class="bi" :class="isCollapsed ? 'bi-arrow-right-circle' : 'bi-arrow-left-circle'"></i>
                        <span class="collapse-btn-text">{{ isCollapsed ? 'Развернуть' : 'Свернуть' }}</span>
                    </button>
                </div>
            </aside>

            <div class="main-area">

                <main class="main-content">
                    <router-view></router-view>

                    <div class="create-menu-container" v-if="showCreateMenu">
                        <div class="create-menu" :style="createMenuStyle">
                            <button @click="goToTaskCreate">
                                Задачу
                            </button>
                            <button @click="goToProjectCreate">
                                Проект
                            </button>
                            <button @click="goToGroupCreate">
                                Группу
                            </button>
                        </div>
                    </div>


                    <div class="profile-menu-container" v-if="showProfileMenu">
                        <div class="profile-menu" :style="profileMenuStyle">
                            <button @click="goToProfile">
                                <i class="bi bi-person-circle"></i> Профиль
                            </button>
                            <button @click="logout">
                                <i class="bi bi-box-arrow-right"></i> Выйти
                            </button>
                        </div>
                    </div>
                </main>

                <footer v-if="showHeaderSideBar" class="main-footer">
                    <div class="footer-content">
                        <div class="footer-links">
                            <router-link to="/" class="footer-btn">
                                <i class="bi bi-list"></i>
                                <span>Доски Agile</span>
                            </router-link>
                            <router-link to="/tasks" class="footer-btn">
                                <i class="bi bi-clock-history"></i>
                                <span>История задач</span>
                            </router-link>
                        </div>
                        <div class="footer-contact">
                            Появились вопросы, пиши на почту <a href="mailto:task_tracker_itis@gmail.com">task_tracker_itis@gmail.com</a>
                        </div>
                    </div>
                </footer>
            </div>


        </div>
    </div>
</template>

<script>

import {createRouter as $router} from "vue-router/dist/vue-router.esm-browser";
import router from "@/router";
import {useAuthStore} from '@/stores/auth'


export default {
    name: 'App',
    setup() {
        const authStore = useAuthStore()
        return {authStore}
    },
    data() {
        return {
            isCollapsed: false,
            isMobile: false,
            wasCollapsedBeforeMobile: false,
            showCreateMenu: false,
            clickOutsideListener: null,
            showProfileMenu: false,
            createMenuStyle: {},
            profileMenuStyle: {}
        };
    },
    async mounted() {
        this.checkScreenSize();
        window.addEventListener('resize', this.checkScreenSize);
        document.addEventListener('click', this.handleClickOutside);

    },
    beforeUnmount() {
        document.removeEventListener('click', this.handleClickOutside);

    },

    methods: {
        router() {
            return router
        },
        $router,
        checkScreenSize() {
            const newIsMobile = window.innerWidth < 992;

            if (!this.isMobile && newIsMobile) {
                this.wasCollapsedBeforeMobile = this.isCollapsed;
                this.isCollapsed = true;
            } else if (this.isMobile && !newIsMobile) {
                this.isCollapsed = this.wasCollapsedBeforeMobile;
            }

            this.isMobile = newIsMobile;
        },
        handleClickOutside(event) {
            if (!this.showCreateMenu && !this.showProfileMenu) return;

            const createMenu = this.$el.querySelector('.create-menu');
            const createBtn = this.$el.querySelector('.create-btn');

            const profileMenu = this.$el.querySelector('.profile-menu');
            const profileBtn = this.$el.querySelector('.profile-btn');

            if ((!createMenu || !createBtn) && (!profileMenu || !profileBtn)) {
                this.showCreateMenu = false;
                this.showProfileMenu = false;
                return;
            }
            if (createMenu != null && createBtn != null) {
                if (!createMenu.contains(event.target) && !createBtn.contains(event.target)) {
                    this.showCreateMenu = false;
                }
            }
            if (profileMenu != null && profileBtn != null) {
                if (!profileMenu.contains(event.target) && !profileBtn.contains(event.target)) {
                    this.showProfileMenu = false;
                }
            }
        },


        goToProfile() {
            router.push(`/user/${this.authStore.user.id}`);
            this.showProfileMenu = false;
        },
        goToTaskCreate() {
            router.push('/task/create');
            this.showCreateMenu = false;
        },
        goToProjectCreate() {
            router.push('/project/create');
            this.showCreateMenu = false;
        },
        goToGroupCreate() {
            router.push('/group/create');
            this.showCreateMenu = false;
        },

        async logout() {
            try {
                await this.authStore.logout()
                router.push('/login')
                this.showProfileMenu = false;
            } catch (error) {
                console.error('Logout failed:', error)
            }
        },

    },
    computed: {
        showHeaderSideBar() {
            return this.$route.name !== 'notFound' && this.$route.name !== 'register' && this.$route.name !== 'login'
                && this.$route.name !== 'access-denied' && this.$route.name !== 'not-found'
                && this.$route.name !== 'network-error';
        },
    },
}
</script>

<style scoped>


body {
    font-family: Arial, Trebuchet MS, Helvetica, serif;
    overflow-x: hidden;
    margin: 0;
}

.app {
    display: flex;
    min-height: 100vh;
    margin: 0;
    padding: 0;
    width: 100%;
    overflow: hidden;
}

.app-container {
    display: flex;
    width: 100%;
    min-height: 100vh;
    height: 100vh;
    margin: 0;
    padding: 0;
}

.main-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    //margin: 0;
    overflow: hidden;
}

.main-content {
    flex: 1;
    background-color: #f5f5f5;
    overflow: auto;

}

.sidebar {
    width: 300px;
    min-width: 300px;
    background-color: #6498F1;
    color: white;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding-top: 20px;
    position: relative;
    top: 0;
    left: 0;
    bottom: 0;
    overflow-y: auto;
    transform: translateX(0);
    transition: transform 0.3s ease;
    will-change: transform;

}

.sidebar ~ .main-area {
    width: calc(100% - 300px);
    transition: margin-left 0.3s ease, width 0.3s ease;
}

.main-footer {
    grid-area: footer;
    position: sticky;
    bottom: 0;
    left: 300px;
    right: 0;
    height: 60px;
    background-color: #F3F4F6;
    padding: 0 20px;
    display: flex;
    align-items: center;
    border-top: 1px solid #6498F1;
    box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
    transition: left 0.3s ease;
    flex-shrink: 0;
}

.footer-content {
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 15px;
}

.footer-links {
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
}


.footer-links a {
    color: #2c3e50;
    text-decoration: none;
    font-size: 1em;
}

.footer-links a:hover {
    text-decoration: underline;
}

.footer-contact {
    font-size: 14px;
    color: #2c3e50;
}

.footer-contact a {
    color: #3498db;
    text-decoration: none;
}

.footer-contact a:hover {
    text-decoration: underline;
}

.sidebar:not(.showHeaderSideBar) ~ .main-footer {
    left: 0;
}


.nav-item {
    padding: 12px 25px;
}

.sidebar-top, .sidebar-bottom {
    padding: 0 15px;
}


.logo {
    padding: 10px 0 30px;
    cursor: pointer;
}

.logo img {
    height: 40px;
}

.create-menu-container,
.profile-menu-container {
    position: absolute;
    z-index: 1000;
}

.create-menu-container {
    top: 10%; /* Позиционируем прямо под кнопкой */
}

.profile-menu-container {
    bottom: 10%;
}

.create-menu,
.profile-menu {
    width: 200px;
    background: white;
    border-radius: 4px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    padding: 5px 0;
    border: 1px solid #E0E0E0;
}

.create-menu button,
.profile-menu button {
    width: 100%;
    padding: 8px 15px;
    text-align: left;
    color: #333;
    border: none;
    background: none;
    cursor: pointer;
    display: flex;
    align-items: center;
}

.create-menu button:hover,
.profile-menu button:hover {
    background-color: #E9ECEF;
}

.profile-menu button i {
    margin-right: 8px;
}


.create-btn {
    width: 100%;
    background-color: transparent;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    display: flex;
    align-items: center;
    text-align: left;
    padding: 10px 15px;
    margin-bottom: 5px;
    position: relative;

}

.create-btn:hover {
    background-color: #34495e;

}


.nav-item i {
    margin-right: 8px;
    font-size: 1em;
}

.nav-item img {
    width: 24px;
    height: 24px;
    margin-right: 8px;
    vertical-align: middle;
}


.nav-item span {
    font-size: 1.2em;
    margin-right: 5px;
}

.create-menu {
    position: absolute;
    width: 200px;
    border-radius: 4px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    z-index: 100;
    padding: 5px 0;
    background: #f8f9fa;
    border: 1px solid #E0E0E0;
    left: 5px;


}

.create-menu button {
    width: 100%;
    padding: 8px 15px;
    text-align: left;
    color: #333;
    border: none;
    background: none;
    cursor: pointer;
}

.create-menu button:hover {
    background-color: #E9ECEF;
}

.profile-btn {
    width: 100%;
    background: none;
    border: none;
    color: white;
    text-align: left;
    cursor: pointer;
    display: flex;
    align-items: center;
    position: relative;

}

.profile-menu {
    position: absolute;
    width: 200px;
    background: white;
    border-radius: 4px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    z-index: 100;
    padding: 5px 0;
    border: 1px solid #E0E0E0;
    left: 5px;

}

.profile-menu button {
    width: 100%;
    padding: 8px 15px;
    text-align: left;
    color: #333;
    border: none;
    background: none;
    cursor: pointer;
    display: flex;
    align-items: center;
}

.profile-menu button i {
    margin-right: 8px;
}

.profile-menu button:hover {
    background-color: #E9ECEF;
}

.nav-item {
    display: block;
    padding: 10px 15px;
    color: white;
    text-decoration: none;
    margin-bottom: 5px;
    border-radius: 4px;
}

.nav-item:hover,
.create-btn:hover {
    background-color: #4A7BC8;
}

.nav-item.router-link-exact-active {
    background-color: #3A6BB8;
}

.sidebar-bottom .nav-item {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 10px 15px;
    color: white;
    text-decoration: none;
    width: 100%;
    box-sizing: border-box;
}

.sidebar-bottom .nav-item:hover {
    background-color: #4A7BC8;
}

.sidebar-bottom .icon-wrapper {
    margin-right: 8px;
    display: flex;
    align-items: center;
}

.sidebar-bottom .username {
    font-size: 1em;
}


.sidebar.collapsed .sidebar-bottom .nav-item {
    justify-content: center;
    padding: 10px;
}

.sidebar.collapsed .sidebar-bottom .username {
    display: none;
}

.sidebar.collapsed .sidebar-bottom .icon-wrapper {
    margin-right: 0;
}

.sidebar.collapsed {
    width: 70px;
    min-width: 70px;
    overflow-x: hidden;
}

.sidebar.collapsed ~ .main-area {
    width: calc(100% - 70px);
    flex: 1;
}

.sidebar.collapsed .nav-item > span:not(.icon-wrapper),
.sidebar.collapsed .username,
.sidebar.collapsed .collapse-btn-text,
.sidebar.collapsed .create-btn > span:not(.icon-wrapper) {
    display: none;
}

.sidebar.collapsed .nav-item,
.sidebar.collapsed .user-profile,
.sidebar.collapsed .create-btn {
    display: flex;
    justify-content: center;
    padding: 10px 5px;
}

.sidebar.collapsed .create-btn .icon-wrapper {
    display: flex;
    justify-content: center;
    width: 100%;
}

.sidebar.collapsed .create-btn {
    padding: 10px;
}

.sidebar.collapsed .create-btn span {
    display: none;
}

.collapse-btn {
    background: none;
    border: none;
    color: white;
    padding: 10px;
    margin-bottom: 15px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
}

.collapse-btn i {
    margin-right: 8px;
}

.sidebar.collapsed .collapse-btn i {
    margin-right: 0;
}

.sidebar.collapsed .bi,
.sidebar.collapsed .nav-item img {
    margin-right: 0;
    font-size: 1.2em;
}

.sidebar.collapsed .collapse-btn {
    justify-content: center;
}

@media (max-width: 992px) {
    .sidebar {
        width: 70px;
        min-width: 70px;
    }

    .sidebar ~ .main-area {
        width: calc(100% - 70px);
    }

    .main-footer {
        left: 70px;
    }

    .sidebar.collapsed .collapse-btn {
        display: none;
    }
}

@media (max-width: 768px) {

    .sidebar {
        width: 60px;
        min-width: 60px;
    }

    .sidebar ~ .main-area {
        width: calc(100% - 70px);
    }

    .main-footer {
        left: 60px;
    }

    .sidebar.collapsed .collapse-btn {
        display: none;
    }
}
</style>
