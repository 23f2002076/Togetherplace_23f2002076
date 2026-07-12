const App = {
    components: { NavBar },
    template: `
    <nav-bar></nav-bar>
    <div class="container pb-5">
        <router-view></router-view>
    </div>`
};

const app = Vue.createApp(App);
app.use(router);
app.mount('#app');
