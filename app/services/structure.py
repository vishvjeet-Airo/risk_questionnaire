import json
import re
from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field
# from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from langchain_core.output_parsers import PydanticOutputParser, OutputFixingParser
from dotenv import load_dotenv
from app.core.clients.bedrock import bedrock_client

load_dotenv()


class ExcelParserV3:
    """
    Advanced Excel parser that analyzes table text and generates detailed response instructions
    for LLM-based question answering. Focuses on creating comprehensive instructions that specify
    exactly where and how responses should be filled at cell, row, column, and header levels.
    """
    
    def __init__(self):
        self.bedrock_client = bedrock_client
    
    def analyze_table_and_generate_instructions(self, table_text: str, sheet_name: str = "Sheet1") -> Dict[str, Any]:
        """
        Main method that analyzes table text and generates simple question-response instruction pairs.
        
        Args:
            table_text: Raw table text extracted from Excel
            sheet_name: Name of the Excel sheet
            
        Returns:
            Dictionary containing questions with their cell locations and detailed response instructions
        """
        
        # Define strict schema for JSON output
        class FollowUpQuestion(BaseModel):
            question_text: str = Field(..., description="Follow-up question text")
            cell_location: str = Field(..., description="Cell location for the follow-up answer, e.g., D24")
            response_instruction: str = Field(..., description="Detailed instructions for answering the follow-up")
            follow_up_questions: List['FollowUpQuestion'] = Field(default_factory=list, description="Nested follow-up questions, if any")

        class Question(BaseModel):
            question_text: str
            cell_location: str
            response_instruction: str
            follow_up_questions: List[FollowUpQuestion] = Field(default_factory=list)

        class QuestionsResponse(BaseModel):
            questions: List[Question]

        # Resolve forward references for recursive model
        FollowUpQuestion.update_forward_refs()

        parser = PydanticOutputParser(pydantic_object=QuestionsResponse)
        format_instructions = parser.get_format_instructions()

        system_message = """You are an expert Excel analyzer that extracts questions and creates detailed response instructions for LLM-based question answering.

Your task is to analyze the provided Excel table text and extract:
1. All questions with their exact cell locations (e.g., "D23", "B15")
2. Comprehensive response instructions for each question that include everything needed to answer it properly
3. Any follow-up questions that logically belong to a main question. Group these under the parent question.

For each question, provide:
- The exact cell reference where the answer should be filled
- The type of response needed (Yes/No, text, options, etc.)
- All available options if it's a choice question
- Any validation rules or constraints
- Format requirements
- Any special instructions
 - A list of follow-up questions (if any) and values are basically a dictionary  containing the same structure as a question: question_text, cell_location, response_instruction

IMPORTANT: Return ONLY valid JSON. Do not include any text before or after the JSON. Start your response with { and end with }.

OUTPUT FORMAT (return ONLY JSON matching this schema; follow-up questions may be nested recursively):
{
  "questions": [
    {
      "question_text": "The actual question text",
      "cell_location": "D23",
      "response_instruction": "Detailed instruction explaining exactly how to answer this question, what format to use, what options are available, validation rules, etc. This should be comprehensive enough for another LLM to answer the question correctly.",
      "follow_up_questions": [
        {
          "question_text": "Follow-up question text",
          "cell_location": "D24",
          "response_instruction": "Detailed instruction for the follow-up",
          "follow_up_questions": [
            {
              "question_text": "Nested follow-up question text",
              "cell_location": "D25",
              "response_instruction": "Instruction for nested follow-up"
            }
          ]
        },
         {
          "question_text": "...",
          "cell_location": "...",
          "response_instruction": "..."
        }
      ]
    }
  ]
}

Make the response_instruction field very detailed and self-sufficient - it should contain everything another LLM needs to know to answer that specific question correctly."""

        prompt = f"""Analyze the following Excel table text and extract questions with their cell locations and response instructions:

SHEET: {sheet_name}

TABLE TEXT:
{table_text}

Extract all questions from this table and for each question:
1. Identify the exact cell location where the answer should be filled (e.g., "D23", "B15")
2. Create a comprehensive response instruction that includes:
   - What type of response is needed (Yes/No, text, choice, etc.)
   - All available options if it's a choice question
   - Format requirements (dates, numbers, text length, etc.)
   - Validation rules
   - Any special instructions or constraints
   - Cell ranges if it's a table question
3. Detect any follow-up questions. Include them under the parent in a field named "follow_up_questions" as a list of dictionaries with the same structure as a question (and they may themselves include nested "follow_up_questions"). Each entry contains: question_text, cell_location, response_instruction, and optionally follow_up_questions.

Make each response_instruction detailed and self-sufficient so another LLM can answer the question correctly.

Return ONLY valid JSON that matches these format instructions:
{format_instructions}
"""

        # Use Bedrock client with tracing
        raw_output = self.bedrock_client.invoke_with_tracing(
            prompt=prompt,
            system_message=system_message
        )
        
        # Get cost estimate
        cost_estimate = self.bedrock_client.get_cost_estimate(prompt, raw_output)
        print(f"📊 Excel V3 analysis cost: ${cost_estimate['total_cost_usd']:.6f}")
        print(f"   Tokens - Input: {cost_estimate['input_tokens']:.0f}, Output: {cost_estimate['output_tokens']:.0f}")
        
        # Clean minimal (remove code fences/reasoning), then rely solely on OutputFixingParser
        cleaned_output = self._clean_llm_output(raw_output)
        
        fixing_parser = OutputFixingParser.from_llm(parser=parser, llm=self.bedrock_client.client)
        
        try:
            structured = fixing_parser.parse(cleaned_output)
            return structured.dict()
        except Exception as e1:
            print(f"❌ FixingParser initial parse failed: {e1}")
            # One repair retry with explicit error + format instructions
            try:
                repair_system = "You repair invalid JSON to match the given Pydantic schema. Return ONLY the corrected JSON."
                repair_prompt = (
                    "The following output failed to parse as JSON according to the schema.\n"
                    f"Output:\n{cleaned_output}\n\n"
                    f"Error:\n{e1}\n\n"
                    f"Return corrected JSON that strictly matches these format instructions:\n{format_instructions}"
                )
                repaired_output = self.bedrock_client.invoke_with_tracing(
                    prompt=repair_prompt,
                    system_message=repair_system
                )
                repaired_clean = self._clean_llm_output(repaired_output)
                structured_repaired = fixing_parser.parse(repaired_clean)
                return structured_repaired.dict()
            except Exception as e2:
                print(f"❌ Repair retry failed: {e2}")
                return {"error": "Failed to parse JSON", "raw_output": cleaned_output}
        
    def create_simple_guide(self, analysis_result: Dict[str, Any]) -> str:
        """
        Create a simple guide showing questions with their cell locations and response instructions.
        
        Args:
            analysis_result: The analysis result from analyze_table_and_generate_instructions
            
        Returns:
            Simple guide as a string
        """
        
        guide = []
        guide.append("# EXCEL QUESTIONS AND RESPONSE INSTRUCTIONS")
        guide.append("=" * 60)
        guide.append("")
        
        # Check if we have an error and try to extract from raw output
        if "error" in analysis_result and "raw_output" in analysis_result:
            guide.append("## Note: JSON parsing failed, showing raw output")
            guide.append("")
            guide.append(analysis_result["raw_output"])
            return "\n".join(guide)
        
        questions = analysis_result.get("questions", [])
        if questions:
            for i, question in enumerate(questions, 1):
                question_text = question.get("question_text", "Unknown question")
                cell_location = question.get("cell_location", "Unknown")
                response_instruction = question.get("response_instruction", "No instructions provided")
                follow_ups = question.get("follow_up_questions", {})
                
                guide.append(f"## {i}. Question")
                guide.append(f"**Question:** {question_text}")
                guide.append(f"**Cell Location:** {cell_location}")
                guide.append("")
                guide.append("**Response Instruction:**")
                guide.append(response_instruction)
                guide.append("")
                # Render follow-up questions recursively (support dict or list)
                def render_followups_recursive(items, indent_level: int = 0):
                    indent = "  " * indent_level
                    if isinstance(items, dict):
                        iterable = items.items()
                    else:
                        iterable = enumerate(items, 1)
                    for key, fu in iterable:
                        fu_q = fu.get("question_text", "Unknown follow-up question")
                        fu_loc = fu.get("cell_location", "Unknown")
                        fu_instr = fu.get("response_instruction", "No instructions provided")
                        guide.append(f"{indent}- {key}:")
                        guide.append(f"{indent}  - Question: {fu_q}")
                        guide.append(f"{indent}  - Cell Location: {fu_loc}")
                        guide.append(f"{indent}  - Instruction: {fu_instr}")
                        nested = fu.get("follow_up_questions")
                        if nested:
                            guide.append(f"{indent}  - Follow-ups:")
                            render_followups_recursive(nested, indent_level + 2)
                        guide.append("")

                if follow_ups:
                    guide.append("**Follow-up Questions:**")
                    render_followups_recursive(follow_ups, 0)
                guide.append("-" * 60)
                guide.append("")
        else:
            guide.append("No questions found in the analysis result.")
        
        return "\n".join(guide)
    
    def _clean_llm_output(self, raw_output: str) -> str:
        """Clean and format the LLM output."""
        # Remove code fences if present
        cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", raw_output.strip())
        cleaned = re.sub(r"\n?```$", "", cleaned).strip()
        
        # Remove reasoning blocks if present
        reasoning_pattern = r'<reasoning>.*?</reasoning>'
        cleaned = re.sub(reasoning_pattern, '', cleaned, flags=re.DOTALL)
        
        # Clean up any extra whitespace
        cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)
        
        return cleaned.strip()