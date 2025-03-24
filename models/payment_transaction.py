# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from werkzeug import urls

from odoo import _, models
from odoo.exceptions import ValidationError

from odoo.addons.payment_sep import const
from odoo.addons.payment_sep.controllers.main import SEPController


_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        """ Override of payment to return SEP-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of provider-specific rendering values
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'sep':
            return res

        payload = self._sep_prepare_payment_request_payload()
        return payload
    
    def _sep_prepare_payment_request_payload(self):
        """ Create the payload for the payment request based on the transaction values.

        :return: The request payload
        :rtype: dict
        """
        base_url = self.provider_id.get_base_url()
        return {
            'provider_id':self.provider_id.id,
            'api_url': urls.url_join(base_url, SEPController._tokenize_url),
            'Amount': int(self.amount),
            'ResNum': self.reference,
            'MID': self.provider_id.sep_terminal_id,
            'RedirectURL': urls.url_join(base_url, SEPController._return_url)
        }

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """ Override of payment to find the transaction based on SEP (Saman Electronic Payment) data.

        :param str provider_code: The code of the provider that handled the transaction
        :param dict notification_data: The notification data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'sep' or len(tx) == 1:
            return tx

        tx = self.search(
            [('reference', '=', notification_data.get('ResNum')), ('provider_code', '=', 'sep')]
        )
        if not tx:
            raise ValidationError("SEP (Saman Electronic Payment): " + _(
                "No transaction found matching reference %s.", notification_data.get('ref')
            ))
        return tx

    def _process_notification_data(self, notification_data):
        """ Override of payment to process the transaction based on SEP (Saman Electronic Payment) data.

        Note: self.ensure_one()

        :param dict notification_data: The notification data sent by the provider
        :return: None
        """
        super()._process_notification_data(notification_data)
        if self.provider_code != 'sep':
            return
        
        # if notification_data.get('State') == 'OK':
        #     self.provider_reference = notification_data.get('RefNum')

        ResNum = notification_data.get('ResNum')
        transaction = self.sudo().search([('reference','=', ResNum)])

        result = self.provider_id._sep_verify_request(notification_data)
        
        if notification_data.get('State') == 'OK' and result and result/10 == transaction.amount:
            self.provider_reference = notification_data.get('RefNum')
            self._set_done()
            # transaction.write({'state':'done'})
        else:
            self._set_error(
                "SEP (Saman Electronic Payment): " + _("The payment encountered an error with code %s", notification_data.get('Status'))
            )
            # transaction.write({'state':'error'})

    