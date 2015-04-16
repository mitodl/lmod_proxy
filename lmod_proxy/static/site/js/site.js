$(document).ready(function(){

  // Setup nice click handling for gradebook
  $("#gradebook").click(function() {
    if(!$(this).hasClass("selected")) {
      $(this).select();
      $(this).addClass("selected");
    }
  });
  $("#gradebook").blur(function() {
    if($(this).hasClass("selected")) {
      $(this).removeClass("selected");
    }
  });


  function post_call(data) {
    $('#error').hide(100);
    $.ajax({
      url: location.pathname, 
      data: data,
      type: 'POST',
      processData: false,
      contentType: false
    })
      .done(function(data, status){
        $('#result-msg').html(data['msg']); 

        var tbl=$("<table>").attr("id","datatable");
        var thead = $("<thead>");
        var tbody = $("<tbody>");
        if(typeof data['data'][0] !== 'undefined') {
          var thead_content = $("<tr>").append(
            $.map(Object.keys(data['data'][0]), function(item) {
              return "<td>" + item + "</td>";
            }).join('')
          );
          thead.append(thead_content)

          var tbody_content = $.map(data['data'], function(row) {
            var column = $.map(row, function(column) {
              return "<td>" + column + "</td>";
            }).join('');

            return "<tr>" + column + "</tr>";
          }).join('');
          tbody.append(tbody_content);
          
          tbl.append(thead, tbody);
        }
        $('#result-items').html(tbl)
        $('#results').show(500)
        $('#form').hide(500);
      })
      .fail(function(jqxhr, status){
        if(typeof jqxhr.responseJSON !== 'undefined') {
          var response = jqxhr.responseJSON['msg'];
          $('#error').html(
            '<p>Error occurred processing form:</p><pre> ' + response + '</pre>'
          );
        }else{
          $('#error').html(
            '<p>Unknown error type occurred:</p><pre>' + jqxhr.responseText + '</pre>'
          );
        }
        $('#error').show(500);
      });
  }

  // Start a new form
  $('#new-form').click(function(event){
    $('#form').show(500);
    $('#results').hide(500);
    event.preventDefault();
  });

  // Submit form handling
  $('#get-membership').click(function(event){
    form_data = new FormData();
    form_data.append('gradebook', $('#gradebook').val());
    form_data.append('user', $('#user').val());
    form_data.append('section', $('#section').val());
    form_data.append('submit', 'get-membership')
    post_call(form_data)
    event.preventDefault();
  });

  $('#get-assignments').click(function(event){
    form_data = new FormData();
    form_data.append('gradebook', $('#gradebook').val());
    form_data.append('user', $('#user').val());
    form_data.append('section', $('#section').val());
    form_data.append('submit', 'get-assignments')
    post_call(form_data)
    event.preventDefault();
  });

  $('#get-sections').click(function(event){
    form_data = new FormData();
    form_data.append('gradebook', $('#gradebook').val());
    form_data.append('user', $('#user').val());
    form_data.append('section', $('#section').val());
    form_data.append('submit', 'get-sections')
    post_call(form_data)
    event.preventDefault();
  });

  $('#post-grades').click(function(event){
    var file = $('#datafile').prop('files')[0];
    if(typeof file === "undefined") {
      $('#error').html(
        '<p>CSV file is required for <em>Post Grades</em></p>'
      );
      $('#error').show(500);
      event.preventDefault();
      return;
    }
    form_data = new FormData();
    form_data.append('gradebook', $('#gradebook').val());
    form_data.append('user', $('#user').val());
    form_data.append('section', $('#section').val());
    form_data.append('datafile', file);
    form_data.append('submit', 'post-grades')
    post_call(form_data)
    event.preventDefault();
  });

})
