# Transcript Agent

A Python script that processes academic transcript PDFs using Microsoft Document Intelligence and Azure OpenAI services to extract and map student information, courses, and grades to predefined fields.

## Features

- **PDF Text Extraction**: Uses Azure Document Intelligence to extract text from PDF transcripts
- **Intelligent Field Mapping**: Leverages Azure OpenAI to intelligently map extracted text to structured transcript fields
- **Standardized JSON Output**: Produces consistent JSON format that remains the same across all transcripts
- **Flexible Input**: Handles transcripts from various educational institutions with different formats
- **Structured Output**: Organizes extracted data into predefined fields for easy processing
- **Fallback Processing**: Includes basic text parsing when AI services are unavailable

## Predefined Fields

The script extracts and maps the following information with clear distinction between required and optional fields:

### Student Information

#### Required Fields:
- **Student Name**: Full name of the student
- **Date of Birth**: Student's date of birth  
- **School Name**: Name of the educational institution

#### Optional Fields:
- **School Address**: Physical address of the school (extracted if available)
- Student ID
- Graduation Date
- Degree
- Major
- GPA

### Course Information (Repeated for ALL terms and courses)

#### Required Fields:
- **Course Code**: Course identifier/number
- **Course Name**: Full course title/name
- **Course Credits**: Number of credits for the course
- **Course Grade**: Grade received (letter grade, percentage, etc.)
- **Date Completed**: When the course was completed

#### Optional Fields:
- **Course Hours**: Course hours (if supplied)
- **Term**: Academic term/semester information

## Prerequisites

1. **Azure Document Intelligence Service**
   - Create a Document Intelligence resource in Azure
   - Note the endpoint and key

2. **Azure OpenAI Service** (optional but recommended)
   - Create an Azure OpenAI resource
   - Deploy a GPT model (e.g., gpt-35-turbo)
   - Note the endpoint, key, and deployment name

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

You can configure the script in two ways:

### Option 1: Configuration File
1. Copy `config.json.template` to `config.json`
2. Fill in your Azure service credentials:
   ```json
   {
     "document_intelligence": {
       "endpoint": "https://your-doc-intelligence-resource.cognitiveservices.azure.com/",
       "key": "your-document-intelligence-key"
     },
     "azure_openai": {
       "endpoint": "https://your-openai-resource.openai.azure.com/",
       "key": "your-azure-openai-key",
       "deployment_name": "gpt-35-turbo"
     }
   }
   ```

### Option 2: Environment Variables
1. Copy `.env.template` to `.env`
2. Fill in your Azure service credentials:
   ```
   DOC_INTELLIGENCE_ENDPOINT=https://your-doc-intelligence-resource.cognitiveservices.azure.com/
   DOC_INTELLIGENCE_KEY=your-document-intelligence-key
   AZURE_OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com/
   AZURE_OPENAI_KEY=your-azure-openai-key
   AZURE_OPENAI_DEPLOYMENT=gpt-35-turbo
   ```

## Usage

### Basic Usage
```bash
python transcript_processor.py path/to/transcript.pdf
```

### With Custom Configuration
```bash
python transcript_processor.py path/to/transcript.pdf --config custom_config.json
```

### Save Output to JSON
```bash
python transcript_processor.py path/to/transcript.pdf --output results.json
```

## Standardized JSON Output Format

The script produces a consistent JSON format that remains the same regardless of the source transcript. This ensures easy integration with downstream systems and databases.

### JSON Structure:

```json
{
  "transcript_metadata": {
    "processing_timestamp": "ISO datetime",
    "source_file": "filename.pdf", 
    "processing_version": "1.0",
    "total_courses": 4
  },
  "student_information": {
    "personal_details": {
      "first_name": "string",
      "last_name": "string",
      "full_name": "string", 
      "student_id": "string"
    },
    "academic_details": {
      "school_name": "string",
      "degree": "string",
      "major": "string",
      "graduation_date": "string",
      "gpa": "string"
    }
  },
  "academic_record": {
    "courses": [
      {
        "course_identification": {
          "course_code": "string",
          "course_title": "string",
          "course_description": "string"
        },
        "enrollment_details": {
          "semester": "string",
          "year": "string", 
          "academic_period": "string"
        },
        "credit_information": {
          "credits_attempted": "string",
          "credits_earned": "string",
          "credit_type": "standard"
        },
        "grade_information": {
          "letter_grade": "string",
          "pass_fail_indicator": "string",
          "grade_points": "string",
          "grade_status": "completed"
        }
      }
    ],
    "summary_statistics": {
      "total_credits_attempted": "string",
      "total_credits_earned": "string", 
      "total_courses": 4,
      "overall_gpa": "string"
    }
  },
  "additional_information": {
    "honors_awards": [],
    "transfer_credits": [],
    "notes": [],
    "extracted_fields": {}
  },
  "raw_data": {
    "extracted_text": "string",
    "text_length": 1250
  }
}
```

### Key Benefits:
- **Consistent Structure**: Same JSON keys and hierarchy for all transcripts
- **Empty Field Handling**: Missing data is represented as empty strings, not null
- **Calculated Fields**: Automatic computation of totals and derived values
- **Metadata Tracking**: Processing timestamp and source file information
- **Raw Data Preservation**: Original extracted text is preserved for reference

### Command Line Options
- `pdf_path`: Path to the PDF transcript file (required)
- `--config`: Path to configuration file (default: config.json)
- `--output`: Path to save JSON output (optional)

## Example Output

```
================================================================================
TRANSCRIPT PROCESSING RESULTS
================================================================================

STUDENT INFORMATION:
----------------------------------------
First Name: John
Last Name: Doe
Student Id: 123456789
Graduation Date: May 2023
Degree: Bachelor of Science
Major: Computer Science
Gpa: 3.75
School Name: University of Example

COURSES (3 found):
----------------------------------------

Course 1:
  Course Code: CS101
  Course Description: Introduction to Computer Science
  Credits: 3
  Credits Earned: 3
  Grade: A
  Semester: Fall
  Year: 2019

Course 2:
  Course Code: MATH201
  Course Description: Calculus II
  Credits: 4
  Credits Earned: 4
  Grade: B+
  Semester: Spring
  Year: 2020

Course 3:
  Course Code: CS301
  Course Description: Data Structures and Algorithms
  Credits: 3
  Credits Earned: 3
  Grade: A-
  Semester: Fall
  Year: 2021

================================================================================
```

## How It Works

1. **PDF Processing**: The script uses Azure Document Intelligence to extract text from the input PDF transcript
2. **Text Analysis**: The extracted text is sent to Azure OpenAI with a specialized prompt to identify and extract structured information
3. **Field Mapping**: The AI response is parsed and mapped to predefined transcript fields
4. **Output Generation**: Results are displayed in a readable format and optionally saved as JSON

## Error Handling

- **Missing Azure Services**: If Azure OpenAI is not available, the script falls back to basic text parsing
- **Invalid PDF**: The script validates input files and provides clear error messages
- **API Errors**: Network and API errors are caught and logged with helpful messages

## Limitations

- The accuracy of extraction depends on the quality and format of the input PDF
- Some transcript formats may require manual adjustment of the AI prompt
- Very complex or non-standard transcript layouts may not be fully processed

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License.