const LoginView = {
    components: { FlashAlert },
    template: `
    <div class="auth-box">
        <h2 class="ppa-title">Login</h2>
        <p class="text-muted">Sign in to your account</p>
        <flash-alert :message="error" type="danger"></flash-alert>
        <form @submit.prevent="submit">
            <div class="mb-3">
                <label class="form-label">Username</label>
                <input class="form-control" v-model="username" required>
            </div>
            <div class="mb-3">
                <label class="form-label">Password</label>
                <input class="form-control" type="password" v-model="password" required>
            </div>
            <button class="btn btn-gold w-100" :disabled="loading">{{ loading ? 'Signing in...' : 'Login' }}</button>
        </form>
        <p class="text-center mt-3">No account? <router-link to="/register">Register here</router-link></p>
        <p class="text-center text-muted small">Admin login: admin / admin@123</p>
    </div>`,
    data() {
        return { username: '', password: '', error: '', loading: false };
    },
    methods: {
        async submit() {
            this.error = ''; this.loading = true;
            try {
                const { data } = await api.post('/auth/login', { username: this.username, password: this.password });
                localStorage.setItem('ppa_token', data.access_token);
                localStorage.setItem('ppa_role', data.role);
                localStorage.setItem('ppa_username', data.username);
                if (data.role === 'admin') this.$router.push('/admin');
                else if (data.role === 'company') this.$router.push('/company');
                else this.$router.push('/student');
            } catch (err) {
                this.error = apiErrorMsg(err);
            } finally {
                this.loading = false;
            }
        }
    }
};

const RegisterChoiceView = {
    template: `
    <div class="auth-box">
        <h2 class="ppa-title">Register</h2>
        <p class="text-muted">Who are you registering as?</p>
        <router-link to="/register/student" class="btn btn-gold w-100 mb-2">Student</router-link>
        <router-link to="/register/company" class="btn btn-gold w-100">Company</router-link>
        <p class="text-center mt-3">Already have an account? <router-link to="/login">Login here</router-link></p>
    </div>`
};

const RegisterStudentView = {
    components: { FlashAlert },
    template: `
    <div class="auth-box" style="max-width:600px">
        <h2 class="ppa-title">Student Registration</h2>
        <flash-alert :message="error" type="danger"></flash-alert>
        <flash-alert :message="success" type="success"></flash-alert>
        <form @submit.prevent="submit">
            <div class="mb-2"><label class="form-label">Username</label><input class="form-control" v-model="form.username" required></div>
            <div class="mb-2"><label class="form-label">Password</label><input type="password" class="form-control" v-model="form.password" required></div>
            <div class="mb-2"><label class="form-label">Full Name</label><input class="form-control" v-model="form.name" required></div>
            <div class="mb-2"><label class="form-label">Email</label><input type="email" class="form-control" v-model="form.email" required></div>
            <div class="mb-2"><label class="form-label">Phone</label><input class="form-control" v-model="form.phone"></div>
            <div class="mb-2"><label class="form-label">Department</label><input class="form-control" v-model="form.department" placeholder="e.g. CSE"></div>
            <div class="mb-2"><label class="form-label">CGPA</label><input type="number" step="0.01" min="0" max="10" class="form-control" v-model="form.cgpa"></div>
            <div class="mb-2"><label class="form-label">Backlogs</label><input type="number" min="0" class="form-control" v-model="form.backlogs"></div>
            <div class="mb-2"><label class="form-label">Skills</label><input class="form-control" v-model="form.skills" placeholder="comma separated"></div>
            <div class="mb-3"><label class="form-label">Resume (PDF)</label><input type="file" class="form-control" accept=".pdf" @change="onFile"></div>
            <button class="btn btn-gold w-100" :disabled="loading">{{ loading ? 'Registering...' : 'Register' }}</button>
        </form>
        <p class="text-center mt-3">Already have an account? <router-link to="/login">Login</router-link></p>
    </div>`,
    data() {
        return {
            form: { username: '', password: '', name: '', email: '', phone: '', department: '', cgpa: '', backlogs: 0, skills: '' },
            resume: null, error: '', success: '', loading: false
        };
    },
    methods: {
        onFile(e) { this.resume = e.target.files[0]; },
        async submit() {
            this.error = ''; this.success = ''; this.loading = true;
            try {
                const fd = new FormData();
                Object.entries(this.form).forEach(([k, v]) => fd.append(k, v));
                if (this.resume) fd.append('resume', this.resume);
                await api.post('/auth/register/student', fd);
                this.success = 'Registered! Redirecting to login...';
                setTimeout(() => this.$router.push('/login'), 1200);
            } catch (err) {
                this.error = apiErrorMsg(err);
            } finally {
                this.loading = false;
            }
        }
    }
};

const RegisterCompanyView = {
    components: { FlashAlert },
    template: `
    <div class="auth-box">
        <h2 class="ppa-title">Company Registration</h2>
        <flash-alert :message="error" type="danger"></flash-alert>
        <flash-alert :message="success" type="success"></flash-alert>
        <form @submit.prevent="submit">
            <div class="mb-2"><label class="form-label">Username</label><input class="form-control" v-model="form.username" required></div>
            <div class="mb-2"><label class="form-label">Password</label><input type="password" class="form-control" v-model="form.password" required></div>
            <div class="mb-2"><label class="form-label">Company Name</label><input class="form-control" v-model="form.cname" required></div>
            <div class="mb-2"><label class="form-label">HR Contact</label><input class="form-control" v-model="form.hr"></div>
            <div class="mb-2"><label class="form-label">Website</label><input class="form-control" v-model="form.website"></div>
            <div class="mb-3"><label class="form-label">Industry</label><input class="form-control" v-model="form.industry"></div>
            <button class="btn btn-gold w-100" :disabled="loading">{{ loading ? 'Registering...' : 'Register' }}</button>
        </form>
        <p class="text-center mt-3">Already have an account? <router-link to="/login">Login</router-link></p>
    </div>`,
    data() {
        return { form: { username: '', password: '', cname: '', hr: '', website: '', industry: '' }, error: '', success: '', loading: false };
    },
    methods: {
        async submit() {
            this.error = ''; this.success = ''; this.loading = true;
            try {
                await api.post('/auth/register/company', this.form);
                this.success = 'Registered! Wait for admin approval, then login.';
                setTimeout(() => this.$router.push('/login'), 1500);
            } catch (err) {
                this.error = apiErrorMsg(err);
            } finally {
                this.loading = false;
            }
        }
    }
};
