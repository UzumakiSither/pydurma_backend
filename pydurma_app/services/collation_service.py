"""
Pydurma collation integration.

This module wraps the Pydurma collation pipeline and returns:
- `result_text`: a plain-text critical edition output
- `weighted_matrix`: JSON-serializable representation of the weighted matrix
"""

from Pydurma.encoder import Encoder
from Pydurma.normalizer import Normalizer
from Pydurma.gen.tokenizer_gen import GenericTokenizer
from Pydurma.aligners.fdmp import FDMPaligner
from Pydurma.weighers.matrix_weigher import TokenMatrixWeigher
from Pydurma.weighers.token_weigher_count import TokenCountWeigher
from Pydurma.serializers.plain_text import PlainTextSerializer


encoder = Encoder()
normalizer = Normalizer()
tokenizer = GenericTokenizer(encoder, normalizer)
aligner = FDMPaligner()
token_matrix_weigher = TokenMatrixWeigher()
token_matrix_weigher.add_weigher(TokenCountWeigher(), weigher_weight=1)


class CollationProcessingError(Exception):
    """Raised when collation fails; may include partial outputs."""

    def __init__(self, message: str, *, weighted_matrix=None, result_text=None):
        super().__init__(message)
        self.weighted_matrix = weighted_matrix
        self.result_text = result_text


def collate_texts(texts: list[str]):
    """
    Collate multiple text witnesses into a single merged text.
    Returns (result_text, weighted_matrix_as_list).
    """
    weighted_matrix = None
    weighted_matrix_serializable = None
    result = None

    try:
        # Tokenize all witnesses
        tokenized = [tokenizer.tokenize(t) for t in texts]

        token_lists = [t[0] for t in tokenized]
        token_strings = [t[1] for t in tokenized]

        # Align tokens
        token_matrix = aligner.get_alignment_matrix(token_strings, token_lists)

        # Compute weights
        weighted_matrix = token_matrix_weigher.get_weight_matrix(token_matrix)

        # Convert matrix to JSON-serializable structure (e.g. list-of-lists)
        try:
            import numpy as np  # type: ignore

            if isinstance(weighted_matrix, np.ndarray):
                weighted_matrix_serializable = weighted_matrix.tolist()
            else:
                weighted_matrix_serializable = weighted_matrix
        except Exception:
            weighted_matrix_serializable = weighted_matrix

        # Serialize to plain text (no file writing needed)
        serializer = PlainTextSerializer(weighted_matrix, "", "")

        result = serializer.serialize_matrix()

        return result, weighted_matrix_serializable
    except Exception as e:
        raise CollationProcessingError(
            str(e),
            weighted_matrix=weighted_matrix_serializable,
            result_text=result,
        ) from e