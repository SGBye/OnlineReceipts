$(document).ready(function () {
    $('[type="tel"]').inputmask("+7 (999) 999-9999", {clearMaskOnLostFocus: false});
    $("#page_name").html(window.location.pathname);
    var path = String(window.location.pathname);
    $('a[href="' + path + '"]').addClass("active")

});

$('#qrScan').on('submit', (function (e) {
    e.preventDefault();

    var formData = new FormData(this);

    $.ajax({
        type: 'POST',
        url: 'receipts/api/scan_qr',
        data: formData,
        cache: false,
        contentType: false,
        processData: false,
        success: function (data) {
            $("#ajaxModal").modal('show');
        },
        error: function (data) {
            $("#ajaxModalError").modal('show');
        }
    });
}))
;

$('#close_modal').click(function () {
    window.location.href = "/receipts"
});

$('#reset_sms').click(function () {

    $.get('/accounts/api/reset_code', function (data) {
        $("#ajaxSmsCode").modal('show');
    })
});

$('#close_modal_sms').click(function () {
    window.location.href = "/profile"
});

$('#changeSmsCode').click(function () {
    $("#ajaxSaveSms").modal('show');
});

$(".nav-link").on("click", function (e) {
    e.preventDefault();

    window.location.href = ($(this).attr("href"));

    $(".nav-item").find(".active").removeClass("active");
    $(this).addClass("active");
});


const deleteReceipts = document.querySelectorAll('.js-delete-receipt');

deleteReceipts.forEach((item) => {
    item.addEventListener('click', () => {
        const id = item.dataset.id;
        console.log(csrftoken)
        fetch(`/receipts/api/delete/${id}/`, {method: 'delete'})
            .then(res => console.log(res))
    })
});