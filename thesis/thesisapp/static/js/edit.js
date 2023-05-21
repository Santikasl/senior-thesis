$(document).on('click', '.edit-button', function (e) {
    var post_id_not_slice =  $(this).attr('id')
    const post_id =  post_id_not_slice.slice(1)
    const url = $(this).attr('action')
    let res
    const like = $(`.like-btn${post_id}`).text()
    const intLike = like
    const trimCount = parseInt(intLike)
    const btnlike = document.querySelectorAll('#btnlike' + post_id)


    $.ajax({
        type: 'POST',
        url: '/edit/',
        data: {
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            'id': idPosts,
            'description': description,
        },
        success: function (res_post2) {
            const dataPost2 = res_post2.data

            description2.style.display = 'flex'
            console.log(dataPost2)
            description2.innerHTML = ""
            descriptionpost2.innerHTML = ""
            textarea.style.display = 'none'
            description2.innerHTML += `
            <p>${dataPost2.split('\n').join('<br>')}</p>
`
            descriptionpost2.innerHTML += `
            ${dataPost2.split('\n').join('<br>')}
            `
            btnlike.style.opacity = '1'
        },

        error: function (xhr, errmsg, err) {
            console.log("error"); // provide a bit more info about the error to the console
        }
    });
});