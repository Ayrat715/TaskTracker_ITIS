import axios from "axios";
import {defineStore} from "pinia";


export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: JSON.parse(localStorage.getItem('authUser')) || null,
        isAuthenticated: !!localStorage.getItem('authUser')
    }),
    actions: {
        setUser(userData) {
            this.user = userData;
            this.isAuthenticated = !!userData;
            if (userData) {
                localStorage.setItem('authUser', JSON.stringify(userData));
            } else {
                localStorage.removeItem('authUser');
            }
        },
        async initialize() {
            const savedUser = localStorage.getItem('authUser');
            if (savedUser) {
                this.user = JSON.parse(savedUser);
                this.isAuthenticated = true;
            }
        },
        async logout() {
            try {
                await axios.get('http://localhost:8000/account/logout', {}, {
                    withCredentials: true,
                    headers: {
                        'X-CSRFToken': this.getCookie('csrftoken'),
                    }
                });
                this.isAuthenticated = false;
                localStorage.removeItem('authUser');
                localStorage.removeItem('lastViewedProject');
                localStorage.removeItem('lastViewedSprint');
                this.setUser(null);
                window.location.href = '/login';
            } catch (error) {
                console.error('Logout failed:', error);
            }
        },
        getCookie(name) {
            const value = `; ${document.cookie}`
            const parts = value.split(`; ${name}=`)
            if (parts.length === 2) return parts.pop().split(';').shift()
        }
    }
})