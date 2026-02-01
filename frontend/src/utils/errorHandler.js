// Rate limiting for multiple identical toasts (prevent bombardment)
let lastNetworkErrorTime = 0;
const NETWORK_ERROR_THROTTLE = 5000; // 5 seconds

export const handleApiError = (error) => {
    // If it's a cancellation, do nothing
    if (error.__CANCEL__) return;

    const response = error.response;
    const request = error.request;

    // Default error message
    let message = 'An unexpected error occurred. Please try again.';
    let errorCode = 'UNKNOWN';

    if (response) {
        // ...Existing response handling...
        const data = response.data;
        if (data && data.error) {
            message = data.message || message;
            errorCode = data.error_code || 'SERVER_ERROR';
        } else if (data && data.detail) {
            message = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
        }

        switch (response.status) {
            case 400: toast.error(`Invalid Request: ${message}`); break;
            case 401: break; // Handled by interceptor
            case 403: toast.error('Access Denied'); break;
            case 404: toast.error('Not Found'); break;
            case 422: toast.error('Validation Error'); break;
            case 429: toast.error('Too Many Requests'); break;
            case 500: toast.error('Server error'); break;
            default: toast.error(message);
        }
    } else if (request) {
        // Handle "bombardment" of Network Errors
        const now = Date.now();
        if (now - lastNetworkErrorTime > NETWORK_ERROR_THROTTLE) {
            toast.error('Network Error: Unable to reach the server. Please check your connection.', {
                id: 'network-error-toast', // Use constant ID to replace existing ones
            });
            lastNetworkErrorTime = now;
        }
        message = 'Network error';
        errorCode = 'NETWORK_ERROR';
    } else {
        toast.error(error.message);
    }

    return { message, errorCode, status: response?.status };
};

/**
 * Setup global error interceptors for the axios instance
 */
export const setupErrorInterceptors = (axiosInstance) => {
    axiosInstance.interceptors.response.use(
        (response) => response,
        (error) => {
            // Use the handleApiError to show toast
            handleApiError(error);
            return Promise.reject(error);
        }
    );
};
