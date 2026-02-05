"""File reader utilities for various input formats."""

import re
from pathlib import Path


class FileReader:
    """Read content from various file formats."""

    SUPPORTED_EXTENSIONS = {".txt", ".srt", ".md", ".pdf"}

    def read(self, file_path: str | Path) -> str:
        """Read content from a file.

        Args:
            file_path: Path to the file to read.

        Returns:
            The file content as a string.

        Raises:
            ValueError: If the file format is not supported.
            FileNotFoundError: If the file doesn't exist.
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        extension = path.suffix.lower()

        if extension == ".txt" or extension == ".md":
            return self._read_text(path)
        elif extension == ".srt":
            return self._read_srt(path)
        elif extension == ".pdf":
            return self._read_pdf(path)
        else:
            raise ValueError(
                f"Unsupported file format: {extension}. "
                f"Supported formats: {', '.join(self.SUPPORTED_EXTENSIONS)}"
            )

    def _read_text(self, path: Path) -> str:
        """Read plain text file."""
        return path.read_text(encoding="utf-8")

    def _read_srt(self, path: Path) -> str:
        """Read SRT subtitle file and extract text content."""
        content = path.read_text(encoding="utf-8")

        # Remove SRT formatting (timestamps, sequence numbers)
        lines = content.split("\n")
        text_lines = []

        for line in lines:
            line = line.strip()
            # Skip empty lines, sequence numbers, and timestamps
            if not line:
                continue
            if line.isdigit():
                continue
            if re.match(r"\d{2}:\d{2}:\d{2}", line):
                continue

            # Remove HTML tags that may be in subtitles
            line = re.sub(r"<[^>]+>", "", line)
            text_lines.append(line)

        return " ".join(text_lines)

    def _read_pdf(self, path: Path) -> str:
        """Read PDF file and extract text content."""
        try:
            import pypdf
        except ImportError:
            raise ImportError(
                "pypdf is required for PDF support. Install it with: pip install pypdf"
            )

        reader = pypdf.PdfReader(str(path))
        text_parts = []

        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)

        return "\n\n".join(text_parts)

    def read_multiple(self, file_paths: list[str | Path]) -> str:
        """Read and concatenate content from multiple files.

        Args:
            file_paths: List of file paths to read.

        Returns:
            Combined content from all files.
        """
        contents = []
        for path in file_paths:
            contents.append(self.read(path))
        return "\n\n---\n\n".join(contents)
