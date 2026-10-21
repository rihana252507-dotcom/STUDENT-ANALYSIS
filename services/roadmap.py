"""
CampusIQ – Career Roadmap & Job Preparation Service
Provides data models, role definitions, skill catalogs, learning roadmaps,
project recommendations, placement preparation checklists, and verified learning resources.
"""

from typing import Dict, List, Any

# ==============================================================================
# 1. SUPPORTED TARGET CAREER ROLES & TECHNICAL SPECIFICATIONS
# ==============================================================================

CAREER_ROLES: Dict[str, Dict[str, Any]] = {
    "Software Developer": {
        "title": "Software Developer",
        "category": "Software Engineering",
        "description": "Design, develop, test, and maintain robust software applications and algorithmic solutions.",
        "suitable_branches": ["CSE", "IT", "AIML", "AIDS", "ECE", "EEE"],
        "core_skills": [
            "Programming (Python, Java, or C++)",
            "Data Structures & Algorithms",
            "Object-Oriented Programming (OOP)",
            "Git & GitHub Version Control",
            "SQL & Relational Databases",
            "Debugging & Unit Testing"
        ],
        "optional_skills": [
            "RESTful API Design",
            "Linux / Unix Shell",
            "Basic System Design",
            "CI/CD Pipelines",
            "Docker Fundamentals"
        ],
        "stages": [
            {
                "stage_num": 1,
                "title": "Programming & Problem-Solving Fundamentals",
                "focus": "Master one primary language and algorithmic thinking",
                "time_allocation": "Week 1 - 2 (approx. 20-25 hrs)",
                "topics": ["Variables, loops, functions, OOP concepts", "Time & Space complexity (Big-O)", "Basic arrays, strings, and recursion"],
                "practical_tasks": ["Solve 30 easy algorithmic questions on LeetCode/HackerRank", "Implement classic sorting algorithms (Merge, Quick, Binary Search) from scratch"],
                "completion_goal": "Comfortably solve arrays, strings, and hash map problems within 25 minutes.",
                "resources": [
                    {"name": "Python Official Documentation", "url": "https://docs.python.org/3/", "type": "Documentation (Free)"},
                    {"name": "GeeksforGeeks DSA Self-Paced", "url": "https://www.geeksforgeeks.org/learn-data-structures-and-algorithms-dsa-tutorial/", "type": "Tutorials & Practice (Free)"}
                ]
            },
            {
                "stage_num": 2,
                "title": "Core Technical Disciplines & Databases",
                "focus": "Data structures, relational databases, and clean code",
                "time_allocation": "Week 3 - 4 (approx. 25-30 hrs)",
                "topics": ["Linked lists, stacks, queues, trees, graphs", "SQL queries, joins, indexing, normalization", "Git branching, merge requests, commit best practices"],
                "practical_tasks": ["Write complex SQL queries with multiple table joins and aggregations", "Push all code assignments to a public GitHub repository with informative READMEs"],
                "completion_goal": "Traverse binary trees and implement BFS/DFS graphs confidently.",
                "resources": [
                    {"name": "SQLZoo Interactive SQL Tutorial", "url": "https://sqlzoo.net/", "type": "Interactive Practice (Free)"},
                    {"name": "Git Official Documentation", "url": "https://git-scm.com/doc", "type": "Reference (Free)"}
                ]
            },
            {
                "stage_num": 3,
                "title": "Practical Application & Project Building",
                "focus": "Build tangible, full-fledged software projects with databases",
                "time_allocation": "Week 5 - 6 (approx. 30 hrs)",
                "topics": ["RESTful API architecture", "CRUD operations with database integration", "Input validation and error handling"],
                "practical_tasks": ["Build a complete REST API or desktop application with authentication", "Write automated unit tests covering core business logic"],
                "completion_goal": "Deploy a working project to a cloud platform (Render/Vercel) with public source code.",
                "resources": [
                    {"name": "MDN Web Docs (HTTP & APIs)", "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP", "type": "Documentation (Free)"}
                ]
            },
            {
                "stage_num": 4,
                "title": "Placement Aptitude & Technical Interviews",
                "focus": "Campus placement tests, speed coding, and CS fundamentals",
                "time_allocation": "Week 7 - 8 (approx. 25 hrs)",
                "topics": ["Quantitative aptitude (Percentages, P&L, Time & Work)", "Logical reasoning & verbal ability", "Core CS subjects: OS, DBMS, Computer Networks"],
                "practical_tasks": ["Complete 5 timed full-length aptitude mock tests", "Practice explaining code complexity out loud during mock peer interviews"],
                "completion_goal": "Score >= 75% on quantitative mock tests and answer OS/DBMS questions fluently.",
                "resources": [
                    {"name": "IndiaBIX Quantitative & Logical Aptitude", "url": "https://www.indiabix.com/", "type": "Practice Portal (Free)"}
                ]
            },
            {
                "stage_num": 5,
                "title": "Resume Finalization & Verified Applications",
                "focus": "Job hunting, technical resume tailoring, and behavioral interview prep",
                "time_allocation": "Week 9+ (Continuous)",
                "topics": ["One-page clean engineering resume", "STAR method for HR/Behavioral questions", "Official employer career portals"],
                "practical_tasks": ["Tailor your resume highlighting GitHub links and live demos", "Apply directly via official corporate careers pages (TCS, Infosys, Wipro, Accenture)"],
                "completion_goal": "Submit verified applications with customized project bullet points.",
                "resources": [
                    {"name": "TCS Official Careers Portal", "url": "https://www.tcs.com/careers", "type": "Official Careers (Free)"},
                    {"name": "Infosys Careers", "url": "https://www.infosys.com/careers.html", "type": "Official Careers (Free)"}
                ]
            }
        ],
        "projects": [
            {
                "title": "Automated Student Attendance & Risk System",
                "level": "Beginner / Intermediate",
                "problem": "Manual attendance calculation is error-prone and fails to identify students at risk of exam debarment in advance.",
                "skills_practiced": ["Python / Java", "SQLite / MySQL", "File I/O", "CLI or GUI"],
                "features": ["Student profile record creation", "Automated percentage calculation", "Warning flags for attendance below 75%", "CSV report generation"],
                "deliverables": "Clean modular code on GitHub with unit tests and a structured README.",
                "interview_pitch": "I built an automated attendance tracking engine that computes statutory attendance compliance in O(N) time and flags at-risk students before final examinations."
            },
            {
                "title": "Campus Resource Scheduling REST API",
                "level": "Intermediate",
                "problem": "College lab computers, seminar halls, and project rooms face double-booking conflicts.",
                "skills_practiced": ["REST API (Flask/Express/Spring Boot)", "Relational Database", "JWT Authentication"],
                "features": ["User role management (Student vs Admin)", "Conflict-detection algorithm for slot bookings", "Filtering by department and date"],
                "deliverables": "Live API deployed on cloud with Postman documentation collection.",
                "interview_pitch": "Engineered a concurrent booking API with transactional integrity to prevent race conditions during peak seminar hall reservation periods."
            },
            {
                "title": "Collaborative Code Snippet & Review Platform",
                "level": "Advanced",
                "problem": "Student study groups need a simple platform to share code snippets, review peers' logic, and run automated syntax checks.",
                "skills_practiced": ["Full-Stack Architecture", "Database Transactions", "Code Highlighting", "CI/CD"],
                "features": ["Syntax-highlighted code editor", "Tagging by programming language", "Upvoting and inline code comments", "Rate-limiting middleware"],
                "deliverables": "Full-stack web application hosted with public demo and documentation.",
                "interview_pitch": "Created a peer-to-peer developer workspace supporting multi-language syntax formatting and token-based authenticated code collaboration."
            }
        ]
    },

    "Full-Stack Developer": {
        "title": "Full-Stack Developer",
        "category": "Web Development",
        "description": "Build end-to-end web applications encompassing interactive client user interfaces, server-side APIs, and robust database layers.",
        "suitable_branches": ["CSE", "IT", "AIML", "AIDS"],
        "core_skills": [
            "HTML5, CSS3 & Responsive Design",
            "JavaScript (ES6+) Fundamentals",
            "Frontend Framework (React, Vue, or Angular)",
            "Backend Framework (Node.js/Express, Python/Flask, or Django)",
            "SQL & Relational Databases",
            "Git & GitHub Version Control"
        ],
        "optional_skills": [
            "MongoDB / NoSQL",
            "REST & GraphQL APIs",
            "JWT & OAuth Security",
            "Docker & Containerization",
            "Cloud Deployment (AWS/Vercel/Render)"
        ],
        "stages": [
            {
                "stage_num": 1,
                "title": "Modern Frontend Core",
                "focus": "HTML5, CSS3, Flexbox/Grid, and JavaScript ES6+",
                "time_allocation": "Week 1 - 2 (approx. 25 hrs)",
                "topics": ["Semantic HTML & accessibility", "Responsive layouts with CSS Flexbox & Grid", "DOM manipulation, event handling, async/await, Fetch API"],
                "practical_tasks": ["Build 2 responsive multi-page landing pages without CSS frameworks", "Create an interactive browser-based dashboard consuming a public API"],
                "completion_goal": "Write vanilla JavaScript asynchronously handling JSON APIs with robust error states.",
                "resources": [
                    {"name": "MDN Web Docs - Learn Web Development", "url": "https://developer.mozilla.org/en-US/docs/Learn", "type": "Documentation (Free)"},
                    {"name": "JavaScript.info", "url": "https://javascript.info/", "type": "Interactive Guide (Free)"}
                ]
            },
            {
                "stage_num": 2,
                "title": "Frontend Component Engineering (React / Vue)",
                "focus": "Component hierarchy, state management, and client routing",
                "time_allocation": "Week 3 - 4 (approx. 25 hrs)",
                "topics": ["React functional components & Hooks (useState, useEffect, useMemo)", "Client-side routing (React Router)", "Global state management and form handling"],
                "practical_tasks": ["Develop a multi-view Single Page Application with dynamic filtering", "Implement debounced search and pagination"],
                "completion_goal": "Build modular component systems with clean state decoupling.",
                "resources": [
                    {"name": "React Official Documentation", "url": "https://react.dev/", "type": "Documentation (Free)"}
                ]
            },
            {
                "stage_num": 3,
                "title": "Server-Side Engineering & REST APIs",
                "focus": "Backend endpoints, database modeling, and authentication",
                "time_allocation": "Week 5 - 6 (approx. 30 hrs)",
                "topics": ["Node.js/Express or Python/Flask servers", "Relational database schema modeling with SQL", "JWT token-based authentication & password hashing"],
                "practical_tasks": ["Construct a secure CRUD API with middleware authorization", "Connect frontend SPA to backend REST services with CORS protection"],
                "completion_goal": "Deliver an end-to-end working system with secure credentials handling.",
                "resources": [
                    {"name": "Node.js Official Documentation", "url": "https://nodejs.org/en/docs", "type": "Documentation (Free)"}
                ]
            },
            {
                "stage_num": 4,
                "title": "Full-Stack Deployment & Aptitude Prep",
                "focus": "Cloud hosting, CI/CD, and placement round readiness",
                "time_allocation": "Week 7 - 8 (approx. 25 hrs)",
                "topics": ["Cloud deployment on Render/Vercel", "Quantitative aptitude & logical puzzles", "Technical interview questions on browser rendering & backend life cycles"],
                "practical_tasks": ["Deploy full-stack project live with custom domain or free cloud tier", "Solve 50 coding problems focusing on string and hash map manipulation"],
                "completion_goal": "Demonstrate a live URL during interviews and answer full-stack architecture questions.",
                "resources": [
                    {"name": "Render Documentation (Deployment)", "url": "https://render.com/docs", "type": "Documentation (Free)"}
                ]
            },
            {
                "stage_num": 5,
                "title": "Portfolio Showcase & Campus Placement Applications",
                "focus": "Interactive portfolio, clean GitHub repositories, and interviews",
                "time_allocation": "Week 9+ (Continuous)",
                "topics": ["Portfolio website showcasing live demos", "STAR interview technique for technical presentations", "Application submission on employer portals"],
                "practical_tasks": ["Assemble a clean technical resume featuring GitHub links", "Apply for Full-Stack Developer openings through official employer drives"],
                "completion_goal": "Present working full-stack applications with architectural trade-offs explained.",
                "resources": [
                    {"name": "Cognizant Careers Portal", "url": "https://careers.cognizant.com", "type": "Official Careers (Free)"}
                ]
            }
        ],
        "projects": [
            {
                "title": "College Placement & Internship Portal",
                "level": "Intermediate",
                "problem": "Students miss campus recruitment drives due to fragmented notices spread across messaging groups.",
                "skills_practiced": ["React/Vue", "Node.js or Python", "PostgreSQL / SQLite", "JWT Auth"],
                "features": ["Student and recruiter role portals", "Application status tracker (Applied, Interview, Selected)", "Skill-based job eligibility filters"],
                "deliverables": "Live web application with responsive UI, authenticated user dashboards, and GitHub repository.",
                "interview_pitch": "Architected a dual-role placement portal facilitating structured application workflows with JWT authentication and responsive data tables."
            },
            {
                "title": "E-Commerce / Digital Marketplace Prototype",
                "level": "Advanced",
                "problem": "Small campus entrepreneurs need a localized platform to sell books, stationery, and electronics securely.",
                "skills_practiced": ["Full-Stack Framework", "Database Transactions", "Payment Mock Workflow", "REST API"],
                "features": ["Product search with price and category filters", "Shopping cart state persistence", "Order placement history", "Admin stock management"],
                "deliverables": "Public live deployment with seeded database and documented REST endpoints.",
                "interview_pitch": "Built an ACID-compliant digital marketplace featuring optimistic UI updates, inventory management, and persistent cart sessions."
            }
        ]
    },

    "Data Analyst": {
        "title": "Data Analyst",
        "category": "Data & Analytics",
        "description": "Transform raw business and operational data into actionable visual insights, interactive dashboards, and executive intelligence.",
        "suitable_branches": ["CSE", "IT", "AIML", "AIDS", "ECE", "EEE", "Mechanical", "Civil"],
        "core_skills": [
            "Advanced Microsoft Excel & Google Sheets",
            "SQL (Window Functions, Aggregations, Subqueries)",
            "Python for Data Analysis (Pandas, NumPy)",
            "Data Visualization (Power BI or Tableau, Matplotlib/Seaborn)",
            "Descriptive Statistics & Exploratory Data Analysis (EDA)",
            "Analytical & Business Problem-Solving"
        ],
        "optional_skills": [
            "R Programming",
            "Data Storytelling & Executive Presentations",
            "Basic ETL Pipelines",
            "Git for Version Control"
        ],
        "stages": [
            {
                "stage_num": 1,
                "title": "Spreadsheets & Business Foundations",
                "focus": "Master Excel formulas, pivot tables, and data hygiene",
                "time_allocation": "Week 1 - 2 (approx. 20 hrs)",
                "topics": ["VLOOKUP/XLOOKUP, INDEX-MATCH", "Pivot tables, calculated fields, and slicing", "Data validation, conditional formatting, chart design"],
                "practical_tasks": ["Build a dynamic financial or operational dashboard in Excel", "Clean a messy 5,000-row real-world dataset removing nulls and duplicates"],
                "completion_goal": "Create executive-ready multi-tab summary models in Excel within 1 hour.",
                "resources": [
                    {"name": "Microsoft Excel Documentation", "url": "https://support.microsoft.com/en-us/excel", "type": "Documentation (Free)"}
                ]
            },
            {
                "stage_num": 2,
                "title": "Advanced SQL for Analytics",
                "focus": "Complex queries, window functions, and database extraction",
                "time_allocation": "Week 3 - 4 (approx. 25 hrs)",
                "topics": ["INNER/LEFT/OUTER JOINs and subqueries", "Window functions: ROW_NUMBER(), RANK(), DENSE_RANK(), LAG(), LEAD()", "GROUP BY, HAVING, and cumulative aggregations"],
                "practical_tasks": ["Solve 40 SQL challenges on LeetCode/HackerRank", "Query multi-table retail or student databases to extract cohort retention metrics"],
                "completion_goal": "Write error-free multi-join SQL queries with CTEs and window partitions.",
                "resources": [
                    {"name": "Mode Analytics SQL Tutorial", "url": "https://mode.com/sql-tutorial/", "type": "Interactive Course (Free)"}
                ]
            },
            {
                "stage_num": 3,
                "title": "Python Data Wrangling & EDA",
                "focus": "Pandas, NumPy, and statistical exploration",
                "time_allocation": "Week 5 - 6 (approx. 25 hrs)",
                "topics": ["Pandas DataFrames, filtering, grouping, merging", "Handling missing values, outlier detection, data type casting", "Visualizations with Seaborn & Matplotlib"],
                "practical_tasks": ["Perform full Exploratory Data Analysis (EDA) on an open Kaggle dataset", "Publish a structured Jupyter Notebook documenting business hypotheses"],
                "completion_goal": "Execute end-to-end data pipelines from CSV ingestion to insight summary.",
                "resources": [
                    {"name": "Pandas Official Documentation", "url": "https://pandas.pydata.org/docs/", "type": "Documentation (Free)"},
                    {"name": "Kaggle Datasets & Notebooks", "url": "https://www.kaggle.com/datasets", "type": "Open Datasets (Free)"}
                ]
            },
            {
                "stage_num": 4,
                "title": "Business Intelligence Dashboards (Power BI / Tableau)",
                "focus": "Interactive reporting, DAX, and storytelling",
                "time_allocation": "Week 7 - 8 (approx. 25 hrs)",
                "topics": ["Power BI data modeling & star schema", "Basic DAX measures (CALCULATE, SUMX, RELATED)", "Interactive dashboard layout, KPIs, and drill-downs"],
                "practical_tasks": ["Build an interactive sales or academic telemetry dashboard in Power BI/Tableau", "Record a 3-minute video presentation explaining the business findings"],
                "completion_goal": "Deliver polished, interactive BI reports with clear KPI cards and slicers.",
                "resources": [
                    {"name": "Microsoft Power BI Guided Learning", "url": "https://learn.microsoft.com/en-us/power-bi/", "type": "Documentation & Tutorials (Free)"}
                ]
            },
            {
                "stage_num": 5,
                "title": "Case Study Preparation & Placement Rounds",
                "focus": "Aptitude tests, business case interviews, and resume positioning",
                "time_allocation": "Week 9+ (Continuous)",
                "topics": ["Quantitative aptitude & data interpretation (DI) sets", "Business case study frameworks (Root Cause, Market Sizing)", "Resume portfolio showcasing GitHub and Tableau Public links"],
                "practical_tasks": ["Solve 20 complex Data Interpretation graph/chart sets", "Apply to analytics roles at Deloitte, KPMG, Accenture, and Mu Sigma"],
                "completion_goal": "Fluently walk interviewers through a complete portfolio project from raw data to recommendation.",
                "resources": [
                    {"name": "Accenture Careers", "url": "https://www.accenture.com/in-en/careers", "type": "Official Careers (Free)"}
                ]
            }
        ],
        "projects": [
            {
                "title": "University Academic Attrition & Risk Dashboard",
                "level": "Intermediate",
                "problem": "Academic administrators need to visualize which courses experience high backlog rates and attendance drops.",
                "skills_practiced": ["SQL", "Power BI / Tableau", "Excel", "Data Modeling"],
                "features": ["Department-wise attendance vs CGPA correlation", "Backlog distribution heat maps", "Early warning risk categorizations"],
                "deliverables": "Power BI dashboard (.pbix) or Tableau Public link with clean documentation.",
                "interview_pitch": "Engineered an interactive academic intelligence dashboard analyzing 1,000+ student records to isolate the primary drivers of course failure rates."
            },
            {
                "title": "Retail E-Commerce Sales & Cohort Retention Analysis",
                "level": "Intermediate / Advanced",
                "problem": "An online retailer experiences high customer acquisition costs but low repeat order rates.",
                "skills_practiced": ["Python (Pandas, Seaborn)", "SQL (Window Functions)", "Jupyter Notebook"],
                "features": ["Monthly customer cohort retention matrix", "RFM (Recency, Frequency, Monetary) segmentation", "Product affinity analysis"],
                "deliverables": "Documented Jupyter Notebook on GitHub with clear executive takeaway slides.",
                "interview_pitch": "Performed customer cohort analysis in Python and SQL revealing that 60% of churn occurred within 45 days of initial purchase, leading to targeted retention recommendations."
            }
        ]
    },

    "AI/ML Engineer": {
        "title": "AI/ML Engineer",
        "category": "Artificial Intelligence",
        "description": "Develop, train, evaluate, and deploy machine learning and deep learning models to automate predictions and power intelligent systems.",
        "suitable_branches": ["AIML", "AIDS", "CSE", "IT", "ECE"],
        "core_skills": [
            "Python Programming (NumPy, Pandas, Scikit-Learn)",
            "Mathematics for ML (Linear Algebra, Calculus, Probability & Statistics)",
            "Supervised & Unsupervised Machine Learning Algorithms",
            "Model Evaluation Metrics (Precision, Recall, F1-Score, ROC-AUC)",
            "Data Preprocessing & Feature Engineering",
            "Git & GitHub Version Control"
        ],
        "optional_skills": [
            "Deep Learning (PyTorch or TensorFlow)",
            "Natural Language Processing (NLP) & LLM Prompting",
            "Model Deployment (Flask/FastAPI, Docker)",
            "MLOps Fundamentals (MLflow, Model Monitoring)"
        ],
        "stages": [
            {
                "stage_num": 1,
                "title": "Mathematical Foundations & Python for ML",
                "focus": "Linear algebra, multivariable calculus, probability, and NumPy",
                "time_allocation": "Week 1 - 2 (approx. 25 hrs)",
                "topics": ["Vectors, matrices, dot products, eigenvalues", "Probability distributions, Bayes' Theorem, hypothesis testing", "Vectorized computing with NumPy and data manipulation with Pandas"],
                "practical_tasks": ["Implement linear regression with gradient descent from scratch in pure NumPy", "Calculate summary statistics and probability densities on real datasets"],
                "completion_goal": "Understand gradient updates and cost functions mathematically without high-level library abstractions.",
                "resources": [
                    {"name": "3Blue1Brown - Essence of Linear Algebra", "url": "https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab", "type": "Video Series (Free)"},
                    {"name": "Scikit-Learn Documentation", "url": "https://scikit-learn.org/stable/", "type": "Documentation (Free)"}
                ]
            },
            {
                "stage_num": 2,
                "title": "Classical Machine Learning Algorithms",
                "focus": "Supervised and unsupervised models with Scikit-Learn",
                "time_allocation": "Week 3 - 4 (approx. 30 hrs)",
                "topics": ["Regression: Linear, Ridge, Lasso", "Classification: Logistic Regression, Decision Trees, Random Forests, SVM", "Clustering & Dimensionality Reduction: K-Means, PCA"],
                "practical_tasks": ["Train classification and regression models on benchmark Kaggle datasets", "Implement cross-validation, hyperparameter tuning (GridSearchCV), and feature scaling"],
                "completion_goal": "Select appropriate algorithms based on problem type, dataset size, and variance-bias trade-off.",
                "resources": [
                    {"name": "Kaggle Learn - Machine Learning", "url": "https://www.kaggle.com/learn", "type": "Interactive Courses (Free)"}
                ]
            },
            {
                "stage_num": 3,
                "title": "Model Evaluation & Deep Learning Basics",
                "focus": "Evaluation rigor, neural networks, and PyTorch",
                "time_allocation": "Week 5 - 6 (approx. 30 hrs)",
                "topics": ["Evaluation metrics: Confusion matrix, Precision-Recall, F1-score, ROC-AUC", "Multilayer Perceptrons (MLP), activation functions, backpropagation", "Introduction to PyTorch or TensorFlow for deep neural networks"],
                "practical_tasks": ["Build an image or text classification model using PyTorch", "Properly diagnose overfitting vs underfitting using validation curves"],
                "completion_goal": "Train a neural network with custom layers, loss functions, and optimizers.",
                "resources": [
                    {"name": "PyTorch Official Tutorials", "url": "https://pytorch.org/tutorials/", "type": "Documentation & Code (Free)"}
                ]
            },
            {
                "stage_num": 4,
                "title": "Model Serving & Placement Coding Prep",
                "focus": "FastAPI/Flask API serving, containerization, and coding tests",
                "time_allocation": "Week 7 - 8 (approx. 25 hrs)",
                "topics": ["Wrapping trained models into a REST API (FastAPI / Flask)", "Data serialization (Pickle / ONNX)", "Aptitude tests and core DSA questions"],
                "practical_tasks": ["Deploy a machine learning model behind a REST endpoint on Render", "Solve 40 algorithmic questions on arrays, trees, and matrices"],
                "completion_goal": "Serve real-time predictions via an accessible web endpoint.",
                "resources": [
                    {"name": "FastAPI Documentation", "url": "https://fastapi.tiangolo.com/", "type": "Documentation (Free)"}
                ]
            },
            {
                "stage_num": 5,
                "title": "Portfolio Refinement & Campus Interviews",
                "focus": "Explainability, project demos, and technical ML interviews",
                "time_allocation": "Week 9+ (Continuous)",
                "topics": ["Explaining model trade-offs in interviews", "Feature importance (SHAP / LIME)", "Technical interviews covering gradient descent, loss functions, and metrics"],
                "practical_tasks": ["Publish GitHub repositories with clean Jupyter notebooks, requirements.txt, and live APIs", "Apply to AI/ML and Data Science roles at campus recruiting firms"],
                "completion_goal": "Confidently explain architectural decisions and evaluation trade-offs to senior engineers.",
                "resources": [
                    {"name": "Infosys AI Careers", "url": "https://www.infosys.com/careers.html", "type": "Official Careers (Free)"}
                ]
            }
        ],
        "projects": [
            {
                "title": "Student Academic Risk Early-Warning Classifier",
                "level": "Intermediate",
                "problem": "Identify at-risk students weeks before semester examinations using historical academic and engagement indicators.",
                "skills_practiced": ["Python", "Pandas", "Scikit-Learn", "FastAPI / Flask"],
                "features": ["Multi-class classification (Low, Medium, High Risk)", "Feature importance visualization using Random Forests", "REST API endpoint returning probability distributions"],
                "deliverables": "Working ML model with evaluation report (Precision, Recall, ROC-AUC) and live API deployment.",
                "interview_pitch": "Trained an ensemble classifier achieving 88% recall on at-risk student cohorts, prioritizing recall to prevent false negatives in student counseling."
            },
            {
                "title": "Customer Sentiment Analysis & Review Categorization",
                "level": "Intermediate / Advanced",
                "problem": "Product teams struggle to read thousands of customer feedback entries manually.",
                "skills_practiced": ["NLP", "TF-IDF / Embeddings", "PyTorch / Scikit-Learn", "Streamlit"],
                "features": ["Text preprocessing (tokenization, stop words, lemmatization)", "Sentiment scoring (Positive, Neutral, Negative)", "Interactive Streamlit web demonstration"],
                "deliverables": "Interactive demo where users paste text reviews and inspect confidence intervals.",
                "interview_pitch": "Developed a text categorization pipeline that classifies customer sentiment with 91% accuracy and highlights salient keywords driving dissatisfaction."
            }
        ]
    },

    "Frontend Developer": {
        "title": "Frontend Developer",
        "category": "Web Development",
        "description": "Craft responsive, accessible, pixel-perfect user interfaces and rich web applications that provide seamless user experiences.",
        "suitable_branches": ["CSE", "IT", "AIML", "AIDS"],
        "core_skills": [
            "Semantic HTML5 & Web Accessibility (WCAG)",
            "Advanced CSS3 (Flexbox, CSS Grid, Custom Properties, Animations)",
            "Modern JavaScript (ES6+, DOM Manipulation, Async/Await)",
            "Component-Based Framework (React, Vue, or Angular)",
            "Git & GitHub Version Control",
            "Browser Developer Tools & Performance Profiling"
        ],
        "optional_skills": [
            "TypeScript",
            "Tailwind CSS / CSS Modules",
            "State Management (Redux Toolkit, Zustand)",
            "Unit Testing (Jest, React Testing Library)",
            "Next.js / SSR"
        ],
        "stages": [
            {
                "stage_num": 1,
                "title": "HTML5, Modern CSS & Responsive Architecture",
                "focus": "Pixel-perfect layouts, responsive design, and CSS mastery",
                "time_allocation": "Week 1 - 2 (approx. 20 hrs)",
                "topics": ["Semantic tags, forms, accessibility basics", "CSS Flexbox and CSS Grid deep dive", "Media queries, mobile-first design, fluid typography"],
                "practical_tasks": ["Build 3 fully responsive web pages without CSS frameworks", "Audit web accessibility using Google Chrome Lighthouse to score 95+"],
                "completion_goal": "Code fluid, responsive layouts that render cleanly on mobile, tablet, and desktop screens.",
                "resources": [
                    {"name": "MDN Web Docs - CSS Layout", "url": "https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout", "type": "Documentation (Free)"}
                ]
            },
            {
                "stage_num": 2,
                "title": "Modern JavaScript & Browser APIs",
                "focus": "ES6+ syntax, asynchronous programming, and DOM manipulation",
                "time_allocation": "Week 3 - 4 (approx. 25 hrs)",
                "topics": ["Arrow functions, destructuring, modules, closures", "Promises, async/await, and Fetch API error handling", "DOM events, bubbling, debouncing, and throttling"],
                "practical_tasks": ["Build an interactive weather or movie catalog web app using a public REST API", "Implement client-side search, filtering, and local storage caching"],
                "completion_goal": "Create dynamic browser apps with asynchronous API integration and zero external libraries.",
                "resources": [
                    {"name": "JavaScript.info", "url": "https://javascript.info/", "type": "Interactive Guide (Free)"}
                ]
            },
            {
                "stage_num": 3,
                "title": "React Component Engineering & State Management",
                "focus": "Single Page Application (SPA) architecture and hooks",
                "time_allocation": "Week 5 - 6 (approx. 25 hrs)",
                "topics": ["Functional components, JSX, and Virtual DOM", "Hooks: useState, useEffect, useRef, useMemo, useCallback", "Component lifecycle, client-side routing, and modular styles"],
                "practical_tasks": ["Develop a complete multi-route Single Page Application in React", "Implement custom hooks for API calls and form validations"],
                "completion_goal": "Build scalable, modular component systems with clean separation of UI and business logic.",
                "resources": [
                    {"name": "React Documentation", "url": "https://react.dev/", "type": "Documentation (Free)"}
                ]
            },
            {
                "stage_num": 4,
                "title": "TypeScript & Performance Optimization",
                "focus": "Type safety, web performance, and placement aptitude",
                "time_allocation": "Week 7 - 8 (approx. 25 hrs)",
                "topics": ["TypeScript basics: interfaces, types, generics", "Bundle optimization, code splitting, lazy loading", "Quantitative aptitude and technical interview coding challenges"],
                "practical_tasks": ["Convert a JavaScript project into TypeScript", "Solve 40 array and string coding problems"],
                "completion_goal": "Deploy a performant TypeScript web app with sub-2-second load times.",
                "resources": [
                    {"name": "TypeScript Handbook", "url": "https://www.typescriptlang.org/docs/", "type": "Documentation (Free)"}
                ]
            },
            {
                "stage_num": 5,
                "title": "Portfolio Presentation & Placement Applications",
                "focus": "Portfolio website, live demos, and technical interviews",
                "time_allocation": "Week 9+ (Continuous)",
                "topics": ["Interactive developer portfolio website", "Technical interview questions (Event loop, closures, CSS box model)", "Official employer career submissions"],
                "practical_tasks": ["Publish interactive portfolio with live project demos and GitHub source code", "Apply for Frontend Developer positions on official corporate portals"],
                "completion_goal": "Present polished frontend applications and explain UI architectural decisions.",
                "resources": [
                    {"name": "Wipro Careers", "url": "https://careers.wipro.com", "type": "Official Careers (Free)"}
                ]
            }
        ],
        "projects": [
            {
                "title": "Interactive Analytics & KPI Dashboard",
                "level": "Intermediate",
                "problem": "Administrators require clean visual representations of metrics with real-time filtering.",
                "skills_practiced": ["HTML5/CSS3", "JavaScript / React", "Chart.js / Recharts", "Responsive Layout"],
                "features": ["Dark and light theme toggles", "Interactive charts (bar, line, doughnut)", "Data filtering by date range and category"],
                "deliverables": "Responsive web application hosted live on Vercel/GitHub Pages.",
                "interview_pitch": "Engineered an accessible web dashboard supporting dynamic chart re-rendering, theme transitions, and responsive grid layouts."
            },
            {
                "title": "Interactive Quiz & Technical Assessment Platform",
                "level": "Intermediate",
                "problem": "Students need a timed practice environment to simulate placement coding and aptitude tests.",
                "skills_practiced": ["React / TypeScript", "State Management", "Timer APIs", "Local Storage"],
                "features": ["Timed question navigation", "Instant score report generation with breakdown", "Review mode displaying correct answers and explanations"],
                "deliverables": "Production-ready SPA with full responsive layout and client-side state persistence.",
                "interview_pitch": "Created an interactive assessment portal with real-time countdown management, state persistence, and responsive UI components."
            }
        ]
    },

    "Cybersecurity Analyst": {
        "title": "Cybersecurity Analyst",
        "category": "Security & Infrastructure",
        "description": "Protect university and corporate networks, applications, and data assets against unauthorized access, vulnerabilities, and cyber threats.",
        "suitable_branches": ["CSE", "IT", "AIML", "ECE"],
        "core_skills": [
            "Computer Networking (TCP/IP, OSI Model, DNS, Subnetting)",
            "Linux / Unix Operating System Administration",
            "Security Fundamentals (CIA Triad, Cryptography, Firewalls)",
            "Vulnerability Assessment & OWASP Top 10",
            "Log Analysis & Incident Response Basics",
            "Scripting for Automation (Python or Bash)"
        ],
        "optional_skills": [
            "Wireshark & Packet Analysis",
            "SIEM Fundamentals (Splunk, Elastic)",
            "Penetration Testing Tools (Nmap, Metasploit in authorized labs)",
            "Cloud Security Basics (AWS/Azure)"
        ],
        "stages": [
            {
                "stage_num": 1,
                "title": "Networking Protocols & Linux Foundations",
                "focus": "TCP/IP, packet routing, and Linux terminal command mastery",
                "time_allocation": "Week 1 - 2 (approx. 20 hrs)",
                "topics": ["OSI 7-layer model, TCP vs UDP, IP addressing and subnetting", "DNS, DHCP, HTTP/HTTPS, SSH, FTP protocols", "Linux filesystem navigation, permissions, process management, bash scripting"],
                "practical_tasks": ["Set up a Linux virtual machine (Ubuntu/Kali) and configure user permissions", "Use network diagnostics (ping, traceroute, netstat, nslookup) to map local connectivity"],
                "completion_goal": "Comfortably configure Linux network interfaces and analyze port statuses via the command line.",
                "resources": [
                    {"name": "Linux Journey (Interactive Linux Guide)", "url": "https://linuxjourney.com/", "type": "Tutorials (Free)"},
                    {"name": "Professor Messer Network+ Series", "url": "https://www.professormesser.com/", "type": "Video Training (Free)"}
                ]
            },
            {
                "stage_num": 2,
                "title": "Packet Analysis & Cryptography Essentials",
                "focus": "Wireshark packet sniffing and cryptographic standards",
                "time_allocation": "Week 3 - 4 (approx. 25 hrs)",
                "topics": ["Wireshark capture filters, TCP three-way handshake analysis", "Symmetric vs asymmetric encryption (AES, RSA)", "Hashing algorithms (SHA-256), SSL/TLS certificates, PKI"],
                "practical_tasks": ["Capture and analyze unencrypted vs encrypted traffic (HTTP vs HTTPS) in Wireshark", "Generate SSH key pairs and encrypt/decrypt files using OpenSSL"],
                "completion_goal": "Identify anomalies in packet streams and explain cryptographic handshake mechanisms.",
                "resources": [
                    {"name": "Wireshark User's Guide", "url": "https://www.wireshark.org/docs/wsug_html_chunked/", "type": "Documentation (Free)"}
                ]
            },
            {
                "stage_num": 3,
                "title": "Web Security & OWASP Top 10",
                "focus": "Web application vulnerabilities and secure coding",
                "time_allocation": "Week 5 - 6 (approx. 25 hrs)",
                "topics": ["OWASP Top 10: SQL Injection, Cross-Site Scripting (XSS), CSRF, Broken Auth", "Input sanitization, prepared statements, secure session cookies", "Port scanning with Nmap in authorized practice environments"],
                "practical_tasks": ["Complete 10 hands-on security rooms on TryHackMe / PortSwigger Web Security Academy", "Audit a demo web application for SQL injection and patch the vulnerable code"],
                "completion_goal": "Demonstrate practical understanding of common web vulnerabilities and effective remediation code.",
                "resources": [
                    {"name": "PortSwigger Web Security Academy", "url": "https://portswigger.net/web-security", "type": "Hands-on Labs (Free)"},
                    {"name": "OWASP Top 10 Official Documentation", "url": "https://owasp.org/www-project-top-ten/", "type": "Documentation (Free)"}
                ]
            },
            {
                "stage_num": 4,
                "title": "Security Log Monitoring & Placement Aptitude",
                "focus": "Log inspection, threat detection, and aptitude tests",
                "time_allocation": "Week 7 - 8 (approx. 25 hrs)",
                "topics": ["SIEM log inspection (auth logs, web server access logs)", "Recognizing brute-force attempts and port scans in logs", "Campus placement quantitative aptitude and logical puzzles"],
                "practical_tasks": ["Write a Python script that parses server logs and alerts on repeated failed login attempts", "Complete timed quantitative aptitude test sets"],
                "completion_goal": "Automate log anomaly identification and score well on aptitude assessments.",
                "resources": [
                    {"name": "IndiaBIX Placement Practice", "url": "https://www.indiabix.com/", "type": "Practice Portal (Free)"}
                ]
            },
            {
                "stage_num": 5,
                "title": "Interview Readiness & Job Applications",
                "focus": "Scenario-based technical interviews and verified applications",
                "time_allocation": "Week 9+ (Continuous)",
                "topics": ["Incident response cycle (NIST framework)", "Explaining security concepts to non-technical stakeholders", "Official careers portal submissions"],
                "practical_tasks": ["Document home lab writeups and CTF challenge solutions on GitHub", "Apply to security analyst roles at TCS, Wipro, Infosys, and Cognizant"],
                "completion_goal": "Articulate defensive security principles and incident handling steps in technical interviews.",
                "resources": [
                    {"name": "TCS Security Careers", "url": "https://www.tcs.com/careers", "type": "Official Careers (Free)"}
                ]
            }
        ],
        "projects": [
            {
                "title": "Automated Security Log Parser & Alerting Tool",
                "level": "Intermediate",
                "problem": "System administrators cannot manually inspect thousands of daily server log entries for brute-force attacks.",
                "skills_practiced": ["Python", "Regular Expressions", "Linux Log Formats", "File I/O"],
                "features": ["Parses Apache/Nginx access logs and Linux auth.log", "Calculates failed login frequencies per IP address", "Outputs a structured CSV summary of suspicious IP addresses"],
                "deliverables": "Clean Python script on GitHub with sample log fixtures and a detailed walkthrough.",
                "interview_pitch": "Created a lightweight Python log monitor that parses authentication logs using regular expressions to flag IP addresses attempting brute-force logins."
            },
            {
                "title": "Web Application Vulnerability Audit & Patch Report",
                "level": "Intermediate / Advanced",
                "problem": "Educational web apps often suffer from SQL injection and XSS vulnerabilities due to unsanitized inputs.",
                "skills_practiced": ["OWASP Top 10", "SQL Injection Remediation", "Input Validation", "Documentation"],
                "features": ["Demonstration of SQL injection vulnerability on a controlled local lab", "Code-level fix using parameterized SQL queries", "Comprehensive vulnerability assessment report with CVSS scoring"],
                "deliverables": "GitHub repository with before-and-after code diffs and formal remediation report.",
                "interview_pitch": "Conducted an authorized security review of a student portal, discovering SQL injection vulnerabilities and implementing parameterized queries to remediate the exposure."
            }
        ]
    },

    "Electronics / Embedded Systems Engineer": {
        "title": "Electronics / Embedded Systems Engineer",
        "category": "Hardware & Embedded Systems",
        "description": "Design, program, and interface microcontrollers, embedded firmware, sensor arrays, and circuit hardware for IoT and intelligent physical devices.",
        "suitable_branches": ["ECE", "EEE", "Mechanical"],
        "core_skills": [
            "Embedded C / C++ Programming",
            "Microcontroller Architectures (ARM, AVR, ESP32, or 8051)",
            "Digital Electronics & Logic Design",
            "Hardware Communication Protocols (UART, SPI, I2C)",
            "Circuit Simulation & Schematic Design (KiCAD, Proteus, or Multisim)",
            "Sensors & Actuator Interfacing"
        ],
        "optional_skills": [
            "FreeRTOS Basics",
            "PCB Layout Design",
            "IoT Protocols (MQTT, HTTP)",
            "Oscilloscope & Multimeter Hardware Debugging"
        ],
        "stages": [
            {
                "stage_num": 1,
                "title": "C Programming for Embedded Systems",
                "focus": "Bitwise operations, pointers, and memory manipulation",
                "time_allocation": "Week 1 - 2 (approx. 20 hrs)",
                "topics": ["Pointers, memory addresses, structure packing", "Bitwise operators (AND, OR, XOR, shifts, bit-masking)", "Volatile and const qualifiers, register-level manipulation"],
                "practical_tasks": ["Write C programs manipulating specific hardware bits without affecting neighboring register bits", "Implement circular buffers and state machines in C"],
                "completion_goal": "Comfortably write low-level C code targeting memory-constrained microcontrollers.",
                "resources": [
                    {"name": "Learn-C.org (Interactive C Tutorial)", "url": "https://www.learn-c.org/", "type": "Interactive Guide (Free)"}
                ]
            },
            {
                "stage_num": 2,
                "title": "Microcontrollers & Peripheral Interfacing",
                "focus": "GPIOs, timers, interrupts, and PWM",
                "time_allocation": "Week 3 - 4 (approx. 25 hrs)",
                "topics": ["Microcontroller clock trees, GPIO configurations (input, output, pull-up)", "Hardware timers, counters, and Pulse Width Modulation (PWM)", "Interrupt Service Routines (ISRs) and debouncing"],
                "practical_tasks": ["Interface push-buttons, LEDs, and alphanumeric LCD displays via GPIOs", "Generate PWM signals to control motor speed or LED brightness"],
                "completion_goal": "Write non-blocking microcontroller code using hardware interrupts rather than delay loops.",
                "resources": [
                    {"name": "All About Circuits - Embedded Systems", "url": "https://www.allaboutcircuits.com/", "type": "Tutorials (Free)"}
                ]
            },
            {
                "stage_num": 3,
                "title": "Hardware Protocols & Sensor Integration",
                "focus": "UART, I2C, and SPI bus protocols",
                "time_allocation": "Week 5 - 6 (approx. 25 hrs)",
                "topics": ["UART asynchronous serial communication (baud rates, parity)", "I2C 2-wire serial protocol (addressing, ACK/NACK)", "SPI high-speed synchronous protocol (Master/Slave, clock polarity)"],
                "practical_tasks": ["Interface temperature (DHT11/BMP280) and motion sensors over I2C/SPI", "Transmit sensor readings to a computer terminal over serial UART"],
                "completion_goal": "Inspect and debug multi-sensor communication busses successfully.",
                "resources": [
                    {"name": "SparkFun Electronics Tutorials", "url": "https://learn.sparkfun.com/", "type": "Hardware Guides (Free)"}
                ]
            },
            {
                "stage_num": 4,
                "title": "Schematic Design, IoT & Placement Aptitude",
                "focus": "KiCAD schematics, IoT connectivity, and campus aptitude",
                "time_allocation": "Week 7 - 8 (approx. 25 hrs)",
                "topics": ["Schematic capture in KiCAD", "Connecting ESP32 to Wi-Fi and sending telemetry via MQTT/HTTP", "Quantitative aptitude, electronic circuit analysis questions"],
                "practical_tasks": ["Design a circuit schematic for a sensor node in KiCAD", "Solve 40 quantitative aptitude problems and digital electronics questions"],
                "completion_goal": "Design readable schematics and pass technical electronic written tests.",
                "resources": [
                    {"name": "KiCAD Official Documentation", "url": "https://docs.kicad.org/", "type": "Documentation (Free)"}
                ]
            },
            {
                "stage_num": 5,
                "title": "Hardware Portfolio & Core Company Interviews",
                "focus": "Documenting hardware prototypes, videos, and technical interviews",
                "time_allocation": "Week 9+ (Continuous)",
                "topics": ["Documenting hardware builds with schematics and demo videos", "Explaining interrupt timing and bus protocols in interviews", "Applications to core electronics and IoT employers"],
                "practical_tasks": ["Upload firmware code to GitHub with clear wiring diagrams and photos", "Apply to core embedded roles at Robert Bosch, Texas Instruments, Wipro VLSI, and Tata Elxsi"],
                "completion_goal": "Present working hardware projects and answer low-level register manipulation questions.",
                "resources": [
                    {"name": "Tata Elxsi Careers", "url": "https://www.tataelxsi.com/careers", "type": "Official Careers (Free)"}
                ]
            }
        ],
        "projects": [
            {
                "title": "IoT Environmental Telemetry Node",
                "level": "Intermediate",
                "problem": "Laboratories and agricultural fields require continuous monitoring of temperature and humidity.",
                "skills_practiced": ["Embedded C / C++", "ESP32 / Arduino", "I2C Protocol", "MQTT / HTTP"],
                "features": ["Periodic temperature & humidity reading over I2C", "Wi-Fi connection with auto-reconnect logic", "Cloud dashboard publishing using MQTT"],
                "deliverables": "Firmware source code on GitHub with schematic diagram and live dashboard.",
                "interview_pitch": "Designed an ESP32-based telemetry node that reads digital sensors over I2C and publishes telemetry packets with deep-sleep power management."
            },
            {
                "title": "Digital Access Control System with EEPROM Storage",
                "level": "Intermediate",
                "problem": "Secure lab doors need digital keypad entry with local credential persistence even during power loss.",
                "skills_practiced": ["Microcontroller C", "Keypad Scanning", "EEPROM", "Interrupts"],
                "features": ["Matrix keypad debouncing algorithm", "Password verification and lock activation", "Non-volatile password storage in internal EEPROM"],
                "deliverables": "C code repository with Proteus / Multisim simulation files and README documentation.",
                "interview_pitch": "Implemented an interrupt-driven embedded security lock utilizing matrix keypad scanning and hardware EEPROM for persistent credential storage."
            }
        ]
    }
}

# Add aliases for common role variants so any selection matches cleanly
ROLE_ALIASES = {
    "Backend Developer": "Software Developer",
    "Python Developer": "Software Developer",
    "Java Developer": "Software Developer",
    "QA / Software Testing Engineer": "Software Developer",
    "DevOps Engineer": "Full-Stack Developer",
    "Cloud Engineer": "Full-Stack Developer",
    "Data Scientist": "AI/ML Engineer",
    "Business Analyst": "Data Analyst"
}

def get_role_data(role_name: str) -> Dict[str, Any]:
    """Resolves a role name (including aliases or custom titles) to structured guidance data."""
    if not role_name:
        role_name = "Software Developer"
    
    clean_name = role_name.strip()
    if clean_name in CAREER_ROLES:
        return CAREER_ROLES[clean_name]
    
    # Check alias map
    if clean_name in ROLE_ALIASES:
        target = ROLE_ALIASES[clean_name]
        data = dict(CAREER_ROLES[target])
        data["title"] = clean_name
        return data

    # Fallback to Software Developer structure for any unrecognized custom role
    data = dict(CAREER_ROLES["Software Developer"])
    data["title"] = clean_name
    data["description"] = f"Comprehensive career preparation and skills roadmap tailored for {clean_name}."
    return data

# ==============================================================================
# 2. PLACEMENT & INTERVIEW PRACTICE QUESTION BANK
# ==============================================================================

INTERVIEW_PREP_BANK = {
    "Quantitative Aptitude": [
        {
            "topic": "Percentages & Ratios",
            "question": "A student scores 75% in an exam of 800 marks. If the passing threshold is increased from 60% to 70%, by how many marks did the student exceed the new passing mark?",
            "options": ["A) 40 marks", "B) 80 marks", "C) 120 marks", "D) 60 marks"],
            "answer": "A) 40 marks",
            "explanation": "Student score = 75% of 800 = 600 marks. New pass mark = 70% of 800 = 560 marks. Excess = 600 - 560 = 40 marks."
        },
        {
            "topic": "Time & Work",
            "question": "Engineer A can complete a feature in 12 days, and Engineer B can complete it in 6 days. Working together, how many days will they take?",
            "options": ["A) 3 days", "B) 4 days", "C) 5 days", "D) 8 days"],
            "answer": "B) 4 days",
            "explanation": "Combined 1-day work rate = (1/12) + (1/6) = 3/12 = 1/4. Hence, they take 4 days together."
        }
    ],
    "Logical Reasoning": [
        {
            "topic": "Series & Patterns",
            "question": "Find the next number in the sequence: 4, 9, 25, 49, 121, ?",
            "options": ["A) 144", "B) 169", "C) 196", "D) 225"],
            "answer": "B) 169",
            "explanation": "The series consists of squares of prime numbers: 2^2=4, 3^2=9, 5^2=25, 7^2=49, 11^2=121. The next prime is 13, and 13^2 = 169."
        }
    ],
    "Technical Interview Questions": [
        {
            "topic": "Data Structures",
            "question": "When would you prefer an Array over a Linked List?",
            "answer": "Arrays provide O(1) random access by index and have better cache locality due to contiguous memory allocation. Linked Lists are preferred when frequent O(1) insertions/deletions at known positions are needed without memory reallocation."
        },
        {
            "topic": "Databases",
            "question": "What is the difference between WHERE and HAVING in SQL?",
            "answer": "WHERE filters rows before any grouping occurs and cannot be used with aggregate functions. HAVING filters aggregated groups after the GROUP BY clause has been evaluated."
        }
    ],
    "HR & Behavioral Questions": [
        {
            "topic": "STAR Method (Situation, Task, Action, Result)",
            "question": "Tell me about a time you faced a difficult deadline on a project and how you handled it.",
            "answer": "Structure your response using STAR: Briefly describe the Situation and project stakes, the specific Task assigned to you, the deliberate Actions you took (prioritization, communication with your mentor, extra effort), and the measurable positive Result achieved."
        },
        {
            "topic": "Self-Awareness",
            "question": "What is an area of technical improvement you are currently working on?",
            "answer": "Select a real technical skill (e.g. system design or unit testing), describe the specific learning step you are taking (e.g. building a project or reading documentation), and share what you have already learned."
        }
    ]
}
