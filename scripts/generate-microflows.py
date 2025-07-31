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
    """Generate XML for a single microflow with comprehensive comments for Mendix 10.18.1"""
    try:
        # Create root microflow element
        microflow = ET.Element("microflow")
        microflow.set("name", microflow_config.get('name', 'UnknownMicroflow'))
        microflow.set("type", microflow_config.get('type', 'action'))
        
        # Add comprehensive header comment
        header_comment = ET.Comment(f"""
=== LAB WORKFLOW MICROFLOW ===
Name: {microflow_config.get('name', 'Unknown')}
Type: {microflow_config.get('type', 'action')}
Compatible with: Mendix 10.18.1, Workflow Commons 3.12.1
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Purpose: {microflow_config.get('description', 'LAB workflow operation')}
Security: Restricted to roles - {', '.join(microflow_config.get('security_roles', ['All users']))}
Usage: Called from workflow steps, pages, or other microflows

IMPLEMENTATION NOTES:
- This is a template structure - implement actual business logic
- Add proper error handling and validation
- Use consistent naming conventions  
- Log important actions for audit trail
- Test with different user roles
""")
        microflow.insert(0, header_comment)
        
        # Add documentation
        if 'description' in microflow_config:
            documentation = ET.SubElement(microflow, "documentation")
            documentation.text = f"""
{microflow_config['description']}

=== IMPLEMENTATION GUIDE ===

For Mendix 10.18.1 implementation:
1. Add input validation at the start
2. Implement core business logic
3. Add error handling (try-catch blocks)
4. Log actions to audit trail
5. Return appropriate values
6. Test with different user roles

Security Roles: {', '.join(microflow_config.get('security_roles', ['All']))}
Return Type: {microflow_config.get('return_type', 'None')}

Business Rules:
- Validate all input parameters
- Check user permissions
- Update audit trail
- Handle error scenarios gracefully
"""
        
        # Add parameters section with detailed comments
        if 'parameters' in microflow_config and microflow_config['parameters']:
            parameters_elem = ET.SubElement(microflow, "parameters")
            
            # Add comment for parameters section
            param_comment = ET.Comment(f" INPUT PARAMETERS - {len(microflow_config['parameters'])} parameters defined ")
            parameters_elem.insert(0, param_comment)
            
            for i, param in enumerate(microflow_config['parameters']):
                # Add comment before each parameter
                param_detail_comment = ET.Comment(f" Parameter {i+1}: {param.get('name', 'Unknown')} ({param.get('type', 'String')}) ")
                parameters_elem.append(param_detail_comment)
                
                param_elem = ET.SubElement(parameters_elem, "parameter")
                param_elem.set("name", param.get('name', 'UnknownParam'))
                param_elem.set("type", param.get('type', 'String'))
                
                # Add parameter documentation
                param_doc = ET.SubElement(param_elem, "documentation")
                param_doc.text = f"""
Parameter: {param.get('name', 'Unknown')}
Type: {param.get('type', 'String')}
Required: Yes
Description: {param.get('description', 'Input parameter for LAB workflow operation')}
Validation: Validate this parameter at microflow start
"""
        
        # Add return type with comments
        if 'return_type' in microflow_config:
            return_elem = ET.SubElement(microflow, "returnType")
            return_elem.set("type", microflow_config['return_type'])
            
            # Add return type comment
            return_comment = ET.Comment(f" RETURN TYPE: {microflow_config['return_type']} - Document what this microflow returns ")
            return_elem.insert(0, return_comment)
        
        # Add security settings with detailed comments
        if 'security_roles' in microflow_config:
            security_elem = ET.SubElement(microflow, "security")
            
            # Add security comment
            security_comment = ET.Comment(f" SECURITY CONFIGURATION - Restricted to: {', '.join(microflow_config['security_roles'])} ")
            security_elem.insert(0, security_comment)
            
            for role in microflow_config['security_roles']:
                role_elem = ET.SubElement(security_elem, "allowedRole")
                role_elem.set("name", role)
                
                # Add role-specific comment
                role_comment = ET.Comment(f" Role: {role} - Ensure users have this role to execute microflow ")
                role_elem.insert(0, role_comment)
        
        # Add microflow flow structure with comprehensive comments
        flow_elem = ET.SubElement(microflow, "flow")
        
        # Add flow structure comment
        flow_comment = ET.Comment(f"""
MICROFLOW FLOW STRUCTURE for Mendix 10.18.1
This is a template - implement actual logic:

1. START EVENT - Entry point
2. INPUT VALIDATION - Validate all parameters
3. PERMISSION CHECK - Verify user permissions  
4. BUSINESS LOGIC - Core functionality
5. AUDIT LOGGING - Record action
6. ERROR HANDLING - Handle exceptions
7. END EVENT - Return result

Remember to:
- Add proper activities between start and end
- Use consistent variable naming
- Add error handling paths
- Log important actions
- Test thoroughly
""")
        flow_elem.insert(0, flow_comment)
        
        # Start event with comment
        start_comment = ET.Comment(" START EVENT - Microflow entry point ")
        flow_elem.append(start_comment)
        start_elem = ET.SubElement(flow_elem, "start")
        start_elem.set("id", "start")
        start_elem.set("name", "Start")
        
        # Add validation activity comment
        validation_comment = ET.Comment(" TODO: Add input validation activities here ")
        flow_elem.append(validation_comment)
        
        # Add business logic comment
        logic_comment = ET.Comment(" TODO: Add core business logic activities here ")
        flow_elem.append(logic_comment)
        
        # Add audit trail comment
        audit_comment = ET.Comment(" TODO: Add audit trail logging here ")
        flow_elem.append(audit_comment)
        
        # End event with comment
        end_comment = ET.Comment(" END EVENT - Microflow exit point ")
        flow_elem.append(end_comment)
        end_elem = ET.SubElement(flow_elem, "end")
        end_elem.set("id", "end")
        end_elem.set("name", "End")
        
        # Sequence flow with comment
        sequence_comment = ET.Comment(" SEQUENCE FLOW - Connect activities in logical order ")
        flow_elem.append(sequence_comment)
        sequence_elem = ET.SubElement(flow_elem, "sequenceFlow")
        sequence_elem.set("id", "flow1")
        sequence_elem.set("sourceRef", "start")
        sequence_elem.set("targetRef", "end")
        
        # Add implementation notes comment
        impl_comment = ET.Comment(f"""
IMPLEMENTATION CHECKLIST for {microflow_config.get('name', 'Unknown')}:

□ Input validation added
□ Permission checks implemented  
□ Core business logic completed
□ Error handling paths added
□ Audit trail logging included
□ Return values configured
□ Security roles tested
□ Performance optimized
□ Documentation updated
□ Unit tests created

Mendix 10.18.1 Best Practices:
- Use proper activity naming
- Add meaningful comments
- Handle null values
- Use consistent error messages
- Log important actions
- Test with different data scenarios
""")
        microflow.append(impl_comment)
        
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