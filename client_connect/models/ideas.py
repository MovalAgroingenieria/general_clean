
from odoo.http import request
from odoo.addons.auth_signup.controllers.main import AuthSignupHome


# Pverride do_signup method
class AuthSignupHome(AuthSignupHome):
    def do_signup(self, qcontext):
        values = dict((key, qcontext.get(key))
                      for key in ('login', 'name', 'password', 'phone'))
        assert any([k for k in values.values()]),\
            "The form was not properly filled in."
        assert values.get('password') == qcontext.get('confirm_password'),\
            "Passwords do not match; please retype them."
        self._signup_with_values(qcontext.get('token'), values)
        request.cr.commit()
