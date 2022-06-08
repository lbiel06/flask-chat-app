var socket = io.connect('http://127.0.0.1:5000')

socket.on('message', (data) => {
    console.log(data, to)
    if (data['from'] == to || data['to'] == to) {
        $('.chat').append(`
        <li><b>${data['from']}: </b>${data['text']}   <i>${data['date']}</i></li><tr>
        `)
    }
})

$('form').on('submit', (event) => {
    event.preventDefault()
    // var to = to
    var text = $('#text').val()
    socket.emit('message', {
        'to': to,
        'text': text
    })
    $('#text').val('')
})
