const TasksTable = document.getElementById('tasks-table');

const Tasks = document.getElementById('tasks');

TasksTable.addEventListener('click', async (event) => {
    const target = event.target.closest('.row');
    if (!target) return;
    const targetId = target.dataset.id;
    try{
        const response = await fetch(`/get_task/${targetId}`);
        const data = await response.json();

        document.getElementById('title').textContent = data.title;
        document.getElementById('text').textContent = data.text;
        document.getElementById('task-window').setAttribute('data-task-id', targetId);

        Tasks.classList.add('active');
    } catch (error) {
        console.log('Ошибка получения задачи');
    };
});

document.getElementById('submit-btn').addEventListener('click', async function(event) {
    event.preventDefault();
    const TaskID = document.getElementById('task-window').getAttribute('data-task-id');
    const Code = document.getElementById('code').value;
    const SubmitButton = document.getElementById('submit-btn');

    if (!Code.trim()){
        alert('Напишите код перед отправкой');
        return;
    };

    const message_block = document.getElementById('message');
    const message_icon = document.getElementById('messageicon');
    const message_txt = document.getElementById('messagetxt');

    try{

        SubmitButton.innerText = 'Проверка...';
        SubmitButton.disabled = true;
        const response = await fetch(`/check_task/${TaskID}`, 
            {
            method: 'POST', 
            headers: { 'Content-Type': 'application/json' }, 
            body: JSON.stringify({code: Code})
        });
        
        if (response.status === 401){
            alert('Сессия истекла! Сейчас Вы будете перенаправлены на страницу входа. Пожалуста, перезайдите для исправления ошибки.');
            window.location.href = '/login';
            return
        }
        
        const result = await response.json();

        message_txt.textContent = result.message;
        message_block.className = 'message';
        message_icon.textContent = result.status ? '[OK]:' : '[ERROR]:';
        const error_block = document.getElementById('error-block');
        if (!result.serverfault === false){
            if (result.status){
                message_block.classList.add('active', 'true');
                error_block.classList.remove('active');
            }else{
                message_block.classList.add('active', 'false');
                error_block.classList.add('active');
                error_block.textContent = result.serverfault;
            };
        }else{
            message_block.classList.add('active', 'false');
        };
    }catch (error){
        console.log('Ошибка');
        console.log(error);
        return
    }finally{
        SubmitButton.innerText = "Сдать на проверку";
        SubmitButton.disabled = false;
        setTimeout(() => {
            message_block.classList.remove('active');
        }, 3000);
    };
});

const BackButton = document.getElementById('back-button');

BackButton.addEventListener('click', () =>{
    Tasks.classList.remove('active');
});