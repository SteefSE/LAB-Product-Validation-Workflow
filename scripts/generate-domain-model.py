#!/usr/bin/env python3
"""
LAB Product Validation Workflow - Domain Model Generator
FIXED VERSION - Compatible with Mendix 10.18.1 and Workflow Commons 3.12.1
"""

import os
import sys
import yaml
import argparse
from pathlib import Path
from datetime import datetime

def load_config(config_path):
    """Load configuration from YAML file with proper error handling"""
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"❌ Configuration file not found: {config_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"❌ Error parsing YAML config: {e}")
        sys.exit(1)

def generate_entity_xml(entity_name, attributes, generalization=None):
    """Generate XML for a single entity compatible with Mendix 10.18.1"""
    
    generalization_xml = ""
    if generalization:
        generalization_xml = f'<generalization>System.{generalization}</generalization>'
    
    attributes_xml = ""
    for attr in attributes:
        attr_type = attr['type']
        attr_name = attr['name']
        attr_desc = attr.get('description', f'{attr_name} attribute')
        
        # Map attribute types to Mendix XML format
        type_mapping = {
            'String': 'String',
            'Integer': 'Integer',  
            'Boolean': 'Boolean',
            'DateTime': 'DateTime',
            'Decimal': 'Decimal',
            'Enum': 'Enumeration'
        }
        
        mendix_type = type_mapping.get(attr_type, 'String')
        
        if mendix_type == 'String':
            attributes_xml += f"""
        <attribute name="{attr_name}" type="{mendix_type}">
            <documentation>{attr_desc}</documentation>
            <value></value>
        </attribute>"""
        elif mendix_type == 'Enumeration':
            enum_name = attr.get('enum_name', f'{attr_name}Enum')
            attributes_xml += f"""
        <attribute name="{attr_name}" type="{mendix_type}">
            <documentation>{attr_desc}</documentation>
            <enumeration>{enum_name}</enumeration>
        </attribute>"""
        else:
            attributes_xml += f"""
        <attribute name="{attr_name}" type="{mendix_type}">
            <documentation>{attr_desc}</documentation>
        </attribute>"""
    
    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<entity xmlns="http://www.mendix.com/metamodel/Domain/7.0.0" 
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
        name="{entity_name}">
    <documentation>LAB Workflow Entity: {entity_name} - Generated for Mendix 10.18.1</documentation>
    {generalization_xml}
    <attributes>{attributes_xml}
    </attributes>
    <associations></associations>
    <indexes></indexes>
    <rules></rules>
    <eventHandlers></eventHandlers>
</entity>"""
    
    return xml_content

def generate_enumeration_xml(enum_name, values):
    """Generate XML for enumeration compatible with Mendix 10.18.1"""
    
    values_xml = ""
    for value in values:
        values_xml += f"""
        <value name="{value['name']}">
            <caption defaultValue="{value['caption']}"/>
        </value>"""
    
    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<enumeration xmlns="http://www.mendix.com/metamodel/Domain/7.0.0" 
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
             name="{enum_name}">
    <documentation>LAB Workflow Enumeration: {enum_name}</documentation>
    <values>{values_xml}
    </values>
</enumeration>"""
    
    return xml_content

def main():
    parser = argparse.ArgumentParser(description="Generate LAB Workflow Domain Model")
    parser.add_argument("--config", required=True, help="Path to configuration file")
    parser.add_argument("--output", default="output", help="Output directory")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Create output directories
    output_dir = Path(args.output)
    domain_dir = output_dir / "domain-model"
    enum_dir = output_dir / "enumerations"
    
    domain_dir.mkdir(parents=True, exist_ok=True)
    enum_dir.mkdir(parents=True, exist_ok=True)
    
    print("🏗️ Generating LAB Workflow Domain Model...")
    print(f"📁 Output directory: {output_dir}")
    
    # Generate entities compatible with Mendix 10.18.1
    entities = [
        {
            "name": "ProductValidation",
            "attributes": [
                {"name": "ProductID", "type": "String", "description": "Unique product identifier"},
                {"name": "ProductName", "type": "String", "description": "Product description"},
                {"name": "BatchNumber", "type": "String", "description": "Production batch number"},
                {"name": "ValidationDate", "type": "DateTime", "description": "Validation start date"},
                {"name": "Status", "type": "Enum", "enum_name": "ValidationStatus", "description": "Current validation status"},
                {"name": "Priority", "type": "Enum", "enum_name": "Priority", "description": "Validation priority level"},
                {"name": "WorkflowOutcome", "type": "Boolean", "description": "TRUE/FALSE workflow result"},
                {"name": "CompletionDate", "type": "DateTime", "description": "Validation completion date"},
                {"name": "RejectionReason", "type": "String", "description": "Reason for rejection if failed"},
                {"name": "CreatedBy", "type": "String", "description": "User who initiated validation"}
            ]
        },
        {
            "name": "ImageAcquisition", 
            "attributes": [
                {"name": "AcquisitionID", "type": "String", "description": "Unique acquisition identifier"},
                {"name": "ImagePath", "type": "String", "description": "Path to stored image file"},
                {"name": "AcquisitionDate", "type": "DateTime", "description": "When image was captured"},
                {"name": "TechnicianID", "type": "String", "description": "Technician performing acquisition"},
                {"name": "ImageQuality", "type": "Enum", "enum_name": "ImageQuality", "description": "Quality assessment result"},
                {"name": "Resolution", "type": "String", "description": "Image resolution specification"},
                {"name": "ColorDepth", "type": "Integer", "description": "Color depth in bits"},
                {"name": "FileSize", "type": "Decimal", "description": "Image file size in MB"},
                {"name": "CaptureSettings", "type": "String", "description": "Camera/equipment settings used"}
            ]
        },
        {
            "name": "ImageQualityValidation",
            "attributes": [
                {"name": "ValidationID", "type": "String", "description": "Unique validation identifier"},
                {"name": "QualityScore", "type": "Decimal", "description": "Numerical quality score"},
                {"name": "QualityThreshold", "type": "Decimal", "description": "Minimum acceptable quality"},
                {"name": "ValidationResult", "type": "Boolean", "description": "Pass/fail validation result"},
                {"name": "ValidatedBy", "type": "String", "description": "User performing validation"},
                {"name": "ValidationDate", "type": "DateTime", "description": "When validation was performed"},
                {"name": "QualityMetrics", "type": "String", "description": "Detailed quality measurements"},
                {"name": "Comments", "type": "String", "description": "Additional validation comments"}
            ]
        },
        {
            "name": "DetailedImageAcquisition",
            "attributes": [
                {"name": "DetailedID", "type": "String", "description": "Unique detailed acquisition ID"},
                {"name": "EnhancedImagePath", "type": "String", "description": "Path to enhanced image"},
                {"name": "ProcessingDate", "type": "DateTime", "description": "When detailed processing occurred"},
                {"name": "TechnicianID", "type": "String", "description": "Technician performing detailed work"},
                {"name": "EnhancementType", "type": "Enum", "enum_name": "EnhancementType", "description": "Type of enhancement applied"},
                {"name": "ProcessingDuration", "type": "Integer", "description": "Processing time in minutes"},
                {"name": "SpecializedEquipment", "type": "String", "description": "Equipment used for enhancement"},
                {"name": "QualityImprovement", "type": "Decimal", "description": "Quality improvement percentage"}
            ]
        },
        {
            "name": "ImageAnalysis",
            "attributes": [
                {"name": "AnalysisID", "type": "String", "description": "Unique analysis identifier"},
                {"name": "AnalysisDate", "type": "DateTime", "description": "When analysis was performed"},
                {"name": "ProcessedBy", "type": "String", "description": "User performing analysis"},
                {"name": "AnalysisType", "type": "Enum", "enum_name": "AnalysisType", "description": "Type of analysis performed"},
                {"name": "AnalysisResults", "type": "String", "description": "Detailed analysis findings"},
                {"name": "ConfidenceLevel", "type": "Decimal", "description": "Analysis confidence percentage"},
                {"name": "ProcessingAlgorithm", "type": "String", "description": "Algorithm used for analysis"},
                {"name": "AnalysisDuration", "type": "Integer", "description": "Analysis time in minutes"}
            ]
        },
        {
            "name": "KPIExtraction",
            "attributes": [
                {"name": "ExtractionID", "type": "String", "description": "Unique extraction identifier"},
                {"name": "ExtractedBy", "type": "String", "description": "User performing extraction"},
                {"name": "ExtractionDate", "type": "DateTime", "description": "When KPIs were extracted"},
                {"name": "KPIValues", "type": "String", "description": "JSON formatted KPI values"},
                {"name": "ExtractionMethod", "type": "Enum", "enum_name": "ExtractionMethod", "description": "Method used for extraction"},
                {"name": "DataAccuracy", "type": "Decimal", "description": "Extraction accuracy percentage"},
                {"name": "ValidationStatus", "type": "Enum", "enum_name": "ValidationStatus", "description": "KPI validation status"}
            ]
        },
        {
            "name": "ValidationResult",
            "attributes": [
                {"name": "ResultID", "type": "String", "description": "Unique result identifier"},
                {"name": "FinalOutcome", "type": "Boolean", "description": "Final TRUE/FALSE outcome"},
                {"name": "ResultDate", "type": "DateTime", "description": "When result was determined"},
                {"name": "ApprovedBy", "type": "String", "description": "User approving final result"},
                {"name": "ApprovalLevel", "type": "Enum", "enum_name": "ApprovalLevel", "description": "Level of approval required"},
                {"name": "ResultSummary", "type": "String", "description": "Summary of validation findings"},
                {"name": "RecommendedActions", "type": "String", "description": "Recommended follow-up actions"}
            ]
        },
        {
            "name": "ValidationReport",
            "attributes": [
                {"name": "ReportID", "type": "String", "description": "Unique report identifier"},
                {"name": "GeneratedDate", "type": "DateTime", "description": "Report generation date"},
                {"name": "GeneratedBy", "type": "String", "description": "User generating report"},
                {"name": "ReportFormat", "type": "Enum", "enum_name": "ReportFormat", "description": "Report output format"},
                {"name": "ReportContent", "type": "String", "description": "Complete report content"},
                {"name": "DistributionList", "type": "String", "description": "Report distribution recipients"},
                {"name": "DigitalSignature", "type": "String", "description": "Digital signature for authenticity"}
            ]
        },
        {
            "name": "WorkflowAuditTrail",
            "attributes": [
                {"name": "AuditID", "type": "String", "description": "Unique audit entry identifier"},
                {"name": "EventTimestamp", "type": "DateTime", "description": "When event occurred"},
                {"name": "PerformedBy", "type": "String", "description": "User performing action"},
                {"name": "ActionType", "type": "Enum", "enum_name": "AuditActionType", "description": "Type of action performed"},
                {"name": "EntityAffected", "type": "String", "description": "Entity that was modified"},
                {"name": "OldValue", "type": "String", "description": "Previous value before change"},
                {"name": "NewValue", "type": "String", "description": "New value after change"},
                {"name": "ChangeReason", "type": "String", "description": "Reason for the change"}
            ]
        }
    ]
    
    # Generate entity XML files
    for entity in entities:
        xml_content = generate_entity_xml(
            entity["name"], 
            entity["attributes"], 
            entity.get("generalization")
        )
        
        entity_file = domain_dir / f"{entity['name']}.xml"
        with open(entity_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        print(f"✅ Generated entity: {entity['name']}.xml")
    
    # Generate enumerations
    enumerations = [
        {
            "name": "ValidationStatus",
            "values": [
                {"name": "Pending", "caption": "Pending"},
                {"name": "InProgress", "caption": "In Progress"},
                {"name": "Approved", "caption": "Approved"},
                {"name": "Rejected", "caption": "Rejected"},
                {"name": "OnHold", "caption": "On Hold"},
                {"name": "Completed", "caption": "Completed"}
            ]
        },
        {
            "name": "Priority",
            "values": [
                {"name": "Low", "caption": "Low"},
                {"name": "Medium", "caption": "Medium"},
                {"name": "High", "caption": "High"},
                {"name": "Critical", "caption": "Critical"}
            ]
        },
        {
            "name": "ImageQuality",
            "values": [
                {"name": "Poor", "caption": "Poor"},
                {"name": "Fair", "caption": "Fair"},
                {"name": "Good", "caption": "Good"},
                {"name": "Excellent", "caption": "Excellent"},
                {"name": "Outstanding", "caption": "Outstanding"}
            ]
        },
        {
            "name": "WorkflowStage",
            "values": [
                {"name": "ImageAcquisition", "caption": "Image Acquisition"},
                {"name": "QualityValidation", "caption": "Quality Validation"},
                {"name": "DetailedAcquisition", "caption": "Detailed Acquisition"},
                {"name": "Analysis", "caption": "Analysis"},
                {"name": "KPIExtraction", "caption": "KPI Extraction"},
                {"name": "LABValidation", "caption": "LAB Validation"},
                {"name": "ReportGeneration", "caption": "Report Generation"}
            ]
        },
        {
            "name": "ApprovalLevel",
            "values": [
                {"name": "Technician", "caption": "Technician"},
                {"name": "Supervisor", "caption": "Supervisor"},
                {"name": "Manager", "caption": "Manager"},
                {"name": "Director", "caption": "Director"}
            ]
        },
        {
            "name": "EnhancementType",
            "values": [
                {"name": "ColorCorrection", "caption": "Color Correction"},
                {"name": "NoiseReduction", "caption": "Noise Reduction"},
                {"name": "SharpnessEnhancement", "caption": "Sharpness Enhancement"},
                {"name": "ContrastAdjustment", "caption": "Contrast Adjustment"}
            ]
        },
        {
            "name": "AnalysisType",
            "values": [
                {"name": "Dimensional", "caption": "Dimensional Analysis"},
                {"name": "ColorAnalysis", "caption": "Color Analysis"},
                {"name": "TextureAnalysis", "caption": "Texture Analysis"},
                {"name": "DefectDetection", "caption": "Defect Detection"}
            ]
        },
        {
            "name": "ExtractionMethod",
            "values": [
                {"name": "Automated", "caption": "Automated"},
                {"name": "SemiAutomated", "caption": "Semi-Automated"},
                {"name": "Manual", "caption": "Manual"}
            ]
        },
        {
            "name": "ReportFormat",
            "values": [
                {"name": "PDF", "caption": "PDF"},
                {"name": "Excel", "caption": "Excel"},
                {"name": "Word", "caption": "Word"},
                {"name": "HTML", "caption": "HTML"}
            ]
        },
        {
            "name": "AuditActionType",
            "values": [
                {"name": "Created", "caption": "Created"},
                {"name": "Modified", "caption": "Modified"},
                {"name": "Deleted", "caption": "Deleted"},
                {"name": "Approved", "caption": "Approved"},
                {"name": "Rejected", "caption": "Rejected"}
            ]
        }
    ]
    
    # Generate enumeration XML files
    for enum in enumerations:
        xml_content = generate_enumeration_xml(enum["name"], enum["values"])
        
        enum_file = enum_dir / f"{enum['name']}.xml"
        with open(enum_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        print(f"✅ Generated enumeration: {enum['name']}.xml")
    
    print(f"\n🎉 Domain model generation completed!")
    print(f"📊 Generated {len(entities)} entities and {len(enumerations)} enumerations")
    print(f"📁 Files saved to: {output_dir}")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)