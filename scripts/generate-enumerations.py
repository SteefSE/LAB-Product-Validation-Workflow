#!/usr/bin/env python3
"""
LAB Product Validation Workflow - Enumerations Generator
Generates complete enumerations for workflow stages, statuses, and outcomes
"""

import yaml
import xml.etree.ElementTree as ET
from pathlib import Path
import argparse
import sys
from datetime import datetime

def load_config(config_path):
    """Load configuration from YAML file with fallback"""
    try:
        # Try the specified path first
        if Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        
        # Try alternative paths
        alternative_paths = [
            Path("config/lab-workflow-config.yaml"),
            Path("config/domain-model-config.yaml"),
            Path("../config/lab-workflow-config.yaml")
        ]
        
        for alt_path in alternative_paths:
            if alt_path.exists():
                print(f"📁 Using configuration from: {alt_path}")
                with open(alt_path, 'r', encoding='utf-8') as file:
                    return yaml.safe_load(file)
        
        # If no config found, provide default enumerations
        print("⚠️ No configuration file found, using default enumerations")
        return get_default_enumerations_config()
        
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return None

def get_default_enumerations_config():
    """Return default enumerations configuration"""
    return {
        'enumerations': [
            {
                'name': 'WorkflowStage',
                'description': 'Stages in the LAB product validation workflow',
                'values': [
                    {'name': 'ImageAcquisition', 'caption': 'Image Acquisition', 'description': 'Initial image capture phase'},
                    {'name': 'QualityValidation', 'caption': 'Quality Validation', 'description': 'Critical quality assessment phase'},
                    {'name': 'DetailedAcquisition', 'caption': 'Detailed Acquisition', 'description': 'Enhanced image processing phase'},
                    {'name': 'Analysis', 'caption': 'Analysis', 'description': 'Automated image analysis phase'},
                    {'name': 'KPIExtraction', 'caption': 'KPI Extraction', 'description': 'Performance indicators extraction phase'},
                    {'name': 'LABValidation', 'caption': 'LAB Validation', 'description': 'Final human validation phase'},
                    {'name': 'ReportGeneration', 'caption': 'Report Generation', 'description': 'Comprehensive report creation phase'},
                    {'name': 'Completed', 'caption': 'Completed', 'description': 'Workflow successfully completed'}
                ]
            },
            {
                'name': 'ProcessingStatus',
                'description': 'Status of image processing and analysis tasks',
                'values': [
                    {'name': 'Pending', 'caption': 'Pending', 'description': 'Task is waiting to be processed'},
                    {'name': 'InProgress', 'caption': 'In Progress', 'description': 'Task is currently being processed'},
                    {'name': 'Completed', 'caption': 'Completed', 'description': 'Task has been successfully completed'},
                    {'name': 'Failed', 'caption': 'Failed', 'description': 'Task processing has failed'},
                    {'name': 'RequiresReview', 'caption': 'Requires Review', 'description': 'Task needs manual review'},
                    {'name': 'Cancelled', 'caption': 'Cancelled', 'description': 'Task has been cancelled'}
                ]
            },
            {
                'name': 'ValidationOutcome',
                'description': 'Final validation decision outcomes',
                'values': [
                    {'name': 'Approved', 'caption': 'Approved', 'description': 'Validation passed - product approved'},
                    {'name': 'Rejected', 'caption': 'Rejected', 'description': 'Validation failed - product rejected'},
                    {'name': 'Pending', 'caption': 'Pending', 'description': 'Validation decision is pending'},
                    {'name': 'RequiresRework', 'caption': 'Requires Rework', 'description': 'Product needs additional work'},
                    {'name': 'ConditionalApproval', 'caption': 'Conditional Approval', 'description': 'Approved with conditions'},
                    {'name': 'Escalated', 'caption': 'Escalated', 'description': 'Decision escalated to higher authority'}
                ]
            },
            {
                'name': 'ReportFormat',
                'description': 'Available formats for validation reports',
                'values': [
                    {'name': 'PDF', 'caption': 'PDF', 'description': 'Portable Document Format'},
                    {'name': 'HTML', 'caption': 'HTML', 'description': 'Web page format'},
                    {'name': 'JSON', 'caption': 'JSON', 'description': 'JavaScript Object Notation'},
                    {'name': 'XML', 'caption': 'XML', 'description': 'Extensible Markup Language'},
                    {'name': 'Excel', 'caption': 'Excel', 'description': 'Microsoft Excel spreadsheet'},
                    {'name': 'CSV', 'caption': 'CSV', 'description': 'Comma-separated values'}
                ]
            },
            {
                'name': 'QualityLevel',
                'description': 'Quality assessment levels for images and processes',
                'values': [
                    {'name': 'Poor', 'caption': 'Poor', 'description': 'Quality is below acceptable standards'},
                    {'name': 'Fair', 'caption': 'Fair', 'description': 'Quality meets minimum standards'},
                    {'name': 'Good', 'caption': 'Good', 'description': 'Quality is good and acceptable'},
                    {'name': 'VeryGood', 'caption': 'Very Good', 'description': 'Quality exceeds standard requirements'},
                    {'name': 'Excellent', 'caption': 'Excellent', 'description': 'Quality is exceptional'},
                    {'name': 'Outstanding', 'caption': 'Outstanding', 'description': 'Quality is the highest possible level'}
                ]
            },
            {
                'name': 'TaskPriority',
                'description': 'Priority levels for workflow tasks',
                'values': [
                    {'name': 'Critical', 'caption': 'Critical', 'description': 'Highest priority - immediate attention required'},
                    {'name': 'High', 'caption': 'High', 'description': 'High priority - urgent processing needed'},
                    {'name': 'Medium', 'caption': 'Medium', 'description': 'Medium priority - standard processing'},
                    {'name': 'Low', 'caption': 'Low', 'description': 'Low priority - can be processed when time allows'},
                    {'name': 'Deferred', 'caption': 'Deferred', 'description': 'Processing has been postponed'}
                ]
            },
            {
                'name': 'UserRole',
                'description': 'User roles in the LAB validation system',
                'values': [
                    {'name': 'LABAdmin', 'caption': 'LAB Administrator', 'description': 'Full system administration rights'},
                    {'name': 'LABTechnician', 'caption': 'LAB Technician', 'description': 'Task execution and data entry'},
                    {'name': 'LABViewer', 'caption': 'LAB Viewer', 'description': 'Read-only access to public information'},
                    {'name': 'LABSupervisor', 'caption': 'LAB Supervisor', 'description': 'Supervisory oversight of technicians'},
                    {'name': 'SystemAdmin', 'caption': 'System Administrator', 'description': 'Technical system administration'}
                ]
            },
            {
                'name': 'AuditActionType',
                'description': 'Types of actions recorded in the audit trail',
                'values': [
                    {'name': 'Create', 'caption': 'Create', 'description': 'Entity was created'},
                    {'name': 'Update', 'caption': 'Update', 'description': 'Entity was modified'},
                    {'name': 'Delete', 'caption': 'Delete', 'description': 'Entity was deleted'},
                    {'name': 'View', 'caption': 'View', 'description': 'Entity was accessed for viewing'},
                    {'name': 'Export', 'caption': 'Export', 'description': 'Data was exported'},
                    {'name': 'Import', 'caption': 'Import', 'description': 'Data was imported'},
                    {'name': 'Approve', 'caption': 'Approve', 'description': 'Approval action was taken'},
                    {'name': 'Reject', 'caption': 'Reject', 'description': 'Rejection action was taken'},
                    {'name': 'Assign', 'caption': 'Assign', 'description': 'Task or role was assigned'},
                    {'name': 'Complete', 'caption': 'Complete', 'description': 'Task was completed'}
                ]
            }
        ]
    }

def generate_enumeration_xml(enum_config):
    """Generate XML for a single enumeration"""
    try:
        # Create root enumeration element
        enumeration = ET.Element("enumeration")
        enumeration.set("name", enum_config.get('name', 'UnknownEnumeration'))
        
        # Add documentation
        if 'description' in enum_config:
            documentation = ET.SubElement(enumeration, "documentation")
            documentation.text = enum_config['description']
        
        # Add enumeration values
        if 'values' in enum_config and enum_config['values']:
            values_elem = ET.SubElement(enumeration, "values")
            
            for value in enum_config['values']:
                value_elem = ET.SubElement(values_elem, "value")
                value_elem.set("name", value.get('name', 'UnknownValue'))
                
                # Add caption (display name)
                if 'caption' in value:
                    value_elem.set("caption", value['caption'])
                else:
                    value_elem.set("caption", value.get('name', 'UnknownValue'))
                
                # Add description
                if 'description' in value:
                    value_doc = ET.SubElement(value_elem, "documentation")
                    value_doc.text = value['description']
        
        return enumeration
        
    except Exception as e:
        print(f"❌ Error creating enumeration XML for {enum_config.get('name', 'unknown')}: {e}")
        return None

def create_mendix_xml_header():
    """Create proper Mendix XML header"""
    return '<?xml version="1.0" encoding="UTF-8"?>\n'

def format_xml_output(element):
    """Format XML with proper indentation"""
    from xml.dom import minidom
    rough_string = ET.tostring(element, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ").split('\n', 1)[1]  # Remove first line

def create_enumerations_summary(enums_config):
    """Create a markdown summary of all enumerations"""
    summary = """# LAB Workflow Enumerations Summary

Generated on: {timestamp}

## Enumerations Overview

This document lists all enumerations used in the LAB Product Validation Workflow system.

""".format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    for enum in enums_config:
        summary += f"### 📊 {enum['name']}\n\n"
        summary += f"**Description:** {enum.get('description', 'No description')}\n\n"
        
        if 'values' in enum and enum['values']:
            summary += "**Values:**\n\n"
            summary += "| Name | Caption | Description |\n"
            summary += "|------|---------|-------------|\n"
            
            for value in enum['values']:
                name = value.get('name', 'Unknown')
                caption = value.get('caption', name)
                description = value.get('description', 'No description')
                summary += f"| `{name}` | {caption} | {description} |\n"
            
            summary += "\n"
        
        summary += "---\n\n"
    
    # Add usage examples
    summary += """## Usage Examples

### In Domain Model Attributes

```yaml
attributes:
  - name: "ValidationStage"
    type: "Enumeration"
    enumeration: "WorkflowStage"
  - name: "Result"
    type: "Enumeration"
    enumeration: "ValidationOutcome"
```

### In Microflows

```javascript
// Check workflow stage
if ($ValidationStage = WorkflowStage.QualityValidation) {
    // Handle quality validation logic
}

// Set validation outcome
$ValidationResult/Result := ValidationOutcome.Approved;
```

### In Pages (Dropdown Components)

```yaml
components:
  - type: "DropDown"
    field: "Result"
    enumeration: "ValidationOutcome"
    title: "Validation Decision"
```

### XPath Constraints

```xpath
// Show only approved validations
[Result = 'Approved']

// Filter by workflow stage
[ValidationStage = 'LABValidation']
```

## Integration Notes

- All enumerations are automatically available in Studio Pro after import
- Use the enumeration names exactly as defined (case-sensitive)
- Enumeration values can be used in XPath expressions and microflows
- Dropdown widgets automatically populate with enumeration values
- Consider adding new values to existing enumerations rather than creating new ones

"""
    
    return summary

def main():
    """Main function to generate enumerations"""
    parser = argparse.ArgumentParser(description='Generate LAB Workflow Enumerations')
    parser.add_argument('--config', default='config/lab-workflow-config.yaml', 
                       help='Path to configuration file')
    parser.add_argument('--output', default='output/enumerations', 
                       help='Output directory for generated files')
    parser.add_argument('--debug', action='store_true', 
                       help='Enable debug output')
    
    args = parser.parse_args()
    
    print("📊 Generating LAB Workflow Enumerations...")
    print(f"📋 Configuration: {args.config}")
    print(f"📁 Output: {args.output}")
    
    if args.debug:
        print(f"🐛 Debug mode enabled")
        print(f"🐛 Python path: {sys.executable}")
        print(f"🐛 Working directory: {Path.cwd()}")
    
    # Create output directory
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"📁 Created output directory: {output_path.absolute()}")
    
    # Load configuration
    config = load_config(args.config)
    if config is None:
        print("❌ Failed to load configuration")
        return 1
    
    if args.debug:
        print(f"🐛 Loaded configuration keys: {list(config.keys())}")
    
    # Generate enumerations
    if 'enumerations' in config and config['enumerations']:
        print(f"📊 Found {len(config['enumerations'])} enumerations to generate")
        
        generated_count = 0
        for enum_config in config['enumerations']:
            try:
                enum_name = enum_config.get('name', 'Unknown')
                print(f"🔨 Generating: {enum_name}")
                
                # Create enumeration XML
                enum_xml = generate_enumeration_xml(enum_config)
                if enum_xml is not None:
                    # Save to file with proper formatting
                    enum_file = output_path / f"{enum_name}.xml"
                    
                    with open(enum_file, 'w', encoding='utf-8') as f:
                        f.write(create_mendix_xml_header())
                        f.write(format_xml_output(enum_xml))
                    
                    print(f"✅ Generated: {enum_name}.xml")
                    generated_count += 1
                else:
                    print(f"❌ Failed to generate XML for {enum_name}")
                    
            except Exception as e:
                print(f"❌ Error generating {enum_config.get('name', 'unknown')}: {e}")
                if args.debug:
                    import traceback
                    traceback.print_exc()
        
        # Generate enumerations summary
        summary = create_enumerations_summary(config['enumerations'])
        summary_file = output_path / "ENUMERATIONS_SUMMARY.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"📋 Generated enumerations summary: ENUMERATIONS_SUMMARY.md")
        
        print(f"📈 Successfully generated {generated_count} enumerations")
    else:
        print("⚠️ No enumerations found in configuration")
    
    print("🎉 Enumerations generation completed!")
    print(f"📁 Files saved to: {output_path.absolute()}")
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Generation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)