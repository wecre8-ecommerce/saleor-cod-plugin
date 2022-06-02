import logging
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, Iterable, Optional

from django.utils.translation import gettext_lazy as _
from prices import Money, TaxedMoney

from saleor.account.models import Address
from saleor.checkout.fetch import CheckoutInfo, CheckoutLineInfo
from saleor.discount import DiscountInfo
from saleor.plugins.avatax import _validate_checkout
from saleor.plugins.base_plugin import BasePlugin, ConfigurationTypeField

from saleor.payment.gateways.utils import get_supported_currencies, require_active_plugin
from cod import authorize, capture, confirm, process_payment, refund, void

from saleor.payment.interface import GatewayResponse, PaymentData, GatewayConfig

GATEWAY_NAME = str(_("Cash"))

logger = logging.getLogger(__name__)


class CashGatewayPlugin(BasePlugin):
    DEFAULT_ACTIVE = True
    PLUGIN_NAME = GATEWAY_NAME
    PLUGIN_ID = "payments.cash"
    CONFIGURATION_PER_CHANNEL = False

    DEFAULT_CONFIGURATION = [
        {"name": "cod_fees", "value": 0.0},
        {"name": "supported_countries", "value": "SA,"},
        {"name": "maximum_allowed_value", "value": 0.0},
        {"name": "supported_currencies", "value": "SAR,"},
        {"name": "automatic_payment_capture", "value": True},
    ]
    CONFIG_STRUCTURE = {
        "automatic_payment_capture": {
            "label": "Automatic payment capture",
            "type": ConfigurationTypeField.BOOLEAN,
            "help_text": "Determines if Saleor should automatically capture payments.",
        },
        "supported_currencies": {
            "label": "Supported Currencies",
            "type": ConfigurationTypeField.STRING,
            "help_text": "Determines currencies that support COD payments.",
        },
        "supported_countries": {
            "label": "Supported Countries",
            "type": ConfigurationTypeField.STRING,
            "help_text": "Determines countries that support COD payments.",
        },
        "cod_fees": {
            "label": "COD Fees",
            "type": ConfigurationTypeField.STRING,
            "help_text": "Cash on delivery fees.",
        },
        "maximum_allowed_value": {
            "label": "Maximum Allowed Value",
            "type": ConfigurationTypeField.STRING,
            "help_text": "Cash maximum allowed value.",
        },
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        configuration = {item["name"]: item["value"] for item in self.configuration}
        self.config = GatewayConfig(
            connection_params={
                "cod_fees": configuration["cod_fees"],
                "supported_countries": configuration["supported_countries"],
                "maximum_allowed_value": configuration["maximum_allowed_value"],
            },
            gateway_name=GATEWAY_NAME,
            auto_capture=configuration["automatic_payment_capture"],
            supported_currencies=configuration["supported_currencies"],
        )

    def _get_gateway_config(self):
        return self.config

    @require_active_plugin
    def get_supported_currencies(self, previous_value):
        config = self._get_gateway_config()
        return get_supported_currencies(config, GATEWAY_NAME)

    @require_active_plugin
    def authorize_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        return authorize(payment_information, self._get_gateway_config())

    @require_active_plugin
    def capture_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        return capture(payment_information, self._get_gateway_config())

    @require_active_plugin
    def confirm_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        return confirm(payment_information, self._get_gateway_config())

    @require_active_plugin
    def refund_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        return refund(payment_information, self._get_gateway_config())

    @require_active_plugin
    def void_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        return void(payment_information, self._get_gateway_config())

    @require_active_plugin
    def process_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        return process_payment(payment_information, self._get_gateway_config())

    @require_active_plugin
    def get_client_token(self):
        return str(uuid.uuid4())

    @require_active_plugin
    def get_payment_config(self, previous_value):
        return [
            {"field": "client_token", "value": self.get_client_token()},
            {"field": "cod_fees", "value": self.config.connection_params["cod_fees"]},
            {
                "field": "supported_countries",
                "value": self.config.connection_params["supported_countries"],
            },
            {
                "field": "maximum_allowed_value",
                "value": self.config.connection_params["maximum_allowed_value"],
            },
        ]

    @require_active_plugin
    def token_is_required_as_payment_input(self, previous_value):
        return False

    @require_active_plugin
    def calculate_checkout_total(
        self,
        checkout_info: "CheckoutInfo",
        lines: Iterable["CheckoutLineInfo"],
        address: Optional["Address"],
        discounts: Iterable[DiscountInfo],
        previous_value: TaxedMoney,
    ) -> TaxedMoney:
        checkout_total = previous_value

        if not _validate_checkout(checkout_info, lines):
            logger.debug("Checkout Invalid in Calculate Checkout Total")
            return checkout_total

        payment = checkout_info.checkout.get_last_active_payment()

        if not payment:
            return checkout_total

        payment_gateway = payment.gateway
        cod_fees_value = Decimal(self.config.connection_params["cod_fees"])

        if payment_gateway == "payments.cash" and cod_fees_value:
            checkout_total += Money(cod_fees_value, checkout_info.checkout.currency)
            return checkout_total
        else:
            return checkout_total
