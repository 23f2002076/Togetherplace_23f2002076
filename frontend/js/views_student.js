const StudentDashboardView = {
    components: { FlashAlert },
    template: `
    <div>
        <h1 class="ppa-title">Welcome, {{ student.name }}</h1>
        <flash-alert :message="msg" type="success"></flash-alert>
        <flash-alert :message="error" type="danger"></flash-alert>

        <div class="ppa-panel">
            <h5 class="ppa-title">Available Drives</h5>
            <input class="form-control mb-2" v-model="searchtxt" placeholder="Search by drive name or company">
            <p v-if="!filteredDrives.length" class="text-muted">No drives found</p>
            <table v-else class="table table-sm">
                <thead><tr><th>Drive</th><th>Company</th><th>Job Title</th><th>Deadline</th><th>Salary</th><th>Eligibility</th><th>Action</th></tr></thead>
                <tbody>
                <tr v-for="d in filteredDrives" :key="d.id">
                    <td>{{ d.drive_name }}</td><td>{{ d.company_name }}</td><td>{{ d.jobtitle }}</td>
                    <td>{{ d.deadline }}</td><td>{{ d.salary }}</td>
                    <td><span class="badge" :class="d.is_eligible ? 'badge-eligible' : 'badge-ineligible'">{{ d.eligibility_reason }}</span></td>
                    <td>
                        <router-link :to="'/student/drive/'+d.id" class="btn btn-sm btn-info text-white">View</router-link>
                        <span v-if="d.already_applied" class="badge bg-success">Applied</span>
                        <button v-else-if="d.is_eligible" class="btn btn-sm btn-gold" @click="apply(d.id)">Apply</button>
                    </td>
                </tr>
                </tbody>
            </table>
        </div>

        <div class="ppa-panel">
            <h5 class="ppa-title">My Applications</h5>
            <p v-if="!applications.length" class="text-muted">No applications yet</p>
            <table v-else class="table table-sm">
                <thead><tr><th>Drive</th><th>Company</th><th>Job Title</th><th>Applied</th><th>Status</th><th>Interview</th><th>Feedback</th></tr></thead>
                <tbody>
                <tr v-for="a in applications" :key="a.id">
                    <td>{{ a.drive_name }}</td><td>{{ a.company_name }}</td><td>{{ a.jobtitle }}</td>
                    <td>{{ a.applied_date }}</td><td>{{ a.status }}</td>
                    <td>{{ a.interview_date || '-' }}</td><td>{{ a.feedback || '-' }}</td>
                </tr>
                </tbody>
            </table>
        </div>
    </div>`,
    data() { return { student: {}, drives: [], applications: [], msg: '', error: '', searchtxt: '' }; },
    computed: {
        filteredDrives() {
            if (!this.searchtxt.trim()) return this.drives;
            const q = this.searchtxt.toLowerCase();
            return this.drives.filter(d =>
                (d.drive_name || '').toLowerCase().includes(q) ||
                (d.company_name || '').toLowerCase().includes(q)
            );
        }
    },
    async mounted() { await this.load(); },
    methods: {
        async load() {
            const [s, d, a] = await Promise.all([api.get('/student/me'), api.get('/student/drives'), api.get('/student/applications')]);
            this.student = s.data; this.drives = d.data; this.applications = a.data;
        },
        async apply(id) {
            this.error = '';
            try {
                await api.post(`/student/drives/${id}/apply`);
                this.msg = 'Applied successfully!';
                setTimeout(() => this.msg = '', 2000);
                await this.load();
            } catch (err) { this.error = apiErrorMsg(err); }
        }
    }
};

const ViewDriveView = {
    template: `
    <div class="ppa-panel" v-if="drive">
        <h1 class="ppa-title">{{ drive.drive_name }}</h1>
        <router-link to="/student" class="btn btn-outline-secondary btn-sm mb-3">Back</router-link>
        <p><strong>Company:</strong> {{ drive.company_name }}</p>
        <p><strong>Job Title:</strong> {{ drive.jobtitle }}</p>
        <p><strong>Description:</strong> {{ drive.jobdescription }}</p>
        <p><strong>Eligibility:</strong> {{ drive.eligible }} (Min CGPA {{ drive.min_cgpa }}, Max backlogs {{ drive.max_backlogs }}<span v-if="drive.eligible_branches">, Branches: {{ drive.eligible_branches }}</span>)</p>
        <p><strong>Skills Required:</strong> {{ drive.skills_required }}</p>
        <p><strong>Experience:</strong> {{ drive.experience }}</p>
        <p><strong>Deadline:</strong> {{ drive.deadline }}</p>
        <p><strong>Salary:</strong> {{ drive.salary }}</p>
        <p><strong>Location:</strong> {{ drive.location }}</p>
        <div class="alert" :class="drive.is_eligible ? 'alert-success' : 'alert-danger'">{{ drive.eligibility_reason }}</div>
        <p v-if="drive.already_applied" class="text-muted">You already applied for this drive</p>
        <button v-else-if="drive.is_eligible" class="btn btn-gold" @click="apply">Apply Now</button>
    </div>`,
    data() { return { drive: null }; },
    async mounted() { await this.load(); },
    methods: {
        async load() { const { data } = await api.get(`/student/drives/${this.$route.params.id}`); this.drive = data; },
        async apply() { await api.post(`/student/drives/${this.$route.params.id}/apply`); await this.load(); }
    }
};

const StudentHistoryView = {
    components: { FlashAlert },
    template: `
    <div>
        <h1 class="ppa-title">Application History</h1>
        <router-link to="/student" class="btn btn-outline-secondary btn-sm mb-3">Back</router-link>

        <div class="ppa-panel">
            <div class="d-flex justify-content-between align-items-center mb-2">
                <h5 class="ppa-title mb-0">Past Applications</h5>
                <button class="btn btn-sm btn-gold" @click="exportCsv" :disabled="exporting">{{ exporting ? 'Exporting...' : 'Export as CSV' }}</button>
            </div>
            <flash-alert :message="exportMsg" type="success"></flash-alert>
            <p v-if="!applications.length" class="text-muted">No application history found</p>
            <table v-else class="table table-sm">
                <thead><tr><th>#</th><th>Drive</th><th>Company</th><th>Job Title</th><th>Applied</th><th>Status</th><th>Interview</th><th>Feedback</th></tr></thead>
                <tbody>
                <tr v-for="(a,i) in applications" :key="a.id">
                    <td>{{ i+1 }}</td><td>{{ a.drive_name }}</td><td>{{ a.company_name }}</td>
                    <td>{{ a.jobtitle }}</td><td>{{ a.applied_date }}</td><td>{{ a.status }}</td>
                    <td>{{ a.interview_date || '-' }}</td><td>{{ a.feedback || '-' }}</td>
                </tr>
                </tbody>
            </table>
        </div>

        <div class="ppa-panel" v-if="placements.length">
            <h5 class="ppa-title">Placement History</h5>
            <table class="table table-sm">
                <thead><tr><th>Company</th><th>Position</th><th>Salary</th><th>Joining Date</th></tr></thead>
                <tbody>
                <tr v-for="p in placements" :key="p.id">
                    <td>{{ p.company_name }}</td><td>{{ p.position }}</td><td>{{ p.salary }}</td><td>{{ p.joining_date }}</td>
                </tr>
                </tbody>
            </table>
        </div>
    </div>`,
    data() { return { applications: [], placements: [], exporting: false, exportMsg: '' }; },
    async mounted() {
        const [a, p] = await Promise.all([api.get('/student/history'), api.get('/student/placements')]);
        this.applications = a.data; this.placements = p.data;
    },
    methods: {
        async exportCsv() {
            this.exporting = true; this.exportMsg = '';
            try {
                const { data } = await api.post('/student/export/csv');
                await this.poll(data.task_id);
            } finally { this.exporting = false; }
        },
        async poll(taskId) {
            for (let i = 0; i < 15; i++) {
                await new Promise(r => setTimeout(r, 1000));
                const { data } = await api.get(`/student/export/status/${taskId}`);
                if (data.state === 'SUCCESS') {
                    this.exportMsg = '';
                    const a = document.createElement('a');
                    a.href = `/static/exports/${data.filename}`;
                    a.download = data.filename;
                    a.click();
                    return;
                }
                if (data.state === 'FAILURE') { this.exportMsg = 'Export failed: ' + data.error; return; }
            }
            this.exportMsg = 'Export is taking longer than expected — check back shortly.';
        }
    }
};

const StudentProfileView = {
    components: { FlashAlert },
    template: `
    <div class="ppa-panel">
        <h1 class="ppa-title">My Profile</h1>
        <flash-alert :message="msg" type="success"></flash-alert>
        <flash-alert :message="error" type="danger"></flash-alert>
        <form @submit.prevent="submit">
            <div class="mb-2"><label class="form-label">Full Name</label><input class="form-control" v-model="form.name"></div>
            <div class="mb-2"><label class="form-label">Email</label><input type="email" class="form-control" v-model="form.email"></div>
            <div class="mb-2"><label class="form-label">Phone</label><input class="form-control" v-model="form.phone"></div>
            <div class="mb-2"><label class="form-label">Department</label>
                <select class="form-control" v-model="form.department">
                    <option value="" disabled>Select Branch</option>
                    <option v-for="b in BRANCH_OPTIONS" :key="b.value" :value="b.value">{{ b.label }}</option>
                </select>
            </div>
            <div class="mb-2"><label class="form-label">CGPA</label><input type="number" step="0.01" min="0" max="10" class="form-control" v-model="form.cgpa"></div>
            <div class="mb-2"><label class="form-label">Backlogs</label><input type="number" min="0" class="form-control" v-model="form.backlogs"></div>
            <div class="mb-2"><label class="form-label">Skills</label><input class="form-control" v-model="form.skills"></div>
            <div class="mb-2">
                <label class="form-label">Resume (PDF)</label>
                <p v-if="form.resume_name"><a :href="'/static/uploads/'+form.resume_name" target="_blank">View current resume</a></p>
                <input type="file" class="form-control" accept=".pdf" @change="onFile">
            </div>
            <button class="btn btn-gold">Save Changes</button>
        </form>
    </div>`,
    data() { return { form: {}, resume: null, msg: '', error: '' }; },
    async mounted() { const { data } = await api.get('/student/me'); this.form = data; },
    methods: {
        onFile(e) { this.resume = e.target.files[0]; },
        async submit() {
            this.msg = ''; this.error = '';
            try {
                const fd = new FormData();
                Object.entries(this.form).forEach(([k, v]) => { if (v !== null && v !== undefined) fd.append(k, v); });
                if (this.resume) fd.append('resume', this.resume);
                const { data } = await api.put('/student/me', fd);
                this.form = data;
                this.msg = 'Profile updated!';
                setTimeout(() => this.msg = '', 2000);
            } catch (err) { this.error = apiErrorMsg(err); }
        }
    }
};