const AdminDashboardView = {
    components: { FlashAlert },
    template: `
    <div>
        <h1 class="ppa-title">Welcome Admin</h1>
        <flash-alert :message="msg" type="success"></flash-alert>

        <div class="row g-3 mb-3">
            <div class="col-6 col-md-3"><div class="stat-card"><h3>{{ stats.total_students }}</h3><p>Students</p></div></div>
            <div class="col-6 col-md-3"><div class="stat-card"><h3>{{ stats.total_companies }}</h3><p>Companies</p></div></div>
            <div class="col-6 col-md-3"><div class="stat-card"><h3>{{ stats.total_drives }}</h3><p>Drives</p></div></div>
            <div class="col-6 col-md-3"><div class="stat-card"><h3>{{ stats.total_applications }}</h3><p>Applications</p></div></div>
        </div>

        <div class="ppa-panel">
            <h5 class="ppa-title">Pending Company Approvals</h5>
            <p v-if="!stats.pending_companies || !stats.pending_companies.length" class="text-muted">No pending approvals</p>
            <table v-else class="table">
                <thead><tr><th>ID</th><th>Company</th><th>HR</th><th>Industry</th><th>Action</th></tr></thead>
                <tbody>
                <tr v-for="c in stats.pending_companies" :key="c.id">
                    <td>{{ c.id }}</td><td>{{ c.cname }}</td><td>{{ c.hr }}</td><td>{{ c.industry }}</td>
                    <td>
                        <button class="btn btn-sm btn-success me-1" @click="approveCompany(c.id)">Approve</button>
                        <button class="btn btn-sm btn-danger" @click="rejectCompany(c.id)">Reject</button>
                    </td>
                </tr>
                </tbody>
            </table>
        </div>

        <div class="ppa-panel">
            <h5 class="ppa-title">Pending Drive Approvals</h5>
            <p v-if="!stats.pending_drives || !stats.pending_drives.length" class="text-muted">No pending drives</p>
            <table v-else class="table">
                <thead><tr><th>ID</th><th>Drive</th><th>Company</th><th>Deadline</th><th>Action</th></tr></thead>
                <tbody>
                <tr v-for="d in stats.pending_drives" :key="d.id">
                    <td>{{ d.id }}</td><td>{{ d.drive_name }}</td><td>{{ d.company_name }}</td><td>{{ d.deadline }}</td>
                    <td>
                        <button class="btn btn-sm btn-success me-1" @click="approveDrive(d.id)">Approve</button>
                        <button class="btn btn-sm btn-danger" @click="rejectDrive(d.id)">Reject</button>
                    </td>
                </tr>
                </tbody>
            </table>
        </div>

        <div class="ppa-panel">
            <h5 class="ppa-title">All Students</h5>
            <table class="table table-sm">
                <thead><tr><th>ID</th><th>Name</th><th>Dept</th><th>CGPA</th><th>Status</th><th>Action</th></tr></thead>
                <tbody>
                <tr v-for="s in students" :key="s.id">
                    <template v-if="editingStudent === s.id">
                        <td>{{ s.id }}</td>
                        <td><input class="form-control form-control-sm" v-model="editForm.name"></td>
                        <td>
                            <select class="form-control form-control-sm" v-model="editForm.department">
                                <option v-for="b in BRANCH_OPTIONS" :key="b.value" :value="b.value">{{ b.label }}</option>
                            </select>
                        </td>
                        <td><input class="form-control form-control-sm" type="number" step="0.01" v-model="editForm.cgpa"></td>
                        <td></td>
                        <td>
                            <button class="btn btn-sm btn-gold me-1" @click="saveStudent(s.id)">Save</button>
                            <button class="btn btn-sm btn-secondary" @click="editingStudent=null">Cancel</button>
                        </td>
                    </template>
                    <template v-else>
                        <td>{{ s.id }}</td><td>{{ s.name }}</td><td>{{ s.department }}</td><td>{{ s.cgpa }}</td>
                        <td><span class="badge" :class="s.is_blacklisted ? 'bg-danger' : 'bg-success'">{{ s.is_blacklisted ? 'Blacklisted' : 'Active' }}</span></td>
                        <td>
                            <button class="btn btn-sm" :class="s.is_blacklisted ? 'btn-success' : 'btn-danger'" @click="toggleStudentBlacklist(s)">{{ s.is_blacklisted ? 'Unblacklist' : 'Blacklist' }}</button>
                            <button class="btn btn-sm btn-info text-white" @click="startEditStudent(s)">Edit</button>
                            <button class="btn btn-sm btn-outline-danger" @click="deleteStudent(s.id)">Delete</button>
                        </td>
                    </template>
                </tr>
                </tbody>
            </table>
        </div>

        <div class="ppa-panel">
            <h5 class="ppa-title">All Companies</h5>
            <table class="table table-sm">
                <thead><tr><th>ID</th><th>Company</th><th>HR</th><th>Approval</th><th>Account Status</th><th>Action</th></tr></thead>
                <tbody>
                <tr v-for="c in companies" :key="c.id">
                    <td>{{ c.id }}</td><td>{{ c.cname }}</td><td>{{ c.hr }}</td>
                    <td><span class="badge" :class="c.approval === 'Approved' ? 'bg-success' : (c.approval === 'Rejected' ? 'bg-danger' : 'bg-warning text-dark')">{{ c.approval }}</span></td>
                    <td><span class="badge" :class="c.is_blacklisted ? 'bg-dark' : 'bg-success'">{{ c.is_blacklisted ? 'Blacklisted' : 'Active' }}</span></td>
                    <td>
                        <button class="btn btn-sm" :class="c.is_blacklisted ? 'btn-success' : 'btn-danger'" @click="toggleCompanyBlacklist(c)">{{ c.is_blacklisted ? 'Unblacklist' : 'Blacklist' }}</button>
                        <button class="btn btn-sm btn-outline-danger" @click="deleteCompany(c.id)">Delete</button>
                    </td>
                </tr>
                </tbody>
            </table>
        </div>

        <div class="ppa-panel">
            <h5 class="ppa-title">All Drives</h5>
            <table class="table table-sm">
                <thead><tr><th>ID</th><th>Drive</th><th>Company</th><th>Deadline</th><th>Status</th><th>Action</th></tr></thead>
                <tbody>
                <tr v-for="d in drives" :key="d.id">
                    <td>{{ d.id }}</td><td>{{ d.drive_name }}</td><td>{{ d.company_name }}</td>
                    <td>{{ d.deadline }}</td><td>{{ d.status }}</td>
                    <td><button class="btn btn-sm btn-outline-danger" @click="deleteDrive(d.id)">Remove</button></td>
                </tr>
                </tbody>
            </table>
        </div>

        <div class="ppa-panel">
            <h5 class="ppa-title">All Applications</h5>
            <table class="table table-sm">
                <thead><tr><th>ID</th><th>Student</th><th>Drive</th><th>Company</th><th>Date</th><th>Status</th></tr></thead>
                <tbody>
                <tr v-for="a in applications" :key="a.id">
                    <td>{{ a.id }}</td><td>{{ a.student_name }}</td><td>{{ a.drive_name }}</td>
                    <td>{{ a.company_name }}</td><td>{{ a.applied_date }}</td><td>{{ a.status }}</td>
                </tr>
                </tbody>
            </table>
        </div>
    </div>`,
    data() {
        return {
            stats: {}, students: [], companies: [], applications: [], drives: [],
            msg: '', editingStudent: null, editForm: {}
        };
    },
    async mounted() { await this.loadAll(); },
    methods: {
        async loadAll() {
            const [d, s, c, a, drv] = await Promise.all([
                api.get('/admin/dashboard'), api.get('/admin/students'),
                api.get('/admin/companies'), api.get('/admin/applications'), api.get('/admin/drives')
            ]);
            this.stats = d.data; this.students = s.data; this.companies = c.data; this.applications = a.data; this.drives = drv.data;
        },
        async deleteDrive(id) { if (confirm('Want to delete this drive?')) { await api.delete(`/admin/drive/${id}`); await this.loadAll(); } },
        async approveCompany(id) { await api.post(`/admin/company/${id}/approve`); this.flash('Company approved'); await this.loadAll(); },
        async rejectCompany(id) { await api.post(`/admin/company/${id}/reject`); this.flash('Company rejected'); await this.loadAll(); },
        async approveDrive(id) { await api.post(`/admin/drive/${id}/approve`); this.flash('Drive approved'); await this.loadAll(); },
        async rejectDrive(id) { await api.post(`/admin/drive/${id}/reject`); this.flash('Drive rejected'); await this.loadAll(); },
        async toggleStudentBlacklist(s) {
            await api.post(`/admin/student/${s.id}/${s.is_blacklisted ? 'unblacklist' : 'blacklist'}`);
            await this.loadAll();
        },
        async toggleCompanyBlacklist(c) {
            await api.post(`/admin/company/${c.id}/${c.is_blacklisted ? 'unblacklist' : 'blacklist'}`);
            await this.loadAll();
        },
        async deleteStudent(id) { if (confirm('Delete this student?')) { await api.delete(`/admin/student/${id}`); await this.loadAll(); } },
        async deleteCompany(id) { if (confirm('Delete this company and its drives?')) { await api.delete(`/admin/company/${id}`); await this.loadAll(); } },
        startEditStudent(s) { this.editingStudent = s.id; this.editForm = { ...s }; },
        async saveStudent(id) {
            await api.put(`/admin/student/${id}`, this.editForm);
            this.editingStudent = null;
            await this.loadAll();
        },
        flash(m) { this.msg = m; setTimeout(() => this.msg = '', 2500); }
    }
};

const AdminSearchView = {
    template: `
    <div>
        <h1 class="ppa-title">Search</h1>
        <div class="ppa-panel">
            <form class="row g-2" @submit.prevent="search">
                <div class="col-auto">
                    <select class="form-select" v-model="type">
                        <option value="student">Student</option>
                        <option value="company">Company</option>
                    </select>
                </div>
                <div class="col"><input class="form-control" v-model="q" placeholder="Search query"></div>
                <div class="col-auto"><button class="btn btn-gold">Search</button></div>
            </form>
        </div>
        <div class="ppa-panel" v-if="results.length">
            <table class="table table-sm" v-if="type==='student'">
                <thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Dept</th><th>CGPA</th><th>Status</th></tr></thead>
                <tbody>
                <tr v-for="r in results" :key="r.id">
                    <td>{{ r.id }}</td><td>{{ r.name }}</td><td>{{ r.email }}</td><td>{{ r.department }}</td><td>{{ r.cgpa }}</td>
                    <td>{{ r.is_blacklisted ? 'Blacklisted' : 'Active' }}</td>
                </tr>
                </tbody>
            </table>
            <table class="table table-sm" v-else>
                <thead><tr><th>ID</th><th>Company</th><th>HR</th><th>Industry</th><th>Approval</th></tr></thead>
                <tbody>
                <tr v-for="r in results" :key="r.id">
                    <td>{{ r.id }}</td><td>{{ r.cname }}</td><td>{{ r.hr }}</td><td>{{ r.industry }}</td><td>{{ r.approval }}</td>
                </tr>
                </tbody>
            </table>
        </div>
        <p v-else-if="searched" class="text-muted">No results found</p>
    </div>`,
    data() { return { q: '', type: 'student', results: [], searched: false }; },
    methods: {
        async search() {
            const { data } = await api.get('/admin/search', { params: { q: this.q, type: this.type } });
            this.results = data; this.searched = true;
        }
    }
};