$( function() {
$('body').append('<u  style="display: block; position: fixed; top: 50px;  left: 40%; width: 600px; height: 500px; margin: 0;">\
    <u  style="display: block; float: left;">\
    <p style="width: 100%; text-align:center; margin: 0;">Filter</p>\
    <input type="text" name="filter-string"\
    style="background-color: rgba(250,250,220); border-radius: 5px; width: 200px;  padding: 2px; outline: none;">\
    </u>\
    <u  style="display: block; float: left; margin-top: 18;">\
    <input type="button" name="filter-registr" value="aA"\
    style="background-color: rgb(250,250,220); margin: 0; margin-left: 5px;width: 30px; height: 25px; border-radius: 5px; outline: none;\
    text-aling: center;">\
    </u>\
    <u style="display: block; float: left; text-aling:center;">\
    <p style="width: 100%; text-align:center; margin: 0;">Find</p>\
    <input type="text" name="find-string" \
    style="background-color: rgba(200,250,250); border-radius: 5px; width: 200px;  padding: 2px; margin-left: 10px; outline: none;">\
    </u>\
    <u style="display: block; float: left; margin-top: 18;f">\
    <input type="button" name="find-registr" value="aA" \
    style="background-color: rgb(200,250,250); margin: 0; margin-left: 5px;width: 30px; height: 25px; border-radius: 5px; outline: none;">\
    </u>\
    </u>');

    filterString  = $("input[name='filter-string']");
    filterRegBut  = $("input[name='filter-registr']");
    filterRegButCol = filterRegBut.css('background-color');
    filterRegistr = -1;

    findString   = $("input[name='find-string']");
    findRegBut   = $("input[name='find-registr']");
    findRegButCol = findRegBut.css('background-color');
    findRegistr  = -1;

    function press(target) {
        if (target == 'filter-string')
        {
            var substr = filterString.val();
            if ( filterRegistr < 0 ) { substr = substr.toLowerCase() }
        }
        else if (target == 'find-string')
        {
            var substr = findString.val();
            if (findRegistr < 0) { substr = substr.toLowerCase() }
        }


        if (target == 'filter-string')
        {
            $('div').each( function(index) {
                filterStr = $(this).text()
                if (filterRegistr < 0) { filterStr = filterStr.toLowerCase() }

                filtered = filterStr.indexOf( substr ) != -1;
                if (filtered) { $(this).css('display', 'block') }
                else { $(this).css('display', 'none') }
            });
        }
        else
        {
            $('div').each( function(index) {
                findStr = $(this).text()
                if (findRegistr < 0) { findStr = findStr.toLowerCase() }

                if ( substr == '' ) { finded = false }
                else { finded = findStr.indexOf( substr ) != -1 }

                if ( finded ) { $(this).css('background-color', 'rgb(163, 255, 194)') }
                else { $(this).css('background-color', 'rgb(255, 255, 255)') }
            });
        }
    }

    filterString.keyup(function(event) {
        if (event.keyCode === 13) {
            press(event.target.name);
        }
    });

    findString.keyup(function(event) {
        if (event.keyCode === 13) {
            press(event.target.name);
        }
    });

    filterRegBut.on('click', function() {
        filterRegistr *= -1;
        filterString.focus();
        (filterRegistr > 0) ? filterRegBut.css('background-color', 'rgb(200,200,170)') : filterRegBut.css('background-color', filterRegButCol);
    });

    findRegBut.on('click', function() {
        findRegistr *= -1;
        findString.focus();
        (findRegistr > 0) ? findRegBut.css('background-color', 'rgb(130,180,180)') : findRegBut.css('background-color', findRegButCol);
    });

});
