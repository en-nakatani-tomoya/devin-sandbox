"""
Mock implementation of the OpenAI interface.
This can be replaced with the actual OpenAI API implementation later.
"""

import time
import random


class OpenAIMock:
    """
    Mock implementation of the OpenAI interface.
    This class simulates the behavior of the OpenAI API for development
    purposes.
    """

    def __init__(self):
        """Initialize the mock OpenAI interface."""
        self.templates = [
            "Based on our investigation of '{query}', we found the following results:\n\n"
            "1. The primary factors involved are related to economic and environmental "
            "considerations.\n"
            "2. Recent studies suggest that this area requires further research.\n"
            "3. Experts recommend a cautious approach to this topic.",
            
            "Investigation results for '{query}':\n\n"
            "Our analysis indicates several key findings:\n"
            "- This is a complex issue with multiple stakeholders involved\n"
            "- Historical data shows a pattern of increasing interest in this area\n"
            "- Future developments will likely depend on regulatory changes",
            
            "Report on '{query}':\n\n"
            "The investigation has concluded with these insights:\n"
            "* There are significant opportunities for innovation in this space\n"
            "* Challenges remain in terms of implementation and adoption\n"
            "* A strategic approach is recommended for addressing these issues",
        ]

    def generate_report(self, query: str) -> str:
        """
        Generate a mock report based on the query.

        Args:
            query: The investigation query string

        Returns:
            A mock report as a string
        """
        time.sleep(1)

        template = random.choice(self.templates)
        report = template.format(query=query)

        return report
