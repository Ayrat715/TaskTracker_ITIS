import axios from "axios";
import { defineStore } from "pinia";

export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: null,
        isAuthenticated: false,
    }),
    actions: {
        async checkAuth() {
            try {
                const response = await axios.get('http://localhost:8000/account/user/', {
                    withCredentials: true,
                });
                this.user = response.data;
                this.isAuthenticated = true;
                return true;
            } catch (error) {
                this.user = null;
                this.isAuthenticated = false;
                return false;
            }
        },
        async logout() {
            try {
                await axios.get('http://localhost:8000/account/logout', {
                    withCredentials: true,
                    headers: {
                        'X-CSRFToken': this.getCookie('csrftoken'),
                    }
                });
                this.user = null;
                this.isAuthenticated = false;
                localStorage.removeItem('lastViewedProject');
                localStorage.removeItem('lastViewedSprint');
                window.location.href = '/login';
            } catch (error) {
                console.error('Logout failed:', error);
            }
        },
        getCookie(name) {
            const value = `; ${document.cookie}`;
            const parts = value.split(`; ${name}=`);
            if (parts.length === 2) return parts.pop().split(';').shift();
        }
    }
});