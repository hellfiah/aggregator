$(document).ready(function(){
    //Prepare forms on the side
    $('form input').change(function () {
        $('form p').text(this.files.length + " file(s) selected");
    });
    $( "#account-edit" ).click(function() {
        $('.remove-account-cross').toggle();

        if ($( "#account-edit" ).text() == 'edit') {
            $( this ).text('stop');
        }
        else {
            $(this).text('edit');
        }
    });
    $( "#upload-edit" ).click(function() {
        $('.remove-upload-cross').toggle();
        if ($(this).text() == 'edit') {
            $(this).text('stop');
        }
        else {
            $(this).text('edit');
        }
    });
    $( ".remove-account-cross" ).click(function(e) {
        e.stopPropagation();
        var account_id = $(this).parent().attr('account-id');
        $('#remove_account_id').attr('value', account_id);
        $('#pop-up-modal').modal('show');
    });
    $( ".remove-upload-cross" ).click(function(e) {
        e.stopPropagation();
        var upload_id = $(this).parent().attr('upload-id');
        //update modal body
        var str = '<h4>Are you sure you want to remove this upload?</h4>'
        str += '<p>This will delete all transactions associated with this CSV, which can not be undone.</p>'
        $('#main-modal-body').html(str);

        //assign functionality to footer
        str = '<button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>';
        str += '<button class="btn btn-primary" id="remove-upload-confirm">Yes</button>';
        $('#modal-footer').html(str);


        $(document).on("click", "#remove-upload-confirm", function(){
            $.post( "/view_accounts/removeUpload", { upload_id: upload_id },
             function(data) {
                location.reload();
             });
        });
        $('#pop-up-modal').modal('show');
    });

    ////////////////////// Transaction table functionality//////////////////////////////////////////////////
    var transaction_table = $('#transaction-table').dataTable( {
        "order": [[ 0, "desc" ]],
        "pageLength": 50,
        "select": {
            style: 'multi'
        }
    });

    //Filters
    $("#transaction-name-filter").keyup(function() {
        transaction_table.fnFilter(this.value, 1);
    });

    //account filter functionality
    $("#select-all-accounts-check").change(function() {
        if ($(this).is(":checked")) {
            var search_string = "";
            $(".account-check").each(function() {
                $(this).prop('checked', true);
                if (search_string == "" ) {
                    search_string += $(this).val();
                }
                else {
                    search_string += "|" + $(this).val();
                }
            });
            transaction_table.fnFilter(search_string, 2, true);
        }
        else {
            $(".account-check").each(function() {
                $(this).prop('checked', false);
                transaction_table.fnFilter("Show nothing in the category section", 2, true);
            });
        }
    });

    $('.account-check').change(function() {
        var search_string = "Show nothing in the category section";
        var check_count = 0;
        $(".account-check").each(function() {
            if ($(this).is(":checked") && search_string == "Show nothing in the category section") {
                search_string = $(this).val();
                check_count += 1;
            }
            else if ($(this).is(":checked")) {
                search_string += "|" + $(this).val();
                check_count += 1;
            }
            else if (!$(this).is(":checked")) {
                $("#select-all-accounts-check").prop('checked', false);
            }
        });
        if (check_count == $(".account-check").length) {$("#select-all-accounts-check").prop('checked', true);}
        console.log(search_string);
        transaction_table.fnFilter(search_string, 2, true);
    });



    //category filter functionality
    $("#select-all-categories-check").change(function() {
        if ($(this).is(":checked")) {
            var search_string = "";
            $(".category-check").each(function() {
                $(this).prop('checked', true);
                if (search_string == "" ) {
                    search_string += $(this).val();
                }
                else {
                    search_string += "|" + $(this).val();
                }
            });
            transaction_table.fnFilter(search_string, 3, true);
        }
        else {
            $(".category-check").each(function() {
                $(this).prop('checked', false);
                transaction_table.fnFilter("Show nothing in the category section", 3, true);
            });
        }
    });

    $('.category-check').change(function() {
        var search_string = "Show nothing in the category section";
        var check_count = 0;
        $(".category-check").each(function() {
            if ($(this).is(":checked") && search_string == "Show nothing in the category section") {
                search_string = $(this).val();
                check_count += 1;
            }
            else if ($(this).is(":checked")) {
                search_string += "|" + $(this).val();
                check_count += 1;
            }
            else if (!$(this).is(":checked")) {
                $("#select-all-categories-check").prop('checked', false);
            }
        });
        if (check_count == $(".category-check").length) {$("#select-all-categories-check").prop('checked', true);}
        transaction_table.fnFilter(search_string, 3, true);
    });

    //select functionality
    $(".transaction-row").on("click", function() {
        //show that the transaction is selected / deselected
        if ($(this).hasClass('selected')) {
            $(this).removeClass('selected');
        }
        else {
            $(this).addClass('selected');
        }
        //show or hide the side bar as necessary
        if ($(".selected").length > 0 && !$("#side-toolbar").hasClass('visible')) {
            $("#side-toolbar").animate({"right":"0px"}, "fast").addClass('visible');
        }
        else if ($(".selected").length == 0 && $("#side-toolbar").hasClass('visible')) {
            $("#side-toolbar").animate({"right":"-90px"}, "fast").removeClass('visible');
        }
    });
    $(".transaction-row").on("contextmenu", function(event) {
        event.preventDefault();
        //show that the transaction is selected / deselected
        if ($(this).hasClass('selected')) {
            $(this).removeClass('selected');
        }
        else {
            $(this).addClass('selected');
        }
        //show or hide the side bar as necessary
        if ($(".selected").length > 0 && !$("#side-toolbar").hasClass('visible')) {
            $("#side-toolbar").animate({"right":"0px"}, "fast").addClass('visible');
        }
        else if ($(".selected").length == 0 && $("#side-toolbar").hasClass('visible')) {
            $("#side-toolbar").animate({"right":"-90px"}, "fast").removeClass('visible');
        }
    });

    // If the sidebar element is clicked
    $(".side-toolbar-option").click(function(){
        // This is the triggered action name
        switch($(this).attr("data-action")) {

            case "categorise-this":
                prepareCategorySelectorModal("categoriseTransactions");
                break;

            case "categorise-all-similar":
                prepareCategorySelectorModal("categoriseSimilarTransactions");
                break;

            case "cancel-selection":
                $('.selected').each(function() {
                    $(this).removeClass('selected');
                });
        }
    });
    ////////////////////// end transaction click menu module

});


function prepareCategorySelectorModal(destination_url) {

    if (($('.selected').length == 1 && destination_url == 'categoriseSimilarTransactions') || destination_url == 'categoriseTransactions') {
        //select transactions to categorise
        var transactions_to_categorise = [];
        $('.selected').each(function() {
            transactions_to_categorise.push({ id: Number($(this).attr('transaction-id')) });
        });

        //Load the possible categories into the popup
        $.get("/view_accounts/loadTransactionCategories", function(data) {
            var looper = 1;
            var categories = $.parseJSON(data);
            //Build the table of categories to populate the
            var str = '<table id="category-selection-table"><tr>';
            $.each(categories , function(index, category) {
                if (((looper-1) % 3) == 0) {
                    str += '</tr><tr><td class="category-select text-link-hover" category-id=' + category[0] + '>' + category[1] + '</td>';
                }
                else {
                    str += '<td class="category-select text-link-hover" category-id=' + category[0] + '>' + category[1] + '</td>';
                };
                looper ++;
            });
            str += '</tr></table>';
            $('#main-modal-body').html(str);

            //assign functionality to footer
            str = '<button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>';
            str += '<button class="btn btn-primary disabled" id="categorise-confirm">Confirm</button>';
            $('#modal-footer').html(str);

            //wait for category selection
            var category_id;
            $(document).on("click", ".category-select", function() {
                if ( $('#category-selected').length > 0) {
                    $('#category-selected').removeAttr('id');
                }
                $(this).attr('id', 'category-selected');
                category_id = Number($(this).attr('category-id'));
                if ($('#categorise-confirm').hasClass('disabled')) {
                    $('#categorise-confirm').removeClass('disabled');
                }
            });

            $("#categorise-confirm").off();
            $(document).on("click", "#categorise-confirm", function() {
                if( typeof category_id === 'number' && !($('#categorise-confirm').hasClass('disabled'))) {
                    data_to_send = {'category_id': category_id, 'transactions': transactions_to_categorise};
                    $.ajax({
                      type: "POST",
                      contentType: "application/json; charset=utf-8",
                      url: "/view_accounts/" + destination_url,
                      data: JSON.stringify(data_to_send),
                      dataType: "json",
                    });
                    location.reload();
                }
            });
            $('#pop-up-modal').modal('show');
        })
    }
}