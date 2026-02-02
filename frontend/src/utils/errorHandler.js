import toast from 'react-hot-toast';

/**
 * Centrally handles API errors.
 * 
 * @param {Error} error - The error object from axios
 */
export const handleApiError = (error) => {
    // If it's a cancellation, do nothing
    if (error.__CANCEL__) return;

    const response = error.response;
    const request = error.request;

    // Default error message
    let message = 'An unexpected error occurred. Please try again.';
    let errorCode = 'UNKNOWN';

    if (response) {
        // The server responded with a status code that falls out of the range of 2xx
        const data = response.data;

        // Handle standardized Nexus error format
        if (data && data.error) {
            message = data.message || message;
            errorCode = data.error_code || 'SERVER_ERROR';
        } else if (data && data.detail) {
            // Standard FastAPI detail
            message = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
        }

        // Specific handling based on status codes
        switch (response.status) {
            case 400:
                toast.error(`Invalid Request: ${message}`);
                break;
            case 401:
                // Handled by axios interceptor (redirect to login)
                break;
            case 403:
                toast.error('Access Denied: You do not have permission.');
                break;
            case 404:
                toast.error('Not Found: The requested resource does not exist.');
                break;
            case 422:
                // Validation error
                toast.error('Validation Error: Please check your input.');
                break;
            case 429:
                toast.error('Too Many Requests: Please slow down.');
                break;
            case 500:
                toast.error('Server error. Our engineers have been notified.');
                break;
            case 503:
                toast.error('Service Unavailable: Please try again later.');
                break;
            default:
                toast.error(message);
        }
    } else if (request) {
        // The request was made but no response was received
        toast.error('Network Error: Unable to reach the server. Please check your connection.');
        message = 'Network error';
        errorCode = 'NETWORK_ERROR';
    } else {
        // Something happened in setting up the request that triggered an Error
        console.error('Error', error.message);
        toast.error(error.message);
    }

    return {
        message,
        errorCode,
        status: response?.status
    };
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
