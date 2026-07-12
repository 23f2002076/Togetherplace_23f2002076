const routes = [
    { path: '/', redirect: '/login' },
    { path: '/login', component: LoginView, meta: { guest: true } },
    { path: '/register', component: RegisterChoiceView, meta: { guest: true } },
    { path: '/register/student', component: RegisterStudentView, meta: { guest: true } },
    { path: '/register/company', component: RegisterCompanyView, meta: { guest: true } },

    { path: '/admin', component: AdminDashboardView, meta: { role: 'admin' } },
    { path: '/admin/search', component: AdminSearchView, meta: { role: 'admin' } },

    { path: '/company', component: CompanyDashboardView, meta: { role: 'company' } },
    { path: '/company/drive/new', component: NewDriveView, meta: { role: 'company' } },
    { path: '/company/drive/:id/edit', component: EditDriveView, meta: { role: 'company' } },
    { path: '/company/drive/:id/applicants', component: ApplicantsView, meta: { role: 'company' } },
    { path: '/company/profile', component: CompanyProfileView, meta: { role: 'company' } },

    { path: '/student', component: StudentDashboardView, meta: { role: 'student' } },
    { path: '/student/drive/:id', component: ViewDriveView, meta: { role: 'student' } },
    { path: '/student/history', component: StudentHistoryView, meta: { role: 'student' } },
    { path: '/student/profile', component: StudentProfileView, meta: { role: 'student' } },
];

const router = VueRouter.createRouter({
    history: VueRouter.createWebHashHistory(),
    routes
});

router.beforeEach((to) => {
    const token = localStorage.getItem('ppa_token');
    const role = localStorage.getItem('ppa_role');

    if (to.meta.guest && token) {
        return role === 'admin' ? '/admin' : role === 'company' ? '/company' : '/student';
    }
    if (to.meta.role) {
        if (!token) return '/login';
        if (to.meta.role !== role) return '/login';
    }
    return true;
});
