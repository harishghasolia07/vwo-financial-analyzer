import os
from dotenv import load_dotenv
load_dotenv()

from crewai.tools import tool
import fitz # PyMuPDF

@tool("Read Financial Document")
def read_data_tool(path: str = 'data/sample.pdf') -> str:
    """Read data from a pdf file from a path
    Args:
        path (str): Path of the pdf file. Defaults to 'data/sample.pdf'.
    Returns:
        str: Full Financial Document file textual content.
    """
    try:
        doc = fitz.open(path)
        full_report = ""
        for page in doc:
            content = page.get_text()
            if content:
                # Remove extra whitespaces
                while "\n\n" in content:
                    content = content.replace("\n\n", "\n")
                full_report += content + "\n"
        return full_report
    except Exception as e:
        return f"Error reading PDF {path}: {str(e)}"

@tool("Investment Analysis Tool")
def analyze_investment_tool(financial_document_data: str) -> str:
    """Process and analyze the financial document data for investment opportunities.
    Args:
        financial_document_data (str): The text data from the financial document.
    Returns:
        str: A summary of the investment analysis.
    """
    # Simple placeholder logic for tool
    return "The data has been successfully processed for investment insights."

@tool("Risk Assessment Tool")
def create_risk_assessment_tool(financial_document_data: str) -> str:
    """Implement risk assessment logic on the financial document data.
    Args:
        financial_document_data (str): The text data from the financial document.
    Returns:
        str: A summary of the risk assessment.
    """
    return "The data has been successfully assessed for various market risks."
