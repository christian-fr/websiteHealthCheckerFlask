var form_data = null

function gather_file_ids() {
    var tbody = $('#files_table').find('tbody')
    var table_rows = tbody.find('tr')
    var file_ids = []

    for(i=0; i<table_rows.length; i++) {
        row_id = table_rows.eq(i).attr('id')
        if(row_id.startsWith('file_')) {
            file_ids.push(row_id.substring(5))
        }
    }

    return file_ids
}

function trigger_process(file_ids) {
    if(file_ids.length > 0) {
        file_id = file_ids[0]
        $("#file_" + file_id).find('td').eq(1).html("processing")

        $.ajax({
            url : '/api/process/' + file_id,
            type : 'GET',
            dataType: 'json',
            success : function(data) {
                $("#file_" + file_id).find('td').eq(1).html("success")
                $("#file_" + file_id).find('td').eq(2).html('<a href="file/processed_'.concat(file_id).concat('_.xml">link</a>'))
                trigger_process(file_ids.slice(1))
            },
            error : function(request, error) {
                $("#file_" + file_id).find('td').eq(1).html("error")
                trigger_process(file_ids.slice(1))
            }
        });
    }
}


function submit_form() {
    var form = $('#add_url_form')[0]
    form_data = new FormData(form);

    $.ajax({
        type: 'POST',
        url: '/api/add_url',
        data: form_data,
        success : function(data) {
            var tbody = $('#files_table').find('tbody')
            tbody.append('<tr>')
            var new_row = tbody.find('tr').last()
            new_row.attr('id', 'file_' + data['file_id'])
            new_row.append('<td>')
            new_row.append('<td>')
            new_row.append('<td>')
            new_row.find('td').eq(0).html(data['filename'])
            new_row.find('td').eq(1).html('uploaded')
            new_row.find('td').eq(2).html('link')
        },
        error : function(request, error) {
            alert(request)
        },
        processData: false,
        contentType: false
    })
}

$( document ).ready(function() {
    $('#upload_button').click(function() {
        submit_form()
    });

    $('#process_button').click(function() {
        trigger_process(gather_file_ids())
    });
});
