"""Generate the mock test dataset required by "Step 15: Testing" of the PDF:

    5 certificates, 5 college notes, 5 Aadhaar/PAN-style mock IDs,
    5 invoices, 5 resumes   ->  25 PDFs + manifest.json (ground truth)

ALL DATA IS FAKE. Names, numbers and companies are invented, and every ID
document is stamped "MOCK / SAMPLE - NOT A REAL DOCUMENT". Never put real
Aadhaar/PAN/passport files into a demo or into GitHub.

Run from the project root:

    python -m database.generate_test_dataset
"""
import json
from pathlib import Path

import pymupdf  # PyMuPDF

OUT_DIR = Path(__file__).resolve().parent.parent / "documents" / "test_dataset"

MOCK_BANNER = "MOCK / SAMPLE - NOT A REAL DOCUMENT"

# slug, category, title, tags, summary, body
DOCS = [
    # ---------------------------------------------------------- certificates
    ("internship_certificate", "certificate", "Internship Certificate - Web Development",
     ["certificate", "internship", "web development", "abc technologies"],
     "Internship certificate from ABC Technologies for web development completed in 2025.",
     "CERTIFICATE OF INTERNSHIP\n\nThis is to certify that Arun Kumar, MCA student, has successfully "
     "completed a three month internship in Web Development at ABC Technologies Pvt Ltd from "
     "June 2025 to August 2025.\n\nDuring the internship he worked on HTML, CSS, JavaScript and "
     "React.js and built a responsive company dashboard. His performance was excellent.\n\n"
     "Issued on 30 August 2025\nHR Manager, ABC Technologies"),
    ("python_course_certificate", "certificate", "Python Programming Course Certificate",
     ["certificate", "python", "course", "programming"],
     "Course completion certificate for Python programming with data structures, OOP and file handling.",
     "CERTIFICATE OF COMPLETION\n\nAwarded to Arun Kumar for completing the 40 hour online course "
     "'Python Programming Masterclass' covering variables, loops, functions, object oriented "
     "programming, file handling and basic data structures.\n\nGrade: A+\nIssued by LearnSmart Academy, "
     "January 2025"),
    ("hackathon_certificate", "certificate", "Hackathon Participation Certificate",
     ["certificate", "hackathon", "participation", "college"],
     "Participation certificate for a 24 hour college hackathon on smart campus ideas.",
     "CERTIFICATE OF PARTICIPATION\n\nThis certificate is presented to Arun Kumar of Team CodeBreakers "
     "for participating in CampusHack 2025, a 24 hour hackathon on smart campus solutions organised by "
     "the Department of Computer Applications.\n\nThe team built a prototype for a smart attendance "
     "tracker. Date: 12 March 2025"),
    ("ml_nptel_certificate", "certificate", "Machine Learning Course Certificate (NPTEL style)",
     ["certificate", "machine learning", "nptel", "ai"],
     "Certificate for completing an eight week machine learning course with a final exam score of 78 percent.",
     "ONLINE COURSE CERTIFICATE\n\nIntroduction to Machine Learning - 8 week course\n\nThis is to certify "
     "that Arun Kumar successfully completed the course and secured 78 percent in the proctored final "
     "exam. Topics: supervised learning, linear regression, classification, decision trees and "
     "clustering.\n\nJuly - September 2025 session"),
    ("cybersecurity_workshop_certificate", "certificate", "Cybersecurity Workshop Certificate",
     ["certificate", "cybersecurity", "workshop", "security"],
     "Certificate for attending a two day cybersecurity workshop on network security and ethical hacking basics.",
     "CERTIFICATE OF ATTENDANCE\n\nArun Kumar attended the two day workshop 'Cybersecurity Essentials' "
     "covering network security, password attacks, phishing awareness, Wireshark packet analysis and "
     "ethical hacking basics.\n\nOrganised by the Cyber Club on 5 and 6 October 2025."),

    # ----------------------------------------------------------- college notes
    ("ml_notes", "notes", "Machine Learning Notes - Semester 2",
     ["notes", "machine learning", "mca", "ai", "semester 2"],
     "Notes explaining supervised learning, classification, regression and clustering with examples.",
     "MACHINE LEARNING NOTES - MCA SEMESTER 2\n\n1. Supervised learning: the model learns from labelled "
     "data. Examples are spam detection and house price prediction.\n\n2. Classification predicts a "
     "category (logistic regression, decision trees, SVM). Regression predicts a number (linear "
     "regression).\n\n3. Unsupervised learning finds structure in unlabelled data. K-means clustering "
     "groups similar points.\n\n4. Overfitting happens when a model memorises training data. Use "
     "cross validation and regularisation to reduce it."),
    ("os_notes", "notes", "Operating Systems Notes",
     ["notes", "operating systems", "mca", "process", "scheduling"],
     "Notes on processes, threads, CPU scheduling algorithms, deadlocks and memory management.",
     "OPERATING SYSTEMS NOTES\n\nProcess vs thread: a process has its own memory, threads share "
     "memory inside a process.\n\nCPU scheduling: FCFS, Shortest Job First, Round Robin and priority "
     "scheduling.\n\nDeadlock needs four conditions: mutual exclusion, hold and wait, no preemption "
     "and circular wait.\n\nMemory management: paging, segmentation and virtual memory with page "
     "replacement (FIFO, LRU)."),
    ("dbms_notes", "notes", "DBMS Notes - Normalization and SQL",
     ["notes", "dbms", "sql", "normalization", "database"],
     "Database notes covering ER model, normalization up to BCNF, SQL joins and transactions.",
     "DBMS NOTES\n\nER model: entities, attributes and relationships.\n\nNormalization removes "
     "redundancy: 1NF atomic values, 2NF no partial dependency, 3NF no transitive dependency, "
     "BCNF every determinant is a candidate key.\n\nSQL: SELECT, INSERT, UPDATE, DELETE, INNER JOIN, "
     "LEFT JOIN, GROUP BY and HAVING.\n\nTransactions follow ACID: atomicity, consistency, isolation, "
     "durability."),
    ("cn_notes", "notes", "Computer Networks Notes",
     ["notes", "computer networks", "osi", "tcp/ip", "networking"],
     "Notes on the OSI and TCP/IP models, IP addressing, routing, DNS and common protocols.",
     "COMPUTER NETWORKS NOTES\n\nOSI model has seven layers: physical, data link, network, transport, "
     "session, presentation and application.\n\nTCP is reliable and connection oriented, UDP is fast "
     "and connectionless.\n\nIP addressing: IPv4 has 32 bits, IPv6 has 128 bits. Subnetting splits a "
     "network into smaller ones.\n\nDNS converts domain names to IP addresses. HTTP and HTTPS carry web "
     "traffic."),
    ("ds_notes", "notes", "Data Structures and Algorithms Notes",
     ["notes", "data structures", "algorithms", "stack", "tree"],
     "Notes on arrays, linked lists, stacks, queues, trees, graphs and sorting algorithms with complexity.",
     "DATA STRUCTURES NOTES\n\nLinear structures: array, linked list, stack (LIFO) and queue (FIFO).\n\n"
     "Trees: binary search tree, AVL tree, heap. Graphs: BFS and DFS traversal.\n\nSorting: bubble "
     "sort O(n^2), merge sort O(n log n), quick sort average O(n log n).\n\nBinary search works on "
     "sorted data in O(log n)."),

    # ------------------------------------------------------------- mock IDs
    ("mock_aadhaar_card", "identity", "Mock Aadhaar Card",
     ["identity", "aadhaar", "government id", "mock"],
     "Mock Aadhaar identity card with a fake 12 digit number for demo purposes only.",
     f"*** {MOCK_BANNER} ***\n\nGOVERNMENT OF INDIA (SAMPLE LAYOUT)\nAADHAAR\n\nName: Priya Sharma "
     "(fictional)\nDate of Birth: 01/01/2000\nGender: Female\nAadhaar Number: 0000 0000 0001\n\n"
     "Address: 12 Sample Street, Test City, Tamil Nadu"),
    ("mock_pan_card", "identity", "Mock PAN Card",
     ["identity", "pan", "tax", "mock"],
     "Mock PAN card with a fake permanent account number for demo purposes only.",
     f"*** {MOCK_BANNER} ***\n\nINCOME TAX DEPARTMENT (SAMPLE LAYOUT)\nPERMANENT ACCOUNT NUMBER\n\n"
     "Name: Priya Sharma (fictional)\nFather's Name: Sample Father\nDate of Birth: 01/01/2000\n"
     "PAN: ZZZZZ0000Z"),
    ("mock_passport", "identity", "Mock Passport",
     ["identity", "passport", "travel", "mock"],
     "Mock passport data page with fictional details for demo purposes only.",
     f"*** {MOCK_BANNER} ***\n\nREPUBLIC OF INDIA - PASSPORT (SAMPLE LAYOUT)\n\nType: P   Country "
     "Code: IND\nPassport No: Z0000000\nSurname: Sharma   Given Name: Priya\nNationality: Indian\n"
     "Date of Issue: 01/01/2024   Date of Expiry: 31/12/2033\nPlace of Issue: Test City"),
    ("mock_driving_licence", "identity", "Mock Driving Licence",
     ["identity", "driving licence", "transport", "mock"],
     "Mock driving licence with fictional holder details, valid for light motor vehicles.",
     f"*** {MOCK_BANNER} ***\n\nDRIVING LICENCE (SAMPLE LAYOUT)\n\nLicence No: TN00 00000000000\n"
     "Name: Priya Sharma (fictional)\nClass of Vehicle: LMV, MCWG\nValid Till: 31/12/2040\n"
     "Issuing Authority: Test RTO"),
    ("mock_voter_id", "identity", "Mock Voter ID Card",
     ["identity", "voter id", "election", "mock"],
     "Mock voter identity card with a fictional EPIC number for demo purposes only.",
     f"*** {MOCK_BANNER} ***\n\nELECTION COMMISSION OF INDIA (SAMPLE LAYOUT)\nELECTOR PHOTO "
     "IDENTITY CARD\n\nEPIC No: ABC0000000\nElector Name: Priya Sharma (fictional)\nAge: 25   "
     "Sex: Female\nConstituency: Sample Constituency"),

    # --------------------------------------------------------------- invoices
    ("laptop_invoice", "invoice", "Laptop Purchase Invoice",
     ["invoice", "laptop", "electronics", "finance", "purchase"],
     "Tax invoice for a laptop purchase with a total of Rs. 58,990 including GST and a one year warranty.",
     "TAX INVOICE\n\nTechMart Electronics, Test City\nInvoice No: TM-2025-0457   Date: 14 July 2025\n\n"
     "Item: Laptop 15 inch, 16 GB RAM, 512 GB SSD   Qty: 1\nPrice: Rs. 50,000\nGST 18%: Rs. 9,000\n"
     "Discount: Rs. 10 (coupon)\nTOTAL: Rs. 58,990\n\nWarranty: 1 year manufacturer warranty."),
    ("grocery_receipt", "invoice", "Grocery Store Receipt",
     ["invoice", "grocery", "receipt", "finance", "shopping"],
     "Supermarket receipt for groceries including rice, milk, vegetables and fruits totalling Rs. 1,245.",
     "FRESH BASKET SUPERMARKET\nReceipt No: 88231   Date: 02 September 2025\n\nRice 5 kg   Rs. 420\n"
     "Milk 2 litre   Rs. 120\nVegetables   Rs. 310\nFruits   Rs. 275\nCooking oil 1 litre   Rs. 120\n\n"
     "TOTAL: Rs. 1,245\nPaid by UPI"),
    ("electricity_bill", "invoice", "Electricity Bill - August 2025",
     ["invoice", "electricity bill", "utility", "finance", "bill"],
     "Monthly electricity bill for August 2025 showing 312 units consumed and an amount due of Rs. 1,860.",
     "STATE ELECTRICITY BOARD (SAMPLE)\nELECTRICITY BILL - AUGUST 2025\n\nConsumer No: 000-123-456\n"
     "Units consumed: 312 kWh\nEnergy charges: Rs. 1,560\nFixed charges: Rs. 300\n\nAMOUNT DUE: "
     "Rs. 1,860\nDue date: 25 September 2025"),
    ("broadband_bill", "invoice", "Broadband Internet Bill",
     ["invoice", "broadband", "internet", "utility", "bill"],
     "Monthly broadband internet bill for a 100 Mbps fibre plan costing Rs. 826 including taxes.",
     "FIBRENET BROADBAND (SAMPLE)\nINTERNET BILL - SEPTEMBER 2025\n\nPlan: 100 Mbps unlimited fibre\n"
     "Plan charges: Rs. 700\nGST: Rs. 126\n\nTOTAL PAYABLE: Rs. 826\nBilling period: 1 to 30 "
     "September 2025"),
    ("course_fee_receipt", "invoice", "Online Course Fee Receipt",
     ["invoice", "course fee", "education", "receipt", "finance"],
     "Payment receipt for an online cybersecurity course fee of Rs. 4,999 paid by card.",
     "LEARNSMART ACADEMY - PAYMENT RECEIPT\n\nReceipt No: LS-77102   Date: 20 August 2025\n\n"
     "Course: Ethical Hacking and Network Security\nFee: Rs. 4,999\nPayment mode: Debit card\n"
     "Status: PAID"),

    # ---------------------------------------------------------------- resumes
    ("resume_software_developer", "resume", "Resume - Software Developer",
     ["resume", "cv", "software developer", "python", "react"],
     "Resume of an MCA fresher applying for software developer roles with Python, React and SQL skills.",
     "ARUN KUMAR - SOFTWARE DEVELOPER\n\nObjective: Fresher seeking a software developer role.\n\n"
     "Education: MCA (pursuing), BCA 2024\nSkills: Python, JavaScript, React.js, SQL, Git\n\nProjects: "
     "OmniLife AI personal document search, Student management system\n\nExperience: Web development "
     "intern, ABC Technologies, 2025"),
    ("resume_data_analyst", "resume", "Resume - Data Analyst",
     ["resume", "cv", "data analyst", "excel", "power bi"],
     "Resume for a data analyst fresher with Excel, SQL, Power BI and Python pandas experience.",
     "ARUN KUMAR - DATA ANALYST\n\nObjective: Entry level data analyst role.\n\nSkills: Excel, SQL, "
     "Power BI, Python (pandas, matplotlib), statistics\n\nProjects: Sales dashboard in Power BI, "
     "COVID data analysis in Python\n\nEducation: MCA (pursuing)"),
    ("resume_placement", "resume", "Placement Resume - Campus Drive",
     ["resume", "cv", "placement", "campus", "fresher"],
     "One page placement resume prepared for campus recruitment drives, listing academics and projects.",
     "PLACEMENT RESUME - CAMPUS DRIVE 2026\n\nArun Kumar | MCA Final Year\nCGPA: 8.4\n\nAcademic "
     "projects: OmniLife AI, Library management system\nCertifications: Python, Machine Learning, "
     "Cybersecurity workshop\nStrengths: quick learner, teamwork, problem solving"),
    ("resume_cybersecurity", "resume", "Resume - Cybersecurity Analyst Fresher",
     ["resume", "cv", "cybersecurity", "security analyst", "fresher"],
     "Resume of a cybersecurity analyst fresher with network security, Wireshark and SIEM basics.",
     "ARUN KUMAR - CYBERSECURITY ANALYST (FRESHER)\n\nSkills: network security, Wireshark, Nmap, "
     "Linux, basics of SIEM, OWASP Top 10, Python scripting\n\nCertifications: Cybersecurity "
     "Essentials workshop\nLabs: TryHackMe beginner paths, DVWA practice"),
    ("resume_web_developer", "resume", "Resume - Web Developer Fresher",
     ["resume", "cv", "web developer", "html", "css"],
     "Resume for a web developer fresher skilled in HTML, CSS, JavaScript, React and Tailwind CSS.",
     "ARUN KUMAR - WEB DEVELOPER (FRESHER)\n\nSkills: HTML5, CSS3, JavaScript, React.js, Tailwind CSS, "
     "REST APIs\n\nProjects: Portfolio website, Responsive company dashboard\nInternship: ABC "
     "Technologies, web development, 2025"),
]

# Natural language searches with the document(s) a good search must return.
#   keyword    = contains words that literally appear in the document title/tags
#   paraphrase = same meaning, different words -> only semantic search can do this
QUERIES = [
    ("Show my internship certificate", ["internship_certificate"], "keyword"),
    ("Find Aadhaar", ["mock_aadhaar_card"], "keyword"),
    ("Machine Learning Notes", ["ml_notes"], "keyword"),
    ("Show my CV", ["resume_software_developer", "resume_data_analyst", "resume_placement",
                    "resume_cybersecurity", "resume_web_developer"], "keyword"),
    ("Passport", ["mock_passport"], "keyword"),
    ("PAN card", ["mock_pan_card"], "keyword"),
    ("electricity bill", ["electricity_bill"], "keyword"),
    ("how much did my laptop cost", ["laptop_invoice"], "keyword"),
    ("database normalization notes", ["dbms_notes"], "keyword"),
    ("cybersecurity workshop attendance", ["cybersecurity_workshop_certificate"], "keyword"),
    ("placement resume", ["resume_placement"], "keyword"),
    ("internet bill", ["broadband_bill"], "keyword"),
    # --- same meaning, different words ---
    ("proof that I worked at a company last summer", ["internship_certificate"], "paraphrase"),
    ("what do I owe the power company", ["electricity_bill"], "paraphrase"),
    ("papers to apply for jobs", ["resume_software_developer", "resume_data_analyst",
                                  "resume_placement", "resume_cybersecurity",
                                  "resume_web_developer"], "paraphrase"),
    ("how do computers share data over the internet", ["cn_notes"], "paraphrase"),
    ("government issued ID with a 12 digit number", ["mock_aadhaar_card"], "paraphrase"),
    ("my notes about algorithms that learn patterns", ["ml_notes"], "paraphrase"),
]


def make_pdf(path: Path, title: str, body: str) -> None:
    doc = pymupdf.open()
    page = doc.new_page()  # A4
    rect = pymupdf.Rect(54, 54, 541, 788)
    leftover = page.insert_textbox(rect, f"{title}\n\n{body}", fontsize=11, fontname="helv")
    if leftover < 0:
        raise ValueError(f"Text too long for one page: {path.name}")
    doc.save(path)
    doc.close()


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {"documents": [], "queries": []}

    for slug, category, title, tags, summary, body in DOCS:
        filename = f"{slug}.pdf"
        make_pdf(OUT_DIR / filename, title, body)
        manifest["documents"].append({
            "slug": slug, "filename": filename, "title": title,
            "category": category, "tags": tags, "summary": summary,
        })

    for query, expected, kind in QUERIES:
        manifest["queries"].append({"query": query, "expected": expected, "kind": kind})

    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Created {len(DOCS)} PDFs and manifest.json in {OUT_DIR}")


if __name__ == "__main__":
    main()
