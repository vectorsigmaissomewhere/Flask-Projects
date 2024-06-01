document.addEventListener('DOMContentLoaded', function() {
    let menu = document.querySelector('#menu-bar');
    let navbar = document.querySelector('.navbar');
    const header = document.querySelector('header');

    menu.addEventListener('click', () => {
        menu.classList.toggle('fa-times');
        navbar.classList.toggle('nav-toggle');
    });

    window.onscroll = () => {
        menu.classList.remove('fa-times');
        navbar.classList.remove('nav-toggle');

        if (document.documentElement.scrollTop > 5) {
            header.classList.add('active');
        } else {
            header.classList.remove('active');
        }
    };
});
