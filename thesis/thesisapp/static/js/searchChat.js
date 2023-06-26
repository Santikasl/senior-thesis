const searchInput2 = document.getElementById("search-input2")
const resultBlock2 = document.getElementById("message-chat-container")
const csrf2 = document.getElementsByName('csrfmiddlewaretoken')[0].value
const originalContent = resultBlock2.innerHTML;

document.addEventListener('click', function(event) {
  const target = event.target;

  // Тут можно добавить условие для определения, что кликнутый элемент является чатом
  if (target.classList.contains('chat')) {
    const chatId = target.getAttribute('data-chat-id');
    showChat(chatId);
  }
});
const sendSearchData2 = (dataName) => {
    $.ajax({
        type: 'POST',
        url: '/searchchat/',
        data: {
            'csrfmiddlewaretoken': csrf2,
            'dataName': dataName,

        },
        success: (res) => {
            const data = res.data
            console.log(data)
            if (Array.isArray(data)) {
                resultBlock2.innerHTML = ""
                data.forEach(dataName => {
                    resultBlock2.innerHTML += `
                    <div class="message-chat-container" data-chat-id="${dataName.pk}"
                                                 id="message${dataName.pk}">
                        <div class="avatar-comment">
                            <img class="main-logo" src="${dataName.img}" alt="" width="50px">
                         </div>
                         <div class="chat-text">
                             <p class="user-name-message">${dataName.name}</p>
                         </div>
                       </div>
                  
                    `
                })
            } else {
                if (searchInput2.value.length > 0) {
                    resultBlock2.innerHTML = "";
                } else {
                    resultBlock2.innerHTML = originalContent;
                }
            }

        },
        error: (err) => {
            console.log(err)
        }
    })
}


searchInput2.addEventListener('keyup', e => {



    sendSearchData2(e.target.value)
})

resultBlock2.addEventListener('click', function(event) {
  const target = event.target;

  if (target.classList.contains('message-chat-container')) {
    const chatId = target.getAttribute('data-chat-id');
    hideAllChats();
    message404.style.display = "none";
    showChat(chatId);
    getCounters(chatId);
    intervalId = setInterval(function() {
      receiveMsg(chatId);
    }, 1000);
  }
});
