from setuptools import setup

setup(
    name="cod-payment-gateway",
    version="0.1.0",
    packages=["cod"],
    package_dir={"cod": "cod"},
    description="COD integration",
    entry_points={
        "saleor.plugins": ["cod = cod.plugin:CashGatewayPlugin"],
    },
)
