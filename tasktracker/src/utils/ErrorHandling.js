import router from '@/router'
import { useErrorStore } from '@/stores/error'


export const useErrorHandling = () => {
    const handleApiError = (error) => {
        const errorStore = useErrorStore()
        if (error.response) {
            switch (error.response.status) {
                case 403:
                    errorStore.allowErrorPage('access-denied')
                    router.push({ name: 'access-denied' })
                    break
                case 404:
                    errorStore.allowErrorPage('not-found')
                    router.push({ name: 'not-found' })
                    break
                default:
                    errorStore.allowErrorPage('network-error')
                    router.push({ name: 'network-error' })
            }
        } else {
            errorStore.allowErrorPage('network-error')
            router.push({ name: 'network-error' })
        }
    }

    return { handleApiError }
}