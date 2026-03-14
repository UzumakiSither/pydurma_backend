from Pydurma.serializers.plain_text import PlainTextSerializer
from Pydurma.serializers.csv import CSVSerializer

from pydurma_app.enums.output_type import OutputType


def get_serializer(output_type, weighted_matrix):

    serializers = {
        OutputType.TEXT: PlainTextSerializer,
        OutputType.CSV: CSVSerializer,
        # OutputType.DOCX: DocxSerializer,
        # OutputType.HFML: HFMLSerializer,
        # OutputType.MD: MdSerializer,
    }

    serializer_class = serializers.get(output_type)

    if serializer_class is None:
        raise ValueError("Unsupported output type")
    
    """if output_type in (OutputType.MD, OutputType.DOCX):
        return serializer_class(
            weighted_matrix,
            "",
            "",
            [],
            {},
        )"""

    return serializer_class(weighted_matrix, "", "")
