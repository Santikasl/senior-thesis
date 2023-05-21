function containsSmileys(text) {
  var regex = /[\uD83C-\uDBFF\uDC00-\uDFFF]+/g; // Регулярное выражение для поиска смайликов
  return regex.test(text);
}

$('.send-message').submit(function (e) {
    e.preventDefault()
    var post_id_not_slice = $(this).attr('id')
    const follow_pk = post_id_not_slice.slice(1)
    const message = document.getElementById('message-btn' + follow_pk).value
    const message_btn = document.getElementById('message-btn' + follow_pk)
    const message_container = document.getElementById('user-message' + follow_pk)
    const like = document.getElementById('like').value

    const url = $(this).attr('action')
    const scrollHeight = message_container.scrollHeight;
    const scrollOptions = {
        top: scrollHeight,
        behavior: "smooth" // Добавляем плавность
    };
    var list = ["🧡","💜","🖤","🤍","💗","💖","💘","💝"];
    $.ajax({
        type: 'POST',
        url: '/message/',
        data: {
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            'follow_pk': follow_pk,
            'message': message,
            'like': list[Math.floor(Math.random() * list.length)]
        },

        success: function (response) {
            message_btn.value = ''

            text = response.text
            if (containsSmileys(text)) {
                message_container.innerHTML += `
<div style=" width: 640px; margin-left: 20px; display: flex; justify-content: right">
                                            <div class="receiver_emoji">${text}</div>
                                        </div>

                 

            `
                message_container.scrollTo(scrollOptions);
            }
            else {
                 message_container.innerHTML += `
      <div style=" width: 640px; margin-left: 20px; display: flex; justify-content: right">
                                           <div class="receiver">${text}</div>
                                        </div>
                 

            `
                message_container.scrollTo(scrollOptions);
            }
        },


        error: function (xhr, errmsg, err) {
            console.log("error"); // provide a bit more info about the error to the console
        }
    });
});

