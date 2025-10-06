#!/usr/bin/env python3
"""
Example usage script for the transcript processor
"""

import os
import sys
import json
from dataclasses import asdict
from transcript_processor import TranscriptProcessor

def main():
    # Example PDF path (you'll need to provide an actual PDF)
    pdf_path = "pdf/Transcript_Two_Student.pdf"
    #pdf_path = "pdf/JodwaySchool transcript.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"Error: Sample PDF not found at {pdf_path}")
        print("Please provide a valid transcript PDF file.")
        return 1
    
    try:
        # Initialize the processor
        processor = TranscriptProcessor()
        
        # Process the transcript
        print("Processing transcript...")
        transcript_data = processor.process_transcript(pdf_path)
        
        # Display results
        processor.display_results(transcript_data)
        
        # Generate standardized JSON output
        standardized_json = processor.generate_standardized_json(transcript_data, pdf_path)
        
        # Save standardized JSON
        output_file = "transcript_results_standardized.json"
        with open(output_file, 'w') as f:
            json.dump(standardized_json, f, indent=2, ensure_ascii=False)
        
        print(f"\nStandardized JSON results saved to: {output_file}")
        
        # Optionally save raw format for comparison
        raw_output_file = "transcript_results_raw.json"
        with open(raw_output_file, 'w') as f:
            json.dump(asdict(transcript_data), f, indent=2, default=str)
        
        print(f"Raw format results saved to: {raw_output_file}")
        
        # Show a preview of the standardized format
        print("\n" + "="*60)
        print("STANDARDIZED JSON FORMAT PREVIEW:")
        print("="*60)
        print("Keys in standardized output:")
        for key in standardized_json.keys():
            print(f"  - {key}")
            if isinstance(standardized_json[key], dict):
                for subkey in standardized_json[key].keys():
                    print(f"    - {subkey}")
        print("="*60)
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())