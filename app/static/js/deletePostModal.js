$('#confirmDeleteModal').on('show.bs.modal', function (event) {
    const button = $(event.relatedTarget) // Button that triggered the modal

    // Extract info from data-* attribute
    const postId = button.data('post-id')
    const postTitle = button.data('post-title')
    const dateCreated = button.data('post-created')

    const form = document.getElementById('delete-post-form')
    form.action = '/blog/delete-post/' + postId
    
    const modal = $(this)

    const msg = postTitle + '<br>' +
    'Written on: ' + dateCreated + ' ?'

    modal.find('#modal-delete-post-title').html(msg)
  })
