#!/usr/bin/env python3
"""
LAB Product Validation Workflow - Project Validator
FIXED VERSION - Validates compatibility with Mendix 10.18.1
"""

import os
import sys
import xml.etree.ElementTree as ET
import argparse
from pathlib import Path
import re

def validate_xml_syntax(file_path):
    """Validate XML syntax and return any errors"""
    try:
        ET.parse(file_path)
        return True, None
    except ET.ParseError as e:
        return False, str(e)

def check_entity_references(file_path):
    """Check for deprecated entity references not compatible with Mendix 10.18.1"""
    
    deprecated_entities = [
        "System.WorkflowEndedUserTask",  # Only available in Mendix 11+
        "WorkflowCommons.UserTaskView",  # Deprecated in WF Commons 4.0+
        "WorkflowCommons.WorkflowView",  # Deprecated in WF Commons 4.0+
        "WorkflowCommons.MyInitiatedWorkflowView"  # View entity not available
    ]
    
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        for deprecated in deprecated_entities:
            if deprecated in content:
                issues.append(f"Found deprecated entity reference: {deprecated}")
                
        return len(issues) == 0, issues
        
    except Exception as e:
        return False, [f"Error reading file: {e}"]

def check_xpath_syntax(file_path):
    """Check XPath constraints for Mendix 10.18.1 compatibility"""
    
    xpath_issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for proper CurrentUser syntax
        if "$currentUser" in content.lower():
            xpath_issues.append("Found '$currentUser' - should be '[%CurrentUser%]' in 10.18.1")
            
        if "%currentuser%" in content.lower() and "[%CurrentUser%]" not in content:
            xpath_issues.append("Found incorrect CurrentUser syntax - use '[%CurrentUser%]'")
            
        # Check for View Entity references in XPath
        view_entity_patterns = [
            r"WorkflowView",
            r"UserTaskView", 
            r"MyInitiatedWorkflowView"
        ]
        
        for pattern in view_entity_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                xpath_issues.append(f"Found View Entity reference in XPath: {pattern}")
                
        return len(xpath_issues) == 0, xpath_issues
        
    except Exception as e:
        return False, [f"Error checking XPath syntax: {e}"]

def validate_security_roles(security_dir):
    """Validate security role configurations"""
    
    security_issues = []
    required_roles = ["LABAdmin", "LABTechnician", "LABViewer"]
    
    if not security_dir.exists():
        return False, ["Security directory not found"]
    
    # Check if all required roles exist
    for role in required_roles:
        role_file = security_dir / f"{role}.xml"
        if not role_file.exists():
            security_issues.append(f"Missing required security role: {role}")
        else:
            # Validate role file
            xml_valid, xml_error = validate_xml_syntax(role_file)
            if not xml_valid:
                security_issues.append(f"Invalid XML in {role}.xml: {xml_error}")
            
            # Check entity references
            entity_valid, entity_errors = check_entity_references(role_file)
            if not entity_valid:
                security_issues.extend([f"{role}.xml: {error}" for error in entity_errors])
            
            # Check XPath syntax
            xpath_valid, xpath_errors = check_xpath_syntax(role_file)
            if not xpath_valid:
                security_issues.extend([f"{role}.xml: {error}" for error in xpath_errors])
    
    return len(security_issues) == 0, security_issues

def validate_domain_model(domain_dir, enum_dir):
    """Validate domain model entities and enumerations"""
    
    domain_issues = []
    
    if not domain_dir.exists():
        return False, ["Domain model directory not found"]
    
    if not enum_dir.exists():
        return False, ["Enumerations directory not found"]
    
    # Required entities for LAB workflow
    required_entities = [
        "ProductValidation",
        "ImageAcquisition", 
        "ImageQualityValidation",
        "DetailedImageAcquisition",
        "ImageAnalysis",
        "KPIExtraction",
        "ValidationResult",
        "ValidationReport",
        "WorkflowAuditTrail"
    ]
    
    # Check required entities
    for entity in required_entities:
        entity_file = domain_dir / f"{entity}.xml"
        if not entity_file.exists():
            domain_issues.append(f"Missing required entity: {entity}")
        else:
            # Validate XML syntax
            xml_valid, xml_error = validate_xml_syntax(entity_file)
            if not xml_valid:
                domain_issues.append(f"Invalid XML in {entity}.xml: {xml_error}")
    
    # Required enumerations
    required_enums = [
        "ValidationStatus",
        "Priority", 
        "ImageQuality",
        "WorkflowStage",
        "ApprovalLevel"
    ]
    
    # Check required enumerations
    for enum in required_enums:
        enum_file = enum_dir / f"{enum}.xml"
        if not enum_file.exists():
            domain_issues.append(f"Missing required enumeration: {enum}")
        else:
            # Validate XML syntax
            xml_valid, xml_error = validate_xml_syntax(enum_file)
            if not xml_valid:
                domain_issues.append(f"Invalid XML in {enum}.xml: {xml_error}")
    
    return len(domain_issues) == 0, domain_issues

def validate_microflows(microflows_dir):
    """Validate microflow definitions"""
    
    microflow_issues = []
    
    if not microflows_dir.exists():
        return False, ["Microflows directory not found"]
    
    # Core microflows that should exist
    core_microflows = [
        "ACT_CreateTask",
        "ACT_CompleteTask",
        "ACT_ProcessImageQuality",
        "SUB_CheckUserPermissions",
        "DS_GetMyTasks"
    ]
    
    # Check core microflows
    for microflow in core_microflows:
        microflow_file = microflows_dir / f"{microflow}.xml"
        if not microflow_file.exists():
            microflow_issues.append(f"Missing core microflow: {microflow}")
        else:
            # Validate XML syntax
            xml_valid, xml_error = validate_xml_syntax(microflow_file)
            if not xml_valid:
                microflow_issues.append(f"Invalid XML in {microflow}.xml: {xml_error}")
            
            # Check entity references
            entity_valid, entity_errors = check_entity_references(microflow_file)
            if not entity_valid:
                microflow_issues.extend([f"{microflow}.xml: {error}" for error in entity_errors])
    
    return len(microflow_issues) == 0, microflow_issues

def validate_project_structure(base_dir):
    """Validate overall project structure"""
    
    structure_issues = []
    
    required_dirs = [
        "output/domain-model",
        "output/enumerations", 
        "output/microflows",
        "output/security",
        "config"
    ]
    
    for dir_path in required_dirs:
        full_path = base_dir / dir_path
        if not full_path.exists():
            structure_issues.append(f"Missing required directory: {dir_path}")
    
    # Check config file
    config_file = base_dir / "config/lab-workflow-config.yaml"
    if not config_file.exists():
        structure_issues.append("Missing configuration file: config/lab-workflow-config.yaml")
    
    return len(structure_issues) == 0, structure_issues

def check_mendix_compatibility(base_dir):
    """Check specific Mendix 10.18.1 compatibility issues"""
    
    compatibility_issues = []
    
    # Check all XML files for compatibility issues
    xml_files = []
    for dir_name in ["domain-model", "microflows", "security", "pages", "workflows"]:
        xml_dir = base_dir / "output" / dir_name
        if xml_dir.exists():
            xml_files.extend(xml_dir.glob("*.xml"))
    
    for xml_file in xml_files:
        try:
            with open(xml_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for Mendix 11+ specific features
            mendix_11_features = [
                "WorkflowEndedUserTask",
                "View Entities",
                "view entity",
                "viewEntity"
            ]
            
            for feature in mendix_11_features:
                if feature.lower() in content.lower():
                    compatibility_issues.append(f"{xml_file.name}: Contains Mendix 11+ feature: {feature}")
            
            # Check for proper XML namespaces
            if "http://www.mendix.com/metamodel/" in content:
                # Ensure version compatibility
                if "/8.0.0" in content or "/9.0.0" in content:
                    compatibility_issues.append(f"{xml_file.name}: Uses newer XML schema version")
                    
        except Exception as e:
            compatibility_issues.append(f"Error checking {xml_file.name}: {e}")
    
    return len(compatibility_issues) == 0, compatibility_issues

def main():
    parser = argparse.ArgumentParser(description="Validate LAB Workflow Project")
    parser.add_argument("--output", default="output", help="Output directory to validate")
    parser.add_argument("--comprehensive", action="store_true", help="Run comprehensive validation")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    base_dir = Path(".")
    output_dir = Path(args.output)
    
    print("🔍 LAB Workflow Project Validation - FIXED VERSION")
    print("=" * 60)
    print(f"📁 Validating: {output_dir}")
    print(f"🎯 Target: Mendix 10.18.1 + Workflow Commons 3.12.1")
    print()
    
    all_passed = True
    total_issues = 0
    
    # 1. Validate project structure
    print("📋 Validating project structure...")
    structure_valid, structure_issues = validate_project_structure(base_dir)
    if structure_valid:
        print("  ✅ Project structure is valid")
    else:
        print("  ❌ Project structure issues:")
        for issue in structure_issues:
            print(f"    • {issue}")
        all_passed = False
        total_issues += len(structure_issues)
    
    if not output_dir.exists():
        print(f"❌ Output directory not found: {output_dir}")
        print("Run the generation script first!")
        sys.exit(1)
    
    # 2. Validate domain model
    print("\n📊 Validating domain model...")
    domain_valid, domain_issues = validate_domain_model(
        output_dir / "domain-model",
        output_dir / "enumerations"
    )
    if domain_valid:
        print("  ✅ Domain model is valid")
    else:
        print("  ❌ Domain model issues:")
        for issue in domain_issues:
            print(f"    • {issue}")
        all_passed = False
        total_issues += len(domain_issues)
    
    # 3. Validate microflows
    print("\n⚡ Validating microflows...")
    microflows_valid, microflow_issues = validate_microflows(output_dir / "microflows")
    if microflows_valid:
        print("  ✅ Microflows are valid")
    else:
        print("  ❌ Microflow issues:")
        for issue in microflow_issues:
            print(f"    • {issue}")
        all_passed = False
        total_issues += len(microflow_issues)
    
    # 4. Validate security roles
    print("\n🔒 Validating security roles...")
    security_valid, security_issues = validate_security_roles(output_dir / "security")
    if security_valid:
        print("  ✅ Security roles are valid")
    else:
        print("  ❌ Security role issues:")
        for issue in security_issues:
            print(f"    • {issue}")
        all_passed = False
        total_issues += len(security_issues)
    
    # 5. Check Mendix compatibility
    if args.comprehensive:
        print("\n🎯 Checking Mendix 10.18.1 compatibility...")
        compat_valid, compat_issues = check_mendix_compatibility(base_dir)
        if compat_valid:
            print("  ✅ Mendix 10.18.1 compatibility verified")
        else:
            print("  ❌ Compatibility issues:")
            for issue in compat_issues:
                print(f"    • {issue}")
            all_passed = False
            total_issues += len(compat_issues)
    
    # Final summary
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("✅ Project is ready for import into Mendix Studio Pro 10.18.1")
        print()
        print("📋 Next steps:")
        print("  1. Open Mendix Studio Pro 10.18.1")
        print("  2. Install Workflow Commons 3.12.1")
        print("  3. Import XML files individually (NOT as MPK)")
        print("  4. Follow import order in PROJECT_SUMMARY.md")
    else:
        print(f"❌ VALIDATION FAILED - {total_issues} issues found")
        print("🔧 Please fix the issues above before importing to Mendix")
        print()
        print("💡 Common fixes:")
        print("  • Check entity references are compatible with 10.18.1")
        print("  • Verify XPath syntax uses [%CurrentUser%]")
        print("  • Ensure no View Entities or Mendix 11+ features")
        print("  • Validate XML syntax in all files")
    
    print()
    
    # Generate validation report if verbose
    if args.verbose:
        report_file = output_dir / "VALIDATION_REPORT.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("LAB Workflow Project Validation Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Validation Date: {Path().resolve()}\n")
            f.write(f"Target Platform: Mendix 10.18.1\n")
            f.write(f"Workflow Commons: 3.12.1\n\n")
            
            if all_passed:
                f.write("✅ ALL VALIDATIONS PASSED\n\n")
            else:
                f.write(f"❌ VALIDATION FAILED - {total_issues} issues\n\n")
                
                if structure_issues:
                    f.write("Structure Issues:\n")
                    for issue in structure_issues:
                        f.write(f"  • {issue}\n")
                    f.write("\n")
                    
                if domain_issues:
                    f.write("Domain Model Issues:\n")
                    for issue in domain_issues:
                        f.write(f"  • {issue}\n")
                    f.write("\n")
                    
                if microflow_issues:
                    f.write("Microflow Issues:\n")
                    for issue in microflow_issues:
                        f.write(f"  • {issue}\n")
                    f.write("\n")
                    
                if security_issues:
                    f.write("Security Issues:\n")
                    for issue in security_issues:
                        f.write(f"  • {issue}\n")
                    f.write("\n")
        
        print(f"📄 Detailed validation report: {report_file}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"❌ Fatal validation error: {e}")
        sys.exit(1)