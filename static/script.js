const Container = document.getElementById('container');
const RegistrBtn = document.getElementById('create-btn');
const LoginBtn = document.getElementById('login-btn');

RegistrBtn.addEventListener('click', ()=>{
    Container.classList.remove("active");
});

LoginBtn.addEventListener('click', ()=>{
    Container.classList.add("active");
});