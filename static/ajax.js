function funny(value)
{
    var ajax = new XMLHttpRequest();

    if (value == "all") {
        ajax.onreadystatechange = function () {
            if (ajax.readyState == 4 && ajax.status == 200) 
            {
                $('#filtr_table').html(ajax.responseText);
            }
        };

    // open the requested file and send
    ajax.open('GET', 'userhome_all.html', true);
    ajax.send();
    }
    
    //when page is loaded do function(), which is filling html inside #filtr_table
    ajax.onreadystatechange = function () {
        if (ajax.readyState == 4 && ajax.status == 200) 
        {
            $('#filtr_table').html(ajax.responseText);
        }
    };

    // open the requested file and send
    ajax.open('GET', 'userhome_filtr.html', true);
    ajax.send();
};