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