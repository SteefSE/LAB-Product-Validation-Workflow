#!/usr/bin/env python3
"""
LAB Product Validation Workflow - Microflows Generator
Generates complete microflows for workflow operations and role-based actions
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
        
        # If no config found, provide default microflows
        print("⚠️ No configuration file found, using default microflows")
        return get_default_microflows_config()
        
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return None

def get_default_microflows_config():
    """Return default microflows configuration"""
    return {
        'microflows': [
            {
                'name': 'ACT_CreateTask',
                'type': 'action',
                'description': 'Creates new task with proper assignment and initial status',
                'parameters': [
                    {'name': 'TaskTitle', 'type': 'String'},
                    {'name': 'AssignedUser', 'type': 'Administration.Account'},
                    {'name': 'WorkflowContext', 'type': 'ProductValidation'}
                ],
                'return_type': 'System.WorkflowUserTask',
                'security_roles': ['LABAdmin', 'LABTechnician']
            },
            {
                'name': 'ACT_AssignTask',
                'type': 'action',
                'description': 'Assigns tasks to users based on role and workload',
                'parameters': [
                    {'name': 'Task', 'type': 'System.WorkflowUserTask'},
                    {'name': 'NewAssignee', 'type': 'Administration.Account'}
                ],
                'return_type': 'Boolean',
                'security_roles': ['LABAdmin']
            },
            {
                'name': 'ACT_CompleteTask',
                'type': 'action',
                'description': 'Marks task as completed, triggers workflow progression',
                'parameters': [
                    {'name': 'Task', 'type': 'System.WorkflowUserTask'},
                    {'name': 'CompletionData', 'type': 'String'}
                ],
                'return_type': 'Boolean',
                'security_roles': ['LABAdmin', 'LABTechnician']
            },
            {
                'name': 'SUB_CheckUserPermissions',
                'type': 'submicroflow',
                'description': 'Validates user access rights for specific actions',
                'parameters': [
                    {'name': 'User', 'type': 'Administration.Account'},
                    {'name': 'RequiredRole', 'type': 'String'},
                    {'name': 'EntityToAccess', 'type': 'String'}
                ],
                'return_type': 'Boolean',
                'security_roles': ['LABAdmin', 'LABTechnician', 'LABViewer']
            },
            {
                'name': 'ACT_ProcessImageQuality',
                'type': 'action',
                'description': 'Validates image quality and determines approval status',
                'parameters': [
                    {'name': 'ImageAcquisition', 'type': 'ImageAcquisition'},
                    {'name': 'QualityThreshold', 'type': 'Decimal'}
                ],
                'return_type': 'Boolean',
                'security_roles': ['LABAdmin', 'LABTechnician']
            },
            {
                'name': 'DS_GetMyTasks',
                'type': 'datasource',
                'description': 'Returns tasks filtered by current user with XPath constraints',
                'parameters': [
                    {'name': 'CurrentUser', 'type': 'Administration.Account'}
                ],
                'return_type': 'List of System.WorkflowUserTask',
                'security_roles': ['LABAdmin', 'LABTechnician']
            },
            {
                'name': 'ACT_InitiateWorkflow',
                'type': 'action',
                'description': 'Initiates new LAB validation workflow instance',
                'parameters': [
                    {'name': 'ProductID', 'type': 'String'},
                    {'name': 'InitiatedBy', 'type': 'Administration.Account'}
                ],
                'return_type': 'ProductValidation',
                'security_roles': ['LABAdmin', 'LABTechnician']
            },
            {
                'name': 'ACT_GenerateValidationReport',
                'type': 'action',
                'description': 'Generates comprehensive validation report',
                'parameters': [
                    {'name': 'ProductValidation', 'type': 'ProductValidation'}
                ],
                'return_type': 'ValidationReport',
                'security_roles': ['LABAdmin', 'LABTechnician', 'LABViewer']
            },
            {
                'name': 'ACT_UpdateAuditTrail',
                'type': 'action',
                'description': 'Records action in workflow audit trail',
                'parameters': [
                    {'name': 'Action', 'type': 'String'},
                    {'name': 'EntityChanged', 'type': 'String'},
                    {'name': 'OldValue', 'type': 'String'},
                    {'name': 'NewValue', 'type': 'String'}
                ],
                'return_type': 'WorkflowAuditTrail',
                'security_roles': ['LABAdmin', 'LABTechnician']
            },
            {
                'name': 'ACT_ValidateWorkflowOutcome',
                'type': 'action',
                'description': 'Critical TRUE/FALSE decision point for workflow progression',
                'parameters': [
                    {'name': 'ProductValidation', 'type': 'ProductValidation'},
                    {'name': 'ValidationCriteria', 'type': 'String'}
                ],
                'return_type': 'Boolean',
                'security_roles': ['LABAdmin']
            }
        ]
    }

def generate_microflow_xml(microflow_config):
    """Generate XML for a single microflow"""
    try:
        # Create root microflow element
        microflow = ET.Element("microflow")
        microflow.set("name", microflow_config.get('name', 'UnknownMicroflow'))
        microflow.set("type", microflow_config.get('type', 'action'))
        
        # Add documentation
        if 'description' in microflow_config:
            documentation = ET.SubElement(microflow, "documentation")
            documentation.text = microflow_config['description']
        
        # Add parameters
        if 'parameters' in microflow_config and microflow_config['parameters']:
            parameters_elem = ET.SubElement(microflow, "parameters")
            
            for param in microflow_config['parameters']:
                param_elem = ET.SubElement(parameters_elem, "parameter")
                param_elem.set("name", param.get('name', 'UnknownParam'))
                param_elem.set("type", param.get('type', 'String'))
        
        # Add return type
        if 'return_type' in microflow_config:
            return_elem = ET.SubElement(microflow, "returnType")
            return_elem.set("type", microflow_config['return_type'])
        
        # Add security settings
        if 'security_roles' in microflow_config:
            security_elem = ET.SubElement(microflow, "security")
            for role in microflow_config['security_roles']:
                role_elem = ET.SubElement(security_elem, "allowedRole")
                role_elem.set("name", role)
        
        # Add basic microflow flow (start -> end)
        flow_elem = ET.SubElement(microflow, "flow")
        
        # Start event
        start_elem = ET.SubElement(flow_elem, "start")
        start_elem.set("id", "start")
        start_elem.set("name", "Start")
        
        # End event
        end_elem = ET.SubElement(flow_elem, "end")
        end_elem.set("id", "end")
        end_elem.set("name", "End")
        
        # Sequence flow
        sequence_elem = ET.SubElement(flow_elem, "sequenceFlow")
        sequence_elem.set("id", "flow1")
        sequence_elem.set("sourceRef", "start")
        sequence_elem.set("targetRef", "end")
        
        return microflow
        
    except Exception as e:
        print(f"❌ Error creating microflow XML for {microflow_config.get('name', 'unknown')}: {e}")
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

def main():
    """Main function to generate microflows"""
    parser = argparse.ArgumentParser(description='Generate LAB Workflow Microflows')
    parser.add_argument('--config', default='config/lab-workflow-config.yaml', 
                       help='Path to configuration file')
    parser.add_argument('--output', default='output/microflows', 
                       help='Output directory for generated files')
    parser.add_argument('--debug', action='store_true', 
                       help='Enable debug output')
    
    args = parser.parse_args()
    
    print("⚡ Generating LAB Workflow Microflows...")
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
    
    # Generate microflows
    if 'microflows' in config and config['microflows']:
        print(f"⚡ Found {len(config['microflows'])} microflows to generate")
        
        generated_count = 0
        for microflow_config in config['microflows']:
            try:
                microflow_name = microflow_config.get('name', 'Unknown')
                print(f"🔨 Generating: {microflow_name}")
                
                # Create microflow XML
                microflow_xml = generate_microflow_xml(microflow_config)
                if microflow_xml is not None:
                    # Save to file with proper formatting
                    microflow_file = output_path / f"{microflow_name}.xml"
                    
                    with open(microflow_file, 'w', encoding='utf-8') as f:
                        f.write(create_mendix_xml_header())
                        f.write(format_xml_output(microflow_xml))
                    
                    print(f"✅ Generated: {microflow_name}.xml")
                    generated_count += 1
                else:
                    print(f"❌ Failed to generate XML for {microflow_name}")
                    
            except Exception as e:
                print(f"❌ Error generating {microflow_config.get('name', 'unknown')}: {e}")
                if args.debug:
                    import traceback
                    traceback.print_exc()
        
        print(f"📈 Successfully generated {generated_count} microflows")
    else:
        print("⚠️ No microflows found in configuration")
    
    print("🎉 Microflows generation completed!")
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