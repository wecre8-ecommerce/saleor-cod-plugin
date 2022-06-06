def authorize(
    payment_information, config
):
    """Perform authorize transaction."""
    from saleor.payment import TransactionKind
    from saleor.payment.interface import GatewayResponse

    return GatewayResponse(
        error=None,
        is_success=True,
        action_required=False,
        kind=TransactionKind.AUTH,
        amount=payment_information.amount,
        currency=payment_information.currency,
        transaction_id=str(payment_information.token),
    )


def void(payment_information, config):
    """Perform void transaction."""
    from saleor.payment import TransactionKind
    from saleor.payment.interface import GatewayResponse

    return GatewayResponse(
        error=None,
        is_success=True,
        action_required=False,
        kind=TransactionKind.VOID,
        amount=payment_information.amount,
        currency=payment_information.currency,
        transaction_id=str(payment_information.token),
    )


def capture(payment_information, config):
    """Perform capture transaction."""
    from saleor.payment import TransactionKind
    from saleor.payment.interface import GatewayResponse

    return GatewayResponse(
        error=None,
        is_success=True,
        action_required=False,
        kind=TransactionKind.CAPTURE,
        amount=payment_information.amount,
        currency=payment_information.currency,
        transaction_id=str(payment_information.token),
    )


def confirm(payment_information, config):
    """Perform confirm transaction."""
    from saleor.payment import TransactionKind
    from saleor.payment.interface import GatewayResponse

    return GatewayResponse(
        error=None,
        is_success=True,
        action_required=False,
        kind=TransactionKind.CAPTURE,
        amount=payment_information.amount,
        currency=str(payment_information.currency),
        transaction_id=str(payment_information.token),
    )


def refund(payment_information, config):
    from saleor.payment import TransactionKind
    from saleor.payment.interface import GatewayResponse

    return GatewayResponse(
        error=None,
        is_success=True,
        action_required=False,
        kind=TransactionKind.REFUND,
        amount=payment_information.amount,
        currency=payment_information.currency,
        transaction_id=str(payment_information.token),
    )


def process_payment(
    payment_information, config
):
    """Process the payment."""
    return authorize(payment_information, config)
