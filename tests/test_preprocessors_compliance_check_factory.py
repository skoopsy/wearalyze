from src.preprocessors.compliance_check_factory import ComplianceCheckFactory
from src.preprocessors.compliance_check_corsano_2872b import ComplianceCheckCorsano2872b
from src.preprocessors.compliance_check_polar_verity import ComplianceCheckPolarVerity

import pytest
from unittest.mock import patch, MagicMock


class TestComplianceCheckFactory:
    def test_get_check_method_corsano(self):
        checker = ComplianceCheckFactory.get_check_method("corsano-2872b")
        assert isinstance(checker, ComplianceCheckCorsano2872b)

    def test_get_check_method_polar(self):
        checker = ComplianceCheckFactory.get_check_method("polar-verity")
        assert isinstance(checker, ComplianceCheckPolarVerity)

    def test_get_check_method_unsupported_device(self):
        with pytest.raises(ValueError) as exc_info:
            ComplianceCheckFactory.get_check_method("unknown-device")
        assert "[ComplianceCheckFactory] Unsupported device: unknown-device" in str(exc_info.value)

    def test_get_check_method_case_sensitivity(self):
        with pytest.raises(ValueError) as exc_info:
            ComplianceCheckFactory.get_check_method("Polar-Verity")  # mismatched case
        assert "Unsupported device" in str(exc_info.value)
