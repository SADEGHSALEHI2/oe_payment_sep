# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pprint

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)


class SEPController(http.Controller):
    _tokenize_url = "/payment/sep/tokenize"
    _return_url = '/payment/sep/return'

    @http.route(
        _tokenize_url, type='http', auth='public', methods=['POST'], csrf=False,
        save_session=False
    )
    def sep_tokenize(self, **data):
        provider_id = int(data.pop('provider_id'))
        provider_sudo = request.env['payment.provider'].sudo().browse(provider_id)
        
        payload = {
            **data,
            'Action': 'token'
        }
        
        payload['Amount']=int(payload['Amount'])*10

        response = provider_sudo._sep_make_request(payload)
        token = response.get('token')
        _logger.info("Received SEP (Saman Electronic Payment) return token:\n%s", pprint.pformat(token))

        if(token):
            return request.redirect('https://sep.shaparak.ir/OnlinePG/SendToken?token=%s' %token, code=301, local=False)

        return request.redirect('/shop/payment')
    
    @http.route(
        _return_url, type='http', auth='public', methods=['GET', 'POST'], csrf=False,
        save_session=False
    )
    def sep_return_from_checkout(self, **data):
        """ Process the notification data sent by SEP (Saman Electronic Payment) after redirection from checkout.

        The route is flagged with `save_session=False` to prevent Odoo from assigning a new session
        to the user if they are redirected to this route with a POST request. Indeed, as the session
        cookie is created without a `SameSite` attribute, some browsers that don't implement the
        recommended default `SameSite=Lax` behavior will not include the cookie in the redirection
        request from the payment provider to Odoo. As the redirection to the '/payment/status' page
        will satisfy any specification of the `SameSite` attribute, the session of the user will be
        retrieved and with it the transaction which will be immediately post-processed.

        :param dict data: The notification data (only `id`) and the transaction reference (`ref`)
                          embedded in the return URL
        """
        _logger.info("handling redirection from SEP (Saman Electronic Payment) with data:\n%s", pprint.pformat(data))
        request.env['payment.transaction'].sudo()._handle_notification_data('sep', data)
        return request.redirect('/payment/status')