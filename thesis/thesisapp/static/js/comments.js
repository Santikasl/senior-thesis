$('.comment-like').submit(function (e) {
    e.preventDefault()
});
$('.comment-form').submit(function (e) {
    e.preventDefault()
    var post_id_not_slice =  $(this).attr('id')
    const post_id = post_id_not_slice.slice(1)
    const text = document.getElementById('btncomment'+post_id).value
    const text_input = document.getElementById('btncomment'+post_id)
    const url = $(this).attr('action')
    const comment_container = document.getElementById("description"+post_id)
    const user_photo = document.getElementById('user_photo').value
    const scrollHeight = comment_container.scrollHeight;
    const scrollOptions = {
      top: scrollHeight,
      behavior: "smooth" // Добавляем плавность
    };

    $.ajax({
        type: 'POST',
        url: '/comment/',
        data: {
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            'post_id': post_id,
            'comment': text
        },

        success: function (response) {
            text_input.value = ''
            text_input.blur()
            user = response.user
            id = response.id
           comment_container.innerHTML +=`
           <div class="comment-box">
               <div class="comment-container" id="comment-container">
                   <div class="avatar-comment">
                      <img class="main-logo" src="${user_photo}" alt="" width="50px">
                   </div>
                   <div class="comment-text">
                      <p class="user-name-comment">${user}</p>
                      <p>${text}</p>
                   </div>
               </div>
               <div class="comment-action">
                    <form action="/comment_like/" class="comment-like" method="post" id="k${id}">
                      <input type="hidden" name="csrfmiddlewaretoken" value="CVYxaOHc2NaLm9P0hFuBXDmgQyECJ4t8w6buidcjXpwifCB6EVEYN14xKrQfC81I">
                      <input type="hidden" name="comment_id" value="${id}">
                      <button class="comment-like-btn" id="comments_num_likes${id}" value="${id}" name="ewfwegew" type="submit">Нравится</button>
                    </form>
                   <p style="margin-left: 10px">Ответить</p>
               </div>
           </div>
            `
        comment_container.scrollTo(scrollOptions);
        },

        error: function (xhr, errmsg, err) {
            console.log("error"); // provide a bit more info about the error to the console
        }
    });
});

$('.comment-like').submit(function (e) {
    e.preventDefault()
    var post_id_not_slice =  $(this).attr('id')
    const comments_id = post_id_not_slice.slice(1)

    const url = $(this).attr('action')
    const comments_num_likes = document.getElementById('comments_num_likes'+comments_id)

    $.ajax({
        type: 'POST',
        url: '/comment_like/',
        data: {
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            'comments_id': comments_id,
        },
        success: function (response) {
            num_likes = response.num_likes
            if (num_likes > 0){
                comments_num_likes.innerHTML =`Нравится(${num_likes})`
            }
            else {
                comments_num_likes.innerHTML =`Нравится`
            }

        },

        error: function (xhr, errmsg, err) {
            console.log("error"); // provide a bit more info about the error to the console
        }
    });
});