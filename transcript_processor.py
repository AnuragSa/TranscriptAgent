"""
Transcript Processor - A Python script to extract and process academic transcript data from PDFs
using Microsoft Document Intelligence and Azure OpenAI services.

This script processes PDF transcripts from various educational institutions and attempts to
extract and map common transcript fields such as student information, courses, grades, etc.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

# Azure SDK imports (will be imported after installation)
try:
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.documentintelligence import DocumentIntelligenceClient
    from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
    from openai import AzureOpenAI
except ImportError:
    print("Azure SDKs not installed. Please install required dependencies.")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class Course:
    """Represents a single course entry in a transcript"""
    course_code: Optional[str] = None
    course_description: Optional[str] = None
    credits: Optional[str] = None
    credits_earned: Optional[str] = None
    grade: Optional[str] = None
    pass_fail: Optional[str] = None
    semester: Optional[str] = None
    year: Optional[str] = None


@dataclass
class StudentInfo:
    """Represents student information from a transcript"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    student_id: Optional[str] = None
    graduation_date: Optional[str] = None
    degree: Optional[str] = None
    major: Optional[str] = None
    gpa: Optional[str] = None
    school_name: Optional[str] = None


@dataclass
class TranscriptData:
    """Complete transcript data structure"""
    student_info: StudentInfo
    courses: List[Course]
    raw_text: str
    additional_info: Dict[str, Any]
    
    def to_standardized_json(self) -> Dict[str, Any]:
        """Convert to standardized JSON format that remains consistent across all transcripts"""
        return {
            "transcript_metadata": {
                "processing_timestamp": "",  # Will be filled at processing time
                "source_file": "",  # Will be filled at processing time
                "processing_version": "1.0",
                "total_courses": len(self.courses)
            },
            "student_information": {
                "personal_details": {
                    "first_name": self.student_info.first_name or "",
                    "last_name": self.student_info.last_name or "",
                    "full_name": f"{self.student_info.first_name or ''} {self.student_info.last_name or ''}".strip() or "",
                    "student_id": self.student_info.student_id or ""
                },
                "academic_details": {
                    "school_name": self.student_info.school_name or "",
                    "degree": self.student_info.degree or "",
                    "major": self.student_info.major or "",
                    "graduation_date": self.student_info.graduation_date or "",
                    "gpa": self.student_info.gpa or ""
                }
            },
            "academic_record": {
                "courses": [
                    {
                        "course_identification": {
                            "course_code": course.course_code or "",
                            "course_title": course.course_description or "",
                            "course_description": course.course_description or ""
                        },
                        "enrollment_details": {
                            "semester": course.semester or "",
                            "year": course.year or "",
                            "academic_period": f"{course.semester or ''} {course.year or ''}".strip() or ""
                        },
                        "credit_information": {
                            "credits_attempted": course.credits or "",
                            "credits_earned": course.credits_earned or "",
                            "credit_type": "standard"  # Could be "standard", "transfer", "audit", etc.
                        },
                        "grade_information": {
                            "letter_grade": course.grade or "",
                            "pass_fail_indicator": course.pass_fail or "",
                            "grade_points": "",  # Could be calculated if needed
                            "grade_status": "completed"  # Could be "completed", "in_progress", "withdrawn", etc.
                        }
                    }
                    for course in self.courses
                ],
                "summary_statistics": {
                    "total_credits_attempted": "",  # Will be calculated
                    "total_credits_earned": "",     # Will be calculated
                    "total_courses": len(self.courses),
                    "overall_gpa": self.student_info.gpa or ""
                }
            },
            "additional_information": {
                "honors_awards": [],
                "transfer_credits": [],
                "notes": [],
                "extracted_fields": self.additional_info
            },
            "raw_data": {
                "extracted_text": self.raw_text,
                "text_length": len(self.raw_text)
            }
        }


class TranscriptProcessor:
    """Main class for processing academic transcripts using Azure services"""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the transcript processor with configuration"""
        self.config = self._load_config(config_path)
        self.doc_intelligence_client = None
        self.openai_client = None
        self._initialize_clients()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found. Using environment variables.")
            return {
                "document_intelligence": {
                    "endpoint": os.getenv("DOC_INTELLIGENCE_ENDPOINT"),
                    "key": os.getenv("DOC_INTELLIGENCE_KEY")
                },
                "azure_openai": {
                    "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
                    "key": os.getenv("AZURE_OPENAI_KEY"),
                    "deployment_name": os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-35-turbo")
                }
            }
    
    def _initialize_clients(self):
        """Initialize Azure service clients"""
        try:
            # Initialize Document Intelligence client
            doc_endpoint = self.config["document_intelligence"]["endpoint"]
            doc_key = self.config["document_intelligence"]["key"]
            
            if doc_endpoint and doc_key:
                self.doc_intelligence_client = DocumentIntelligenceClient(
                    endpoint=doc_endpoint,
                    credential=AzureKeyCredential(doc_key)
                )
                logger.info("Document Intelligence client initialized successfully")
            
            # Initialize Azure OpenAI client
            openai_endpoint = self.config["azure_openai"]["endpoint"]
            openai_key = self.config["azure_openai"]["key"]
            
            if openai_endpoint and openai_key:
                self.openai_client = AzureOpenAI(
                    azure_endpoint=openai_endpoint,
                    api_key=openai_key,
                    api_version="2024-12-01-preview"
                )
                logger.info("Azure OpenAI client initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing clients: {e}")
            raise
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using Azure Document Intelligence"""
        logger.info(f"Processing PDF: {pdf_path}")
        
        if not self.doc_intelligence_client:
            raise ValueError("Document Intelligence client not initialized")
        
        try:
            with open(pdf_path, "rb") as f:
                pdf_content = f.read()
            
            # Analyze document using the layout model
            poller = self.doc_intelligence_client.begin_analyze_document(
                "prebuilt-layout",
                pdf_content,
                content_type="application/pdf"
            )
            
            result = poller.result()
            
            # Extract text content
            extracted_text = ""
            if result.content:
                extracted_text = result.content
            
            logger.info(f"Successfully extracted text from {pdf_path}")
            return extracted_text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    def map_to_transcript_fields(self, extracted_text: str) -> TranscriptData:
        """Map extracted text to predefined transcript fields using Azure OpenAI"""
        logger.info("Mapping extracted text to transcript fields")
        
        if not self.openai_client:
            logger.warning("Azure OpenAI client not available. Using basic text parsing.")
            return self._basic_text_parsing(extracted_text)
        
        # Create a prompt for the AI to extract structured data
        system_prompt = """You are an expert at extracting structured information from academic transcripts.
Given the raw text from a transcript, extract the following information in VALID JSON format.

IMPORTANT: Your response must be ONLY valid JSON with no additional text, explanations, or markdown formatting.

Extract this exact structure:
{
    "student_info": {
        "first_name": "string or null",
        "last_name": "string or null", 
        "student_id": "string or null",
        "graduation_date": "string or null",
        "degree": "string or null",
        "major": "string or null",
        "gpa": "string or null",
        "school_name": "string or null"
    },
    "courses": [
        {
            "course_code": "string or null",
            "course_description": "string or null",
            "credits": "string or null",
            "credits_earned": "string or null",
            "grade": "string or null",
            "pass_fail": "string or null",
            "semester": "string or null",
            "year": "string or null"
        }
    ],
    "additional_info": {
        "any_other_relevant_fields": "values"
    }
}

Rules:
- Only extract information that is clearly present in the text
- Use null for missing information (not empty strings)
- For courses, create separate entries for each course found
- Response must be valid JSON only - no explanations or formatting
- If no information is found, still return the structure with null values"""
        
        user_prompt = f"Extract structured data from this transcript text:\n\n{extracted_text}"
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.config["azure_openai"]["deployment_name"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=3000  # Ensure we don't get truncated responses
            )
            
            # Parse the JSON response
            ai_response = response.choices[0].message.content
            
            # Validate that we have a response
            if not ai_response or ai_response.strip() == "":
                raise ValueError("Empty response from AI")
            
            # Clean the response - sometimes AI includes markdown formatting
            ai_response = ai_response.strip()
            if ai_response.startswith("```json"):
                ai_response = ai_response[7:]  # Remove ```json
            if ai_response.endswith("```"):
                ai_response = ai_response[:-3]  # Remove closing ```
            ai_response = ai_response.strip()
            
            # Log the AI response for debugging
            logger.debug(f"AI response: {ai_response[:200]}...")
            
            # Try to parse JSON
            try:
                structured_data = json.loads(ai_response)
            except json.JSONDecodeError as json_error:
                logger.error(f"JSON parsing error: {json_error}")
                logger.error(f"AI response was: {ai_response[:500]}...")
                raise ValueError(f"Invalid JSON response from AI: {json_error}")
            
            # Validate the structure
            if not isinstance(structured_data, dict):
                raise ValueError("AI response is not a JSON object")
            
            # Convert to our data structures with null handling
            student_info_data = structured_data.get("student_info", {})
            # Convert null values to None for our dataclass
            student_info_data = {k: (v if v != "null" and v is not None else None) 
                                for k, v in student_info_data.items()}
            student_info = StudentInfo(**student_info_data)
            
            # Handle courses with null value conversion
            courses = []
            for course_data in structured_data.get("courses", []):
                # Convert null values to None for our dataclass
                clean_course_data = {k: (v if v != "null" and v is not None else None) 
                                   for k, v in course_data.items()}
                courses.append(Course(**clean_course_data))
            
            additional_info = structured_data.get("additional_info", {})
            
            transcript_data = TranscriptData(
                student_info=student_info,
                courses=courses,
                raw_text=extracted_text,
                additional_info=additional_info
            )
            
            logger.info("Successfully mapped text to transcript fields using AI")
            return transcript_data
            
        except Exception as e:
            logger.error(f"Error using AI for field mapping: {e}")
            logger.info("Falling back to basic text parsing")
            return self._basic_text_parsing(extracted_text)
    
    def _basic_text_parsing(self, text: str) -> TranscriptData:
        """Basic text parsing fallback when AI is not available"""
        logger.info("Using basic text parsing for field extraction")
        
        # Simple keyword-based extraction (basic implementation)
        student_info = StudentInfo()
        courses = []
        additional_info = {}
        
        # This is a very basic implementation - in practice, you'd want more sophisticated parsing
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for patterns that might indicate student information
            if any(keyword in line.lower() for keyword in ['name:', 'student name', 'student:']):
                # Try to extract name information
                parts = line.split()
                if len(parts) >= 2:
                    additional_info['potential_name_line'] = line
            
            # Look for patterns that might indicate courses
            if any(keyword in line.lower() for keyword in ['course', 'class', 'grade', 'credit']):
                additional_info.setdefault('potential_course_lines', []).append(line)
        
        return TranscriptData(
            student_info=student_info,
            courses=courses,
            raw_text=text,
            additional_info=additional_info
        )
    
    def _calculate_summary_statistics(self, transcript_data: TranscriptData) -> Dict[str, str]:
        """Calculate summary statistics for the transcript"""
        total_credits_attempted = 0
        total_credits_earned = 0
        
        for course in transcript_data.courses:
            try:
                if course.credits:
                    # Try to extract numeric value from credits string
                    credits_str = course.credits.replace(' ', '').replace('credits', '').replace('credit', '')
                    if credits_str.replace('.', '').isdigit():
                        total_credits_attempted += float(credits_str)
                
                if course.credits_earned:
                    # Try to extract numeric value from credits earned string
                    earned_str = course.credits_earned.replace(' ', '').replace('credits', '').replace('credit', '')
                    if earned_str.replace('.', '').isdigit():
                        total_credits_earned += float(earned_str)
            except (ValueError, AttributeError):
                # Skip courses with invalid credit information
                continue
        
        return {
            "total_credits_attempted": str(total_credits_attempted) if total_credits_attempted > 0 else "",
            "total_credits_earned": str(total_credits_earned) if total_credits_earned > 0 else ""
        }
    
    def process_transcript(self, pdf_path: str) -> TranscriptData:
        """Main method to process a transcript PDF"""
        logger.info(f"Starting transcript processing for: {pdf_path}")
        
        # Validate input file
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Extract text from PDF
        extracted_text = self.extract_text_from_pdf(pdf_path)
        
        # Map to structured fields
        transcript_data = self.map_to_transcript_fields(extracted_text)
        
        logger.info("Transcript processing completed successfully")
        return transcript_data
    
    def display_results(self, transcript_data: TranscriptData):
        """Display the extracted transcript data in a readable format"""
        print("\n" + "="*80)
        print("TRANSCRIPT PROCESSING RESULTS")
        print("="*80)
        
        # Display student information
        print("\nSTUDENT INFORMATION:")
        print("-" * 40)
        student_dict = asdict(transcript_data.student_info)
        for field, value in student_dict.items():
            if value:
                print(f"{field.replace('_', ' ').title()}: {value}")
        
        # Display courses
        print(f"\nCOURSES ({len(transcript_data.courses)} found):")
        print("-" * 40)
        if transcript_data.courses:
            for i, course in enumerate(transcript_data.courses, 1):
                print(f"\nCourse {i}:")
                course_dict = asdict(course)
                for field, value in course_dict.items():
                    if value:
                        print(f"  {field.replace('_', ' ').title()}: {value}")
        else:
            print("No courses extracted")
        
        # Display additional information
        if transcript_data.additional_info:
            print("\nADDITIONAL INFORMATION:")
            print("-" * 40)
            for key, value in transcript_data.additional_info.items():
                print(f"{key.replace('_', ' ').title()}: {value}")
        
        print("\n" + "="*80)
    
    def generate_standardized_json(self, transcript_data: TranscriptData, source_file: str) -> Dict[str, Any]:
        """Generate standardized JSON output with consistent format"""
        from datetime import datetime
        
        # Get the standardized structure
        standardized_data = transcript_data.to_standardized_json()
        
        # Calculate summary statistics
        summary_stats = self._calculate_summary_statistics(transcript_data)
        
        # Fill in metadata
        standardized_data["transcript_metadata"]["processing_timestamp"] = datetime.now().isoformat()
        standardized_data["transcript_metadata"]["source_file"] = os.path.basename(source_file)
        
        # Update summary statistics
        standardized_data["academic_record"]["summary_statistics"].update(summary_stats)
        
        return standardized_data


def main():
    """Main function to run the transcript processor"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Process academic transcript PDFs")
    parser.add_argument("pdf_path", help="Path to the PDF transcript file")
    parser.add_argument("--config", default="config.json", help="Path to configuration file")
    parser.add_argument("--output", help="Path to save JSON output (optional)")
    
    args = parser.parse_args()
    
    try:
        # Initialize processor
        processor = TranscriptProcessor(args.config)
        
        # Process transcript
        transcript_data = processor.process_transcript(args.pdf_path)
        
        # Display results
        processor.display_results(transcript_data)
        
        # Save to file if requested
        if args.output:
            # Generate standardized JSON format
            standardized_json = processor.generate_standardized_json(transcript_data, args.pdf_path)
            
            with open(args.output, 'w') as f:
                json.dump(standardized_json, f, indent=2, ensure_ascii=False)
            print(f"\nStandardized results saved to: {args.output}")
            
            # Also save raw format for comparison if needed
            if args.output.endswith('.json'):
                raw_output = args.output.replace('.json', '_raw.json')
                with open(raw_output, 'w') as f:
                    json.dump(asdict(transcript_data), f, indent=2, default=str)
                print(f"Raw format also saved to: {raw_output}")
    
    except Exception as e:
        logger.error(f"Error processing transcript: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())