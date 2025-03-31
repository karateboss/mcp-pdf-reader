from dataclasses import dataclass
from typing import AsyncIterator
from mcp.server.fastmcp import FastMCP
import pymupdf
import os
from contextlib import asynccontextmanager

# Initialize the MCP server
mcp = FastMCP("PDF Reader", dependencies=["pymupdf"])

# Directory where PDFs are stored
PDF_DIRECTORY = os.getenv("PDF_DIRECTORY", "./pdfs")

@dataclass
class AppContext:
    """Application context for lifecycle management."""
    pdf_directory: str

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with type-safe context"""
    try:
        # Initialize PDF storage directory
        yield AppContext(pdf_directory=PDF_DIRECTORY)
    finally:
        pass  # No cleanup needed for now

# Pass lifespan to server
mcp = FastMCP("PDF Reader", lifespan=app_lifespan)

@mcp.tool()
def read_pdf(ctx, filename: str) -> str:
    """
    Reads and extracts text from a specified PDF file.
    :param ctx: FastMCP context
    :param filename: Name of the PDF file to read
    :return: Extracted text from the PDF
    """
    pdf_path = os.path.join(PDF_DIRECTORY, filename)

    if not os.path.exists(pdf_path):
        return f"Error: File '{filename}' not found."

    try:
        # Open and extract text from the PDF
        doc = pymupdf.open(pdf_path)
        text = "\n".join([page.get_text("text") for page in doc])
        return text if text else "No text found in the PDF."
    except Exception as e:
        return f"Error reading PDF: {str(e)}"


# Run the MCP server
if __name__ == "__main__":
    mcp.run()
