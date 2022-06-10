var socket = io.connect('http://127.0.0.1:5000')

socket.on('message', (data) => {
    console.log(data, to)
    if (data['from'] == to || data['to'] == to) {
        $('.chat').append(`
        <p style="margin:0 !important;"><span style="color:#9EBC97 ;">${data['from']}:</span> ${data['text']}<span style="color:gray;"> ${data['date']}</span></p>
        `)
        $('.chat').scrollTop($('.chat').height());

    }
})

$('form').on('submit', (event) => {
    event.preventDefault()
    console.log('submit')
    // var to = to
    var text = $('#message-text').val()
    socket.emit('message', {
        'to': to,
        'text': text
    })
    $('#message-text').val('')
})
