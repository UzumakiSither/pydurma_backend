"""
Pydurma collation integration.

This module wraps the Pydurma collation pipeline and returns:
- `result`: serialized text critical edition output based on output type
- `weighted_matrix`: JSON-serializable representation of the weighted matrix
"""
from Pydurma.encoder import Encoder
from Pydurma.normalizer import Normalizer
from Pydurma.gen.tokenizer_gen import GenericTokenizer
from Pydurma.aligners.fdmp import FDMPaligner
from Pydurma.weighers.matrix_weigher import TokenMatrixWeigher
from Pydurma.weighers.token_weigher_count import TokenCountWeigher
from pydurma_app.enums.output_type import OutputType
from pydurma_app.services.serializer_factory import get_serializer


encoder = Encoder()
normalizer = Normalizer()
tokenizer = GenericTokenizer(encoder, normalizer)
aligner = FDMPaligner()
token_matrix_weigher = TokenMatrixWeigher()
token_matrix_weigher.add_weigher(TokenCountWeigher(), weigher_weight=1)


class CollationProcessingError(Exception):
    """Raised when collation fails; may include partial outputs."""

    def __init__(self, message: str, *, weighted_matrix=None, result=None):
        super().__init__(message)
        self.weighted_matrix = weighted_matrix
        self.result = result


def compute_weighted_matrix(texts: list[str]):
    """
    Tokenize, align, and compute weight matrix.
    """
    weighted_matrix = None

    try:
        tokenized = [tokenizer.tokenize(t) for t in texts]

        token_lists = [t[0] for t in tokenized]
        token_strings = [t[1] for t in tokenized]

        token_matrix = aligner.get_alignment_matrix(token_strings, token_lists)

        weighted_matrix = token_matrix_weigher.get_weight_matrix(token_matrix)

        return weighted_matrix

    except Exception as e:
        raise CollationProcessingError(str(e), weighted_matrix=weighted_matrix) from e


def collate_texts(texts: list[str], output_type: OutputType):
    """
    Collate multiple text witnesses into a single merged text.
    Returns (result, weighted_matrix).
    """
    weighted_matrix = compute_weighted_matrix(texts)
    result = None

    try:
        serializer = get_serializer(output_type, weighted_matrix)

        result = serializer.serialize_matrix()

        return result, weighted_matrix
    except Exception as e:
        raise CollationProcessingError(
            str(e),
            weighted_matrix=weighted_matrix,
            result=result,
        ) from e
