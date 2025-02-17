from typing import Optional
from unittest.mock import Mock

import pytest

from pandasai.dataframe.base import DataFrame
from pandasai.helpers.logger import Logger
from pandasai.llm.fake import FakeLLM
from pandasai.pipelines.chat.result_parsing import ResultParsing
from pandasai.pipelines.pipeline_context import PipelineContext


class TestResultParsing:
    "Unit test for Result Parsing"

    throw_exception = True

    @pytest.fixture
    def llm(self, output: Optional[str] = None):
        return FakeLLM(output=output)

    @pytest.fixture
    def sample_df(self):
        return DataFrame(
            {
                "country": [
                    "United States",
                    "United Kingdom",
                    "France",
                    "Germany",
                    "Italy",
                    "Spain",
                    "Canada",
                    "Australia",
                    "Japan",
                    "China",
                ],
                "gdp": [
                    19294482071552,
                    2891615567872,
                    2411255037952,
                    3435817336832,
                    1745433788416,
                    1181205135360,
                    1607402389504,
                    1490967855104,
                    4380756541440,
                    14631844184064,
                ],
                "happiness_index": [
                    6.94,
                    7.16,
                    6.66,
                    7.07,
                    6.38,
                    6.4,
                    7.23,
                    7.22,
                    5.87,
                    5.12,
                ],
            }
        )

    @pytest.fixture
    def config(self, llm):
        return {"llm": llm, "enable_cache": True}

    @pytest.fixture
    def context(self, sample_df, config):
        return PipelineContext([sample_df], config)

    @pytest.fixture
    def logger(self):
        return Logger(True, False)

    def test_init(self, context, config):
        # Test the initialization of the CodeExecution
        result_parsing = ResultParsing()
        assert isinstance(result_parsing, ResultParsing)

    def test_result_parsing_successful_with_no_exceptions(self, context, logger):
        # Test Flow : Code Execution Successful with no exceptions
        result_parsing = ResultParsing()
        result_parsing._add_result_to_memory = Mock()
        mock_response_parser = Mock()

        def mock_intermediate_values(key: str):
            if key == "response_parser":
                return mock_response_parser

        context.get = Mock(side_effect=mock_intermediate_values)

        result = result_parsing.execute(
            input={"type": "string", "value": "Test Result"},
            context=context,
            logger=logger,
        )

        assert isinstance(result_parsing, ResultParsing)
        assert result.output == "Test Result"
        assert result.success is True
        assert result.message == "Results parsed successfully"
        assert result.metadata is None

    def test_result_parsing_unsuccessful_with_exceptions(self, context, logger):
        # Test Flow : Code Execution Unsuccessful with exceptions
        result_parsing = ResultParsing()
        result_parsing._add_result_to_memory = Mock()
        mock_response_parser = Mock()

        def mock_result_parsing(*args, **kwargs):
            raise Exception("Unit test exception")

        def mock_intermediate_values(key: str):
            if key == "response_parser":
                return mock_response_parser

        context.get = Mock(side_effect=mock_intermediate_values)

        result = None
        try:
            result = result_parsing.execute(
                input="Test Result", context=context, logger=logger
            )
        except Exception:
            assert result is None
        assert isinstance(result_parsing, ResultParsing)

    def test_add_number_result_to_memory(self, context):
        result_parsing = ResultParsing()
        result_parsing.execute(input={"type": "number", "value": 42}, context=context)
        assert context.memory.last()["message"] == "42"
