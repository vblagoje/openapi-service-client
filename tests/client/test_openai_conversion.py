from openapi_service_client.schema_converter.openai import OpenAISchemaConverter
from openapi_service_client.spec import OpenAPISpecification


class TestOpenAPISchemaConversion:

    def test_serperdev(self, test_files_path):
        spec = OpenAPISpecification.from_file(test_files_path / "serper.yaml")
        converter = OpenAISchemaConverter()
        functions = converter.convert(spec)
        assert functions
        assert len(functions) == 1
        function = functions[0]
        assert function["name"] == "search"
        assert function["description"] == "Search the web with Google"
        assert function["parameters"] == {"type": "object", "properties": {"q": {"type": "string"}}, "required": ["q"]}

    def test_github(self, test_files_path):
        spec = OpenAPISpecification.from_file(test_files_path / "github_compare.yml")
        converter = OpenAISchemaConverter()
        functions = converter.convert(spec)
        assert functions
        assert len(functions) == 1
        function = functions[0]
        assert function["name"] == "compare_branches"
        assert function["description"] == "Compares two branches against one another."
        assert function["parameters"] == {
            "type": "object",
            "properties": {
                "basehead": {
                    "type": "string",
                    "description": "The base branch and head branch to compare. "
                    "This parameter expects the format `BASE...HEAD`",
                },
                "owner": {"type": "string", "description": "The repository owner, usually a company or orgnization"},
                "repo": {"type": "string", "description": "The repository itself, the project"},
            },
            "required": ["basehead", "owner", "repo"],
        }

    def test_complex_types(self, test_files_path):
        spec = OpenAPISpecification.from_file(test_files_path / "complex_types_openapi_service.json")
        converter = OpenAISchemaConverter()
        functions = converter.convert(spec)
        assert functions
        assert len(functions) == 1
        function = functions[0]
        assert function["name"] == "processPayment"
        assert function["description"] == "Process a new payment using the specified payment method"
        assert function["parameters"] == {
            "type": "object",
            "properties": {
                "transaction_amount": {"type": "number", "description": "The amount to be paid"},
                "description": {"type": "string", "description": "A brief description of the payment"},
                "payment_method_id": {"type": "string", "description": "The payment method to be used"},
                "payer": {
                    "type": "object",
                    "description": "Information about the payer, including their name, email, "
                    "and identification number",
                    "properties": {
                        "name": {"type": "string", "description": "The payer's name"},
                        "email": {"type": "string", "description": "The payer's email address"},
                        "identification": {
                            "type": "object",
                            "description": "The payer's identification number",
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "description": "The type of identification document (e.g., CPF, CNPJ)",
                                },
                                "number": {"type": "string", "description": "The identification number"},
                            },
                            "required": ["type", "number"],
                        },
                    },
                    "required": ["name", "email", "identification"],
                },
            },
            "required": ["transaction_amount", "description", "payment_method_id", "payer"],
        }