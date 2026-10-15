import ast
from typing import Optional, Tuple
from app.schemas.analysis import SyntaxErrorInfo
from app.core.config import settings


class SafeASTParser:
    """Safely parses Python source code into an AST without execution."""

    @staticmethod
    def parse_code(code: str) -> Tuple[Optional[ast.AST], Optional[SyntaxErrorInfo]]:
        # Size limit check
        if len(code.encode("utf-8")) > settings.MAX_CODE_LENGTH_BYTES:
            return None, SyntaxErrorInfo(
                line=1,
                column=1,
                message=f"Source code exceeds maximum allowed size ({settings.MAX_CODE_LENGTH_BYTES} bytes).",
                snippet=code[:100] + "..."
            )

        line_count = len(code.splitlines())
        if line_count > settings.MAX_CODE_LINES:
            return None, SyntaxErrorInfo(
                line=1,
                column=1,
                message=f"Source code exceeds maximum allowed line count ({settings.MAX_CODE_LINES} lines).",
                snippet=f"{line_count} lines"
            )

        try:
            tree = ast.parse(code)
            return tree, None
        except SyntaxError as e:
            # Extract line snippet safely
            snippet = None
            lines = code.splitlines()
            if e.lineno and 1 <= e.lineno <= len(lines):
                snippet = lines[e.lineno - 1]

            return None, SyntaxErrorInfo(
                line=e.lineno or 1,
                column=e.offset or 1,
                message=str(e.msg) if hasattr(e, 'msg') and e.msg else str(e),
                snippet=snippet
            )
        except Exception as e:
            return None, SyntaxErrorInfo(
                line=1,
                column=1,
                message=f"Failed to parse source: {str(e)}",
                snippet=None
            )
