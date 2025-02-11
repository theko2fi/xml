import re
from lxml import etree, objectify

def validate_jobname(jobname, pattern, element_type, line_number):
    if jobname and pattern.match(jobname):
        print(f"{element_type} JOBNAME '{jobname}' matches the format.")
    else:
        print(f"{element_type} JOBNAME '{jobname}' does not match the format (line {line_number}).")

def validate_application(application, pattern, element_type, line_number):
    if application and pattern.match(application):
        print(f"{element_type} APPLICATION '{application}' matches the format.")
    else:
        print(f"{element_type} APPLICATION '{application}' does not match the format (line {line_number}).")

def validate_sub_application(smart_folder, job, line_number):
    smart_folder_sub_application = smart_folder.get("SUB_APPLICATION")
    smart_folder_jobname = smart_folder.get("JOBNAME")
    job_sub_application = job.get("SUB_APPLICATION")

    if smart_folder_sub_application != smart_folder_jobname:
        print(f"SMART_FOLDER SUB_APPLICATION '{smart_folder_sub_application}' does not match JOBNAME '{smart_folder_jobname}' (line {line_number}).")

    if job_sub_application != smart_folder_sub_application:
        print(f"JOB SUB_APPLICATION '{job_sub_application}' does not match SMART_FOLDER SUB_APPLICATION '{smart_folder_sub_application}' (line {line_number}).")

def parseXML(xmlFile):
    """Parse the XML file"""
    with open(xmlFile, 'rb') as f:
        xml = f.read()

    root = objectify.fromstring(xml)

    # Regular expression to match the SMART_FOLDER JOBNAME format
    smart_folder_jobname_pattern = re.compile(r'^[A-Za-z0-9]{5}\d{2}[A-Za-z]-\d{3}-[A-Za-z0-9]{3,}$')

    # Regular expression to match the JOB JOBNAME format
    job_jobname_pattern = re.compile(r'^[A-Za-z][A-Za-z0-9]{5}\d{2}[A-Za-z]\d{3}[A-Za-z0-9]{3}\d{3}$')

    # Regular expression to match the APPLICATION format
    application_pattern = re.compile(r'^[A-Za-z0-9]{5}-[A-Za-z0-9]{5}-[A-Za-z]\d$')

    validate_xml_standard(root, smart_folder_jobname_pattern, job_jobname_pattern, application_pattern)

def validate_xml_standard(root, smart_folder_jobname_pattern, job_jobname_pattern, application_pattern):
    # iterate over all SMART_FOLDER elements and check their JOBNAME and APPLICATION attributes
    for smart_folder in root.findall('SMART_FOLDER'):
        jobname = smart_folder.get("JOBNAME")
        application = smart_folder.get("APPLICATION")
        line_number = smart_folder.sourceline

        validate_jobname(jobname, smart_folder_jobname_pattern, "SMART_FOLDER", line_number)
        validate_application(application, application_pattern, "SMART_FOLDER", line_number)

        # iterate over all JOB elements within the SMART_FOLDER and check their JOBNAME and APPLICATION attributes
        for job in smart_folder.findall('JOB'):
            jobname = job.get("JOBNAME")
            application = job.get("APPLICATION")
            line_number = job.sourceline

            validate_jobname(jobname, job_jobname_pattern, "JOB", line_number)
            validate_application(application, application_pattern, "JOB", line_number)
            validate_sub_application(smart_folder, job, line_number)

if __name__ == "__main__":
    f = r'/tmp/xml/test.xml'
    parseXML(f)