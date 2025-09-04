import pytest
from neonpay.core import NeonPayCore, PaymentStage, PaymentResult
from neonpay.errors import PaymentValidationError
from neonpay.adapters.base import PaymentAdapter


class MockAdapter(PaymentAdapter):
    def __init__(self):
        self.sent_invoices = []
        self.should_fail = False

    async def send_invoice(self, chat_id: int, stage: PaymentStage) -> bool:
        if self.should_fail:
            return False
        self.sent_invoices.append((chat_id, stage))
        return True

    async def handle_payment(self, payment_data: dict) -> PaymentResult:
        return PaymentResult(
            success=not self.should_fail,
            payment_id="test_payment_123",
            amount=payment_data.get("amount", 100),
            currency="XTR",
            user_id=payment_data.get("user_id", 12345),
            stage_id=payment_data.get("stage_id", "test_stage"),
        )


@pytest.fixture
def mock_adapter():
    return MockAdapter()


@pytest.fixture
def neon_pay(mock_adapter):
    return NeonPayCore(mock_adapter)


class TestPaymentStage:
    def test_payment_stage_creation(self):
        stage = PaymentStage(
            stage_id="test_stage",
            title="Test Product",
            description="Test Description",
            amount=100,
            currency="XTR",
        )
        assert stage.stage_id == "test_stage"
        assert stage.title == "Test Product"
        assert stage.amount == 100
        assert stage.currency == "XTR"

    def test_payment_stage_with_logo(self):
        stage = PaymentStage(
            stage_id="test_stage",
            title="Test Product",
            description="Test Description",
            amount=100,
            currency="XTR",
            logo_url="https://example.com/logo.png",
        )
        assert stage.logo_url == "https://example.com/logo.png"


class TestPaymentResult:
    def test_payment_result_success(self):
        result = PaymentResult(
            success=True,
            payment_id="pay_123",
            amount=100,
            currency="XTR",
            user_id=12345,
            stage_id="test_stage",
        )
        assert result.success is True
        assert result.payment_id == "pay_123"
        assert result.amount == 100

    def test_payment_result_failure(self):
        result = PaymentResult(
            success=False,
            error_message="Payment failed",
            user_id=12345,
            stage_id="test_stage",
        )
        assert result.success is False
        assert result.error_message == "Payment failed"


class TestNeonPayCore:
    def test_core_initialization(self, mock_adapter):
        core = NeonPayCore(mock_adapter)
        assert core.adapter == mock_adapter
        assert len(core.stages) == 0

    def test_create_stage(self, neon_pay):
        stage = neon_pay.create_stage(
            stage_id="test_stage",
            title="Test Product",
            description="Test Description",
            amount=100,
        )
        assert stage.stage_id == "test_stage"
        assert "test_stage" in neon_pay.stages

    def test_create_duplicate_stage_raises_error(self, neon_pay):
        neon_pay.create_stage("test_stage", "Test", "Description", 100)
        with pytest.raises(PaymentValidationError):
            neon_pay.create_stage("test_stage", "Test2", "Description2", 200)

    @pytest.mark.asyncio
    async def test_send_payment_request_success(self, neon_pay, mock_adapter):
        stage = neon_pay.create_stage("test_stage", "Test", "Description", 100)
        result = await neon_pay.send_payment_request(12345, "test_stage")
        assert result is True
        assert len(mock_adapter.sent_invoices) == 1
        assert mock_adapter.sent_invoices[0][0] == 12345
        assert mock_adapter.sent_invoices[0][1] == stage

    @pytest.mark.asyncio
    async def test_send_payment_request_nonexistent_stage(self, neon_pay):
        with pytest.raises(PaymentValidationError):
            await neon_pay.send_payment_request(12345, "nonexistent_stage")

    @pytest.mark.asyncio
    async def test_send_payment_request_adapter_failure(self, neon_pay, mock_adapter):
        neon_pay.create_stage("test_stage", "Test", "Description", 100)
        mock_adapter.should_fail = True
        result = await neon_pay.send_payment_request(12345, "test_stage")
        assert result is False

    @pytest.mark.asyncio
    async def test_process_payment_success(self, neon_pay, mock_adapter):
        neon_pay.create_stage("test_stage", "Test", "Description", 100)
        payment_data = {"user_id": 12345, "stage_id": "test_stage", "amount": 100}
        result = await neon_pay.process_payment(payment_data)
        assert result.success is True
        assert result.payment_id == "test_payment_123"
        assert result.amount == 100

    @pytest.mark.asyncio
    async def test_process_payment_failure(self, neon_pay, mock_adapter):
        neon_pay.create_stage("test_stage", "Test", "Description", 100)
        mock_adapter.should_fail = True
        payment_data = {"user_id": 12345, "stage_id": "test_stage", "amount": 100}
        result = await neon_pay.process_payment(payment_data)
        assert result.success is False

    def test_get_stage(self, neon_pay):
        stage = neon_pay.create_stage("test_stage", "Test", "Description", 100)
        retrieved_stage = neon_pay.get_stage("test_stage")
        assert retrieved_stage == stage

    def test_get_nonexistent_stage_returns_none(self, neon_pay):
        result = neon_pay.get_stage("nonexistent")
        assert result is None

    def test_list_stages(self, neon_pay):
        neon_pay.create_stage("stage1", "Test1", "Description1", 100)
        neon_pay.create_stage("stage2", "Test2", "Description2", 200)
        stages = neon_pay.list_stages()
        assert len(stages) == 2
        assert "stage1" in stages
        assert "stage2" in stages
