import re
import sys
from lxml import etree, objectify


def replace_cc_in_smart_folder_jobname(jobname, new_cc):
    # Regular expression to match the SMART_FOLDER JOBNAME format
    jobname_pattern = re.compile(r'^([A-Za-z0-9]{5})(\d{2})([A-Za-z]-\d{3}-[A-Za-z0-9]{3,})$')
    match = jobname_pattern.match(jobname)
    if match:
        part1 = match.group(1)
        part3 = match.group(3)
        return f"{part1}{new_cc}{part3}"
    return jobname

def replace_e_and_cc_in_job_jobname(jobname, new_e, new_cc):
    # Regular expression to match the JOB JOBNAME format
    jobname_pattern = re.compile(r'^([A-Za-z])([A-Za-z0-9]{5})(\d{2})([A-Za-z]\d{3}[A-Za-z0-9]{3}\d{3})$')
    match = jobname_pattern.match(jobname)
    if match:
        code5car = match.group(2)
        therest = match.group(4)
        return f"{new_e}{code5car}{new_cc}{therest}"
    return jobname

def replace_e_and_c_in_application(application, new_e, new_c):
    # Regular expression to match the APPLICATION format
    application_pattern = re.compile(r'^([A-Za-z0-9]{5}-[A-Za-z0-9]{5}-)([A-Za-z])(\d)$')
    match = application_pattern.match(application)
    if match:
        part1 = match.group(1)
        return f"{part1}{new_e}{new_c}"
    return application

def replace_e_and_c_in_nodeid(nodeid, new_e, new_c):
    # Regular expression to match the NODEID format
    nodeid_pattern = re.compile(r'^(NG_[A-Za-z0-9]{5}-[A-Za-z0-9]{5}-)([A-Za-z])(\d)(_[A-Za-z0-9]+)$')
    match = nodeid_pattern.match(nodeid)
    if match:
        return f"{match.group(1)}{new_e}{new_c}{match.group(4)}"
    return nodeid

def parse_and_replace_xml(xmlFile, new_e, new_cc, new_c, new_datacenter, outputFile):
    """Parse the XML file and replace CC in SMART_FOLDER JOBNAME, E and CC in JOB JOBNAME, and E and C in APPLICATION attributes"""
    with open(xmlFile, 'rb') as f:
        xml = f.read()

    root = objectify.fromstring(xml)

    # iterate over all SMART_FOLDER elements and replace CC in JOBNAME and E and C in APPLICATION attributes
    for smart_folder in root.findall('SMART_FOLDER'):
        if smart_folder.get("DATACENTER"):
            smart_folder.set("DATACENTER", new_datacenter)

        smart_folder_jobname = smart_folder.get("JOBNAME")
        new_smart_folder_jobname = replace_cc_in_smart_folder_jobname(smart_folder_jobname, new_cc)
        smart_folder.set("JOBNAME", new_smart_folder_jobname)

        application = smart_folder.get("APPLICATION")
        new_application = replace_e_and_c_in_application(application, new_e, new_c)
        smart_folder.set("APPLICATION", new_application)

        smart_folder.set("SUB_APPLICATION", new_smart_folder_jobname)

        # iterate over all JOB elements within the SMART_FOLDER and replace E and CC in JOBNAME, E and C in APPLICATION attributes, E and C in NODEID attribute
        for job in smart_folder.findall('JOB'):
            job_jobname = job.get("JOBNAME")
            new_job_jobname = replace_e_and_cc_in_job_jobname(job_jobname, new_e, new_cc)
            job.set("JOBNAME", new_job_jobname)

            application = job.get("APPLICATION")
            new_application = replace_e_and_c_in_application(application, new_e, new_c)
            job.set("APPLICATION", new_application)

            job.set("SUB_APPLICATION", new_smart_folder_jobname)

            nodeid = job.get("NODEID")
            new_nodeid = replace_e_and_c_in_nodeid(nodeid, new_e, new_c)
            job.set("NODEID", new_nodeid)

    # Write the modified XML to the new file
    with open(outputFile, 'wb') as f:
        f.write(etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8'))

if __name__ == "__main__":
    
    xml_file = "test.xml"
    new_e = "D"
    new_c = "3"
    # Ensure new_cc is two digits
    new_cc = new_c.zfill(2)
    new_datacenter = "ZEPEQUINO"
    output_file = "test_replaced.xml"

    if not re.match(r'^[A-Za-z]$', new_e):
        print("Error: new_e must be a single letter")
        sys.exit(1)

    if not re.match(r'^\d{1,2}$', new_cc):
        print("Error: new_cc must be a one or two-digit number")
        sys.exit(1)

    parse_and_replace_xml(xml_file, new_e, new_cc, new_c, new_datacenter, output_file)