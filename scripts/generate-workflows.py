#!/usr/bin/env python3
"""
LAB Product Validation Workflow - Workflow Definition Generator
Generates complete workflow definitions with TRUE/FALSE decision logic
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
            Path("config/workflow-config.yaml"),
            Path("../config/lab-workflow-config.yaml")
        ]
        
        for alt_path in alternative_paths:
            if alt_path.exists():
                print(f"📁 Using configuration from: {alt_path}")
                with open(alt_path, 'r', encoding='utf-8') as file:
                    return yaml.safe_load(file)
        
        # If no config found, provide default workflow configuration
        print("⚠️ No configuration file found, using default workflow")
        return get_default_workflow_config()
        
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return None

def get_default_workflow_config():
    """Return default workflow configuration"""
    return {
        'workflows': [
            {
                'name': 'LAB_ProductValidation',
                'description': 'Main LAB product validation workflow with TRUE/FALSE decision logic',
                'context_entity': 'ProductValidation',
                'steps': [
                    {
                        'id': 'start',
                        'name': 'Start',
                        'type': 'start_event',
                        'description': 'Workflow initiation'
                    },
                    {
                        'id': 'image_acquisition',
                        'name': 'Image Acquisition',
                        'type': 'user_task',
                        'description': 'Capture product validation images',
                        'page': 'ImageAcquisitionTask',
                        'assignee_expression': '$WorkflowContext/InitiatedBy',
                        'outcomes': ['completed', 'cancelled']
                    },
                    {
                        'id': 'quality_validation',
                        'name': 'Quality Validation',
                        'type': 'decision',
                        'description': 'CRITICAL: TRUE/FALSE decision point for image quality',
                        'condition': '$WorkflowContext/LAB_ProductValidation/ImageAcquisition/IsQualityApproved',
                        'outcomes': ['true', 'false']
                    },
                    {
                        'id': 'detailed_acquisition',
                        'name': 'Detailed Image Acquisition',
                        'type': 'user_task',
                        'description': 'Enhanced image processing (TRUE path only)',
                        'page': 'DetailedImageAcquisitionTask',
                        'assignee_expression': '$WorkflowContext/InitiatedBy',
                        'condition': 'quality_validation == true',
                        'outcomes': ['completed']
                    },
                    {
                        'id': 'image_analysis',
                        'name': 'Automated Analysis',
                        'type': 'service_task',
                        'description': 'Automated image analysis and KPI extraction',
                        'microflow': 'ACT_ProcessImageAnalysis',
                        'condition': 'quality_validation == true',
                        'outcomes': ['completed']
                    },
                    {
                        'id': 'kpi_extraction',
                        'name': 'KPI Extraction',
                        'type': 'service_task',
                        'description': 'Extract performance indicators',
                        'microflow': 'ACT_ExtractKPIs',
                        'condition': 'quality_validation == true',
                        'outcomes': ['completed']
                    },
                    {
                        'id': 'lab_validation',
                        'name': 'LAB Validation',
                        'type': 'user_task',
                        'description': 'Final validation decision by LAB administrator',
                        'page': 'ValidationResultPage',
                        'assignee_role': 'LABAdmin',
                        'condition': 'quality_validation == true',
                        'outcomes': ['approved', 'rejected', 'requires_rework']
                    },
                    {
                        'id': 'report_generation',
                        'name': 'Report Generation',
                        'type': 'service_task',
                        'description': 'Generate comprehensive validation report',
                        'microflow': 'ACT_GenerateValidationReport',
                        'condition': 'quality_validation == true AND lab_validation == approved',
                        'outcomes': ['completed']
                    },
                    {
                        'id': 'workflow_approved',
                        'name': 'Workflow Approved',
                        'type': 'end_event',
                        'description': 'Successful completion - TRUE outcome',
                        'condition': 'quality_validation == true AND lab_validation == approved',
                        'result': 'true'
                    },
                    {
                        'id': 'workflow_rejected',
                        'name': 'Workflow Rejected',
                        'type': 'end_event',
                        'description': 'Validation failed - FALSE outcome',
                        'condition': 'quality_validation == false OR lab_validation == rejected',
                        'result': 'false'
                    }
                ],
                'flows': [
                    {'from': 'start', 'to': 'image_acquisition'},
                    {'from': 'image_acquisition', 'to': 'quality_validation', 'condition': 'completed'},
                    {'from': 'quality_validation', 'to': 'detailed_acquisition', 'condition': 'true'},
                    {'from': 'quality_validation', 'to': 'workflow_rejected', 'condition': 'false'},
                    {'from': 'detailed_acquisition', 'to': 'image_analysis', 'condition': 'completed'},
                    {'from': 'image_analysis', 'to': 'kpi_extraction', 'condition': 'completed'},
                    {'from': 'kpi_extraction', 'to': 'lab_validation', 'condition': 'completed'},
                    {'from': 'lab_validation', 'to': 'report_generation', 'condition': 'approved'},
                    {'from': 'lab_validation', 'to': 'workflow_rejected', 'condition': 'rejected'},
                    {'from': 'report_generation', 'to': 'workflow_approved', 'condition': 'completed'}
                ]
            }
        ]
    }

def generate_workflow_xml(workflow_config):
    """Generate XML for a single workflow definition"""
    try:
        # Create root workflow element
        workflow = ET.Element("workflow")
        workflow.set("name", workflow_config.get('name', 'UnknownWorkflow'))
        
        # Add documentation
        if 'description' in workflow_config:
            documentation = ET.SubElement(workflow, "documentation")
            documentation.text = workflow_config['description']
        
        # Add context entity
        if 'context_entity' in workflow_config:
            context = ET.SubElement(workflow, "contextEntity")
            context.set("name", workflow_config['context_entity'])
        
        # Add workflow steps
        if 'steps' in workflow_config and workflow_config['steps']:
            steps_elem = ET.SubElement(workflow, "steps")
            
            for step in workflow_config['steps']:
                step_elem = ET.SubElement(steps_elem, "step")
                step_elem.set("id", step.get('id', 'unknown'))
                step_elem.set("name", step.get('name', 'Unknown Step'))
                step_elem.set("type", step.get('type', 'task'))
                
                # Add step documentation
                if 'description' in step:
                    step_doc = ET.SubElement(step_elem, "documentation")
                    step_doc.text = step['description']
                
                # Add step-specific properties
                if 'page' in step:
                    step_elem.set("page", step['page'])
                if 'microflow' in step:
                    step_elem.set("microflow", step['microflow'])
                if 'assignee_expression' in step:
                    assignee = ET.SubElement(step_elem, "assignee")
                    assignee.text = step['assignee_expression']
                if 'assignee_role' in step:
                    role = ET.SubElement(step_elem, "assigneeRole")
                    role.text = step['assignee_role']
                if 'condition' in step:
                    condition = ET.SubElement(step_elem, "condition")
                    condition.text = step['condition']
                if 'result' in step:
                    step_elem.set("result", step['result'])
                
                # Add outcomes
                if 'outcomes' in step:
                    outcomes = ET.SubElement(step_elem, "outcomes")
                    for outcome in step['outcomes']:
                        outcome_elem = ET.SubElement(outcomes, "outcome")
                        outcome_elem.set("name", outcome)
        
        # Add workflow flows (connections between steps)
        if 'flows' in workflow_config and workflow_config['flows']:
            flows_elem = ET.SubElement(workflow, "flows")
            
            for flow in workflow_config['flows']:
                flow_elem = ET.SubElement(flows_elem, "flow")
                flow_elem.set("from", flow.get('from', ''))
                flow_elem.set("to", flow.get('to', ''))
                
                if 'condition' in flow:
                    condition = ET.SubElement(flow_elem, "condition")
                    condition.text = flow['condition']
        
        return workflow
        
    except Exception as e:
        print(f"❌ Error creating workflow XML for {workflow_config.get('name', 'unknown')}: {e}")
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

def create_workflow_diagram(workflow_config, output_path):
    """Create a visual diagram of the workflow in Mermaid format"""
    diagram = """# LAB Product Validation Workflow Diagram

```mermaid
flowchart TD
    Start([Start]) --> ImageAcq[Image Acquisition]
    ImageAcq --> QualityCheck{{Quality Validation<br/>TRUE/FALSE}}
    
    %% TRUE Path - Continue Processing
    QualityCheck -->|TRUE| DetailedAcq[Detailed Image Acquisition]
    DetailedAcq --> Analysis[Automated Analysis]
    Analysis --> KPI[KPI Extraction]
    KPI --> LABValidation[LAB Validation]
    LABValidation -->|Approved| ReportGen[Report Generation]
    ReportGen --> Approved([Workflow Approved<br/>Result: TRUE])
    
    %% FALSE Path - Immediate Termination
    QualityCheck -->|FALSE| Rejected([Workflow Rejected<br/>Result: FALSE])
    LABValidation -->|Rejected| Rejected
    
    %% Styling
    classDef startEnd fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef decision fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef process fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef approved fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef rejected fill:#ffebee,stroke:#c62828,stroke-width:2px
    
    class Start,Approved,Rejected startEnd
    class QualityCheck decision
    class ImageAcq,DetailedAcq,Analysis,KPI,LABValidation,ReportGen process
    class Approved approved
    class Rejected rejected
```

## Workflow Logic

### Critical Decision Point: Quality Validation

The workflow implements a **TRUE/FALSE decision logic** at the Quality Validation step:

- **TRUE Path**: Quality approved → Continue through all workflow steps
- **FALSE Path**: Quality rejected → Terminate workflow immediately

### Step Details

1. **Image Acquisition**: Capture product validation images
2. **Quality Validation**: ❗ **CRITICAL DECISION POINT** ❗
   - If `IsQualityApproved = TRUE` → Continue to detailed processing
   - If `IsQualityApproved = FALSE` → Terminate with FALSE result
3. **Detailed Acquisition**: Enhanced image processing (TRUE path only)
4. **Automated Analysis**: AI-powered image analysis
5. **KPI Extraction**: Extract performance metrics
6. **LAB Validation**: Final human validation decision
7. **Report Generation**: Comprehensive validation report

### Outcomes

- **TRUE Result**: Quality approved AND LAB validation approved
- **FALSE Result**: Quality rejected OR LAB validation rejected

### Role Assignments

- **LABTechnician**: Image Acquisition, Detailed Acquisition
- **LABAdmin**: LAB Validation, Final Approval
- **System**: Automated Analysis, KPI Extraction, Report Generation

"""
    
    diagram_file = output_path / "WORKFLOW_DIAGRAM.md"
    with open(diagram_file, 'w', encoding='utf-8') as f:
        f.write(diagram)
    
    return diagram_file

def main():
    """Main function to generate workflows"""
    parser = argparse.ArgumentParser(description='Generate LAB Workflow Definitions')
    parser.add_argument('--config', default='config/lab-workflow-config.yaml', 
                       help='Path to configuration file')
    parser.add_argument('--output', default='output/workflows', 
                       help='Output directory for generated files')
    parser.add_argument('--debug', action='store_true', 
                       help='Enable debug output')
    
    args = parser.parse_args()
    
    print("🔄 Generating LAB Workflow Definitions...")
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
    
    # Generate workflows
    if 'workflows' in config and config['workflows']:
        print(f"🔄 Found {len(config['workflows'])} workflows to generate")
        
        generated_count = 0
        for workflow_config in config['workflows']:
            try:
                workflow_name = workflow_config.get('name', 'Unknown')
                print(f"🔨 Generating: {workflow_name}")
                
                # Create workflow XML
                workflow_xml = generate_workflow_xml(workflow_config)
                if workflow_xml is not None:
                    # Save to file with proper formatting
                    workflow_file = output_path / f"{workflow_name}.xml"
                    
                    with open(workflow_file, 'w', encoding='utf-8') as f:
                        f.write(create_mendix_xml_header())
                        f.write(format_xml_output(workflow_xml))
                    
                    print(f"✅ Generated: {workflow_name}.xml")
                    generated_count += 1
                    
                    # Generate workflow diagram
                    diagram_file = create_workflow_diagram(workflow_config, output_path)
                    print(f"📊 Generated workflow diagram: {diagram_file.name}")
                else:
                    print(f"❌ Failed to generate XML for {workflow_name}")
                    
            except Exception as e:
                print(f"❌ Error generating {workflow_config.get('name', 'unknown')}: {e}")
                if args.debug:
                    import traceback
                    traceback.print_exc()
        
        print(f"📈 Successfully generated {generated_count} workflows")
    else:
        print("⚠️ No workflows found in configuration")
    
    print("🎉 Workflow generation completed!")
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