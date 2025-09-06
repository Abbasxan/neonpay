import pytest

from neonpay.adapters.base import PaymentAdapter
from neonpay.core import NeonPayCore, PaymentResult, PaymentStage, PaymentStatus


class MockAdapter(PaymentAdapter):
    def __init__(self):
        self.sent_invoices = []
        self.should_fail = False

    async def send_invoice(self, user_id: int, stage: PaymentStage) -> bool:
        if self.should_fail:
            return False
        self.sent_invoices.append((user_id, stage))
        return True

    async def setup_handlers(self, payment_callback) -> None:
        pass

    def get_library_info(self) -> dict:
        return {"name": "MockAdapter", "version": "1.0.0"}


@pytest.fixture
def mock_adapter():
    return MockAdapter()


@pytest.fixture
def neon_pay(mock_adapter):
    return NeonPayCore(mock_adapter)


class TestPaymentStage:
    def test_payment_stage_creation(self):
        stage = PaymentStage(
            title="Test Product",
            description="Test Description",
            price=100,
        )
        assert stage.title == "Test Product"
        assert stage.price == 100

    def test_payment_stage_with_logo(self):
        stage = PaymentStage(
            title="Test Product",
            description="Test Description",
            price=100,
            photo_url="https://example.com/logo.png",
        )
        assert stage.photo_url == "https://example.com/logo.png"


class TestPaymentResult:
    def test_payment_result_success(self):
        result = PaymentResult(
            user_id=12345,
            amount=100,
            transaction_id="pay_123",
        )
        assert result.user_id == 12345
        assert result.amount == 100
        assert result.transaction_id == "pay_123"
        assert result.status == PaymentStatus.COMPLETED

    def test_payment_result_failure(self):
        result = PaymentResult(
            user_id=12345,
            amount=100,
            status=PaymentStatus.FAILED,
        )
        assert result.user_id == 12345
        assert result.amount == 100
        assert result.status == PaymentStatus.FAILED


class TestNeonPayCore:
    def test_core_initialization(self, mock_adapter):
        core = NeonPayCore(mock_adapter)
        assert core.adapter == mock_adapter
        assert len(core.list_payment_stages()) == 0

    def test_create_stage(self, neon_pay):
        stage = PaymentStage(
            title="Test Product",
            description="Test Description",
            price=100,
        )
        neon_pay.create_payment_stage("test_stage", stage)
        assert "test_stage" in neon_pay.list_payment_stages()

    def test_create_duplicate_stage_raises_error(self, neon_pay):
        stage1 = PaymentStage(title="Test", description="Description", price=100)
        stage2 = PaymentStage(title="Test2", description="Description2", price=200)
        neon_pay.create_payment_stage("test_stage", stage1)
        with pytest.raises(ValueError):
            neon_pay.create_payment_stage("test_stage", stage2)

    @pytest.mark.asyncio
    async def test_send_payment_request_success(self, neon_pay, mock_adapter):
        stage = PaymentStage(title="Test", description="Description", price=100)
        neon_pay.create_payment_stage("test_stage", stage)
        result = await neon_pay.send_payment(12345, "test_stage")
        assert result is True
        assert len(mock_adapter.sent_invoices) == 1
        assert mock_adapter.sent_invoices[0][0] == 12345
        assert mock_adapter.sent_invoices[0][1] == stage

    @pytest.mark.asyncio
    async def test_send_payment_request_nonexistent_stage(self, neon_pay):
        result = await neon_pay.send_payment(12345, "nonexistent_stage")
        assert result is False

    @pytest.mark.asyncio
    async def test_send_payment_request_adapter_failure(self, neon_pay, mock_adapter):
        stage = PaymentStage(title="Test", description="Description", price=100)
        neon_pay.create_payment_stage("test_stage", stage)
        mock_adapter.should_fail = True
        result = await neon_pay.send_payment(12345, "test_stage")
        assert result is False

    @pytest.mark.asyncio
    async def test_process_payment_success(self, neon_pay, mock_adapter):
        stage = PaymentStage(title="Test", description="Description", price=100)
        neon_pay.create_payment_stage("test_stage", stage)
        result = await neon_pay.send_payment(12345, "test_stage")
        assert result is True

    @pytest.mark.asyncio
    async def test_process_payment_failure(self, neon_pay, mock_adapter):
        stage = PaymentStage(title="Test", description="Description", price=100)
        neon_pay.create_payment_stage("test_stage", stage)
        mock_adapter.should_fail = True
        result = await neon_pay.send_payment(12345, "test_stage")
        assert result is False

    def test_get_stage(self, neon_pay):
        stage = PaymentStage(title="Test", description="Description", price=100)
        neon_pay.create_payment_stage("test_stage", stage)
        retrieved_stage = neon_pay.get_payment_stage("test_stage")
        assert retrieved_stage == stage

    def test_get_nonexistent_stage_returns_none(self, neon_pay):
        result = neon_pay.get_payment_stage("nonexistent")
        assert result is None

    def test_list_stages(self, neon_pay):
        stage1 = PaymentStage(title="Test1", description="Description1", price=100)
        stage2 = PaymentStage(title="Test2", description="Description2", price=200)
        neon_pay.create_payment_stage("stage1", stage1)
        neon_pay.create_payment_stage("stage2", stage2)
        stages = neon_pay.list_payment_stages()
        assert len(stages) == 2
        assert "stage1" in stages
        assert "stage2" in stages
