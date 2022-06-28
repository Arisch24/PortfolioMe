function showHidePassword(from, to) {
    $('.toggle-password').on('click', function (e) {
        const input = $(this).prev();
        const type = input.attr('type') == 'password' ? 'text' : 'password';
        input.attr('type', type);
        type == 'password'
            ? $(this).attr('src', from)
            : $(this).attr('src', to);
    });
}
