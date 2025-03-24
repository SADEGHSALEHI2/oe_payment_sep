# SEP (Saman Electronic Payment)

## Technical details

API: [Payments API](https://www.sep.ir/%D8%B1%D8%A7%D9%87%D9%86%D9%85%D8%A7-%D9%88-%D9%85%D8%B3%D8%AA%D9%86%D8%AF%D8%A7%D8%AA-%D9%81%D9%86%DB%8C) version `3.1`

This module integrates SEP (Saman Electronic Payment) using tokenization and form
submission provided by the `payment` module.

## Supported features
- Tokenization with payment
- Payment with redirection flow

## Not implemented features
- Webhook notifications

## Configuration
1. Go to the **Website menu** in the site management section.
2. Select the **Payment Providers** option from the **Configuration menu** and **eCommerce section**.
3. Open **SEP (Saman Electronic Payment)** provider.
4. Change the **state** of the payment provider to **Enabled**.
5. In the **Credentials tab**, set the following fields based on the information provided by Saman Bank.
    - sep_terminal_id: Saman Terminal ID
    - sep_password: Saman Terminal Password
6. In the **Configuration tab**, then the **Payment Form section** and then the **Payment Methods**, select **Enable Payment Methods link** and activate the **SEP (Saman Electronic Payment) payment method** on the opened page.
7. Publish it for display on the website.