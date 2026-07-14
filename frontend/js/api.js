const API_BASE = '/api';

const api = axios.create({ baseURL: API_BASE });

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('ppa_token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
});

api.interceptors.response.use(
    (res) => res,
    (err) => {
        if (err.response && err.response.status === 401) {
            localStorage.removeItem('ppa_token');
            localStorage.removeItem('ppa_role');
            localStorage.removeItem('ppa_username');
            window.location.hash = '#/login';
        }
        return Promise.reject(err);
    }
);

function apiErrorMsg(err) {
    return (err.response && err.response.data && err.response.data.error) || 'Something went wrong';
}
