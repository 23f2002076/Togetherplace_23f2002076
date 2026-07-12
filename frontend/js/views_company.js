const CompanyDashboardView = {
    components: { FlashAlert },
    template: `
    <div>
        <h1 class="ppa-title">Welcome, {{ company.cname }}</h1>
        <flash-alert :message="msg" type="success"></flash-alert>
        <div class="ppa-panel">
            <h5 class="ppa-title">Company Info</h5>
            <p><strong>HR:</strong> {{ company.hr }}</p>
            <p><strong>Industry:</strong> {{ company.industry }}</p>
            <p><strong>Website:</strong> {{ company.website }}</p>
            <p><strong>Status:</strong>
                <span class="badge" :class="company.approval==='Approved' ? 'bg-success' : (company.approval==='Rejected' ? 'bg-danger' : 'bg-warning text-dark')">{{ company.approval }}</span>
            </p>
        </div>

        <div class="ppa-panel">
            <div class="d-flex justify-content-between align-items-center mb-2">
                <h5 class="ppa-title mb-0">Your Drives</h5>
                <router-link v-if="company.approval==='Approved'" to="/company/drive/new" class="btn btn-gold btn-sm">+ New Drive</router-link>
            </div>
            <p v-if="!drives.length" class="text-muted">No drives created yet</p>
            <table v-else class="table table-sm">
                <thead><tr><th>ID</th><th>Drive</th><th>Job Title</th><th>Deadline</th><th>Status</th><th>Applicants</th><th>Actions</th></tr></thead>
                <tbody>
                <tr v-for="d in drives" :key="d.id">
                    <td>{{ d.id }}</td><td>{{ d.drive_name }}</td><td>{{ d.jobtitle }}</td><td>{{ d.deadline }}</td>
                    <td>{{ d.status }}</td><td>{{ d.applicant_count }}</td>
                    <td>
                        <router-link :to="'/company/drive/'+d.id+'/applicants'" class="btn btn-sm btn-success">Applicants</router-link>
                        <template v-if="d.status!=='Rejected' && d.status!=='Closed'">
                            <router-link :to="'/company/drive/'+d.id+'/edit'" class="btn btn-sm btn-info text-white">Edit</router-link>
                            <button class="btn btn-sm btn-warning" @click="closeDrive(d.id)">Close</button>
                        </template>
                        <button class="btn btn-sm btn-outline-danger" @click="deleteDrive(d.id)">Delete</button>
                    </td>
                </tr>
                </tbody>
            </table>
        </div>
    </div>`,
    data() { return { company: {}, drives: [], msg: '' }; },
    async mounted() { await this.load(); },
    methods: {
        async load() {
            const [c, d] = await Promise.all([api.get('/company/me'), api.get('/company/drives')]);
            this.company = c.data; this.drives = d.data;
        },
        async closeDrive(id) { await api.post(`/company/drives/${id}/close`); await this.load(); },
        async deleteDrive(id) { if (confirm('Delete this drive?')) { await api.delete(`/company/drives/${id}`); await this.load(); } }
    }
};

const driveFormTemplate = `
    <div class="ppa-panel">
        <h1 class="ppa-title">{{ isEdit ? 'Edit Drive' : 'Create New Drive' }}</h1>
        <flash-alert :message="error" type="danger"></flash-alert>
        <form @submit.prevent="submit">
            <div class="mb-2"><label class="form-label">Drive Name</label><input class="form-control" v-model="form.drive_name" required></div>
            <div class="mb-2"><label class="form-label">Job Title</label><input class="form-control" v-model="form.jobtitle" required></div>
            <div class="mb-2"><label class="form-label">Job Description</label><textarea class="form-control" rows="3" v-model="form.jobdescription"></textarea></div>
            <div class="mb-2"><label class="form-label">Eligibility Note (shown to students)</label><input class="form-control" v-model="form.eligible" placeholder="e.g. Final year CSE/IT, no active backlogs"></div>
            <div class="row">
                <div class="col-md-4 mb-2"><label class="form-label">Min CGPA</label><input type="number" step="0.1" min="0" max="10" class="form-control" v-model="form.min_cgpa"></div>
                <div class="col-md-4 mb-2"><label class="form-label">Max Backlogs Allowed</label><input type="number" min="0" class="form-control" v-model="form.max_backlogs"></div>
                <div class="col-md-4 mb-2"><label class="form-label">Eligible Branches</label><input class="form-control" v-model="form.eligible_branches" placeholder="cse,it (blank = all)"></div>
            </div>
            <div class="mb-2"><label class="form-label">Skills Required</label><input class="form-control" v-model="form.skills_required"></div>
            <div class="mb-2"><label class="form-label">Experience</label><input class="form-control" v-model="form.experience"></div>
            <div class="mb-2"><label class="form-label">Deadline</label><input type="date" class="form-control" v-model="form.deadline" required></div>
            <div class="mb-2"><label class="form-label">Salary (CTC)</label><input class="form-control" v-model="form.salary"></div>
            <div class="mb-3"><label class="form-label">Location</label><input class="form-control" v-model="form.location"></div>
            <button class="btn btn-gold" :disabled="loading">{{ isEdit ? 'Update Drive' : 'Submit for Approval' }}</button>
            <router-link to="/company" class="btn btn-secondary ms-2">Cancel</router-link>
        </form>
    </div>`;

const NewDriveView = {
    components: { FlashAlert },
    template: driveFormTemplate,
    data() {
        return {
            isEdit: false, loading: false, error: '',
            form: { drive_name: '', jobtitle: '', jobdescription: '', eligible: '', min_cgpa: 0, max_backlogs: 99, eligible_branches: '', skills_required: '', experience: '', deadline: '', salary: '', location: '' }
        };
    },
    methods: {
        async submit() {
            this.error = ''; this.loading = true;
            try {
                await api.post('/company/drives', this.form);
                this.$router.push('/company');
            } catch (err) {
                this.error = apiErrorMsg(err);
            } finally { this.loading = false; }
        }
    }
};

const EditDriveView = {
    components: { FlashAlert },
    template: driveFormTemplate,
    data() { return { isEdit: true, loading: false, error: '', form: {} }; },
    async mounted() {
        const { data } = await api.get('/company/drives');
        this.form = data.find(d => d.id == this.$route.params.id);
    },
    methods: {
        async submit() {
            this.error = ''; this.loading = true;
            try {
                await api.put(`/company/drives/${this.$route.params.id}`, this.form);
                this.$router.push('/company');
            } catch (err) {
                this.error = apiErrorMsg(err);
            } finally { this.loading = false; }
        }
    }
};

const ApplicantsView = {
    template: `
    <div>
        <h1 class="ppa-title">Applicants{{ drive ? ' for ' + drive.drive_name : '' }}</h1>
        <router-link to="/company" class="btn btn-outline-secondary btn-sm mb-3">Back</router-link>
        <div class="ppa-panel">
            <p v-if="!applicants.length" class="text-muted">No applicants yet</p>
            <table v-else class="table table-sm">
                <thead><tr><th>Name</th><th>Email</th><th>Dept</th><th>CGPA</th><th>Backlogs</th><th>Resume</th><th>Applied</th><th>Status</th><th>Update</th></tr></thead>
                <tbody>
                <tr v-for="a in applicants" :key="a.id">
                    <td>{{ a.student.name }}</td><td>{{ a.student.email }}</td><td>{{ a.student.department }}</td>
                    <td>{{ a.student.cgpa }}</td><td>{{ a.student.backlogs }}</td>
                    <td><a v-if="a.student.resume_name" :href="resumeUrl(a.student.resume_name)" target="_blank" class="btn btn-sm btn-info text-white">View</a><span v-else>N/A</span></td>
                    <td>{{ a.applied_date }}</td>
                    <td>{{ a.status }}</td>
                    <td>
                        <select class="form-select form-select-sm mb-1" v-model="a._status">
                            <option>Applied</option><option>Shortlisted</option><option>Interview</option><option>Selected</option><option>Rejected</option>
                        </select>
                        <input type="date" class="form-control form-control-sm mb-1" v-model="a._interview_date" title="interview date, sirf 'Interview' status ke liye">
                        <button class="btn btn-sm btn-gold" @click="update(a)">Update</button>
                    </td>
                </tr>
                </tbody>
            </table>
        </div>
    </div>`,
    data() { return { applicants: [], drive: null }; },
    async mounted() { await this.load(); },
    methods: {
        resumeUrl(name) { return `/static/uploads/${name}`; },
        async load() {
            const did = this.$route.params.id;
            const { data } = await api.get(`/company/drives/${did}/applicants`);
            this.applicants = data.map(a => ({ ...a, _status: a.status, _interview_date: a.interview_date || '' }));
            const drives = await api.get('/company/drives');
            this.drive = drives.data.find(d => d.id == did);
        },
        async update(a) {
            await api.put(`/company/applications/${a.id}`, { status: a._status, interview_date: a._interview_date });
            await this.load();
        }
    }
};

const CompanyProfileView = {
    components: { FlashAlert },
    template: `
    <div class="ppa-panel">
        <h1 class="ppa-title">Edit Company Profile</h1>
        <flash-alert :message="msg" type="success"></flash-alert>
        <form @submit.prevent="submit">
            <div class="mb-2"><label class="form-label">Company Name</label><input class="form-control" v-model="form.cname"></div>
            <div class="mb-2"><label class="form-label">HR Contact</label><input class="form-control" v-model="form.hr"></div>
            <div class="mb-2"><label class="form-label">Website</label><input class="form-control" v-model="form.website"></div>
            <div class="mb-3"><label class="form-label">Industry</label><input class="form-control" v-model="form.industry"></div>
            <button class="btn btn-gold">Save Changes</button>
        </form>
    </div>`,
    data() { return { form: {}, msg: '' }; },
    async mounted() { const { data } = await api.get('/company/me'); this.form = data; },
    methods: {
        async submit() {
            await api.put('/company/me', this.form);
            this.msg = 'Profile updated!';
            setTimeout(() => this.msg = '', 2000);
        }
    }
};
