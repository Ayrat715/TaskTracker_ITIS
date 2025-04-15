import axios from "axios";
import {defineStore} from "pinia";

export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: null
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
        async logout() {
            try {
                await axios.post('/account/logout/', {}, {
                    withCredentials: true
                });
                this.user = null;
                this.isAuthenticated = false;
                localStorage.removeItem('authUser');
            } catch (error) {
                console.error('Logout failed:', error);
            }
        }
    }
})
