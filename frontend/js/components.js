const BRANCH_OPTIONS = [
    { value: 'cse', label: 'CSE' },
    { value: 'cyber', label: 'Cyber Security' },
    { value: 'cloud', label: 'Cloud Computing' },
    { value: 'ai', label: 'AI' },
    { value: 'data science', label: 'Data Science' },
];

const NavBar = {
    template: `
    <nav class="navbar navbar-expand navbar-ppa px-3 mb-3">
        <span class="navbar-brand">Placement Portal</span>
        <div class="navbar-nav ms-auto flex-row gap-3" v-if="role">
            <router-link v-if="role==='admin'" class="nav-link" to="/admin">Dashboard</router-link>
            <router-link v-if="role==='admin'" class="nav-link" to="/admin/search">Search</router-link>

            <router-link v-if="role==='company'" class="nav-link" to="/company">Dashboard</router-link>
            <router-link v-if="role==='company'" class="nav-link" to="/company/drive/new">New Drive</router-link>
            <router-link v-if="role==='company'" class="nav-link" to="/company/profile">Profile</router-link>

            <router-link v-if="role==='student'" class="nav-link" to="/student">Dashboard</router-link>
            <router-link v-if="role==='student'" class="nav-link" to="/student/history">History</router-link>
            <router-link v-if="role==='student'" class="nav-link" to="/student/profile">Profile</router-link>

            <a class="nav-link btn btn-sm btn-logout px-3" href="#" @click.prevent="logout">Logout</a>
        </div>
    </nav>`,
    data() {
        return { role: localStorage.getItem('ppa_role') };
    },
    watch: {
        '$route'() { this.role = localStorage.getItem('ppa_role'); }
    },
    methods: {
        logout() {
            localStorage.clear();
            this.role = null;
            this.$router.push('/login');
        }
    }
};

const FlashAlert = {
    props: ['message', 'type'],
    template: `
    <div v-if="message" class="alert" :class="'alert-' + (type || 'warning')" role="alert">
        {{ message }}
    </div>`
};