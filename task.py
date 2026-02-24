from crewai import Task

from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from tools import read_data_tool, analyze_investment_tool, create_risk_assessment_tool

verification = Task(
    description="Read the file located at: {file_path} using your tools. Verify whether the provided document is indeed a valid financial report.",
    expected_output="A confirmation statement indicating whether the document contains valid, readable financial data, and its general category.",
    agent=verifier,
    tools=[read_data_tool],
    async_execution=False
)

analyze_financial_document = Task(
    description="Analyze the verified financial document located at {file_path} to answer the user's query: {query}. "
                "Extract key financial metrics, revenues, profit margins, and summarize the overall financial health.",
    expected_output="A detailed summary of the financial document, including key metrics, trends, and an overall health assessment based strictly on the extracted facts.",
    agent=financial_analyst,
    tools=[read_data_tool],
    async_execution=False,
)

investment_analysis = Task(
    description="Based on the financial analysis previously conducted, provide sound investment recommendations considering the query: {query}. "
                "Highlight any solid opportunities or areas to avoid.",
    expected_output="An actionable investment advisory report outlining potential opportunities and strategies, supported by data from the financial document.",
    agent=investment_advisor,
    tools=[analyze_investment_tool],
    async_execution=False,
)

risk_assessment = Task(
    description="Assess the financial and market risks related to the extracted financial data and the user's query: {query}. "
                "Provide a clear picture of potential downsides.",
    expected_output="A comprehensive risk assessment report detailing potential vulnerabilities, market risks, and risk mitigation strategies.",
    agent=risk_assessor,
    tools=[create_risk_assessment_tool],
    async_execution=False,
)