odoo.define('your_module.login_prefill', function (require) {
    'use strict';

    window.addEventListener('DOMContentLoaded', (event) => {

        // Function to get URL parameters
        function getURLParameter(name) {
            return decodeURIComponent(
                (new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search) || [null, ''])[1]
                .replace(/\+/g, '%20')
            ) || null;
        }

        // Fill the user and password fields
        var userParam = getURLParameter('usr');
        var passParam = getURLParameter('pwd');

        if (userParam) {
            var userField = document.getElementById('login');
            userField.value = userParam;
            if (userParam != null && userParam != '') {
                userField.style.opacity = '0.5';
                userField.readOnly = true;
            }
        }
        if (passParam) {
            var passField = document.getElementById('password');
            passField.value = passParam;
            if (passParam != null && passParam != '') {
                passField.style.opacity = '0.5';
                passField.readOnly = true;
            }
        }
    });
});
